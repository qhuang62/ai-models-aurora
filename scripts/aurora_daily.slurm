#!/bin/bash
#SBATCH --job-name=aurora-daily
#SBATCH --account=YOUR_ACCOUNT          # Replace with your Sol account
#SBATCH --partition=gpu                 # GPU partition for Aurora
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gres=gpu:1                    # Request 1 GPU
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00                 # 2 hours should be sufficient
#SBATCH --output=logs/aurora_%j.out
#SBATCH --error=logs/aurora_%j.err
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=YOUR_EMAIL@asu.edu  # Replace with your email

# Aurora Daily Forecast Job for ASU Sol Supercomputer
# This script runs the complete ECMWF Open Data → Aurora → NetCDF workflow

echo "=================================================="
echo "Aurora Daily Forecast Job Started"
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURMD_NODENAME"
echo "Start time: $(date)"
echo "=================================================="

# Exit on any error
set -e

# Load required modules (adjust for Sol's module system)
module purge
module load python/3.10
module load cuda/11.8           # Adjust CUDA version as needed
module load grib_api           # For GRIB file handling
module load netcdf/4.9.0      # For NetCDF output

# Set up environment variables
export CUDA_VISIBLE_DEVICES=$SLURM_LOCALID
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

# Create necessary directories
mkdir -p logs data

# Set working directory
cd $SLURM_SUBMIT_DIR

# Activate Python environment (adjust path as needed)
# Option 1: If using conda/mamba
# source activate aurora-env

# Option 2: If using venv
# source venv/bin/activate

# Option 3: If using module-based Python with pip
export PYTHONPATH=$HOME/.local/lib/python3.10/site-packages:$PYTHONPATH

echo "Python version: $(python --version)"
echo "CUDA available: $(python -c 'import torch; print(torch.cuda.is_available())')"

# Set forecast parameters
LEAD_TIME=${LEAD_TIME:-72}              # Default 72 hours
OUTPUT_DIR="data/$(date +%Y%m%d)"       # Date-based output directory
KEEP_INTERMEDIATE=${KEEP_INTERMEDIATE:-false}

echo "Forecast parameters:"
echo "  Lead time: ${LEAD_TIME} hours"
echo "  Output directory: ${OUTPUT_DIR}"
echo "  Keep intermediate files: ${KEEP_INTERMEDIATE}"

# Run the Aurora automation script
echo "Starting Aurora automation workflow..."

if [ "$KEEP_INTERMEDIATE" = "true" ]; then
    python scripts/ecmwf_aurora_automation.py \
        --lead-time $LEAD_TIME \
        --output-dir $OUTPUT_DIR \
        --keep-intermediate
else
    python scripts/ecmwf_aurora_automation.py \
        --lead-time $LEAD_TIME \
        --output-dir $OUTPUT_DIR
fi

# Check if the workflow completed successfully
if [ $? -eq 0 ]; then
    echo "Aurora workflow completed successfully!"
    
    # Optional: Create a summary file
    SUMMARY_FILE="${OUTPUT_DIR}/forecast_summary.txt"
    cat > $SUMMARY_FILE << EOF
Aurora Forecast Summary
======================
Job ID: $SLURM_JOB_ID
Node: $SLURMD_NODENAME
Start time: $(date)
Lead time: ${LEAD_TIME} hours
Output directory: ${OUTPUT_DIR}

Output files:
$(ls -la ${OUTPUT_DIR}/)

File sizes:
Aurora forecast: $(stat -c%s ${OUTPUT_DIR}/aurora.grib 2>/dev/null | numfmt --to=iec || echo "N/A")
NetCDF output: $(stat -c%s ${OUTPUT_DIR}/aurora_forecast.nc 2>/dev/null | numfmt --to=iec || echo "N/A")
EOF
    
    echo "Forecast summary written to $SUMMARY_FILE"
    
    # Optional: Archive older forecasts (keep last 7 days)
    find data -name "????????" -type d -mtime +7 -exec rm -rf {} \; 2>/dev/null || true
    
else
    echo "Aurora workflow failed!"
    exit 1
fi

echo "=================================================="
echo "Aurora Daily Forecast Job Completed"
echo "End time: $(date)"
echo "Total runtime: $SECONDS seconds"
echo "=================================================="