# Development Guide

This guide covers the technical architecture and development aspects of the ai-models-aurora project.

## Project Architecture

### Core Components

#### 1. Aurora Plugin (`src/ai_models_aurora/`)
The official ECMWF ai-models plugin implementation for Microsoft's Aurora model.

**Main Module: `model.py`**
- **AuroraModel**: Base class implementing the ai-models interface
- **Aurora0p25Pretrained**: 0.25° resolution pretrained model
- **Aurora0p25FineTuned**: 0.25° resolution fine-tuned model
- **Aurora0p1FineTuned**: 0.1° high-resolution fine-tuned model

**Key Features:**
```python
# Model variants available
models = {
    "0.25-pretrained": Aurora0p25Pretrained,
    "0.25-finetuned": Aurora0p25FineTuned, 
    "0.1-finetuned": Aurora0p1FineTuned,
    "default": Aurora0p1FineTuned
}
```

**Technical Specifications:**
- **Input Variables**:
  - Surface: `2t`, `10u`, `10v`, `msl`
  - Atmospheric: `z`, `u`, `v`, `t`, `q`
  - Pressure Levels: 1000-50 hPa (13 levels)
- **Grid Resolution**: 0.25° or 0.1° global
- **Lagged Inputs**: -6h and 0h (two time steps)
- **Output Format**: GRIB2 with ECMWF conventions

#### 2. Automation Scripts (`scripts/`)
Production-ready automation for operational forecasting.

**Main Script: `ecmwf_aurora_automation.py`**
- **ECMWFAuroraAutomation**: Main automation class
- **Workflow**: Cycle detection → Data download → Aurora execution → NetCDF conversion
- **Integration**: Uses ai-models CLI with ECMWF Open Data

#### 3. Interactive Notebooks
- **`Aurora_RealTime_Weather_Forecasting.ipynb`**: Complete demonstration workflow
- **Educational**: Step-by-step process explanation
- **Research**: Interactive development and visualization

## Technical Details

### Aurora Model Integration

The Aurora plugin integrates with the ai-models framework through:

```python
# Entry points in pyproject.toml
entry-points."ai_models.model".aurora = "ai_models_aurora.model:model"
entry-points."ai_models.model"."aurora-0.1-finetuned" = "ai_models_aurora.model:Aurora0p1FineTuned"
```

### Data Flow Architecture

```
ECMWF IFS Open Data → ai-models CLI → Aurora Plugin → GPU Inference → GRIB Output
                                     ↓
                              Batch Processing:
                              - Surface variables
                              - Atmospheric levels  
                              - Static variables
                              - Metadata handling
```

### GPU Acceleration

Aurora leverages PyTorch for GPU acceleration:

```python
# Model execution (simplified)
model = model.to(self.device)  # Move to GPU
model.eval()                   # Inference mode

with torch.inference_mode():
    for pred in rollout(model, batch, steps=self.lead_time // 6):
        # Process 6-hour time steps
        self.write(data, template=template, step=step)
```

### Variable Processing

**Surface Variables:**
- Shape: `(Batch, Time, Lat, Lon)`
- Variables: 2m temperature, 10m winds, sea level pressure

**Atmospheric Variables:**
- Shape: `(Batch, Time, Level, Lat, Lon)`
- Variables: Geopotential, winds, temperature, humidity
- Levels: 13 pressure levels from 1000-50 hPa

**Static Variables:**
- Topography and land-sea mask
- Loaded from pickle files
- Shape: `(Lat, Lon)`

## Development Setup

### Local Development

```bash
# Clone repository
git clone <repository-url>
cd ai-models-aurora

# Create development environment
conda create -n aurora-dev python=3.10
conda activate aurora-dev

# Install in development mode
pip install -e .
pip install -r scripts/requirements.txt

# Install additional dev tools
pip install pre-commit pytest black isort
```

### Code Structure

```
src/ai_models_aurora/
├── __init__.py          # Package initialization
├── model.py            # Core Aurora plugin implementation
└── _version.py         # Version management (auto-generated)
```

### Testing Framework

**Current Status**: Minimal test suite
```python
# tests/test_code.py
def test_code():
    pass  # Placeholder for future tests
```

**Planned Testing:**
- Unit tests for model classes
- Integration tests with ai-models CLI
- Performance benchmarks
- Data validation tests

## Model Variants

### Aurora 0.25° Pretrained
- **Use Case**: General weather forecasting
- **Training**: Pretrained on reanalysis data
- **LoRA**: Disabled
- **Checkpoint**: `aurora-0.25-pretrained.ckpt`

### Aurora 0.25° Fine-tuned
- **Use Case**: Enhanced operational forecasting
- **Training**: Fine-tuned on recent operational data
- **LoRA**: Enabled
- **Checkpoint**: `aurora-0.25-finetuned.ckpt`

### Aurora 0.1° Fine-tuned (Default)
- **Use Case**: High-resolution forecasting
- **Training**: Fine-tuned for detailed predictions
- **LoRA**: Enabled
- **Checkpoint**: `aurora-0.1-finetuned.ckpt`
- **Class**: `AuroraHighRes`

## Configuration Management

### Model Selection
```bash
# Use specific model variant
ai-models aurora --model-version 0.25-pretrained

# Use high-resolution model (default)
ai-models aurora --model-version 0.1-finetuned

# Enable/disable LoRA
ai-models aurora --lora true
```

### Performance Tuning
- **GPU Memory**: Monitor usage during inference
- **Batch Size**: Fixed at 1 for current implementation
- **Time Steps**: 6-hour intervals (standard for Aurora)
- **Lead Time**: Configurable up to 240+ hours

## Contributing

### Code Style
- **Python**: Follow PEP 8 conventions
- **Formatting**: Use black and isort
- **Type Hints**: Encouraged for new code
- **Documentation**: Docstrings for all public methods

### Pull Request Process
1. **Fork** the repository
2. **Create** feature branch
3. **Implement** changes with tests
4. **Format** code with pre-commit hooks
5. **Submit** pull request with description

### Development Priorities
1. **Testing**: Expand test coverage
2. **Documentation**: API documentation
3. **Performance**: Optimization studies
4. **Features**: Additional model variants
5. **Integration**: Enhanced automation tools

## Debugging and Troubleshooting

### Common Development Issues

**1. CUDA/GPU Problems**
```bash
# Check PyTorch CUDA
python -c "import torch; print(torch.cuda.is_available())"

# Monitor GPU usage
nvidia-smi -l 1
```

**2. Model Loading Issues**
```python
# Debug model checkpoint loading
LOG.info("Loading Aurora model from %s", path)
model.load_checkpoint_local(path, strict=False)
```

**3. Memory Issues**
- Monitor GPU memory usage
- Reduce lead time for testing
- Check tensor shapes and dtypes

### Logging and Monitoring
```python
import logging
LOG = logging.getLogger(__name__)

# Key logging points
LOG.info("Starting inference")
LOG.info("Loading Aurora model to device %s", self.device)
```

## Future Development

### Planned Enhancements
- **Ensemble Forecasting**: Multiple model runs
- **Data Assimilation**: Integration with observations
- **Post-processing**: Statistical corrections
- **Visualization**: Enhanced plotting capabilities
- **APIs**: RESTful service interfaces

### Research Opportunities
- **Model Validation**: Systematic accuracy assessment
- **Bias Correction**: Statistical post-processing
- **Downscaling**: High-resolution regional applications
- **Climate Studies**: Long-term prediction analysis

---

This development guide provides the technical foundation for contributing to and extending the ai-models-aurora project.