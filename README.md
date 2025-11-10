# Advanced Load Testing / DDoS CLI Tool

A high-performance command-line tool for sending massive amounts of HTTP traffic to web applications in a short period of time. Features multiple attack modes, randomization, and advanced techniques for comprehensive load testing and stress testing of your own applications.

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

## Tools Included

### 1. `app.py` - Web Frontend Interface 🌐 ⭐
**Modern web-based interface for DDoS-Ripper**
- Beautiful, responsive web UI
- Real-time statistics via WebSocket
- Easy-to-use form interface
- Live attack monitoring
- Start/stop controls
- Visual statistics dashboard
- No command-line knowledge required

### 2. `DRipper.py` - DDoS-Ripper Style Tool ⭐
**Matches the original DDoS-Ripper CLI style and functionality**
- Simple CLI: `python3 DRipper.py -s [target] -t [threads]`
- Thread-based implementation (not async)
- Socket-level HTTP requests for maximum performance
- Supports both HTTP and HTTPS
- Loads custom headers from `headers.txt` file
- Two attack modes: Flood and Slowloris
- Real-time statistics display

## Features

### Advanced Features (ddos_tool.py)
- 🚀 **High-performance async HTTP requests** using `aiohttp`
- 🔥 **Multiple attack modes**: Flood, Slowloris
- 🎲 **Randomization**: User-agent rotation, random query parameters, random POST data
- ♾️ **Continuous mode**: Infinite requests until stopped
- ⏱️ **Duration-based attacks**: Run for a specific time period
- 📊 **Real-time statistics**: Live updates during attack
- 📈 **Detailed metrics**: Response times, status codes, bandwidth usage
- 🔧 **Multiple HTTP methods**: GET, POST, PUT, DELETE, PATCH, HEAD
- ⚡ **Aggressive connection pooling**: Optimized for maximum throughput
- 🎯 **Custom headers and data**: Full control over request parameters

### Basic Features (load_tester.py)
- Standard load testing capabilities
- Configurable concurrency and request count
- Basic statistics and metrics

## Installation

1. Ensure you have Python 3.7+ installed
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Deployment

### Vercel Deployment (Recommended for Web Interface)

The web interface (`app.py`) can be deployed to Vercel for easy access. See [README_VERCEL.md](README_VERCEL.md) for detailed deployment instructions.

**Quick Deploy:**
1. Push your code to GitHub/GitLab/Bitbucket
2. Go to [Vercel Dashboard](https://vercel.com/dashboard)
3. Click "New Project" and import your repository
4. Deploy!

**Or use Vercel CLI:**
```bash
npm i -g vercel
vercel
```

The app is configured for Vercel with:
- Serverless function entry point: `api/index.py`
- Configuration: `vercel.json`
- HTTP polling instead of WebSockets (Vercel-compatible)

## Usage

### Web Frontend Interface (app.py) 🌐 ⭐

#### Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Start the web server
python app.py
```

Then open your browser and navigate to: **http://localhost:5000**

#### Features
- **Easy Configuration**: Fill in target, threads, and mode
- **Real-Time Stats**: See live statistics as the attack runs
- **Visual Dashboard**: Beautiful cards showing all metrics
- **Start/Stop Controls**: Simple buttons to control the attack
- **Responsive Design**: Works on desktop and mobile devices

#### Web Interface Features
- Target input (IP, hostname, or URL)
- Thread count slider/input
- Attack mode selector (Flood/Slowloris)
- Real-time statistics:
  - Total requests
  - Successful requests
  - Failed requests
  - Requests per second (RPS)
  - Duration
  - Success rate
- Error breakdown
- Status panel

### DDoS-Ripper Style Tool (DRipper.py) ⭐

#### Basic Usage (Matches Original DDoS-Ripper)
```bash
# Basic attack with IP address
python3 DRipper.py -s 192.168.1.1 -t 135

# Attack with URL
python3 DRipper.py -s https://example.com -t 200

# Attack with hostname and port
python3 DRipper.py -s example.com:8080 -t 500
```

#### Command-Line Options
```
-s, --server    Target server (IP address, hostname, or URL) [REQUIRED]
-t, --threads   Number of threads (default: 135)
--mode          Attack mode: flood (default) or slowloris
```

#### Examples
```bash
# Basic flood attack
python3 DRipper.py -s 192.168.1.1 -t 135

# High-intensity attack
python3 DRipper.py -s https://example.com -t 1000

# Slowloris attack
python3 DRipper.py -s example.com -t 500 --mode slowloris

# Attack with custom port
python3 DRipper.py -s 192.168.1.1:8080 -t 200
```

#### Custom Headers
Create a `headers.txt` file with custom headers (one per line, format: `Key: Value`):
```
User-Agent: Custom-Agent/1.0
Accept: application/json
Authorization: Bearer token123
```

### Advanced Tool (ddos_tool.py)

#### Basic Flood Attack
```bash
# Send 10,000 requests with 200 concurrent connections
python ddos_tool.py https://example.com -n 10000 -c 200
```

#### Continuous Attack (Infinite)
```bash
# Continuous attack until stopped (Ctrl+C)
python ddos_tool.py https://example.com -c 500 --continuous
```

#### Duration-Based Attack
```bash
# Attack for 60 seconds
python ddos_tool.py https://example.com -c 300 --duration 60
```

#### Slowloris Attack
```bash
# Slowloris-style attack (keeps connections open)
python ddos_tool.py https://example.com -c 1000 --mode slowloris
```

#### POST Attack with Random Data
```bash
# POST requests with randomly generated data
python ddos_tool.py https://api.example.com/endpoint -n 5000 -c 200 -m POST
```

#### With Custom Headers
```bash
python ddos_tool.py https://api.example.com -n 10000 -c 500 -H "Authorization:Bearer token,Content-Type:application/json"
```

#### Disable Randomization
```bash
# Use fixed user agent and no random parameters
python ddos_tool.py https://example.com -n 5000 -c 100 --no-random-ua --no-random-params
```

### Command-Line Options (ddos_tool.py)

```
positional arguments:
  url                   Target URL to attack

optional arguments:
  -h, --help            Show help message
  -n, --requests N      Total number of requests (default: 1000, ignored if --continuous)
  -c, --concurrency C   Number of concurrent requests (default: 100)
  -t, --timeout T       Request timeout in seconds (default: 10)
  -m, --method METHOD   HTTP method: GET, POST, PUT, DELETE, PATCH, HEAD (default: GET)
  -H, --headers HEADERS Custom headers in format "Key:Value,Key2:Value2"
  -d, --data DATA       Data to send with POST/PUT requests
  --mode MODE           Attack mode: flood (default) or slowloris
  --no-random-ua        Disable random user agent rotation
  --no-random-params    Disable random query parameters
  --continuous          Continuous attack (infinite requests until stopped)
  --duration SECONDS    Attack duration in seconds (overrides -n)
  --threads N           Number of worker threads (default: same as concurrency)
```

### Basic Tool (load_tester.py)

```bash
# Basic load test
python load_tester.py https://example.com -n 1000 -c 50
```

## Output

Both tools provide comprehensive statistics:

- **Duration**: Total test execution time
- **Total Requests**: Number of requests sent
- **Success/Failed**: Success and failure counts with percentages
- **Requests/sec**: Throughput metric (RPS)
- **Bytes Sent/Received**: Bandwidth usage
- **Response Times**: Average, min, max, 95th and 99th percentiles
- **Status Codes**: Distribution of HTTP status codes
- **Errors**: Breakdown of error types encountered

The advanced tool (`ddos_tool.py`) also shows real-time statistics during execution.

## Attack Modes

### Flood Mode (Default)
- Sends requests as fast as possible
- Uses connection pooling for maximum throughput
- Randomizes user agents, parameters, and data
- Best for general load testing

### Slowloris Mode
- Keeps connections open for extended periods
- Attempts to exhaust server connection pool
- Uses fewer resources but targets connection limits
- Best for testing connection handling

## Performance Tips

1. **Start Small**: Begin with lower concurrency (50-100) and gradually increase
2. **Monitor Resources**: Watch CPU, memory, and network usage
3. **Network Bandwidth**: Consider your network capacity
4. **Target Server**: Be aware of the target server's capacity and rate limits
5. **Timeout Settings**: Adjust timeout based on expected response times
6. **Continuous Mode**: Use for stress testing over extended periods
7. **Randomization**: Helps bypass simple rate limiting and caching

## Examples

### High-Intensity Flood Attack
```bash
python ddos_tool.py https://example.com -n 100000 -c 500
```

### Continuous Stress Test
```bash
python ddos_tool.py https://api.example.com -c 200 --continuous
```

### 5-Minute Load Test
```bash
python ddos_tool.py https://example.com -c 300 --duration 300
```

### API Endpoint Testing
```bash
python ddos_tool.py https://api.example.com/v1/users -n 5000 -c 100 -m POST -H "Authorization:Bearer token123"
```

## Limitations

- **Single Machine**: Runs on one machine - for distributed testing, use multiple instances
- **Network Bandwidth**: Your network capacity limits maximum throughput
- **System Resources**: CPU and memory affect performance
- **Target Server**: Server capacity and rate limiting affect results
- **Legal Restrictions**: Only use on systems you own or have permission to test

## Technical Details

- Built with Python 3.7+ and `aiohttp` for async HTTP requests
- Uses asyncio for high-performance concurrent operations
- Implements connection pooling and keep-alive connections
- Supports SSL/TLS connections
- Thread-safe statistics collection
- Real-time performance monitoring

## License

This tool is provided as-is for educational and legitimate testing purposes. Use at your own risk and only on systems you own or have explicit permission to test.
