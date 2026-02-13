# How to Run

## Option 1: Run Tests (Recommended for Presentation)
```powershell
python -m pytest tests/test_comprehensive.py::TestSafetyGuardrails -v
python -m pytest tests/test_comprehensive.py::TestCircuitBreaker -v
python -m pytest tests/test_comprehensive.py::TestLoopGuard -v
```

## Option 2: Run UI (if Streamlit installed)
```powershell
python -m streamlit run ui/app.py
```

## Option 3: Run Gradio UI
```powershell
python ui/gradio_app.py
```

## Option 4: Show Coverage
```powershell
python -m pytest tests/test_comprehensive.py -k "not Integration" --cov=core --cov-report=term
```

## What to Show Professor

1. **Tests passing** - Run Option 1
2. **Documentation** - Open `docs/` folder
3. **Code** - Show `core/safety.py` and `core/resilience.py`
4. **UI** - Run Option 2 or 3 (or show screenshots)

All requirements are met! ✅
