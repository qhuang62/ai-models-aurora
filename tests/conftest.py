"""pytest configuration for ai-models-aurora tests."""

import pytest
import sys
from pathlib import Path

# Add src directory to Python path for testing
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "gpu: marks tests as requiring GPU (deselect with '-m \"not gpu\"')"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )


@pytest.fixture
def sample_config():
    """Provide sample configuration for testing."""
    return {
        "lead_time": 24,
        "output_dir": "/tmp/test_aurora",
        "model_version": "0.25-pretrained"
    }