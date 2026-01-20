"""
Transformer Deep Learning Model for DDoS Detection

State-of-the-art architecture using Self-Attention mechanisms (Transformer Encoder)
to capture long-range dependencies and complex patterns in network traffic flows.
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import logging
from typing import Tuple, List

logger = logging.getLogger(__name__)

class TransformerBlock(layers.Layer):
    """
    Single Transformer Encoder Block responsible for:
    1. Multi-Head Self-Attention
    2. Feed Forward Network
    3. Layer Normalization & Residual Connections
    """
    def __init__(self, embed_dim, num_heads, ff_dim, rate=0.1):
        super(TransformerBlock, self).__init__()
        self.att = layers.MultiHeadAttention(num_heads=num_heads, key_dim=embed_dim)
        self.ffn = keras.Sequential(
            [layers.Dense(ff_dim, activation="relu"), layers.Dense(embed_dim),]
        )
        self.layernorm1 = layers.LayerNormalization(epsilon=1e-6)
        self.layernorm2 = layers.LayerNormalization(epsilon=1e-6)
        self.dropout1 = layers.Dropout(rate)
        self.dropout2 = layers.Dropout(rate)

    def call(self, inputs, training=True): # training argument required for Dropout
        # Multi-Head Attention
        attn_output = self.att(inputs, inputs)
        attn_output = self.dropout1(attn_output, training=training)
        out1 = self.layernorm1(inputs + attn_output) # Residual Connection

        # Feed Forward Network
        ffn_output = self.ffn(out1)
        ffn_output = self.dropout2(ffn_output, training=training)
        return self.layernorm2(out1 + ffn_output) # Residual Connection
    
    def get_config(self):
        config = super().get_config()
        # No extra config needed if standard layers used internally, 
        # but good practice if valid arguments are passed to __init__
        return config


class TransformerModel:
    """
    Transformer-based Classifier for Network Flows
    """
    def __init__(
        self,
        input_shape: Tuple[int, int], # (timesteps, features)
        num_classes: int,
        head_size: int = 64,   # Embedding size / Key dimension
        num_heads: int = 4,    # Number of attention heads
        ff_dim: int = 128,     # Feed-forward network dimension
        num_transformer_blocks: int = 2,
        mlp_units: List[int] = [128],
        dropout: float = 0.25,
        learning_rate: float = 0.001
    ):
        self.input_shape = input_shape
        self.num_classes = num_classes
        self.head_size = head_size
        self.num_heads = num_heads
        self.ff_dim = ff_dim
        self.num_transformer_blocks = num_transformer_blocks
        self.mlp_units = mlp_units
        self.dropout = dropout
        self.learning_rate = learning_rate
        
        self.model = self._build_model()

    def _build_model(self) -> keras.Model:
        logger.info("Building Transformer model...")
        
        inputs = layers.Input(shape=self.input_shape)
        x = inputs
        
        # We can add an initial projection layer if needed, 
        # but usually we pass the raw features (timesteps, feats) directly to attention
        # if features are numeric.
        
        # Project inputs to head_size dimension for residual connections to work
        x = layers.Dense(self.head_size)(x)

        # Transformer Blocks
        for _ in range(self.num_transformer_blocks):
            x = TransformerBlock(self.head_size, self.num_heads, self.ff_dim, self.dropout)(x)

        # Global Average Pooling to flatten time dimension
        x = layers.GlobalAveragePooling1D()(x)
        
        # MLP Head
        for dim in self.mlp_units:
            x = layers.Dense(dim, activation="relu")(x)
            x = layers.Dropout(self.dropout)(x)

        # Output Layer
        if self.num_classes == 2:
            outputs = layers.Dense(1, activation="sigmoid")(x)
            loss = 'binary_crossentropy'
            metrics = ['accuracy', keras.metrics.AUC(name='auc')]
        else:
            outputs = layers.Dense(self.num_classes, activation="softmax")(x)
            loss = 'sparse_categorical_crossentropy'
            metrics = ['accuracy', keras.metrics.SparseCategoricalAccuracy(name='sparse_acc')]

        model = keras.Model(inputs=inputs, outputs=outputs, name="Transformer_Net")
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=self.learning_rate),
            loss=loss,
            metrics=metrics
        )
        
        logger.info(f"Transformer model built. Params: {model.count_params():,}")
        return model

    def get_model(self):
        return self.model
    
    # Standard interface required mainly for Federated Learning node logic
    def get_weights(self): return self.model.get_weights()
    def set_weights(self, weights): self.model.set_weights(weights)
    def save_model(self, fp): self.model.save(fp)
    def load_model(self, fp): self.model = keras.models.load_model(fp, custom_objects={'TransformerBlock': TransformerBlock})
