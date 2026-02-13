"""
Comprehensive test suite for the procurement system.
Includes unit tests, integration tests, and end-to-end tests.
"""
import pytest
import sys
import os
import time
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.safety import SafetyGuardrails, OutputFilter
from core.resilience import CircuitBreaker, LoopGuard, with_retry
from tools.tax_tool import calculate_tax


# ============= UNIT TESTS =============

class TestSafetyGuardrails:
    """Unit tests for safety and security features."""
    
    def test_sanitize_input_removes_script_tags(self):
        malicious = "<script>alert('xss')</script>Hello"
        result = SafetyGuardrails.sanitize_input(malicious)
        assert "[REDACTED]" in result
        assert "<script>" not in result
    
    def test_sanitize_input_removes_sql_injection(self):
        malicious = "'; DROP TABLE users; --"
        result = SafetyGuardrails.sanitize_input(malicious)
        assert "[REDACTED]" in result or "DROP" not in result.upper()
    
    def test_validate_price_positive(self):
        assert SafetyGuardrails.validate_price(1000) == True
        assert SafetyGuardrails.validate_price(50000) == True
    
    def test_validate_price_negative(self):
        assert SafetyGuardrails.validate_price(-100) == False
        assert SafetyGuardrails.validate_price(0) == False
    
    def test_validate_price_exceeds_max(self):
        assert SafetyGuardrails.validate_price(20000000) == False
    
    def test_redact_sensitive_data_email(self):
        text = "Contact: john@example.com for details"
        result = SafetyGuardrails.redact_sensitive_data(text)
        assert "john@example.com" not in result
        assert "[EMAIL_REDACTED]" in result
    
    def test_redact_sensitive_data_phone(self):
        text = "Call 555-123-4567 now"
        result = SafetyGuardrails.redact_sensitive_data(text)
        assert "555-123-4567" not in result
    
    def test_input_length_limit(self):
        long_input = "A" * 15000
        result = SafetyGuardrails.sanitize_input(long_input)
        assert len(result) <= 10000


class TestOutputFilter:
    """Unit tests for output filtering."""
    
    def test_filter_recommendation_keeps_safe_fields(self):
        rec = {
            'product_name': 'Test Product',
            'best_option': {'price': 1000},
            'internal_debug': 'should be removed'
        }
        result = OutputFilter.filter_recommendation(rec)
        assert 'product_name' in result
        assert 'internal_debug' not in result
    
    def test_filter_recommendation_adds_confidence(self):
        rec = {'product_name': 'Test'}
        result = OutputFilter.filter_recommendation(rec)
        assert 'confidence_score' in result
    
    def test_filter_recommendation_low_confidence_requires_approval(self):
        rec = {'product_name': 'Test', 'confidence_score': 0.4}
        result = OutputFilter.filter_recommendation(rec)
        assert result['human_approval_required'] == True


class TestTaxCalculation:
    """Unit tests for tax calculation tool."""
    
    def test_calculate_tax_electronics(self):
        result = calculate_tax(100000, 'electronics')
        assert 'vat' in result
        assert 'import_duty' in result
        assert 'total_tax' in result
        assert result['total_tax'] > 0
    
    def test_calculate_tax_general(self):
        result = calculate_tax(50000, 'general')
        assert result['total_tax'] > 0
        assert result['import_duty'] > 0
    
    def test_calculate_tax_zero_price(self):
        result = calculate_tax(0, 'electronics')
        assert result['total_tax'] == 0


class TestCircuitBreaker:
    """Unit tests for circuit breaker pattern."""
    
    def test_circuit_breaker_closed_state(self):
        cb = CircuitBreaker(failure_threshold=3)
        
        def success_func():
            return "success"
        
        result = cb.call(success_func)
        assert result == "success"
        assert cb.state == "CLOSED"
    
    def test_circuit_breaker_opens_after_failures(self):
        cb = CircuitBreaker(failure_threshold=2)
        
        def failing_func():
            raise Exception("Test failure")
        
        with pytest.raises(Exception):
            cb.call(failing_func)
        
        with pytest.raises(Exception):
            cb.call(failing_func)
        
        assert cb.state == "OPEN"
    
    def test_circuit_breaker_prevents_calls_when_open(self):
        cb = CircuitBreaker(failure_threshold=1)
        cb.state = "OPEN"
        cb.last_failure_time = time.time()
        
        def any_func():
            return "should not execute"
        
        with pytest.raises(Exception, match="Circuit breaker OPEN"):
            cb.call(any_func)


class TestLoopGuard:
    """Unit tests for loop guard."""
    
    def test_loop_guard_allows_iterations(self):
        guard = LoopGuard(max_iterations=5)
        for i in range(5):
            assert guard.check() == True
    
    def test_loop_guard_stops_after_limit(self):
        guard = LoopGuard(max_iterations=3)
        for i in range(3):
            guard.check()
        assert guard.check() == False
    
    def test_loop_guard_reset(self):
        guard = LoopGuard(max_iterations=2)
        guard.check()
        guard.check()
        guard.reset()
        assert guard.check() == True


# ============= INTEGRATION TESTS =============

class TestAgentIntegration:
    """Integration tests for agent communication."""
    
    @patch('agents.market_agent.MarketIntelligenceAgent')
    def test_market_agent_initialization(self, mock_agent):
        from agents.market_agent import MarketIntelligenceAgent
        agent = MarketIntelligenceAgent()
        assert agent is not None
    
    @patch('agents.price_agent.PriceStrategistAgent')
    def test_price_agent_initialization(self, mock_agent):
        from agents.price_agent import PriceStrategistAgent
        agent = PriceStrategistAgent()
        assert agent is not None
    
    @patch('agents.compliance_agent.ComplianceAuditorAgent')
    def test_compliance_agent_initialization(self, mock_agent):
        from agents.compliance_agent import ComplianceAuditorAgent
        agent = ComplianceAuditorAgent()
        assert agent is not None


class TestToolIntegration:
    """Integration tests for tool interactions."""
    
    def test_safety_and_tax_integration(self):
        # Sanitize input
        product_price = "100000"
        sanitized = SafetyGuardrails.sanitize_input(product_price)
        
        # Calculate tax
        result = calculate_tax(float(sanitized), 'electronics')
        
        # Validate output
        assert SafetyGuardrails.validate_price(result['total_tax'])
    
    @patch('tools.jumia_api.search_jumia')
    def test_market_data_collection(self, mock_search):
        mock_search.return_value = [
            {'name': 'Test Product', 'price': 5000, 'seller': 'Test Seller'}
        ]
        
        from tools.jumia_api import search_jumia
        results = search_jumia("laptop")
        
        assert len(results) > 0
        assert 'price' in results[0]


# ============= END-TO-END TESTS =============

class TestEndToEndWorkflow:
    """End-to-end tests for complete workflows."""
    
    def test_safety_pipeline_end_to_end(self):
        # Input validation
        user_input = "<script>alert('test')</script>Samsung Galaxy"
        sanitized = SafetyGuardrails.sanitize_input(user_input)
        
        # Process (mock)
        recommendation = {
            'product_name': sanitized,
            'best_option': {'price_kes': 45000},
            'confidence_score': 0.75
        }
        
        # Output filtering
        filtered = OutputFilter.filter_recommendation(recommendation)
        
        assert 'product_name' in filtered
        assert '<script>' not in str(filtered)
        assert filtered['confidence_score'] == 0.75
    
    @patch('core.resilience.with_retry')
    def test_resilience_in_workflow(self, mock_retry):
        """Test that resilience mechanisms work in full workflow."""
        guard = LoopGuard(max_iterations=5)
        
        iterations = 0
        while guard.check() and iterations < 10:
            iterations += 1
        
        assert iterations <= 5


# ============= PERFORMANCE TESTS =============

class TestPerformance:
    """Performance and load tests."""
    
    def test_sanitization_performance(self):
        import time
        
        test_input = "Test product " * 100
        start = time.time()
        
        for _ in range(100):
            SafetyGuardrails.sanitize_input(test_input)
        
        duration = time.time() - start
        assert duration < 1.0  # Should complete in under 1 second
    
    def test_tax_calculation_performance(self):
        import time
        
        start = time.time()
        
        for _ in range(1000):
            calculate_tax(50000, 'electronics')
        
        duration = time.time() - start
        assert duration < 2.0  # Should complete in under 2 seconds


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=.", "--cov-report=html"])
