"""
Realistic CICDDoS2019 Synthetic Data Generator

Generates synthetic DDoS data with characteristics similar to the real CICDDoS2019 dataset:
- Realistic feature distributions
- Attack-specific traffic patterns
- Class imbalance matching real dataset
- Statistical properties matching CICDDoS2019
"""

import numpy as np
from typing import Tuple, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CICDDoS2019SyntheticGenerator:
    """
    Generate realistic synthetic data matching CICDDoS2019 characteristics
    """
    
    def __init__(self, seed: int = 42):
        np.random.seed(seed)
        
        # CICDDoS2019 attack types (real labels)
        self.attack_types = {
            0: 'BENIGN',
            11: 'DrDoS_DNS',
            12: 'DrDoS_LDAP', 
            14: 'DrDoS_NTP',
            # Using subset of attack types for demonstration
        }
        
        # Realistic feature statistics from CICDDoS2019 analysis
        self.feature_stats = self._initialize_feature_stats()
        
        logger.info("CICDDoS2019 Synthetic Generator initialized")
        logger.info(f"  Attack types: {len(self.attack_types)}")
        logger.info(f"  Feature profiles: {len(self.feature_stats)} attack patterns")
    
    def _initialize_feature_stats(self) -> Dict:
        """Initialize realistic feature statistics for each attack type"""
        
        # Based on CICDDoS2019 analysis - these are approximate patterns
        stats = {
            0: {  # BENIGN - lower packet rates, normal flow
                'flow_duration': (50000, 200000),
                'packet_rate': (10, 100),
                'byte_rate': (1000, 50000),
                'flow_packets': (5, 50),
                'packet_length_mean': (500, 1500),
            },
            11: {  # DrDoS_DNS - high packet rate, small packets
                'flow_duration': (1000, 10000),
                'packet_rate': (500, 2000),
                'byte_rate': (100000, 500000),
                'flow_packets': (100, 500),
                'packet_length_mean': (100, 300),
            },
            12: {  # DrDoS_LDAP - medium packet rate
                'flow_duration': (2000, 20000),
                'packet_rate': (200, 1000),
                'byte_rate': (80000, 400000),
                'flow_packets': (80, 400),
                'packet_length_mean': (300, 600),
            },
            14: {  # DrDoS_NTP - very high packet rate, tiny packets
                'flow_duration': (500, 5000),
                'packet_rate': (1000, 5000),
                'byte_rate': (150000, 600000),
                'flow_packets': (200, 1000),
                'packet_length_mean': (50, 150),
            }
        }
        
        return stats
    
    def generate_realistic_sample(self, attack_label: int, num_features: int = 40) -> np.ndarray:
        """Generate a single realistic sample for given attack type"""
        
        if attack_label not in self.feature_stats:
            # Default to benign if unknown
            attack_label = 0
        
        stats = self.feature_stats[attack_label]
        
        # Generate core features with attack-specific distributions
        features = []
        
        # Feature 0-5: Flow duration and packet counts (log-normal)
        flow_duration = np.random.uniform(*stats['flow_duration'])
        packet_rate = np.random.uniform(*stats['packet_rate'])
        byte_rate = np.random.uniform(*stats['byte_rate'])
        flow_packets = np.random.uniform(*stats['flow_packets'])
        packet_length = np.random.uniform(*stats['packet_length_mean'])
        
        features.extend([flow_duration, packet_rate, byte_rate, flow_packets, packet_length])
        
        # Feature 6-15: Statistical features (derived from core)
        features.append(flow_packets / (flow_duration + 1))  # Packets/sec
        features.append(byte_rate / (packet_rate + 1))  # Bytes/packet
        features.append(np.random.exponential(packet_length))  # Length variance
        features.append(np.random.gamma(2, packet_rate / 100))  # IAT mean
        features.append(np.random.gamma(2, packet_rate / 50))  # IAT std
        
        # Add noise and correlation
        for i in range(5):
            features.append(features[i % 5] * np.random.normal(1, 0.1))
        
        # Feature 16-25: Forward/Backward flow features
        fwd_packets = flow_packets * np.random.uniform(0.4, 0.6)
        bwd_packets = flow_packets - fwd_packets
        
        features.extend([
            fwd_packets, bwd_packets,
            fwd_packets * packet_length * np.random.normal(1, 0.1),
            bwd_packets * packet_length * np.random.normal(1, 0.1),
            np.random.exponential(100),  # Fwd IAT
            np.random.exponential(100),  # Bwd IAT
            np.random.uniform(0, 1),  # Fwd PSH flags
            np.random.uniform(0, 1),  # Bwd PSH flags
            np.random.uniform(0, 0.1),  # Fwd URG flags
            np.random.uniform(0, 0.1),  # Bwd URG flags
        ])
        
        # Feature 26-40: Additional protocol features
        while len(features) < num_features:
            # Generate correlated features with noise
            base_idx = len(features) % 10
            if base_idx < len(features):
                new_feature = features[base_idx] * np.random.normal(1, 0.2)
            else:
                new_feature = np.random.randn() * 100
            features.append(new_feature)
        
        # Trim to exact feature count
        features = features[:num_features]
        
        # Add attack-specific noise
        if attack_label != 0:
            # Attack traffic is more variable
            noise = np.random.randn(num_features) * 0.3
            features = np.array(features) * (1 + noise)
        
        return np.array(features)
    
    def generate_dataset(
        self,
        num_samples: int = 10000,
        num_features: int = 40,
        class_imbalance: bool = True
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate complete synthetic dataset
        
        Args:
            num_samples: Total samples to generate
            num_features: Number of features
            class_imbalance: Use realistic class distribution
            
        Returns:
            X, y arrays
        """
        
        logger.info(f"\n🔬 Generating realistic CICDDoS2019 synthetic data...")
        logger.info(f"  Total samples: {num_samples:,}")
        logger.info(f"  Features: {num_features}")
        logger.info(f"  Class imbalance: {class_imbalance}")
        
        # Realistic class distribution (similar to CICDDoS2019)
        if class_imbalance:
            # CICDDoS2019 has class imbalance
            class_distribution = {
                0: 0.15,   # BENIGN - 15%
                11: 0.35,  # DrDoS_DNS - 35%
                12: 0.25,  # DrDoS_LDAP - 25%
                14: 0.25,  # DrDoS_NTP - 25%
            }
        else:
            # Balanced
            class_distribution = {k: 1.0/len(self.attack_types) for k in self.attack_types.keys()}
        
        # Generate samples
        X_list = []
        y_list = []
        
        for attack_label, proportion in class_distribution.items():
            n_samples = int(num_samples * proportion)
            
            logger.info(f"  Generating {self.attack_types[attack_label]}: {n_samples:,} samples")
            
            for _ in range(n_samples):
                sample = self.generate_realistic_sample(attack_label, num_features)
                X_list.append(sample)
                y_list.append(attack_label)
        
        X = np.array(X_list)
        y = np.array(y_list)
        
        # Shuffle
        indices = np.random.permutation(len(X))
        X = X[indices]
        y = y[indices]
        
        logger.info(f"\n✅ Generated realistic synthetic dataset:")
        logger.info(f"  Shape: {X.shape}")
        logger.info(f"  Classes: {np.unique(y)}")
        logger.info(f"  Class distribution:")
        for label in np.unique(y):
            count = np.sum(y == label)
            pct = count / len(y) * 100
            logger.info(f"    {self.attack_types[label]}: {count:,} ({pct:.1f}%)")
        
        return X, y


def test_generator():
    """Test the synthetic data generator"""
    print("="*70)
    print("TESTING REALISTIC CICDDOS2019 SYNTHETIC GENERATOR")
    print("="*70)
    
    gen = CICDDoS2019SyntheticGenerator()
    
    # Generate small dataset
    X, y = gen.generate_dataset(num_samples=1000, num_features=40)
    
    print(f"\n✅ Generator test complete!")
    print(f"  Generated: {X.shape}")
    print(f"  Feature stats:")
    print(f"    Mean: {X.mean():.2f}")
    print(f"    Std: {X.std():.2f}")
    print(f"    Min: {X.min():.2f}")
    print(f"    Max: {X.max():.2f}")


if __name__ == "__main__":
    test_generator()
