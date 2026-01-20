"""
Modern 2026 Attack Pattern Synthetic Data Generator

Generates realistic synthetic data for contemporary DDoS attack patterns:
- IoT botnet attacks (Mirai variants, Reaper)
- DDoS-as-a-Service (booter/stresser services)
- Amplification attacks (DNS, NTP, Memcached, SSDP)
- Application layer attacks (HTTP floods, Slowloris, RUDY)
- Volumetric attacks (UDP/TCP floods)
- Protocol attacks (SYN flood, ACK flood)
"""

import numpy as np
from typing import Tuple, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Modern2026AttackGenerator:
    """
    Generate synthetic data matching 2026 attack patterns
    """
    
    def __init__(self, seed: int = 42):
        np.random.seed(seed)
        
        # Modern attack types (2026 threat landscape)
        self.attack_types = {
            0: 'BENIGN',
            1: 'Mirai_IoT_Botnet',
            2: 'DDoS_as_Service',
            3: 'DNS_Amplification',
            4: 'Memcached_Amplification',
            5: 'HTTP_Flood',
            6: 'Slowloris',
            7: 'SYN_Flood',
            8: 'UDP_Flood',
            9: 'SSDP_Amplification',
        }
        
        self.feature_profiles = self._initialize_modern_profiles()
        
        logger.info("Modern 2026 Attack Generator initialized")
        logger.info(f"  Attack types: {len(self.attack_types)}")
        logger.info(f"  Threat landscape: 2026 contemporary attacks")
    
    def _initialize_modern_profiles(self) -> Dict:
        """Initialize feature profiles for modern attacks"""
        
        profiles = {
            0: {  # BENIGN - normal web traffic
                'flow_duration': (10000, 300000),
                'packet_rate': (5, 50),
                'byte_rate': (500, 100000),
                'flow_packets': (3, 100),
                'packet_length_mean': (800, 1500),
                'packets_per_second': (1, 20),
                'syn_flag_ratio': (0.05, 0.15),
                'ack_flag_ratio': (0.7, 0.9),
            },
            1: {  # Mirai IoT Botnet - massive distributed attack
                'flow_duration': (100, 5000),
                'packet_rate': (2000, 10000),
                'byte_rate': (500000, 2000000),
                'flow_packets': (1000, 5000),
                'packet_length_mean': (64, 512),  # Small packets
                'packets_per_second': (100, 500),
                'syn_flag_ratio': (0.3, 0.5),
                'ack_flag_ratio': (0.1, 0.3),
            },
            2: {  # DDoS-as-a-Service (booter/stresser)
                'flow_duration': (500, 10000),
                'packet_rate': (5000, 20000),
                'byte_rate': (1000000, 5000000),
                'flow_packets': (2000, 10000),
                'packet_length_mean': (128, 1024),
                'packets_per_second': (200, 1000),
                'syn_flag_ratio': (0.4, 0.6),
                'ack_flag_ratio': (0.1, 0.2),
            },
            3: {  # DNS Amplification - high amplification factor
                'flow_duration': (50, 2000),
                'packet_rate': (10000, 50000),
                'byte_rate': (3000000, 10000000),
                'flow_packets': (5000, 25000),
                'packet_length_mean': (512, 1500),  # Large responses
                'packets_per_second': (500, 2000),
                'syn_flag_ratio': (0.0, 0.05),
                'ack_flag_ratio': (0.0, 0.1),
            },
            4: {  # Memcached Amplification - extreme amplification
                'flow_duration': (30, 1000),
                'packet_rate': (15000, 60000),
                'byte_rate': (5000000, 20000000),
                'flow_packets': (10000, 50000),
                'packet_length_mean': (1024, 1500),  # Max size packets
                'packets_per_second': (1000, 3000),
                'syn_flag_ratio': (0.0, 0.02),
                'ack_flag_ratio': (0.0, 0.05),
            },
            5: {  # HTTP Flood - application layer
                'flow_duration': (1000, 20000),
                'packet_rate': (500, 5000),
                'byte_rate': (200000, 1000000),
                'flow_packets': (200, 2000),
                'packet_length_mean': (400, 1200),
                'packets_per_second': (50, 200),
                'syn_flag_ratio': (0.1, 0.2),
                'ack_flag_ratio': (0.6, 0.8),
            },
            6: {  # Slowloris - low and slow
                'flow_duration': (60000, 300000),  # Very long
                'packet_rate': (1, 10),  # Very slow
                'byte_rate': (100, 5000),
                'flow_packets': (10, 100),
                'packet_length_mean': (50, 200),  # Tiny packets
                'packets_per_second': (0.1, 1),
                'syn_flag_ratio': (0.05, 0.1),
                'ack_flag_ratio': (0.8, 0.95),
            },
            7: {  # SYN Flood - classic protocol attack
                'flow_duration': (10, 500),
                'packet_rate': (10000, 50000),
                'byte_rate': (800000, 4000000),
                'flow_packets': (5000, 30000),
                'packet_length_mean': (40, 80),  # SYN packets
                'packets_per_second': (500, 2000),
                'syn_flag_ratio': (0.9, 1.0),  # All SYN
                'ack_flag_ratio': (0.0, 0.05),
            },
            8: {  # UDP Flood - volumetric
                'flow_duration': (100, 5000),
                'packet_rate': (8000, 40000),
                'byte_rate': (2000000, 8000000),
                'flow_packets': (3000, 15000),
                'packet_length_mean': (256, 1024),
                'packets_per_second': (300, 1500),
                'syn_flag_ratio': (0.0, 0.0),  # No TCP flags
                'ack_flag_ratio': (0.0, 0.0),
            },
            9: {  # SSDP Amplification - modern IoT attack
                'flow_duration': (50, 3000),
                'packet_rate': (12000, 55000),
                'byte_rate': (4000000, 15000000),
                'flow_packets': (6000, 30000),
                'packet_length_mean': (600, 1400),
                'packets_per_second': (600, 2500),
                'syn_flag_ratio': (0.0, 0.03),
                'ack_flag_ratio': (0.0, 0.08),
            },
        }
        
        return profiles
    
    def generate_modern_sample(self, attack_label: int, num_features: int = 40) -> np.ndarray:
        """Generate a single sample with modern attack characteristics"""
        
        if attack_label not in self.feature_profiles:
            attack_label = 0
        
        profile = self.feature_profiles[attack_label]
        
        features = []
        
        # Core features (0-9)
        flow_duration = np.random.uniform(*profile['flow_duration'])
        packet_rate = np.random.uniform(*profile['packet_rate'])
        byte_rate = np.random.uniform(*profile['byte_rate'])
        flow_packets = np.random.uniform(*profile['flow_packets'])
        packet_length = np.random.uniform(*profile['packet_length_mean'])
        packets_per_sec = np.random.uniform(*profile['packets_per_second'])
        syn_ratio = np.random.uniform(*profile['syn_flag_ratio'])
        ack_ratio = np.random.uniform(*profile['ack_flag_ratio'])
        
        features.extend([
            flow_duration, packet_rate, byte_rate, flow_packets, packet_length,
            packets_per_sec, syn_ratio, ack_ratio,
            np.random.exponential(100),  # Inter-arrival time
            np.random.gamma(2, packet_rate / 100)  # Burstiness
        ])
        
        # Statistical features (10-20)
        features.extend([
            flow_packets / (flow_duration / 1000 + 1),  # Packets/sec normalized
            byte_rate / (packet_rate + 1),  # Bytes/packet
            np.random.exponential(packet_length / 2),  # Length variance
            np.random.uniform(0, 1),  # FIN flag ratio
            np.random.uniform(0, 0.1),  # RST flag ratio
            np.random.uniform(0, 0.1),  # PSH flag ratio
            np.random.uniform(0, 0.05),  # URG flag ratio
            np.random.exponential(50),  # Forward IAT
            np.random.exponential(50),  # Backward IAT
            flow_packets * 0.6,  # Forward packets
            flow_packets * 0.4,  # Backward packets
        ])
        
        # Protocol-specific features (21-30)
        features.extend([
            byte_rate * 0.6,  # Forward bytes
            byte_rate * 0.4,  # Backward bytes
            np.random.uniform(0, 100),  # Forward header length
            np.random.uniform(0, 100),  # Backward header length
            packets_per_sec / (flow_packets + 1),  # Flow rate
            np.random.exponential(10),  # Down/Up ratio
            packet_length * np.random.normal(1, 0.1),  # Average packet size
            np.random.uniform(0, 10),  # Segment size avg
            np.random.uniform(0, 5),  # Active mean
            np.random.uniform(0, 10),  # Idle mean
        ])
        
        # Pad or trim to exact feature count
        while len(features) < num_features:
            base_idx = len(features) % 10
            features.append(features[base_idx] * np.random.normal(1, 0.15))
        
        features = features[:num_features]
        
        # Add attack-specific noise
        if attack_label != 0:
            noise = np.random.randn(num_features) * 0.2
            features = np.array(features) * (1 + noise)
        
        return np.array(features)
    
    def generate_modern_dataset(
        self,
        num_samples: int = 20000,
        num_features: int = 40
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Generate complete modern attack dataset"""
        
        logger.info(f"\n🔬 Generating Modern 2026 Attack Data...")
        logger.info(f"  Total samples: {num_samples:,}")
        logger.info(f"  Features: {num_features}")
        logger.info(f"  Attack types: Contemporary 2026 threats")
        
        # Realistic distribution (modern threat landscape)
        class_distribution = {
            0: 0.20,   # BENIGN - 20%
            1: 0.15,   # Mirai IoT - 15%
            2: 0.12,   # DDoS-as-Service - 12%
            3: 0.10,   # DNS Amplification - 10%
            4: 0.08,   # Memcached - 8%
            5: 0.12,   # HTTP Flood - 12%
            6: 0.05,   # Slowloris - 5%
            7: 0.08,   # SYN Flood - 8%
            8: 0.06,   # UDP Flood - 6%
            9: 0.04,   # SSDP - 4%
        }
        
        X_list = []
        y_list = []
        
        for attack_label, proportion in class_distribution.items():
            n_samples = int(num_samples * proportion)
            
            logger.info(f"  Generating {self.attack_types[attack_label]}: {n_samples:,} samples")
            
            for _ in range(n_samples):
                sample = self.generate_modern_sample(attack_label, num_features)
                X_list.append(sample)
                y_list.append(attack_label)
        
        X = np.array(X_list)
        y = np.array(y_list)
        
        # Shuffle
        indices = np.random.permutation(len(X))
        X = X[indices]
        y = y[indices]
        
        logger.info(f"\n✅ Generated modern attack dataset:")
        logger.info(f"  Shape: {X.shape}")
        logger.info(f"  Classes: {len(np.unique(y))}")
        logger.info(f"\n  📊 2026 Threat Distribution:")
        for label in np.unique(y):
            count = np.sum(y == label)
            pct = count / len(y) * 100
            logger.info(f"    {self.attack_types[label]}: {count:,} ({pct:.1f}%)")
        
        return X, y


def test_modern_generator():
    """Test the modern attack generator"""
    print("="*70)
    print("TESTING MODERN 2026 ATTACK GENERATOR")
    print("="*70)
    
    gen = Modern2026AttackGenerator()
    
    # Generate dataset
    X, y = gen.generate_modern_dataset(num_samples=5000, num_features=40)
    
    print(f"\n✅ Generator test complete!")
    print(f"  Generated: {X.shape}")
    print(f"  Attack types: {len(np.unique(y))}")
    print(f"  Feature stats:")
    print(f"    Mean: {X.mean():.2f}")
    print(f"    Std: {X.std():.2f}")


if __name__ == "__main__":
    test_modern_generator()
