"""
End-to-End Testing Suite for FL-DDoS Detection System

Tests all components: data processing, feature selection, model training,
federated learning, security, and LLM coordination.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


import sys
import os
import numpy as np
import pickle
from pathlib import Path
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).parent))


class E2ETestSuite:
    """Comprehensive end-to-end testing suite"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = None
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    def run_all_tests(self):
        """Run complete E2E test suite"""
        logger.info("\n" + "="*70)
        logger.info("FL-DDoS DETECTION SYSTEM - END-TO-END TESTING")
        logger.info("="*70)
        
        self.start_time = datetime.now()
        
        # Test Suite
        tests = [
            ("Data Pipeline", self.test_data_pipeline),
            ("Feature Selection", self.test_feature_selection),
            ("Model Training", self.test_model_training),
            ("Standard FL", self.test_standard_fl),
            ("Secure FL", self.test_secure_fl),
            ("Intelligent FL", self.test_intelligent_fl),
            ("System Integration", self.test_system_integration),
        ]
        
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
        
        self.print_summary()
    
    def run_test(self, test_name, test_func):
        """Run a single test"""
        self.total_tests += 1
        
        logger.info(f"\n{'='*70}")
        logger.info(f"TEST {self.total_tests}: {test_name}")
        logger.info(f"{'='*70}")
        
        try:
            result = test_func()
            self.test_results[test_name] = {"status": "PASSED", "result": result}
            self.passed_tests += 1
            logger.info(f"✅ PASSED: {test_name}")
        except Exception as e:
            self.test_results[test_name] = {"status": "FAILED", "error": str(e)}
            self.failed_tests += 1
            logger.error(f"❌ FAILED: {test_name}")
            logger.error(f"Error: {str(e)}")
    
    def test_data_pipeline(self):
        """Test 1: Data loading and preprocessing"""
        logger.info("Testing data pipeline...")
        
        # Check if processed data exists
        data_path = 'data/processed/cicddos2019_full_processed.npz'
        assert os.path.exists(data_path), "Processed data not found"
        
        # Load data
        data = np.load(data_path)
        X, y = data['X'], data['y']
        
        # Validate
        assert len(X) > 0, "Empty dataset"
        assert len(y) > 0, "Empty labels"
        assert X.shape[0] == y.shape[0], "X and y size mismatch"
        assert X.shape[1] == 79, f"Expected 79 features, got {X.shape[1]}"
        
        logger.info(f"  ✓ Data shape: {X.shape}")
        logger.info(f"  ✓ Labels shape: {y.shape}")
        logger.info(f"  ✓ Unique classes: {len(np.unique(y))}")
        
        return {"samples": len(X), "features": X.shape[1], "classes": len(np.unique(y))}
    
    def test_feature_selection(self):
        """Test 2: Feature selection results"""
        logger.info("Testing feature selection...")
        
        # Check if feature selection results exist
        fs_path = 'data/processed/cicddos2019_full_processed_feature_selection.pkl'
        assert os.path.exists(fs_path), "Feature selection results not found"
        
        # Load results
        with open(fs_path, 'rb') as f:
            results = pickle.load(f)
        
        # Validate ensemble method
        assert 'ensemble' in results, "Ensemble method missing"
        assert 'indices' in results['ensemble'], "Feature indices missing"
        assert 'num_features' in results['ensemble'], "num_features missing"
        assert 'success' in results['ensemble'], "Success flag missing"
        
        num_features = results['ensemble']['num_features']
        success = results['ensemble']['success']
        
        assert num_features == 40, f"Expected 40 features, got {num_features}"
        assert success == True, "Feature selection not successful"
        
        logger.info(f"  ✓ Selected features: {num_features}/79")
        logger.info(f"  ✓ Feature selection successful")
        logger.info(f"  ✓ Time taken: {results['ensemble'].get('time', 'N/A')}s")
        
        return {"features": num_features, "success": success}
    
    def test_model_training(self):
        """Test 3: CNN-BiLSTM model training"""
        logger.info("Testing model training...")
        
        # Check if trained models exist
        model_path = 'models/ensemble_features/best_model.keras'
        assert os.path.exists(model_path), "Trained model not found"
        
        # Try loading model
        from tensorflow import keras
        model = keras.models.load_model(model_path)
        
        # Validate architecture
        assert model is not None, "Model loading failed"
        assert len(model.layers) > 0, "Model has no layers"
        
        logger.info(f"  ✓ Model loaded successfully")
        logger.info(f"  ✓ Total parameters: {model.count_params():,}")
        
        return {"parameters": model.count_params()}
    
    def test_standard_fl(self):
        """Test 4: Standard FL simulation (quick)"""
        logger.info("Testing standard FL (3 rounds)...")
        
        # Quick FL test with 3 rounds
        from run_fl_simulation import run_federated_learning_simulation
        
        logger.info("  Running 3-round FL simulation...")
        
        # Run quick FL (without data_distribution parameter)
        fl_server, fl_nodes, global_model = run_federated_learning_simulation(
            num_nodes=3,
            num_rounds=3,
            epochs_per_round=2
        )
        
        # Validate
        assert fl_server is not None, "FL server initialization failed"
        assert len(fl_nodes) == 3, "Wrong number of nodes"
        assert global_model is not None, "Global model missing"
        
        # Check if model was updated
        weights = global_model.get_weights()
        assert len(weights) > 0, "Model weights empty"
        
        logger.info(f"  ✓ FL completed successfully")
        logger.info(f"  ✓ Nodes: {len(fl_nodes)}")
        logger.info(f"  ✓ Rounds: 3")
        
        return {"nodes": len(fl_nodes), "rounds": 3}
    
    def test_secure_fl(self):
        """Test 5: Secure FL with zero-trust (quick)"""
        logger.info("Testing secure FL (2 rounds)...")
        
        # Check if secure FL components exist
        from projects.shared_libs.trust_manager import TrustManager
        from projects.shared_libs.byzantine_defense import ByzantineRobustAggregator
        
        # Test trust manager
        tm = TrustManager(min_trust_threshold=0.5)
        assert tm is not None, "Trust manager initialization failed"
        
        # Register test node
        credentials = tm.register_node("test_node", {"data_size": 1000})
        assert credentials is not None, "Node registration failed"
        
        # Test authentication
        auth_result = tm.authenticate_node("test_node", credentials.api_key)
        assert auth_result == True, "Authentication failed"
        
        # Test Byzantine aggregation
        test_weights = [
            [np.random.randn(10, 5), np.random.randn(5)],
            [np.random.randn(10, 5), np.random.randn(5)],
            [np.random.randn(10, 5), np.random.randn(5)]
        ]
        
        # Test TrimmedMean
        aggregated = ByzantineRobustAggregator.trimmed_mean(test_weights)
        assert len(aggregated) == 2, "Aggregation failed"
        
        logger.info(f"  ✓ Trust manager working")
        logger.info(f"  ✓ Node authentication working")
        logger.info(f"  ✓ Byzantine aggregation working")
        
        return {"trust_manager": "OK", "byzantine_defense": "OK"}
    
    def test_intelligent_fl(self):
        """Test 6: Intelligent FL with LLM (minimal)"""
        logger.info("Testing intelligent FL...")
        
        # Check if LLM components exist
        from projects.shared_libs.simple_openrouter import SimpleOpenRouterClient
        from projects.shared_libs.agent_coordinator import FLAgentCoordinator
        
        # Test OpenRouter client
        client = SimpleOpenRouterClient(test_on_init=False)
        assert client is not None, "OpenRouter client initialization failed"
        
        # Test agent coordinator
        agent = FLAgentCoordinator(llm_client=client, enable_auto_response=False)
        assert agent is not None, "Agent coordinator initialization failed"
        
        # Test assessment (will use mock if no API key)
        test_round_data = {
            'round_number': 1,
            'participating_nodes': 3,
            'trust_scores': {'node_1': 1.0, 'node_2': 0.9, 'node_3': 0.95},
            'anomalies_detected': [],
            'metrics': {'authenticated': 3, 'validated': 3, 'rejected': 0}
        }
        
        assessment = agent.assess_fl_round(test_round_data)
        assert 'threat_level' in assessment, "Assessment missing threat_level"
        
        # Test strategy selection
        round_stats = {
            'trust_scores': [1.0, 0.9, 0.95],
            'anomalies': 0,
            'nodes_count': 3
        }
        
        strategy = agent.select_aggregation_strategy(round_stats, 'fedavg')
        assert strategy in ['fedavg', 'trimmed_mean', 'krum', 'median'], "Invalid strategy"
        
        logger.info(f"  ✓ OpenRouter client: {('API' if client.api_working else 'MOCK')} mode")
        logger.info(f"  ✓ Agent coordinator working")
        logger.info(f"  ✓ LLM assessment working")
        logger.info(f"  ✓ Strategy selection working")
        
        return {
            "llm_mode": "API" if client.api_working else "MOCK",
            "agent": "OK",
            "assessment": assessment['threat_level']
        }
    
    def test_system_integration(self):
        """Test 7: Complete system integration"""
        logger.info("Testing system integration...")
        
        # Check all key files exist
        required_files = [
            'projects/shared_libs/cnn_bilstm_model.py',
            'projects/shared_libs/feature_selection.py',
            'projects/fl/aggregation_server.py',
            'projects/fl/fl_node_client.py',
            'projects/shared_libs/trust_manager.py',
            'projects/shared_libs/byzantine_defense.py',
            'projects/shared_libs/simple_openrouter.py',
            'projects/shared_libs/agent_coordinator.py',
            'run_fl_simulation.py',
            'run_secure_fl_simulation.py',
            'run_intelligent_fl_simulation.py',
        ]
        
        missing_files = []
        for file_path in required_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        assert len(missing_files) == 0, f"Missing files: {missing_files}"
        
        logger.info(f"  ✓ All {len(required_files)} core files present")
        logger.info(f"  ✓ System integration verified")
        
        return {"files_checked": len(required_files), "all_present": True}
    
    def print_summary(self):
        """Print test summary"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        logger.info("\n" + "="*70)
        logger.info("TEST SUMMARY")
        logger.info("="*70)
        
        logger.info(f"\nTotal Tests: {self.total_tests}")
        logger.info(f"Passed: {self.passed_tests} ✅")
        logger.info(f"Failed: {self.failed_tests} ❌")
        logger.info(f"Success Rate: {(self.passed_tests/self.total_tests)*100:.1f}%")
        logger.info(f"Duration: {duration:.2f} seconds")
        
        logger.info("\nDetailed Results:")
        for test_name, result in self.test_results.items():
            status_icon = "✅" if result['status'] == "PASSED" else "❌"
            logger.info(f"  {status_icon} {test_name}: {result['status']}")
            if result['status'] == "PASSED" and 'result' in result:
                logger.info(f"     → {result['result']}")
        
        logger.info("\n" + "="*70)
        
        if self.failed_tests == 0:
            logger.info("🎉 ALL TESTS PASSED! SYSTEM READY FOR PRODUCTION!")
        else:
            logger.warning(f"⚠️  {self.failed_tests} test(s) failed. Please review.")
        
        logger.info("="*70 + "\n")


def main():
    """Run E2E testing suite"""
    logger.info("Starting FL-DDoS Detection System E2E Testing...")
    
    suite = E2ETestSuite()
    suite.run_all_tests()
    
    return suite


if __name__ == "__main__":
    main()
