"""
Synthetic DDoS Traffic Generator

Generates realistic synthetic network traffic with various DDoS attack patterns
for testing FL-DDoS system on new, unseen data.
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import logging
from typing import Tuple, Dict
import pickle

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SyntheticDDoSGenerator:
    """
    Generate synthetic DDoS traffic data matching CICDDoS2019 feature space.
    """
    
    def __init__(self, num_features: int = 40, random_seed: int = 42):
        """
        Initialize generator.
        
        Args:
            num_features: Number of features (matches selected features)
            random_seed: Random seed for reproducibility
        """
        self.num_features = num_features
        self.random_seed = random_seed
        np.random.seed(random_seed)
        
        # Attack type definitions
        self.attack_types = {
            0: 'BENIGN',
            1: 'UDP_Flood',
            2: 'SYN_Flood',
            3: 'DNS_Amplification',
            4: 'ICMP_Flood',
            5: 'HTTP_Flood',
            6: 'SlowLoris',
            7: 'NTP_Amplification',
            8: 'SSDP_Amplification',
            9: 'Port_Scan'
        }
        
        logger.info(f"Initialized synthetic generator with {num_features} features")
        logger.info(f"Attack types: {len(self.attack_types)}")
    
    def _generate_benign_traffic(self, n_samples: int) -> np.ndarray:
        """Generate benign (normal) traffic patterns"""
        
        # Benign traffic characteristics
        features = np.zeros((n_samples, self.num_features))
        
        # Flow duration: moderate
        features[:, 0] = np.random.exponential(scale=5.0, size=n_samples)
        
        # Total packets: low to moderate
        features[:, 1] = np.random.poisson(lam=50, size=n_samples)
        features[:, 2] = np.random.poisson(lam=50, size=n_samples)
        
        # Packet sizes: normal distribution
        features[:, 3] = np.random.normal(loc=500, scale=100, size=n_samples)
        features[:, 4] = np.random.normal(loc=500, scale=100, size=n_samples)
        
        # Inter-arrival times: varied
        features[:, 5] = np.random.exponential(scale=0.1, size=n_samples)
        
        # Flags: mostly normal combinations
        features[:, 6] = np.random.binomial(1, 0.3, size=n_samples)  # SYN flag
        features[:, 7] = np.random.binomial(1, 0.3, size=n_samples)  # ACK flag
        
        # Fill remaining features with normal patterns
        for i in range(8, self.num_features):
            features[:, i] = np.random.normal(loc=0.5, scale=0.2, size=n_samples)
        
        return features
    
    def _generate_udp_flood(self, n_samples: int) -> np.ndarray:
        """Generate UDP flood attack patterns"""
        
        features = np.zeros((n_samples, self.num_features))
        
        # UDP flood: high packet rate, short duration
        features[:, 0] = np.random.exponential(scale=0.5, size=n_samples)  # Short duration
        features[:, 1] = np.random.poisson(lam=500, size=n_samples)  # Many packets
        features[:, 2] = np.random.poisson(lam=10, size=n_samples)  # Few responses
        
        # Small packet sizes (typical for floods)
        features[:, 3] = np.random.normal(loc=64, scale=10, size=n_samples)
        features[:, 4] = np.random.normal(loc=64, scale=10, size=n_samples)
        
        # Very short inter-arrival times
        features[:, 5] = np.random.exponential(scale=0.01, size=n_samples)
        
        # No TCP flags (UDP)
        features[:, 6] = 0
        features[:, 7] = 0
        
        # High throughput indicators
        for i in range(8, self.num_features):
            features[:, i] = np.random.normal(loc=0.9, scale=0.1, size=n_samples)
        
        return features
    
    def _generate_syn_flood(self, n_samples: int) -> np.ndarray:
        """Generate SYN flood attack patterns"""
        
        features = np.zeros((n_samples, self.num_features))
        
        # SYN flood: many SYN packets, no completion
        features[:, 0] = np.random.exponential(scale=1.0, size=n_samples)
        features[:, 1] = np.random.poisson(lam=200, size=n_samples)
        features[:, 2] = np.random.poisson(lam=5, size=n_samples)  # No responses
        
        # Small packets
        features[:, 3] = np.random.normal(loc=60, scale=5, size=n_samples)
        
        # Short intervals
        features[:, 5] = np.random.exponential(scale=0.02, size=n_samples)
        
        # SYN flag always set, ACK never
        features[:, 6] = 1  # SYN
        features[:, 7] = 0  # No ACK
        
        for i in range(8, self.num_features):
            features[:, i] = np.random.normal(loc=0.8, scale=0.15, size=n_samples)
        
        return features
    
    def _generate_http_flood(self, n_samples: int) -> np.ndarray:
        """Generate HTTP flood attack patterns"""
        
        features = np.zeros((n_samples, self.num_features))
        
        # HTTP flood: moderate connections, high request rate
        features[:, 0] = np.random.exponential(scale=2.0, size=n_samples)
        features[:, 1] = np.random.poisson(lam=100, size=n_samples)
        features[:, 2] = np.random.poisson(lam=100, size=n_samples)
        
        # Larger packets (HTTP headers/data)
        features[:, 3] = np.random.normal(loc=800, scale=200, size=n_samples)
        features[:, 4] = np.random.normal(loc=1500, scale=300, size=n_samples)
        
        # Moderate intervals
        features[:, 5] = np.random.exponential(scale=0.05, size=n_samples)
        
        # Normal TCP flags
        features[:, 6] = np.random.binomial(1, 0.5, size=n_samples)
        features[:, 7] = np.random.binomial(1, 0.8, size=n_samples)
        
        for i in range(8, self.num_features):
            features[:, i] = np.random.normal(loc=0.7, scale=0.2, size=n_samples)
        
        return features
    
    def _generate_slowloris(self, n_samples: int) -> np.ndarray:
        """Generate SlowLoris attack patterns"""
        
        features = np.zeros((n_samples, self.num_features))
        
        # SlowLoris: long connections, slow data rate
        features[:, 0] = np.random.exponential(scale=100.0, size=n_samples)  # Long duration
        features[:, 1] = np.random.poisson(lam=20, size=n_samples)  # Few packets
        features[:, 2] = np.random.poisson(lam=20, size=n_samples)
        
        # Small packets sent slowly
        features[:, 3] = np.random.normal(loc=100, scale=20, size=n_samples)
        
        # Long inter-arrival times (slow sending)
        features[:, 5] = np.random.exponential(scale=5.0, size=n_samples)
        
        features[:, 6] = 1
        features[:, 7] = 1
        
        for i in range(8, self.num_features):
            features[:, i] = np.random.normal(loc=0.3, scale=0.1, size=n_samples)
        
        return features
    
    def generate_dataset(
        self,
        n_samples: int = 50000,
        attack_distribution: Dict[str, float] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate complete synthetic dataset.
        
        Args:
            n_samples: Total number of samples
            attack_distribution: Distribution of attack types (defaults to balanced)
            
        Returns:
            (X, y) features and labels
        """
        logger.info(f"\nGenerating {n_samples:,} synthetic samples...")
        
        if attack_distribution is None:
            # Default: balanced distribution
            attack_distribution = {
                'BENIGN': 0.50,
                'UDP_Flood': 0.10,
                'SYN_Flood': 0.10,
                'DNS_Amplification': 0.05,
                'ICMP_Flood': 0.05,
                'HTTP_Flood': 0.10,
                'SlowLoris': 0.05,
                'NTP_Amplification': 0.02,
                'SSDP_Amplification': 0.02,
                'Port_Scan': 0.01
            }
        
        # Calculate samples per class
        samples_per_class = {}
        for attack_name, ratio in attack_distribution.items():
            samples_per_class[attack_name] = int(n_samples * ratio)
        
        # Generate data
        all_features = []
        all_labels = []
        
        for attack_id, attack_name in self.attack_types.items():
            n = samples_per_class.get(attack_name, 0)
            if n == 0:
                continue
            
            logger.info(f"  Generating {n:,} samples of {attack_name}...")
            
            if attack_name == 'BENIGN':
                features = self._generate_benign_traffic(n)
            elif attack_name == 'UDP_Flood':
                features = self._generate_udp_flood(n)
            elif attack_name == 'SYN_Flood':
                features = self._generate_syn_flood(n)
            elif attack_name == 'HTTP_Flood':
                features = self._generate_http_flood(n)
            elif attack_name == 'SlowLoris':
                features = self._generate_slowloris(n)
            else:
                # For other attacks, use UDP flood with variation
                features = self._generate_udp_flood(n)
                features += np.random.normal(0, 0.1, features.shape)
            
            labels = np.full(n, attack_id)
            
            all_features.append(features)
            all_labels.append(labels)
        
        # Combine and shuffle
        X = np.vstack(all_features)
        y = np.concatenate(all_labels)
        
        # Shuffle
        shuffle_idx = np.random.permutation(len(X))
        X = X[shuffle_idx]
        y = y[shuffle_idx]
        
        # Normalize features
        scaler = StandardScaler()
        X = scaler.fit_transform(X)
        
        logger.info(f"\n✓ Generated {len(X):,} samples")
        logger.info(f"  Features shape: {X.shape}")
        logger.info(f"  Unique labels: {len(np.unique(y))}")
        logger.info(f"  Label distribution:")
        for label_id in np.unique(y):
            count = np.sum(y == label_id)
            attack_name = self.attack_types[label_id]
            logger.info(f"    {attack_name}: {count:,} ({count/len(y)*100:.1f}%)")
        
        return X, y
    
    def save_dataset(
        self,
        X: np.ndarray,
        y: np.ndarray,
        filename: str = 'data/processed/synthetic_ddos_data.npz'
    ):
        """Save generated dataset"""
        import os
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        np.savez(filename, X=X, y=y)
        logger.info(f"\n✓ Saved synthetic dataset to: {filename}")
        logger.info(f"  Size: {os.path.getsize(filename) / (1024**2):.2f} MB")


def test_generator():
    """Test the synthetic generator"""
    
    print("\n" + "="*70)
    print("SYNTHETIC DDOS TRAFFIC GENERATOR TEST")
    print("="*70)
    
    generator = SyntheticDDoSGenerator(num_features=40)
    
    # Generate small dataset for testing
    X, y = generator.generate_dataset(n_samples=10000)
    
    # Save
    generator.save_dataset(X, y)
    
    print("\n✓ Synthetic data generation test complete!")
    
    return X, y


if __name__ == "__main__":
    test_generator()
