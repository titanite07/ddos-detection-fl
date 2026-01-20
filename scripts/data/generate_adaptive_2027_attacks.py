"""
Generate "Smart-Adaptive 2027" Synthetic DDoS Dataset
Sophisticated adversarial attacks designed to evade traditional detection.

Attack Types:
1. Smart Pulse DDoS (Sinusoidal triggers)
2. AI-Morphing Botnet (Drifting features)
3. Low-Rate DoS (LDoS - Stealthy)
4. Encrypted Tunnel Flood (High entropy)
"""

import numpy as np
import pandas as pd
import time

class Adaptive2027AttackGenerator:
    def __init__(self, seed=42):
        np.random.seed(seed)
        self.attack_types = [
            'BENIGN',
            'Smart_Pulse_DDoS',
            'AI_Morphing_Botnet',
            'Low_Rate_DoS',
            'Encrypted_Tunnel_Flood'
        ]
        
    def generate_adaptive_dataset(self, num_samples=15000, num_features=40):
        """Generate smart-adaptive dataset"""
        print(f"Generating {num_samples} samples with {num_features} features...")
        
        X = np.zeros((num_samples, num_features))
        y = np.zeros(num_samples, dtype=int)
        
        samples_per_class = num_samples // len(self.attack_types)
        
        for i, attack_type in enumerate(self.attack_types):
            start_idx = i * samples_per_class
            end_idx = start_idx + samples_per_class
            
            print(f"  Generating {attack_type}...")
            
            if attack_type == 'BENIGN':
                self._generate_benign(X, start_idx, end_idx)
            elif attack_type == 'Smart_Pulse_DDoS':
                self._generate_smart_pulse(X, start_idx, end_idx)
            elif attack_type == 'AI_Morphing_Botnet':
                self._generate_ai_morphing(X, start_idx, end_idx)
            elif attack_type == 'Low_Rate_DoS':
                self._generate_ldos(X, start_idx, end_idx)
            elif attack_type == 'Encrypted_Tunnel_Flood':
                self._generate_encrypted_flood(X, start_idx, end_idx)
            
            y[start_idx:end_idx] = i
            
        print("Generation complete!")
        return X, y
        
    def _generate_benign(self, X, start, end):
        """Normal traffic patterns: Realistic scales"""
        count = end - start
        
        # flow_duration: 10k - 300k
        X[start:end, 0] = np.random.uniform(10000, 300000, count)
        # packet_rate: 5 - 50
        X[start:end, 1] = np.random.uniform(5, 50, count)
        # byte_rate: 500 - 100k
        X[start:end, 2] = np.random.uniform(500, 100000, count)
        
        # Other features random but scaled
        for i in range(3, X.shape[1]):
            X[start:end, i] = np.random.uniform(0, 100, count)
        
    def _generate_smart_pulse(self, X, start, end):
        """
        Smart Pulse: Packet rate follows sine wave (High Rate)
        """
        count = end - start
        
        # Base traffic (High rate attack)
        # flow_duration: 100 - 5000 (Short pulsing flows)
        X[start:end, 0] = np.random.uniform(100, 5000, count)
        # packet_rate: 10k - 50k (High)
        base_rate = np.random.uniform(10000, 50000, count)
        
        # Add sinusoidal pulse
        t = np.linspace(0, 4*np.pi, count)
        pulse = 10000 * np.sin(t)
        
        X[start:end, 1] = base_rate + pulse
        X[start:end, 2] = X[start:end, 1] * np.random.uniform(60, 1500, count) # Byte rate
        
        # Other features
        for i in range(3, X.shape[1]):
            X[start:end, i] = np.random.uniform(10, 1000, count)
            
    def _generate_ai_morphing(self, X, start, end):
        """
        AI Morphing: Features drift over time (High variation)
        """
        count = end - start
        
        # Random walk for feature centers
        current = np.random.uniform(1000, 50000, X.shape[1])
        
        for i in range(count):
            drift = np.random.normal(0, 100, X.shape[1])
            current += drift
            current = np.clip(current, 0, 1000000)
            X[start+i] = current + np.random.normal(0, 50, X.shape[1])
        
    def _generate_ldos(self, X, start, end):
        """
        Low-Rate DoS: Very stealthy, hides in benign noise
        """
        count = end - start
        # Mimic benign scales closely
        X[start:end, 0] = np.random.uniform(10000, 300000, count) # flow_duration
        X[start:end, 1] = np.random.uniform(5, 60, count) # slightly higher packet rate
        X[start:end, 2] = np.random.uniform(500, 120000, count) # byte_rate
        
        # Anomalous timing (indices 9-10)
        X[start:end, 9] = np.random.uniform(0.1, 0.2, count) # Fixed IAT
        
        for i in range(3, 9):
            X[start:end, i] = np.random.uniform(0, 100, count)
        for i in range(11, X.shape[1]):
            X[start:end, i] = np.random.uniform(0, 100, count)
        
    def _generate_encrypted_flood(self, X, start, end):
        """
        Encrypted Tunnel: High entropy (High byte rates)
        """
        count = end - start
        
        # High byte rates, moderate packet rates
        X[start:end, 0] = np.random.uniform(50, 3000, count)
        X[start:end, 1] = np.random.uniform(5000, 20000, count)
        X[start:end, 2] = np.random.uniform(5000000, 20000000, count) # Huge bandwidth
        
        # Packet size (idx 4) is large and constant-ish (MTU)
        X[start:end, 4] = np.random.normal(1400, 20, count)
        
        for i in range(5, X.shape[1]):
            X[start:end, i] = np.random.uniform(0, 5000, count)

if __name__ == "__main__":
    gen = Adaptive2027AttackGenerator()
    X, y = gen.generate_adaptive_dataset(150, 40)
    print("Test shape:", X.shape)
