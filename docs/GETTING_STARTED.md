# Getting Started with Aurora Real-Time Weather Forecasting

This guide walks you through setting up and running your first Aurora weather forecast using ECMWF Open Data.

## Prerequisites

### System Requirements
- **GPU**: CUDA-compatible GPU with ≥8GB memory
- **RAM**: ≥16GB system memory (32GB recommended)
- **Storage**: ≥5GB available space
- **Network**: Internet access for ECMWF Open Data

### Software Requirements
- **Python**: 3.8 or higher
- **CUDA**: Compatible with your GPU driver
- **Git**: For repository management

## Step 1: Environment Setup

### Option A: Conda Environment (Recommended)
```bash
# Create and activate conda environment
conda create -n aurora python=3.10
conda activate aurora

# Install CUDA and PyTorch
conda install pytorch pytorch-cuda=11.8 -c pytorch -c nvidia

# Install required packages
pip install ai-models ai-models-aurora
pip install ecmwf-opendata xarray cfgrib netcdf4
```

### Option B: Virtual Environment
```bash
# Create virtual environment
python -m venv aurora_env
source aurora_env/bin/activate  # Linux/Mac
# aurora_env\Scripts\activate  # Windows

# Install dependencies
pip install ai-models ai-models-aurora
pip install ecmwf-opendata xarray cfgrib netcdf4 torch
```

## Step 2: Verify Installation

```bash
# Test GPU availability
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"

# Test Aurora model
ai-models aurora --help

# Test ECMWF client
python -c "from ecmwf.opendata import Client; print('ECMWF client OK')"
```

## Step 3: Run Your First Forecast

### Option A: Interactive Notebook
```bash
# Start Jupyter
jupyter notebook Aurora_RealTime_Weather_Forecasting.ipynb

# Follow the notebook cells to:
# 1. Download latest IFS data
# 2. Run Aurora forecast
# 3. Visualize results
```

### Option B: Automated Script
```bash
# Run 72-hour forecast with default settings
python scripts/ecmwf_aurora_automation.py

# Custom forecast
python scripts/ecmwf_aurora_automation.py --lead-time 120 --output-dir ./my_forecast
```

### Option C: HPC Batch Job
```bash
# Edit Slurm template for your system
nano scripts/aurora_daily.slurm

# Submit job
sbatch scripts/aurora_daily.slurm
```

## Step 4: Understanding the Output

### File Structure
```
output_directory/
├── aurora_forecast.grib    # Primary Aurora output (GRIB2 format)
├── aurora_forecast.nc      # NetCDF for analysis
└── forecast_summary.txt    # Run metadata and statistics
```

### Loading Results in Python
```python
import xarray as xr
import matplotlib.pyplot as plt

# Load NetCDF forecast data
ds = xr.open_dataset('aurora_forecast.nc')

# Plot 2-meter temperature at final time
ds.t2m.isel(time=-1).plot()
plt.title('Aurora 2m Temperature Forecast')
plt.show()

# Extract time series for a location (e.g., Phoenix, AZ)
point_data = ds.sel(latitude=33.4, longitude=-112.0, method='nearest')
point_data.t2m.plot()
plt.title('Temperature Forecast - Phoenix, AZ')
plt.show()
```

## Step 5: Production Deployment

### Daily Automated Forecasts
```bash
# Setup automated daily runs with cron
crontab -e

# Add line for daily 12Z forecast:
# 0 16 * * * /path/to/conda/envs/aurora/bin/python /path/to/scripts/ecmwf_aurora_automation.py
```

### HPC Integration
```bash
# Copy and modify Slurm template
cp scripts/aurora_daily.slurm my_aurora_job.slurm

# Edit for your system:
# - Account/partition settings
# - Resource requirements
# - Email notifications
# - Output directories

# Submit recurring jobs
sbatch my_aurora_job.slurm
```

## Troubleshooting

### Common Issues

**1. CUDA/GPU Problems**
```bash
# Check GPU status
nvidia-smi

# Verify PyTorch CUDA
python -c "import torch; print(torch.cuda.is_available())"

# Reinstall PyTorch with correct CUDA version
pip uninstall torch
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

**2. Data Download Failures**
- ECMWF Open Data has ~4-hour delay after cycle times
- Check internet connectivity
- Verify no firewall blocking ECMWF servers

**3. Memory Issues**
- Reduce forecast lead time
- Close other GPU applications
- Use smaller model variants if available

**4. Slow Performance**
- Verify GPU usage during forecast
- Check network speed for data download
- Consider using faster storage (SSD)

### Getting Help

1. **Check logs**: Look for error messages in console output
2. **Aurora documentation**: https://microsoft.github.io/aurora/
3. **ai-models issues**: https://github.com/ecmwf-lab/ai-models/issues
4. **ECMWF Open Data**: https://www.ecmwf.int/en/forecasts/datasets/open-data

## Next Steps

### Advanced Usage
- **Ensemble Forecasting**: Run multiple forecasts with different parameters
- **Custom Validation**: Compare Aurora output with observations
- **Downscaling**: Use Aurora as boundary conditions for high-resolution models
- **Climate Studies**: Long-term forecast analysis and trends

### Integration Examples
- **Web Services**: Serve forecasts via REST API
- **Visualization**: Advanced plotting with cartopy/basemap
- **Post-processing**: Statistical correction and bias adjustment
- **Applications**: Decision support systems and specialized products

### Contributing
- **Feedback**: Report issues and suggest improvements
- **Documentation**: Help improve guides and examples
- **Testing**: Validate on different systems and configurations
- **Development**: Contribute new features and optimizations

---

**Happy Forecasting!** 🌤️

You're now ready to generate state-of-the-art AI weather forecasts using Aurora and ECMWF Open Data.