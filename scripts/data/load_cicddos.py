"""
Real Dataset Loading and Preparation Script

Loads CICDDoS2019 and NSLKDD datasets from local storage,
preprocesses them, and prepares for federated learning training.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


import sys
import logging
import numpy as np
import pandas as pd
from pathlib import Path
import pickle
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add projects to path
sys.path.insert(0, str(Path(__file__).parent))

from ddosdfl.projects.shared_libs import (
    DatasetLoader, FeatureExtractor, DataPartitioner, split_data,
    CNNBiLSTMModel, ModelTrainer
)


# Configuration
DATA_PATH = Path("C:/Users/HP/Desktop/Major Project/Main File-Code/data")
OUTPUT_DIR = Path("./data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Dataset paths
CICDDOS2019_PATH = DATA_PATH / "CIC-DDoS2019 Dataset" / "cicddos2019_dataset.csv"
NSLKDD_TRAIN_PATH = DATA_PATH / "NSLKDD" / "KDDTrain+.txt"
NSLKDD_TEST_PATH = DATA_PATH / "NSLKDD" / "KDDTest+.txt"
SAMPLED_DATA_PATH = DATA_PATH / "Data" / "sampled_data.csv"


def load_cicddos2019(sample_size: int = None, random_state: int = 42):
    """
    Load CICDDoS2019 dataset
    
    Args:
        sample_size: Number of samples to load (None = all)
        random_state: Random state for sampling
        
    Returns:
        DataFrame
    """
    logger.info("="*70)
    logger.info("Loading CICDDoS2019 Dataset")
    logger.info("="*70)
    
    if not CICDDOS2019_PATH.exists():
        raise FileNotFoundError(f"CICDDoS2019 dataset not found at {CICDDOS2019_PATH}")
    
    logger.info(f"Reading from: {CICDDOS2019_PATH}")
    logger.info("This may take a few minutes for large files...")
    
    # Read CSV
    df = pd.read_csv(CICDDOS2019_PATH, encoding='utf-8', low_memory=False)
    
    logger.info(f"Loaded {len(df):,} records with {len(df.columns)} columns")
    
    # Sample if requested
    if sample_size and sample_size < len(df):
        logger.info(f"Sampling {sample_size:,} records...")
        df = df.sample(n=sample_size, random_state=random_state)
    
    # Display basic info
    logger.info(f"\nDataset shape: {df.shape}")
    logger.info(f"Columns: {list(df.columns)[:10]}{'...' if len(df.columns) > 10 else ''}")
    
    # Check for label column
    label_candidates = [col for col in df.columns if 'label' in col.lower()]
    if label_candidates:
        logger.info(f"\nLabel column(s) found: {label_candidates}")
        label_col = label_candidates[0]
        logger.info(f"Label distribution:\n{df[label_col].value_counts()}")
    
    return df


def load_nslkdd(use_20_percent: bool = False):
    """
    Load NSLKDD dataset
    
    Args:
        use_20_percent: Use 20% subset for faster training
        
    Returns:
        Tuple of (train_df, test_df)
    """
    logger.info("="*70)
    logger.info("Loading NSLKDD Dataset")
    logger.info("="*70)
    
    # NSLKDD column names (standard)
    column_names = [
        'duration', 'protocol_type', 'service', 'flag', 'src_bytes',
        'dst_bytes', 'land', 'wrong_fragment', 'urgent', 'hot',
        'num_failed_logins', 'logged_in', 'num_compromised', 'root_shell',
        'su_attempted', 'num_root', 'num_file_creations', 'num_shells',
        'num_access_files', 'num_outbound_cmds', 'is_host_login',
        'is_guest_login', 'count', 'srv_count', 'serror_rate',
        'srv_serror_rate', 'rerror_rate', 'srv_rerror_rate', 'same_srv_rate',
        'diff_srv_rate', 'srv_diff_host_rate', 'dst_host_count',
        'dst_host_srv_count', 'dst_host_same_srv_rate',
        'dst_host_diff_srv_rate', 'dst_host_same_src_port_rate',
        'dst_host_srv_diff_host_rate', 'dst_host_serror_rate',
        'dst_host_srv_serror_rate', 'dst_host_rerror_rate',
        'dst_host_srv_rerror_rate', 'label', 'difficulty_level'
    ]
    
    # Load training data
    if use_20_percent:
        train_path = DATA_PATH / "NSLKDD" / "KDDTrain+_20Percent.txt"
    else:
        train_path = NSLKDD_TRAIN_PATH
    
    if not train_path.exists():
        raise FileNotFoundError(f"NSLKDD training data not found at {train_path}")
    
    logger.info(f"Loading training data from: {train_path}")
    train_df = pd.read_csv(train_path, header=None, names=column_names)
    
    logger.info(f"Loaded {len(train_df):,} training records")
    
    # Load test data
    if not NSLKDD_TEST_PATH.exists():
        logger.warning(f"NSLKDD test data not found at {NSLKDD_TEST_PATH}")
        test_df = None
    else:
        logger.info(f"Loading test data from: {NSLKDD_TEST_PATH}")
        test_df = pd.read_csv(NSLKDD_TEST_PATH, header=None, names=column_names)
        logger.info(f"Loaded {len(test_df):,} test records")
    
    # Display label distribution
    logger.info(f"\nTraining label distribution:\n{train_df['label'].value_counts()}")
    
    return train_df, test_df


def load_sampled_data():
    """Load preprocessed sampled data if available"""
    logger.info("="*70)
    logger.info("Loading Sampled/Preprocessed Dataset")
    logger.info("="*70)
    
    if not SAMPLED_DATA_PATH.exists():
        raise FileNotFoundError(f"Sampled data not found at {SAMPLED_DATA_PATH}")
    
    logger.info(f"Reading from: {SAMPLED_DATA_PATH}")
    df = pd.read_csv(SAMPLED_DATA_PATH, encoding='utf-8', low_memory=False)
    
    logger.info(f"Loaded {len(df):,} records with {len(df.columns)} columns")
    
    return df


def preprocess_and_save(df, dataset_name, output_dir=OUTPUT_DIR):
    """
    Preprocess dataset and save encoders
    
    Args:
        df: Input DataFrame
        dataset_name: Name of dataset (for saving)
        output_dir: Output directory
        
    Returns:
        Tuple of (X, y, feature_extractor)
    """
    logger.info("="*70)
    logger.info(f"Preprocessing {dataset_name}")
    logger.info("="*70)
    
    # Extract features
    extractor = FeatureExtractor()
    X, y = extractor.preprocess(df, fit=True)
    
    # Save feature extractor
    extractor_path = output_dir / f"{dataset_name}_feature_extractor.pkl"
    extractor.save(str(extractor_path))
    logger.info(f"Saved feature extractor to {extractor_path}")
    
    # Save processed data
    data_path = output_dir / f"{dataset_name}_processed.npz"
    np.savez_compressed(data_path, X=X, y=y)
    logger.info(f"Saved processed data to {data_path}")
    
    return X, y, extractor


def prepare_for_federated_learning(X, y, num_nodes=5, iid=True):
    """
    Partition data for federated learning
    
    Args:
        X: Features
        y: Labels
        num_nodes: Number of FL nodes
        iid: Whether to use IID partitioning
        
    Returns:
        List of (X_node, y_node) tuples
    """
    logger.info("="*70)
    logger.info(f"Preparing data for Federated Learning ({num_nodes} nodes, IID={iid})")
    logger.info("="*70)
    
    partitioner = DataPartitioner(num_nodes=num_nodes, iid=iid)
    node_datasets = partitioner.partition(X, y)
    
    return node_datasets


def reshape_for_cnn_bilstm(X, timesteps=10):
    """
    Reshape flat features for CNN-BiLSTM input
    
    Args:
        X: Features (num_samples, num_features)
        timesteps: Number of timesteps
        
    Returns:
        Reshaped X (num_samples, timesteps, features_per_timestep)
    """
    num_samples, num_features = X.shape
    
    # Calculate features per timestep (round up to ensure all features fit)
    import math
    features_per_timestep = math.ceil(num_features / timesteps)
    
    # Calculate required total features
    required_features = features_per_timestep * timesteps
    
    # Pad if necessary
    if required_features > num_features:
        pad_size = required_features - num_features
        logger.info(f"Padding {num_features} features to {required_features} (adding {pad_size} zeros)")
        X = np.pad(X, ((0, 0), (0, pad_size)), mode='constant', constant_values=0)
    
    # Reshape
    X_reshaped = X.reshape(num_samples, timesteps, features_per_timestep)
    
    logger.info(f"Reshaped data: ({num_samples}, {num_features}) -> {X_reshaped.shape}")
    
    return X_reshaped



def main():
    """Main data loading and preparation pipeline"""
    logger.info("\n" + "🚀"*35)
    logger.info("DDoS Detection System - Real Dataset Loading")
    logger.info("🚀"*35 + "\n")
    
    print("\nSelect dataset to load:")
    print("1. CICDDoS2019 (full dataset)")
    print("2. CICDDoS2019 (sampled - 100k records)")
    print("3. NSLKDD (full)")
    print("4. NSLKDD (20% subset)")
    print("5. Pre-sampled dataset")
    
    choice = input("\nEnter choice (1-5): ").strip()
    
    try:
        if choice == "1":
            df = load_cicddos2019()
            dataset_name = "cicddos2019_full"
            
        elif choice == "2":
            df = load_cicddos2019(sample_size=100000)
            dataset_name = "cicddos2019_100k"
            
        elif choice == "3":
            train_df, test_df = load_nslkdd(use_20_percent=False)
            df = train_df  # Use training data
            dataset_name = "nslkdd_full"
            
        elif choice == "4":
            train_df, test_df = load_nslkdd(use_20_percent=True)
            df = train_df
            dataset_name = "nslkdd_20pct"
            
        elif choice == "5":
            df = load_sampled_data()
            dataset_name = "sampled_data"
            
        else:
            logger.error("Invalid choice")
            return 1
        
        # Preprocess
        X, y, extractor = preprocess_and_save(df, dataset_name)
        
        # Check for rare classes (important for NSL-KDD)
        from collections import Counter
        class_counts = Counter(y)
        min_samples = min(class_counts.values())
        
        logger.info(f"\nClass distribution:")
        logger.info(f"  Total classes: {len(class_counts)}")
        logger.info(f"  Min samples per class: {min_samples}")
        logger.info(f"  Max samples per class: {max(class_counts.values())}")
        
        # If any class has < 6 samples, can't do stratified 70/15/15 split
        use_stratify = min_samples >= 6
        
        if not use_stratify:
            logger.warning(f"⚠️ Rare classes detected (min={min_samples} samples)")
            logger.warning("Using non-stratified split to avoid errors")
        
        # Split into train/val/test
        try:
            X_train, X_val, X_test, y_train, y_val, y_test = split_data(
                X, y,
                train_ratio=0.7,
                val_ratio=0.15,
                test_ratio=0.15,
                stratify=use_stratify  # Disable stratify for rare classes
            )
        except ValueError as e:
            if "least populated class" in str(e):
                logger.warning(f"Stratified split failed, retrying without stratification...")
                X_train, X_val, X_test, y_train, y_val, y_test = split_data(
                    X, y,
                    train_ratio=0.7,
                    val_ratio=0.15,
                    test_ratio=0.15,
                    stratify=False  # Force non-stratified
                )
            else:
                raise

        
        # Save splits
        splits_path = OUTPUT_DIR / f"{dataset_name}_splits.npz"
        np.savez_compressed(
            splits_path,
            X_train=X_train, y_train=y_train,
            X_val=X_val, y_val=y_val,
            X_test=X_test, y_test=y_test
        )
        logger.info(f"\nSaved train/val/test splits to {splits_path}")
        
        # Prepare for federated learning
        print("\nPrepare data for Federated Learning?")
        fl_choice = input("Enter number of nodes (or 0 to skip): ").strip()
        
        if fl_choice and int(fl_choice) > 0:
            num_nodes = int(fl_choice)
            iid_choice = input("Use IID partitioning? (y/n): ").strip().lower() == 'y'
            
            node_datasets = prepare_for_federated_learning(
                X_train, y_train,
                num_nodes=num_nodes,
                iid=iid_choice
            )
            
            # Save node datasets
            for i, (X_node, y_node) in enumerate(node_datasets):
                node_path = OUTPUT_DIR / f"{dataset_name}_node_{i+1:03d}.npz"
                np.savez_compressed(node_path, X=X_node, y=y_node)
            
            logger.info(f"\nSaved {num_nodes} node datasets to {OUTPUT_DIR}")
        
        # Reshape for CNN-BiLSTM
        print("\nReshape data for CNN-BiLSTM?")
        timesteps = input("Enter number of timesteps (e.g., 10) or 0 to skip: ").strip()
        
        if timesteps and int(timesteps) > 0:
            timesteps = int(timesteps)
            
            X_train_reshaped = reshape_for_cnn_bilstm(X_train, timesteps)
            X_val_reshaped = reshape_for_cnn_bilstm(X_val, timesteps)
            X_test_reshaped = reshape_for_cnn_bilstm(X_test, timesteps)
            
            # Save reshaped data
            reshaped_path = OUTPUT_DIR / f"{dataset_name}_reshaped_t{timesteps}.npz"
            np.savez_compressed(
                reshaped_path,
                X_train=X_train_reshaped, y_train=y_train,
                X_val=X_val_reshaped, y_val=y_val,
                X_test=X_test_reshaped, y_test=y_test,
                timesteps=timesteps,
                features_per_timestep=X_train_reshaped.shape[2]
            )
            logger.info(f"\nSaved reshaped data to {reshaped_path}")
            
            # Display model input shape info
            logger.info("\n" + "="*70)
            logger.info("For CNN-BiLSTM Model Creation:")
            logger.info("="*70)
            logger.info(f"input_shape = ({timesteps}, {X_train_reshaped.shape[2]})")
            logger.info(f"num_classes = {len(np.unique(y))}")
        
        logger.info("\n" + "✅"*35)
        logger.info("DATA PREPARATION COMPLETE!")
        logger.info("✅"*35)
        
        logger.info(f"\nProcessed files saved to: {OUTPUT_DIR}")
        logger.info("\nNext steps:")
        logger.info("1. Review processed data statistics")
        logger.info("2. Create CNN-BiLSTM model with appropriate input_shape")
        logger.info("3. Train model or run federated learning experiment")
        
    except Exception as e:
        logger.error(f"\n❌ Error: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
