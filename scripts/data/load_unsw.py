"""
UNSW-NB15 Dataset Loader

Loads and preprocesses UNSW-NB15 dataset for cross-dataset
FL validation with CICDDoS2019.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


import pandas as pd
import numpy as np
from pathlib import Path
import logging
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UNSWDatasetLoader:
    """
    Load and preprocess UNSW-NB15 dataset.
    
    Dataset: Modern network intrusion detection (2015)
    Records: ~2.5M (training: ~175K, testing: ~82K)
    Features: 49 features
    Classes: 10 attack types + normal
    """
    
    def __init__(self, data_dir='../data/UNSW-NB15'):
        self.data_dir = Path(data_dir)
        self.label_encoder = LabelEncoder()
        self.scaler = StandardScaler()
        
        # Expected columns (UNSW-NB15 format)
        self.feature_cols = None  # Will be determined from data
        self.label_col = 'attack_cat'  # Attack category column
        
    def load_data(self):
        """Load UNSW-NB15 training and testing sets"""
        
        logger.info("Loading UNSW-NB15 dataset...")
        
        # Load parquet files
        train_file = self.data_dir / 'UNSW_NB15_training-set.parquet'
        test_file = self.data_dir / 'UNSW_NB15_testing-set.parquet'
        
        if not train_file.exists():
            raise FileNotFoundError(f"Training file not found: {train_file}")
        if not test_file.exists():
            raise FileNotFoundError(f"Testing file not found: {test_file}")
        
        # Read parquet files
        df_train = pd.read_parquet(train_file)
        df_test = pd.read_parquet(test_file)
        
        logger.info(f"Loaded training set: {df_train.shape}")
        logger.info(f"Loaded testing set: {df_test.shape}")
        
        # Combine for preprocessing
        df = pd.concat([df_train, df_test], ignore_index=True)
        
        logger.info(f"Total samples: {len(df)}")
        logger.info(f"Columns: {list(df.columns)[:10]}...")
        
        return df
    
    def preprocess(self, df, sample_size=None):
        """
        Preprocess UNSW-NB15 dataset.
        
        Args:
            df: Raw dataframe
            sample_size: Optional number of samples to use (for faster testing)
            
        Returns:
            X, y: Features and labels
        """
        logger.info("Preprocessing UNSW-NB15...")
        
        # Sample if requested
        if sample_size and len(df) > sample_size:
            logger.info(f"Sampling {sample_size} records from {len(df)}...")
            df = df.sample(n=sample_size, random_state=42)
        
        # Identify label column (common names)
        label_candidates = ['attack_cat', 'label', 'Label', 'attack', 'Attack']
        label_col = None
        for col in label_candidates:
            if col in df.columns:
                label_col = col
                break
        
        if label_col is None:
            # Try to find any column with 'label' or 'attack' in name
            for col in df.columns:
                if 'label' in col.lower() or 'attack' in col.lower():
                    label_col = col
                    break
        
        if label_col is None:
            raise ValueError(f"Could not find label column. Available columns: {list(df.columns)}")
        
        logger.info(f"Using label column: {label_col}")
        
        # Separate features and labels
        y = df[label_col].values
        X = df.drop(columns=[label_col])
        
        # Handle categorical columns
        categorical_cols = X.select_dtypes(include=['object', 'category']).columns
        
        if len(categorical_cols) > 0:
            logger.info(f"Encoding {len(categorical_cols)} categorical columns...")
            for col in categorical_cols:
                le = LabelEncoder()
                X[col] = le.fit_transform(X[col].astype(str))
        
        # Convert to numeric
        X = X.apply(pd.to_numeric, errors='coerce')
        
        # Handle missing values
        if X.isnull().any().any():
            logger.info("Filling missing values...")
            X = X.fillna(X.median())
        
        # Encode labels
        y_encoded = self.label_encoder.fit_transform(y)
        
        # Convert to numpy
        X = X.values.astype(np.float32)
        y = y_encoded.astype(np.int32)
        
        # Normalize features
        X = self.scaler.fit_transform(X)
        
        logger.info(f"Preprocessed shape: X={X.shape}, y={y.shape}")
        logger.info(f"Classes: {len(np.unique(y))} ({list(self.label_encoder.classes_)[:5]}...)")
        
        return X, y
    
    def get_attack_distribution(self, y):
        """Get attack type distribution"""
        
        unique, counts = np.unique(y, return_counts=True)
        distribution = dict(zip(
            [self.label_encoder.classes_[i] for i in unique],
            counts
        ))
        
        logger.info("\nAttack Distribution:")
        for attack, count in sorted(distribution.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"  {attack}: {count} ({count/len(y)*100:.1f}%)")
        
        return distribution


def load_unsw_nb15(
    data_dir='../data/UNSW-NB15',
    sample_size=None,
    test_size=0.15,
    random_state=42
):
    """
    Convenience function to load and split UNSW-NB15 dataset.
    
    Args:
        data_dir: Path to UNSW-NB15 data directory
        sample_size: Optional sample size
        test_size: Test split ratio
        random_state: Random seed
        
    Returns:
        X_train, X_test, y_train, y_test
    """
    loader = UNSWDatasetLoader(data_dir=data_dir)
    
    # Load raw data
    df = loader.load_data()
    
    # Preprocess
    X, y = loader.preprocess(df, sample_size=sample_size)
    
    # Get distribution
    loader.get_attack_distribution(y)
    
    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=test_size,
        random_state=random_state,
        stratify=y
    )
    
    logger.info(f"\nFinal split:")
    logger.info(f"  Training: {X_train.shape}")
    logger.info(f"  Testing: {X_test.shape}")
    
    return X_train, X_test, y_train, y_test, loader


def save_processed_unsw(
    X_train, X_test, y_train, y_test,
    output_dir='data/processed'
):
    """Save processed UNSW-NB15 dataset"""
    
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, 'unsw_nb15_processed.npz')
    
    np.savez_compressed(
        output_file,
        X_train=X_train,
        X_test=X_test,
        y_train=y_train,
        y_test=y_test
    )
    
    logger.info(f"\n✓ Saved to: {output_file}")
    
    return output_file


def main():
    """Test UNSW-NB15 loader"""
    
    logger.info("Testing UNSW-NB15 Dataset Loader...")
    
    # Load dataset (sample for quick test)
    X_train, X_test, y_train, y_test, loader = load_unsw_nb15(
        data_dir='../data/UNSW-NB15',
        sample_size=100000  # Sample 100K for testing
    )
    
    # Save processed data
    save_processed_unsw(X_train, X_test, y_train, y_test)
    
    logger.info("\n✓ UNSW-NB15 dataset loaded and processed successfully!")
    
    return X_train, X_test, y_train, y_test


if __name__ == "__main__":
    main()
