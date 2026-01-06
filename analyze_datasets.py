"""
Quick Dataset Analysis Script

Provides a quick overview of available datasets without loading full data.
"""

import pandas as pd
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dataset paths
DATA_PATH = Path("C:/Users/HP/Desktop/Major Project/Main File-Code/data")
CICDDOS2019_PATH = DATA_PATH / "CIC-DDoS2019 Dataset" / "cicddos2019_dataset.csv"
NSLKDD_TRAIN_PATH = DATA_PATH / "NSLKDD" / "KDDTrain+.txt"
SAMPLED_DATA_PATH = DATA_PATH / "Data" / "sampled_data.csv"


def quick_peek_csv(filepath, nrows=5):
    """
    Quick peek at CSV file
    
    Args:
        filepath: Path to CSV
        nrows: Number of rows to read
    """
    logger.info(f"\n{'='*70}")
    logger.info(f"Quick Peek: {filepath.name}")
    logger.info(f"{'='*70}")
    
    if not filepath.exists():
        logger.error(f"File not found: {filepath}")
        return
    
    # File size
    size_mb = filepath.stat().st_size / (1024 * 1024)
    logger.info(f"File size: {size_mb:.2f} MB")
    
    # Read first few rows
    try:
        df = pd.read_csv(filepath, nrows=nrows, low_memory=False)
        logger.info(f"Columns ({len(df.columns)}): {list(df.columns)}")
        logger.info(f"\nFirst {nrows} rows:")
        print(df.head())
        
        # Try to find label column
        label_cols = [col for col in df.columns if 'label' in col.lower() or 'class' in col.lower()]
        if label_cols:
            logger.info(f"\nPotential label columns: {label_cols}")
            
    except Exception as e:
        logger.error(f"Error reading file: {e}")


def main():
    """Run quick analysis"""
    logger.info("\n" + "📊"*35)
    logger.info("Quick Dataset Analysis")
    logger.info("📊"*35)
    
    # CICDDoS2019
    quick_peek_csv(CICDDOS2019_PATH, nrows=3)
    
    # Sampled data
    quick_peek_csv(SAMPLED_DATA_PATH, nrows=3)
    
    logger.info("\n" + "="*70)
    logger.info("RECOMMENDATIONS")
    logger.info("="*70)
    logger.info("For fastest experimentation:")
    logger.info("  - Use 'sampled_data.csv' (already preprocessed)")
    logger.info("  - Or load CICDDoS2019 with sample_size=50000")
    logger.info("\nFor full training:")
    logger.info("  - Use complete CICDDoS2019 or NSLKDD datasets")
    logger.info("\nRun 'python load_dataset.py' to begin data preparation")


if __name__ == "__main__":
    main()
