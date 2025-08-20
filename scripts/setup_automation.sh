#!/bin/bash

# Setup script for ECMWF Aurora automation on ASU Sol
# This script sets up the environment and dependencies

set -e

echo "Setting up ECMWF Aurora automation environment..."

# Create necessary directories
mkdir -p scripts data logs

# Make scripts executable
chmod +x scripts/ecmwf_aurora_automation.py
chmod +x scripts/aurora_daily.slurm

# Install Python dependencies
echo "Installing Python dependencies..."

# Option 1: If using pip
pip install --user -r scripts/requirements.txt

# Option 2: If using conda/mamba (uncomment if preferred)
# conda install -c conda-forge ecmwf-opendata xarray cfgrib netcdf4 numpy pandas scipy eccodes tqdm psutil

echo "Verifying installations..."

# Check critical dependencies
python -c "import ecmwf.opendata; print('✓ ecmwf-opendata installed')"
python -c "import xarray; print('✓ xarray installed')"
python -c "import cfgrib; print('✓ cfgrib installed')"
python -c "import netCDF4; print('✓ netCDF4 installed')"

# Check if ai-models and Aurora are available
if python -c "import ai_models" 2>/dev/null; then
    echo "✓ ai-models available"
else
    echo "⚠ ai-models not found. Install with: pip install ai-models"
fi

if python -c "import aurora" 2>/dev/null; then
    echo "✓ Aurora available"
else
    echo "⚠ Aurora not found. Install with: pip install microsoft-aurora"
fi

# Test ECMWF Open Data client
echo "Testing ECMWF Open Data client..."
python -c "
from ecmwf.opendata import Client
client = Client()
print('✓ ECMWF Open Data client working')
"

echo ""
echo "Setup completed!"
echo ""
echo "Next steps:"
echo "1. Edit aurora_daily.slurm to set your account and email"
echo "2. Test the automation script:"
echo "   python scripts/ecmwf_aurora_automation.py --help"
echo "3. Submit daily job:"
echo "   sbatch scripts/aurora_daily.slurm"
echo ""
echo "For manual runs:"
echo "   python scripts/ecmwf_aurora_automation.py --lead-time 72 --output-dir ./test_data"