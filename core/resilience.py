"""
Resilience and monitoring for the procurement system.
Includes retry logic, timeout handling, and circuit breakers.
"""
import time
import functools
from typing import Any, Callable, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from core.logging import get_logger

logger = get_logger("resilience")

class CircuitBreaker:
    """Circuit breaker to prevent cascading failures."""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
                logger.info(f"Circuit breaker entering HALF_OPEN state")
            else:
                raise Exception(f"Circuit breaker OPEN for {func.__name__}")
        
        try:
            result = func(*args, **kwargs)
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failures = 0
                logger.info(f"Circuit breaker CLOSED for {func.__name__}")
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure_time = time.time()
            
            if self.failures >= self.failure_threshold:
                self.state = "OPEN"
                logger.error(f"Circuit breaker OPEN for {func.__name__}", error=str(e))
            raise


def with_retry(max_attempts: int = 3, backoff_seconds: int = 2):
    """Decorator for retry logic with exponential backoff."""
    def decorator(func):
        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=backoff_seconds, min=1, max=30),
            retry=retry_if_exception_type((ConnectionError, TimeoutError)),
            reraise=True
        )
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                logger.debug(f"Attempting {func.__name__}")
                return func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Retry triggered for {func.__name__}", error=str(e))
                raise
        return wrapper
    return decorator


def with_timeout(seconds: int = 30):
    """Decorator to enforce timeout on function execution."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError(f"{func.__name__} exceeded {seconds}s timeout")
            
            # Set timeout (Unix-like systems)
            try:
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(seconds)
                result = func(*args, **kwargs)
                signal.alarm(0)
                return result
            except AttributeError:
                # Windows fallback - no timeout enforcement
                logger.warning(f"Timeout not supported on this platform for {func.__name__}")
                return func(*args, **kwargs)
        return wrapper
    return decorator


class LoopGuard:
    """Prevent infinite loops in agent workflows."""
    
    def __init__(self, max_iterations: int = 10):
        self.max_iterations = max_iterations
        self.iteration_count = 0
    
    def check(self) -> bool:
        """Returns True if loop should continue, False if limit reached."""
        self.iteration_count += 1
        if self.iteration_count > self.max_iterations:
            logger.error(f"Loop limit exceeded: {self.iteration_count} iterations")
            return False
        return True
    
    def reset(self):
        """Reset iteration counter."""
        self.iteration_count = 0


class HealthMonitor:
    """Monitor system health and component status."""
    
    def __init__(self):
        self.component_status = {}
        self.last_check = {}
    
    def register_component(self, name: str, check_func: Callable):
        """Register a component with its health check function."""
        self.component_status[name] = check_func
    
    def check_health(self) -> dict:
        """Run health checks on all components."""
        results = {}
        for name, check_func in self.component_status.items():
            try:
                status = check_func()
                results[name] = {"status": "healthy" if status else "unhealthy", "timestamp": time.time()}
                self.last_check[name] = time.time()
            except Exception as e:
                results[name] = {"status": "error", "error": str(e), "timestamp": time.time()}
                logger.error(f"Health check failed for {name}", error=str(e))
        return results


# Global instances
health_monitor = HealthMonitor()
circuit_breakers = {}

def get_circuit_breaker(name: str) -> CircuitBreaker:
    """Get or create a circuit breaker for a component."""
    if name not in circuit_breakers:
        circuit_breakers[name] = CircuitBreaker()
    return circuit_breakers[name]
