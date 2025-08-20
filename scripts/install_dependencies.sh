#!/bin/bash

# Installation script for Aurora IFS OpenData Demo dependencies
# Run this before using the Jupyter notebook

echo "Installing dependencies for Aurora IFS OpenData Demo..."

# Core dependencies for the notebook
pip install --user ecmwf-opendata
pip install --user xarray
pip install --user cfgrib
pip install --user netcdf4
pip install --user matplotlib
pip install --user pandas
pip install --user numpy
pip install --user psutil

# Optional: Install cartopy for advanced mapping (may require system dependencies)
echo "Installing cartopy (optional - for advanced mapping)..."
pip install --user cartopy || echo "Cartopy installation failed - notebook will use basic plotting"

# Check if ai-models is available
if ! python -c "import ai_models" 2>/dev/null; then
    echo "Warning: ai-models not found. Install with:"
    echo "  pip install ai-models"
fi

# Check if Aurora is available
if ! python -c "import aurora" 2>/dev/null; then
    echo "Warning: Aurora not found. Install with:"
    echo "  pip install microsoft-aurora"
fi

echo "Dependency installation complete!"
echo ""
echo "To verify installations, run:"
echo "  python -c \"from ecmwf.opendata import Client; print('ECMWF Open Data: OK')\""
echo "  python -c \"import xarray; print('xarray: OK')\""
echo "  python -c \"import cfgrib; print('cfgrib: OK')\""