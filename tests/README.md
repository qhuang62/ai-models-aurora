# Testing Framework

This directory contains the test suite for ai-models-aurora.

## Running Tests

### Basic Test Execution
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_code.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=ai_models_aurora
```

### Test Categories

**Unit Tests** (`test_code.py`):
- Import verification
- Model class definitions
- Configuration validation
- No GPU/data requirements

**Integration Tests** (future):
- Full workflow testing
- Data download verification
- Aurora execution validation

**GPU Tests** (skipped by default):
- Model instantiation
- Inference testing
- Performance benchmarks

### Selective Test Execution
```bash
# Skip GPU-dependent tests
pytest -m "not gpu"

# Skip slow tests
pytest -m "not slow"

# Run only integration tests
pytest -m "integration"
```

## Test Environment Setup

### Minimal Testing (CI/CD)
```bash
pip install pytest pytest-cov
pytest
```

### Full Testing (with GPU)
```bash
pip install -r requirements.txt
pip install -r tests/requirements.txt
pytest --cov=ai_models_aurora
```

## Current Test Status

**✅ Implemented:**
- Basic import tests
- Model class verification
- Configuration validation
- Test infrastructure setup

**🚧 Future Development:**
- Integration testing with ai-models CLI
- Data download testing
- Aurora inference validation
- Performance benchmarking
- Error handling verification

## Contributing Tests

### Adding New Tests
1. Create test files following `test_*.py` naming
2. Use appropriate pytest markers (`@pytest.mark.gpu`, etc.)
3. Include docstrings explaining test purpose
4. Mock external dependencies when possible

### Test Guidelines
- **Fast by default**: Avoid GPU/network operations in basic tests
- **Isolated**: Each test should be independent
- **Descriptive**: Clear test names and docstrings
- **Robust**: Handle expected failures gracefully

### Mock Testing Example
```python
import pytest
from unittest.mock import patch, MagicMock

@patch('ai_models_aurora.model.torch.cuda.is_available')
def test_gpu_detection(mock_cuda):
    mock_cuda.return_value = True
    # Test GPU-related functionality without actual GPU
```

## Test Data

For future integration tests, consider:
- **Sample GRIB files**: Small test datasets
- **Mock responses**: ECMWF API simulation
- **Reference outputs**: Expected Aurora results
- **Configuration files**: Test parameter sets

---

**Note**: This test framework is designed to grow with the project. Start simple and add complexity as needed.