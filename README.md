# Privacy-Preserving Distributed DDoS Detection System

A **federated learning-based, multi-agent DDoS detection system** with **zero-trust security** and **blockchain accountability**, powered by **LLM-based intelligent agents** via OpenRouter API.

## Features

- **Federated Learning (FL)**: Privacy-preserving distributed training across multiple edge nodes
- **CNN-BiLSTM Model**: Hybrid deep learning for spatial and temporal DDoS pattern recognition
- **Zero-Trust Security**: Continuous authentication, trust scoring, and anomaly detection
- **LLM-Based Agents**: Intelligent decision-making using OpenRouter API (GPT-4, Claude, LLaMA, etc.)
- **Simulated Blockchain**: Lightweight, immutable audit trail for accountability
- **Multi-Dataset Support**: CICDDoS2019 and NSLKDD datasets
- **Byzantine Resilience**: Robust aggregation and malicious node detection

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Aggregation Server                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   FedAvg     │  │  Trust Mgr   │  │  Blockchain  │          │
│  │ Aggregator   │  │   (Zero-     │  │   Audit      │          │
│  │              │  │   Trust)     │  │   Trail      │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└────────────┬────────────────────────────────┬──────────────────┘
             │                                │
        Global Model                     Trust Scores
      & Participation                   & Security Events
             │                                │
   ┌─────────┴────────────┬───────────────────┴─────┬────────────┐
   │                      │                          │            │
┌──▼───┐              ┌───▼──┐                  ┌───▼──┐     ┌───▼──┐
│Node 1│              │Node 2│                  │Node 3│ ... │Node N│
│      │              │      │                  │      │     │      │
│ CNN- │              │ CNN- │                  │ CNN- │     │ CNN- │
│BiLSTM│              │BiLSTM│                  │BiLSTM│     │BiLSTM│
│      │              │      │                  │      │     │      │
│Local │              │Local │                  │Local │     │Local │
│ Data │              │ Data │                  │ Data │     │ Data │
└──────┘              └──────┘                  └──────┘     └──────┘
   ▲                      ▲                         ▲            ▲
   │                      │                         │            │
   └──────────────────────┴─────────────────────────┴────────────┘
              Traffic Data (Local, Privacy-Preserved)

                    ┌─────────────────────┐
                    │  LLM Agent Engine   │
                    │  (OpenRouter API)   │
                    │                     │
                    │ • Detection Agent   │
                    │ • Coordination      │
                    │ • Trust Assessment  │
                    └─────────────────────┘
```

---

## Quick Start

### 1. Installation

```bash
# Clone repository
cd c:\Users\HP\Desktop\Major Project\Main File-Code\ddosdfl

# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Setup Environment Variables

```bash
# Copy example env file
copy .env.example .env

# Edit .env and add your OpenRouter API key
notepad .env
```

Required environment variables:

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=openai/gpt-4-turbo
DATASET_PATH=C:\Users\HP\Desktop\Major Project\Main File-Code\data
```

Get your OpenRouter API key from: [https://openrouter.ai/](https://openrouter.ai/)

### 3. Verify Setup

```bash
python quick_test.py
```

This will verify:

- Python 3.10+ ✅
- All dependencies installed ✅
- Configuration loaded ✅

---

## Dataset Setup

The system supports **CICDDoS2019** and **NSLKDD** datasets.

### Expected Directory Structure

```
C:\Users\HP\Desktop\Major Project\Main File-Code\data\
│
├── CICDDoS2019\
│   ├── CIC-DDoS-2019-*.csv
│   └── ...
│
└── NSLKDD\
    ├── KDDTrain+.txt
    ├── KDDTest+.txt
    └── ...
```

### Datasets

- **CICDDoS2019**: [Download from Canadian Institute for Cybersecurity](https://www.unb.ca/cic/datasets/ddos-2019.html)
- **NSLKDD**: [Download from UNB](https://www.unb.ca/cic/datasets/nsl.html)

---

## Project Structure

```
ddosdfl/
├── config/
│   ├── node_config.yaml           # Node configuration
│   └── server_config.yaml         # Server configuration (TBD)
│
├── data/                          # Datasets (not in repo)
│
├── projects/
│   ├── aggregation_server/
│   │   ├── __init__.py
│   │   └── aggregation_server.py # FL aggregation server (TBD)
│   │
│   ├── fl_node/
│   │   ├── __init__.py
│   │   ├── local_trainer.py      # ✅ Local model training
│   │   └── node_client.py        # FL node client (TBD)
│   │
│   └── shared_libs/
│       ├── __init__.py
│       ├── config_loader.py      # ✅ YAML config loader
│       ├── data_processor.py     # ✅ Dataset loading & preprocessing
│       ├── cnn_bilstm_model.py   # ✅ CNN-BiLSTM DL model
│       ├── trust_manager.py      # ✅ Zero-trust security
│       ├── openrouter_client.py  # ✅ LLM agent integration
│       └── blockchain_interface.py # ✅ Simulated blockchain
│
├── logs/                          # Training & security logs
├── models/                        # Saved model checkpoints
├── experiments/                   # Experiment scripts (TBD)
│
├── main.py                        # Main orchestrator (TBD)
├── requirements.txt               # ✅ Python dependencies
├── .env.example                   # ✅ Environment template
├── quick_test.py                  # ✅ Setup verification
└── README.md                      # ✅ This file
```

---

## Core Components

### 1. Data Processing (`data_processor.py`)

Load and preprocess CICDDoS2019/NSLKDD datasets:

```python
from projects.shared_libs.data_processor import DatasetLoader, FeatureExtractor, DataPartitioner

# Load dataset
loader = DatasetLoader(dataset_path="C:/path/to/data")
df = loader.load_dataset("cicddos2019")

# Extract features
extractor = FeatureExtractor()
X, y = extractor.preprocess(df, fit=True)

# Partition for FL nodes (IID or non-IID)
partitioner = DataPartitioner(num_nodes=5, iid=True)
node_datasets = partitioner.partition(X, y)
```

### 2. CNN-BiLSTM Model (`cnn_bilstm_model.py`)

Hybrid deep learning architecture:

```python
from projects.shared_libs.cnn_bilstm_model import CNNBiLSTMModel, ModelTrainer

# Build model
model = CNNBiLSTMModel(
    input_shape=(10, 20),  # (timesteps, features)
    num_classes=2,
    cnn_filters=(64, 128),
    lstm_units=(64, 32),
    dropout_rate=0.5
)

# Train
trainer = ModelTrainer(model)
trainer.train(X_train, y_train, X_val, y_val, epochs=50)
```

### 3. Zero-Trust Security (`trust_manager.py`)

Authenticate nodes and detect anomalies:

```python
from projects.shared_libs.trust_manager import TrustManager

trust_mgr = TrustManager(min_trust_threshold=0.5)

# Register node
credentials = trust_mgr.register_node("node-001", {"name": "Edge Node 1"})

# Authenticate
authenticated = trust_mgr.authenticate_node("node-001", credentials.api_key)

# Validate model update
is_valid, analysis = trust_mgr.validate_model_update("node-001", model_weights)
```

### 4. LLM-Based Agents (`openrouter_client.py`)

Intelligent decision-making via OpenRouter:

```python
from projects.shared_libs.openrouter_client import OpenRouterClient, AgentDecisionEngine

client = OpenRouterClient()
engine = AgentDecisionEngine(client)

# Get detection decision
decision = await engine.detect_and_classify(
    traffic_features={"packet_rate": 1500, "byte_volume": 5000000},
    model_prediction="DDoS_UDP_Flood",
    confidence=0.92
)

# result: {"threat_level": "HIGH", "recommended_action": "BLOCK", ...}
```

### 5. Blockchain Audit (`blockchain_interface.py`)

Immutable audit trail:

```python
from projects.shared_libs.blockchain_interface import Blockchain, SmartContract, AuditLogger

blockchain = Blockchain()
smart_contract = SmartContract(blockchain)
audit_logger = AuditLogger(blockchain, smart_contract)

# Register node
smart_contract.register_node("node-001", {"name": "Edge Node 1"})

# Log FL round
smart_contract.record_participation("node-001", round_number=1, model_update_hash="abc123")

# Generate audit report
report = audit_logger.generate_audit_report()
```

### 6. Local Training (`local_trainer.py`)

Train model on local node data:

```python
from projects.fl_node.local_trainer import LocalTrainer

trainer = LocalTrainer(model=model.get_model(), node_id="node-001")

# Train locally
metrics = trainer.train_local_model(
    X_train, y_train, X_val, y_val,
    epochs=5,
    round_number=1
)

# Get weights to send to server
weights = trainer.get_model_weights()
```

---

## Configuration

### Node Configuration (`config/node_config.yaml`)

```yaml
node:
  id: "node-001"
  name: "Local Development Node"
  ip_address: "localhost"
  port: 8080

server:
  aggregation_server_ip: "127.0.0.1"
  aggregation_server_port: 8888

training:
  local_epochs: 5
  batch_size: 32
  learning_rate: 0.001
  max_training_time: 3600

data:
  dataset_path: "./data"
  train_split: 0.7
  val_split: 0.15
  test_split: 0.15

model:
  input_timesteps: 10
  cnn_filters: [64, 128]
  lstm_units: [64, 32]
  dropout_rate: 0.5

security:
  enable_zero_trust: true
  min_trust_threshold: 0.5
  enable_blockchain: true

agent:
  enable_llm_agents: true
  coordination_enabled: true
```

---

## Roadmap

### ✅ Phase 1: Foundation (Complete)

- [x] Data processing for CICDDoS2019/NSLKDD
- [x] CNN-BiLSTM model architecture
- [x] Zero-trust security manager
- [x] OpenRouter LLM agent integration
- [x] Simulated blockchain
- [x] Local trainer

### 🔄 Phase 2: FL Infrastructure (In Progress)

- [ ] FL node client
- [ ] Aggregation server with FedAvg
- [ ] Robust aggregation (Krum, TrimmedMean)
- [ ] Multi-agent coordinator

### 📋 Phase 3: Integration & Orchestration

- [ ] Main orchestrator
- [ ] Multi-node simulation
- [ ] Experiment scripts

### 📋 Phase 4: Testing & Validation

- [ ] Unit tests
- [ ] Integration tests
- [ ] Byzantine attack simulation
- [ ] Performance benchmarks

---

## Research Objectives

1. **High Accuracy**: Achieve >97% DDoS detection accuracy on benchmark datasets
2. **Privacy Preservation**: No raw traffic data leaves local nodes (FL paradigm)
3. **Byzantine Resilience**: Detect and mitigate 20-30% malicious nodes
4. **Scalability**: Support 10+ FL nodes without degradation
5. **Auditability**: Immutable blockchain audit trail for all FL rounds and security events
6. **Intelligent Response**: LLM-based agents for adaptive mitigation strategies

---

## OpenRouter Models

Supported models for LLM agents (configure in `.env`):

- **OpenAI**: `openai/gpt-4-turbo`, `openai/gpt-3.5-turbo`
- **Anthropic**: `anthropic/claude-3-opus`, `anthropic/claude-3-sonnet`
- **Meta**: `meta-llama/llama-3-70b-instruct`
- **Google**: `google/gemini-pro`
- **Mistral**: `mistralai/mixtral-8x7b-instruct`

See [OpenRouter Models](https://openrouter.ai/models) for full list.

---

## License

[Specify License]

---

## Citation

If you use this system in your research, please cite:

```
[Author], [Title], [Conference/Journal], [Year]
```

---

## Contributors

- [Your Name]
- AntiGravity AI Assistant (Google DeepMind)

---

## Support

For issues, questions, or contributions, please contact [your contact info].

---

**Status**: 🔄 **Active Development** - Phase 2 in progress

**Last Updated**: 2026-01-05
