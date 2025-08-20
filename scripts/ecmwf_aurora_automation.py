#!/usr/bin/env python3
"""
ECMWF Open Data to Aurora Automation Script

This script automates the complete workflow from ECMWF Open Data download
to Aurora weather forecasting for HPC environments.

Usage:
    python ecmwf_aurora_automation.py [--lead-time HOURS] [--output-dir PATH]
"""

import argparse
import logging
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Tuple

import xarray as xr
from ecmwf.opendata import Client


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ECMWFAuroraAutomation:
    """Main automation class for ECMWF Open Data to Aurora workflow."""
    
    # Surface variables required by Aurora
    SURFACE_VARS = ["2t", "2d", "10u", "10v", "msl", "tp", "sp", "tcwv"]
    
    # Pressure level variables and levels required by Aurora
    PRESSURE_VARS = ["u", "v", "t", "q"]
    PRESSURE_LEVELS = [1000, 925, 850, 700, 600, 500, 400, 300, 250, 200, 150, 100]  # Full Aurora levels
    
    # IFS forecast cycles (UTC hours)
    IFS_CYCLES = [0, 6, 12, 18]
    
    def __init__(self, output_dir: str = "./data", lead_time: int = 72):
        """Initialize automation with output directory and forecast lead time."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.lead_time = lead_time
        self.client = Client()
        
        # File paths
        self.sfc_file = self.output_dir / "ifs_sfc_latest.grib2"
        self.pl_file = self.output_dir / "ifs_pl_latest.grib2"
        self.init_file = self.output_dir / "init.grib2"
        self.aurora_output = self.output_dir / "aurora.grib"
        self.netcdf_output = self.output_dir / "aurora_forecast.nc"
    
    def detect_latest_cycle(self) -> Tuple[datetime, int]:
        """
        Detect the latest available IFS cycle from ECMWF Open Data.
        
        Returns:
            Tuple of (date, cycle_hour) for the latest available cycle
        """
        logger.info("Detecting latest available IFS cycle...")
        
        now = datetime.utcnow()
        
        # Check cycles in reverse chronological order
        for hours_back in range(0, 48, 6):  # Check up to 48 hours back
            check_time = now - timedelta(hours=hours_back)
            
            for cycle in reversed(self.IFS_CYCLES):
                candidate_date = check_time.replace(hour=cycle, minute=0, second=0, microsecond=0)
                
                # Skip future times
                if candidate_date > now:
                    continue
                
                # Add delay for data availability (typically 3-4 hours after cycle time)
                if now < candidate_date + timedelta(hours=4):
                    continue
                
                if self._check_cycle_availability(candidate_date):
                    logger.info(f"Latest available cycle: {candidate_date.strftime('%Y%m%d')} {cycle:02d}Z")
                    return candidate_date, cycle
        
        raise RuntimeError("No available IFS cycles found in the last 48 hours")
    
    def _check_cycle_availability(self, cycle_datetime: datetime) -> bool:
        """Check if a specific cycle is available by testing a small download."""
        try:
            # Test with a single surface variable
            date_str = cycle_datetime.strftime("%Y%m%d")
            hour_str = f"{cycle_datetime.hour:02d}"
            
            # Try to get a small surface field to test availability
            self.client.retrieve(
                date=date_str,
                time=hour_str,
                stream="oper",
                type="fc",
                step="0",
                param="2t",
                target=None  # Don't actually download
            )
            return True
        except Exception:
            return False
    
    def download_surface_data(self, date: datetime, cycle: int) -> bool:
        """
        Download IFS surface variables.
        
        Args:
            date: Forecast initialization date
            cycle: Forecast cycle hour (0, 6, 12, 18)
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Downloading surface data for {date.strftime('%Y%m%d')} {cycle:02d}Z...")
        
        try:
            self.client.retrieve(
                date=date.strftime("%Y%m%d"),
                time=f"{cycle:02d}",
                stream="oper",
                type="fc",
                step="0",  # Analysis step
                param=self.SURFACE_VARS,
                target=str(self.sfc_file)
            )
            logger.info(f"Surface data saved to {self.sfc_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to download surface data: {e}")
            return False
    
    def download_pressure_level_data(self, date: datetime, cycle: int) -> bool:
        """
        Download IFS pressure level variables.
        
        Args:
            date: Forecast initialization date
            cycle: Forecast cycle hour (0, 6, 12, 18)
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Downloading pressure level data for {date.strftime('%Y%m%d')} {cycle:02d}Z...")
        
        try:
            self.client.retrieve(
                date=date.strftime("%Y%m%d"),
                time=f"{cycle:02d}",
                stream="oper",
                type="fc",
                step="0",  # Analysis step
                param=self.PRESSURE_VARS,
                levelist=self.PRESSURE_LEVELS,
                target=str(self.pl_file)
            )
            logger.info(f"Pressure level data saved to {self.pl_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to download pressure level data: {e}")
            return False
    
    def concatenate_grib_files(self) -> bool:
        """
        Concatenate surface and pressure level GRIB files for Aurora input.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("Concatenating GRIB files for Aurora input...")
        
        try:
            # Use cat command to concatenate GRIB files
            cmd = ["cat", str(self.sfc_file), str(self.pl_file)]
            
            with open(self.init_file, "wb") as outfile:
                result = subprocess.run(cmd, stdout=outfile, stderr=subprocess.PIPE)
            
            if result.returncode != 0:
                logger.error(f"GRIB concatenation failed: {result.stderr.decode()}")
                return False
            
            logger.info(f"Concatenated GRIB file saved to {self.init_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to concatenate GRIB files: {e}")
            return False
    
    def run_aurora_forecast(self) -> bool:
        """
        Run Aurora forecast using ai-models CLI with ECMWF Open Data integration.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Running Aurora forecast with {self.lead_time}h lead time...")
        
        try:
            # Use ECMWF's recommended approach with ai-models CLI
            cmd = [
                "ai-models", "aurora",
                "--input", "ecmwf-open-data",
                "--lead-time", str(self.lead_time),
                "--output", "file",
                "--path", str(self.aurora_output)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Aurora forecast failed: {result.stderr}")
                return False
            
            logger.info(f"Aurora forecast completed. Output saved to {self.aurora_output}")
            logger.info(f"Aurora stdout: {result.stdout}")
            return True
        except Exception as e:
            logger.error(f"Failed to run Aurora forecast: {e}")
            return False
    
    def convert_to_netcdf(self) -> bool:
        """
        Convert Aurora GRIB output to NetCDF using cfgrib/xarray.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("Converting Aurora output to NetCDF...")
        
        try:
            # Use cfgrib backend to read GRIB data
            ds = xr.open_dataset(
                self.aurora_output,
                engine="cfgrib",
                backend_kwargs={
                    "filter_by_keys": {},
                    "read_keys": ["paramId", "cfName", "cfVarName", "units"]
                }
            )
            
            # Add metadata
            ds.attrs.update({
                "title": "Aurora Weather Forecast",
                "source": "ECMWF IFS initial conditions",
                "model": "Microsoft Aurora",
                "institution": "Arizona State University",
                "created": datetime.utcnow().isoformat()
            })
            
            # Save to NetCDF
            ds.to_netcdf(
                self.netcdf_output,
                format="NETCDF4",
                engine="netcdf4"
            )
            
            logger.info(f"NetCDF output saved to {self.netcdf_output}")
            logger.info(f"Variables: {list(ds.data_vars.keys())}")
            logger.info(f"Dimensions: {dict(ds.dims)}")
            
            ds.close()
            return True
        except Exception as e:
            logger.error(f"Failed to convert to NetCDF: {e}")
            return False
    
    def cleanup_intermediate_files(self):
        """Remove intermediate GRIB files to save space."""
        logger.info("Cleaning up intermediate files...")
        
        for file_path in [self.sfc_file, self.pl_file, self.init_file]:
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Removed {file_path}")
    
    def run_complete_workflow(self) -> bool:
        """
        Execute the complete automation workflow.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("Starting ECMWF Open Data to Aurora automation workflow...")
        
        try:
            # Use ECMWF's recommended approach: let Aurora handle data download automatically
            logger.info("Using ai-models aurora with ECMWF Open Data integration")
            
            # Step 1: Run Aurora forecast (handles data download internally)
            if not self.run_aurora_forecast():
                return False
            
            # Step 2: Convert to NetCDF for analysis
            if not self.convert_to_netcdf():
                return False
            
            logger.info("Workflow completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Workflow failed: {e}")
            return False


def main():
    """Main entry point for command-line usage."""
    parser = argparse.ArgumentParser(
        description="ECMWF Open Data to Aurora automation script"
    )
    parser.add_argument(
        "--lead-time",
        type=int,
        default=72,
        help="Forecast lead time in hours (default: 72)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./data",
        help="Output directory for all files (default: ./data)"
    )
    parser.add_argument(
        "--keep-intermediate",
        action="store_true",
        help="Keep intermediate GRIB files"
    )
    
    args = parser.parse_args()
    
    # Create automation instance
    automation = ECMWFAuroraAutomation(
        output_dir=args.output_dir,
        lead_time=args.lead_time
    )
    
    # Override cleanup if requested
    if args.keep_intermediate:
        automation.cleanup_intermediate_files = lambda: None
    
    # Run workflow
    success = automation.run_complete_workflow()
    
    if success:
        logger.info("Automation completed successfully!")
        sys.exit(0)
    else:
        logger.error("Automation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()