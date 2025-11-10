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
- 🎲 **Randomization**: User-agent rotation and random query parameters
- 📊 **Real-Time Statistics**: Live updates during attack execution
- 🔧 **Flexible Configuration**: Support for HTTP/HTTPS, custom ports, and headers
- 💻 **Cross-Platform**: Works on Windows, Linux, and macOS
- 📦 **No Dependencies**: Uses only Python standard library

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

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

3. **No additional dependencies required!** The tool uses only Python standard library.

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
| `--threads` | `-t` | Number of concurrent threads | `135` | `-t 500` |
| `--mode` | Attack mode (flood/slowloris) | `flood` | `--mode slowloris` |
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
└── requirements.txt   # Dependencies (none required)
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
