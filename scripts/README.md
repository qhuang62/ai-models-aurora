# ECMWF Open Data to Aurora Automation

This directory contains production-ready scripts for automating the ECMWF Open Data → Aurora weather forecasting workflow on ASU's Sol supercomputer.

## Quick Start

1. **Setup environment:**
   ```bash
   ./scripts/setup_automation.sh
   ```

2. **Edit Slurm configuration:**
   ```bash
   # Edit aurora_daily.slurm to set your account and email
   nano scripts/aurora_daily.slurm
   ```

3. **Submit daily forecast job:**
   ```bash
   sbatch scripts/aurora_daily.slurm
   ```

## Files Overview

### Core Scripts

- **`ecmwf_aurora_automation.py`** - Main automation script
  - Detects latest IFS cycle from ECMWF Open Data
  - Downloads surface and pressure level variables
  - Concatenates GRIB files for Aurora input
  - Runs Aurora forecast using ai-models CLI
  - Converts output to NetCDF format

- **`aurora_daily.slurm`** - Slurm batch job template
  - Configured for Sol's GPU partition
  - Handles module loading and environment setup
  - Includes error handling and logging
  - Archives old forecasts automatically

### Support Files

- **`setup_automation.sh`** - Environment setup script
- **`requirements.txt`** - Python dependencies
- **`README.md`** - This documentation

## Usage Examples

### Manual Forecast Run
```bash
# Basic run with default 72h lead time
python scripts/ecmwf_aurora_automation.py

# Custom lead time and output directory
python scripts/ecmwf_aurora_automation.py --lead-time 120 --output-dir ./custom_output

# Keep intermediate GRIB files for debugging
python scripts/ecmwf_aurora_automation.py --keep-intermediate
```

### Scheduled Daily Runs
```bash
# Submit job with default settings
sbatch scripts/aurora_daily.slurm

# Submit with custom lead time
LEAD_TIME=120 sbatch scripts/aurora_daily.slurm

# Submit with different output directory
OUTPUT_DIR="/scratch/forecasts" sbatch scripts/aurora_daily.slurm
```

## Data Flow

1. **IFS Cycle Detection** - Automatically finds latest available cycle (00, 06, 12, 18 UTC)
2. **Data Download** - Fetches key variables:
   - Surface: 2t, 2d, 10u, 10v, msl, tp, sp, tcwv
   - Pressure levels: u, v, t, q at 850, 700, 500, 300 hPa
3. **GRIB Concatenation** - Combines files into Aurora-compatible `init.grib2`
4. **Aurora Forecast** - Runs forecast using `ai-models aurora` CLI
5. **NetCDF Conversion** - Converts output using cfgrib/xarray for analysis

## Output Files

For each forecast run:
- `aurora.grib` - Raw Aurora forecast output
- `aurora_forecast.nc` - NetCDF format for analysis
- `forecast_summary.txt` - Run summary and metadata

## Configuration

### Slurm Job Parameters
Edit `aurora_daily.slurm` to customize:
- `#SBATCH --account=` - Your Sol account
- `#SBATCH --mail-user=` - Your notification email
- `#SBATCH --time=` - Job time limit
- `#SBATCH --mem=` - Memory allocation

### Environment Variables
- `LEAD_TIME` - Forecast hours (default: 72)
- `OUTPUT_DIR` - Output directory (default: data/YYYYMMDD)
- `KEEP_INTERMEDIATE` - Keep GRIB files (default: false)

## Dependencies

### Required Python Packages
- `ecmwf-opendata` - ECMWF Open Data client
- `xarray` - NetCDF handling
- `cfgrib` - GRIB to xarray conversion
- `netcdf4` - NetCDF I/O
- `ai-models` - Aurora CLI interface
- `microsoft-aurora` - Aurora model

### System Requirements
- GPU access (Aurora requires CUDA)
- Sufficient disk space (~2-5 GB per forecast)
- Internet access for ECMWF Open Data

## Troubleshooting

### Common Issues

1. **No available cycles found**
   - ECMWF data has ~4 hour delay after cycle time
   - Check internet connectivity to ECMWF servers

2. **Aurora execution fails**
   - Verify GPU availability: `nvidia-smi`
   - Check CUDA environment: `python -c "import torch; print(torch.cuda.is_available())"`
   - Ensure ai-models and aurora packages are installed

3. **NetCDF conversion errors**
   - Install eccodes: `conda install -c conda-forge eccodes`
   - Check cfgrib installation: `python -c "import cfgrib"`

4. **Slurm job failures**
   - Check account permissions: `sacctmgr show user $USER`
   - Verify GPU allocation: `sinfo -p gpu`
   - Review job logs in `logs/` directory

### Log Files
- Slurm logs: `logs/aurora_JOBID.out` and `logs/aurora_JOBID.err`
- Python logs: Console output with timestamps
- Forecast summaries: `data/YYYYMMDD/forecast_summary.txt`

## Performance Notes

### Typical Runtimes (on Sol GPU node)
- Data download: 5-15 minutes
- Aurora forecast (72h): 10-30 minutes
- NetCDF conversion: 1-2 minutes
- **Total: ~20-45 minutes**

### Storage Requirements
- Input GRIB files: ~500 MB
- Aurora output: ~1-3 GB (depends on lead time)
- NetCDF output: ~500 MB - 1 GB
- **Total per forecast: ~2-5 GB**

## Integration with Downstream Analysis

The NetCDF output (`aurora_forecast.nc`) can be directly used with:
- Python: `xarray.open_dataset()`
- R: `ncdf4` or `stars` packages
- MATLAB: `ncread()` function
- CDO/NCO tools for post-processing

Example Python analysis:
```python
import xarray as xr

# Load Aurora forecast
ds = xr.open_dataset('data/20241201/aurora_forecast.nc')

# Plot 2m temperature at final time step
ds.t2m.isel(time=-1).plot()

# Extract time series for a location
point_data = ds.sel(latitude=33.4, longitude=-112.0, method='nearest')
```

## Support

For issues specific to:
- **Aurora model**: https://github.com/microsoft/aurora
- **AI Models**: https://github.com/ecmwf-lab/ai-models
- **ECMWF Open Data**: https://github.com/ecmwf/ecmwf-opendata
- **Sol supercomputer**: ASU Research Computing support