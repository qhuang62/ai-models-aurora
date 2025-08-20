# Aurora Real-Time Weather Forecasting

Near real-time global weather forecasting using Microsoft's Aurora AI model with ECMWF Open Data integration. This project demonstrates the complete workflow from operational data acquisition to high-resolution AI-powered weather prediction.

## Overview

**Aurora** is a state-of-the-art foundation model for atmospheric forecasting developed by Microsoft Research ([arXiv:2405.13063](https://arxiv.org/abs/2405.13063)). This implementation integrates Aurora with ECMWF's Integrated Forecasting System (IFS) Open Data to enable near real-time global weather prediction at 0.25° resolution.

**Key Features:**
- **Automated Data Access**: Real-time detection and download of latest IFS cycles
- **AI-Powered Forecasting**: Transformer-based neural weather model
- **Production Ready**: Complete workflow from data acquisition to forecast output
- **Multiple Formats**: Outputs in both GRIB and NetCDF formats
- **HPC Optimized**: Designed for GPU-accelerated supercomputing environments

Aurora was created by Cristian Bodnar, Wessel P. Bruinsma, Ana Lucic, Megan Stanley, Johannes Brandstetter, Patrick Garvan, Maik Riechert, Jonathan Weyn, Haiyu Dong, Anna Vaughan, Jayesh K. Gupta, Kit Tambiratnam, Alex Archibald, Elizabeth Heider, Max Welling, Richard E. Turner, Paris Perdikaris.

**Documentation**: https://microsoft.github.io/aurora/intro.html  
**License**: Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)

## Quick Start

### Installation

```bash
# Install ai-models framework and Aurora plugin
pip install ai-models ai-models-aurora

# Install additional dependencies for data processing
pip install ecmwf-opendata xarray cfgrib netcdf4
```

### Basic Usage

```bash
# Interactive notebook demonstration
jupyter notebook Aurora_RealTime_Weather_Forecasting.ipynb

# Automated production script
python scripts/ecmwf_aurora_automation.py --lead-time 72

# HPC batch job submission
sbatch scripts/aurora_daily.slurm
```

## Project Structure

```
ai-models-aurora/
├── Aurora_RealTime_Weather_Forecasting.ipynb  # Interactive demonstration notebook
├── README.md                                   # This file
├── LICENSE                                     # Project license
├── pyproject.toml                             # Python package configuration
├── aurora-0.1-static.pickle                   # Aurora model weights (downloaded)
├── data/                                       # Output directory for forecasts
├── demo_output/                               # Example outputs from notebook runs
├── docs/                                       # Additional documentation
├── examples/                                   # Example configurations and tutorials
├── scripts/                                    # Production automation scripts
│   ├── ecmwf_aurora_automation.py             # Main automation script
│   ├── aurora_daily.slurm                     # Slurm batch job template
│   ├── setup_automation.sh                    # Environment setup
│   ├── install_dependencies.sh                # Dependency installation
│   ├── requirements.txt                       # Python dependencies
│   └── README.md                              # Scripts documentation
├── src/                                        # Source code
│   └── ai_models_aurora/                      # Official Aurora plugin for ai-models
│       ├── __init__.py                        # Package initialization
│       ├── model.py                          # Core Aurora model implementations
│       └── _version.py                       # Version management
└── tests/                                      # Test suite (minimal)
    ├── test_code.py                          # Placeholder test file
    └── requirements.txt                      # Test dependencies
```

## Workflow Overview

### 1. Data Acquisition
- **Source**: ECMWF IFS Open Data (updated 4x daily at 00, 06, 12, 18 UTC)
- **Variables**: Surface (2t, 2d, 10u, 10v, msl, tp, sp, tcwv) and pressure levels (u, v, t, q)
- **Resolution**: 0.25° global grid
- **Format**: GRIB2 with automatic cycle detection

### 2. AI Forecasting
- **Model**: Microsoft Aurora transformer-based foundation model
- **Framework**: ai-models CLI integration
- **Acceleration**: GPU-optimized inference
- **Lead Times**: Configurable up to 240+ hours

### 3. Output Processing
- **Primary**: GRIB format for meteorological applications
- **Analysis**: NetCDF conversion with CF-compliant metadata
- **Validation**: Automated quality checks and visualization
- **Archiving**: Organized storage with summary reports

## Usage Examples

### Interactive Development
```bash
# Start Jupyter for interactive exploration
jupyter notebook Aurora_RealTime_Weather_Forecasting.ipynb
```

### Automated Production
```bash
# Run forecast with default 72-hour lead time
python scripts/ecmwf_aurora_automation.py

# Custom configuration
python scripts/ecmwf_aurora_automation.py \
    --lead-time 120 \
    --output-dir ./custom_forecasts \
    --keep-intermediate
```

### HPC Batch Processing
```bash
# Submit daily forecast job
sbatch scripts/aurora_daily.slurm

# Submit with custom parameters
LEAD_TIME=96 OUTPUT_DIR="/scratch/forecasts" sbatch scripts/aurora_daily.slurm
```

## Technical Requirements

### System Requirements
- **GPU**: CUDA-compatible GPU with ≥8GB memory (recommended: A100, V100)
- **RAM**: ≥32GB system memory
- **Storage**: ≥10GB available space per forecast
- **Network**: Internet access for ECMWF Open Data

### Software Dependencies
- **Python**: ≥3.8
- **Core**: `ai-models`, `ai-models-aurora`
- **Data**: `ecmwf-opendata`, `xarray`, `cfgrib`, `netcdf4`
- **Compute**: `torch` (with CUDA support)
- **Optional**: `cartopy` (for advanced mapping), `matplotlib` (for visualization)

## Performance Characteristics

### Typical Runtimes (A100 GPU)
- **Data Download**: 5-15 minutes
- **Aurora Inference**: 10-30 minutes (72h forecast)
- **Post-processing**: 2-5 minutes
- **Total Workflow**: ~20-50 minutes

### Output Sizes
- **Input Data**: ~35MB (surface + pressure levels)
- **Aurora Output**: ~1-3GB (depends on lead time)
- **NetCDF Processed**: ~500MB-1GB
- **Total per Forecast**: ~2-5GB

## Contributing

This project follows the open science principles:
1. **Reproducibility**: All workflows are fully documented and automated
2. **Accessibility**: Designed for educational and research use
3. **Transparency**: Open-source implementation with clear documentation
4. **Interoperability**: Standard formats and interfaces

### Development Setup
```bash
# Clone and setup development environment
git clone <repository-url>
cd ai-models-aurora
pip install -e .
pip install -r scripts/requirements.txt
```

## Support and References

### Documentation
- **Getting Started**: `docs/GETTING_STARTED.md` - Complete setup and usage guide
- **Development Guide**: `docs/DEVELOPMENT.md` - Technical architecture and contributing
- **Aurora Model**: https://microsoft.github.io/aurora/
- **ai-models Framework**: https://github.com/ecmwf-lab/ai-models
- **ECMWF Open Data**: https://www.ecmwf.int/en/forecasts/datasets/open-data

### Scientific References
- Aurora Paper: [arXiv:2405.13063](https://arxiv.org/abs/2405.13063)
- ECMWF Blog: [Run AI models yourself with ECMWF open data](https://www.ecmwf.int/en/about/media-centre/aifs-blog/2024/run-ai-models-yourself-ecmwf-open-data)

### License and Attribution
This project is licensed under the Apache 2.0 License. Aurora model weights are available under CC BY-NC-SA 4.0.

When using this work, please cite:
- The Aurora paper (arXiv:2405.13063)
- ECMWF for the IFS Open Data
- This implementation if contributing to your research
