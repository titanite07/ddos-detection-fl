"""
Real-Time FL-DDoS Monitoring Dashboard

Flask-based web dashboard with WebSocket support for real-time monitoring.
Visualizes FL training progress, node status, and attack detection.
"""

from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import json
import time
from datetime import datetime
from pathlib import Path
import threading
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fl-ddos-dashboard-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Store current FL state
fl_state = {
    'current_round': 0,
    'total_rounds': 20,
    'accuracy': 0.0,
    'loss': 0.0,
    'nodes': {},
    'attacks_detected': 0,
    'is_training': False,
    'history': []
}


@app.route('/')
def index():
    """Dashboard home page"""
    return render_template('dashboard.html')


@app.route('/api/status')
def get_status():
    """Get current FL status"""
    return jsonify(fl_state)


@app.route('/api/start_training')
def start_training():
    """Start FL training simulation"""
    fl_state['is_training'] = True
    threading.Thread(target=simulate_fl_training, daemon=True).start()
    return jsonify({'status': 'started'})


@app.route('/api/stop_training')
def stop_training():
    """Stop FL training"""
    fl_state['is_training'] = False
    return jsonify({'status': 'stopped'})


def simulate_fl_training():
    """Simulate FL training for demo purposes"""
    
    fl_state['current_round'] = 0
    fl_state['accuracy'] = 0.5
    fl_state['loss'] = 2.0
    fl_state['attacks_detected'] = 0
    fl_state['history'] = []
    
    # Initialize nodes
    for i in range(1, 6):
        fl_state['nodes'][f'node{i}'] = {
            'status': 'active',
            'accuracy': 0.5,
            'samples': random.randint(5000, 15000),
            'trust_score': random.uniform(0.85, 1.0)
        }
    
    while fl_state['is_training'] and fl_state['current_round'] < fl_state['total_rounds']:
        fl_state['current_round'] += 1
        
        # Simulate improvement
        fl_state['accuracy'] = min(0.99, fl_state['accuracy'] + random.uniform(0.01, 0.03))
        fl_state['loss'] = max(0.01, fl_state['loss'] * 0.9)
        
        # Update nodes
        for node_id in fl_state['nodes']:
            node = fl_state['nodes'][node_id]
            node['accuracy'] = fl_state['accuracy'] + random.uniform(-0.05, 0.05)
            
            # Simulate Byzantine node in round 10
            if fl_state['current_round'] == 10 and node_id == 'node3':
                node['trust_score'] = 0.4
                node['status'] = 'suspicious'
                fl_state['attacks_detected'] += 1
            elif node['status'] == 'suspicious':
                node['status'] = 'removed'
            else:
                node['trust_score'] = min(1.0, node['trust_score'] + random.uniform(-0.02, 0.05))
        
        # Add to history
        fl_state['history'].append({
            'round': fl_state['current_round'],
            'accuracy': fl_state['accuracy'],
            'loss': fl_state['loss'],
            'timestamp': datetime.now().isoformat()
        })
        
        # Emit update via WebSocket
        socketio.emit('fl_update', fl_state)
        
        time.sleep(2)  # 2 seconds per round
    
    fl_state['is_training'] = False
    socketio.emit('training_complete', {'message': 'Training completed!'})


@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('status', fl_state)


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')


@socketio.on('request_update')
def handle_update_request():
    """Handle update request from client"""
    emit('fl_update', fl_state)


if __name__ == '__main__':
    print("="*70)
    print("FL-DDoS Monitoring Dashboard")
    print("="*70)
    print(f"\n🌐 Dashboard running at: http://localhost:5000")
    print(f"📊 Features:")
    print(f"  - Real-time FL monitoring")
    print(f"  - Node status visualization")
    print(f"  - Attack detection alerts")
    print(f"  - Performance graphs")
    print(f"\n💡 Open http://localhost:5000 in your browser")
    print("="*70 + "\n")
    
    socketio.run(app, debug=True, port=5000, allow_unsafe_werkzeug=True)
