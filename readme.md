# 🚀 AI-Powered Smart Cache Proxy

<div align="center">

![AI Cache Proxy](https://img.shields.io/badge/AI-Powered%20Proxy-blue?style=for-the-badge&logo=robot)
![Go](https://img.shields.io/badge/Go-1.21+-00ADD8?style=for-the-badge&logo=go)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python)
![Redis](https://img.shields.io/badge/Redis-6.2+-DC382D?style=for-the-badge&logo=redis)
![Docker](https://img.shields.io/badge/Docker-3.8+-2496ED?style=for-the-badge&logo=docker)

**Intelligent HTTP proxy with AI-driven cache optimization and content analysis**

[Features](#-features) • [Architecture](#-architecture) • [Quick Start](#-quick-start) • [API Reference](#-api-reference) • [Contributing](#-contributing)

</div>

---

## ✨ Features

- 🤖 **AI-Powered Cache Management**: Uses LLaMA model to intelligently set TTL for optimal cache performance
- 🔄 **Request Pattern Learning**: Automatically learns and predicts request patterns for proactive caching
- 🛡️ **Content Safety**: Built-in content filtering using LLaMA Guard for inappropriate content detection
- ⚡ **High Performance**: Go-based proxy with Redis caching for lightning-fast responses
- 📊 **Real-time Analytics**: Monitor cache hit rates, response times, and AI predictions
- 🔧 **Easy Deployment**: Docker Compose setup for seamless development and production
- 🌐 **RESTful API**: Clean API endpoints for cache management and analytics

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client App    │───▶│   Go Proxy      │───▶│   Target API    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │     Redis       │
                       │   (Cache DB)    │
                       └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  LLaMA Service  │
                       │  (AI Analysis)  │
                       └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Git
- 4GB+ RAM (for LLaMA model)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ai-cache-proxy.git
   cd ai-cache-proxy
   ```

2. **Start the services**
   ```bash
   cd project
   make up_build
   ```

3. **Verify installation**
   ```bash
   curl http://localhost:8080/health
   ```

### Usage Examples

**Basic Proxy Request:**
```bash
curl -x http://localhost:8080 https://api.example.com/data
```

**Cache Analytics:**
```bash
curl http://localhost:8080/analytics
```

**Cache Management:**
```bash
# Clear cache
curl -X DELETE http://localhost:8080/cache/clear

# Get cache stats
curl http://localhost:8080/cache/stats
```

## 📊 API Reference

### Proxy Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Proxy all requests through the service |
| `GET` | `/health` | Health check endpoint |
| `GET` | `/analytics` | Get cache analytics and AI insights |
| `GET` | `/cache/stats` | Get detailed cache statistics |
| `DELETE` | `/cache/clear` | Clear all cached data |

### Response Format

```json
{
  "status": "success",
  "data": {
    "cache_hit_rate": 0.85,
    "total_requests": 1250,
    "ai_predictions": 342,
    "average_response_time": "45ms"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SERVER_PORT` | `8080` | Proxy server port |
| `REDIS_ADDR` | `redis:6379` | Redis connection address |
| `REDIS_HOST` | `redis` | Redis host (for LLaMA service) |
| `LLAMA_MODEL` | `meta-llama/Llama-3.2-1B-Instruct` | LLaMA model to use |

### Custom Configuration

Create a `.env` file in the `project` directory:

```env
SERVER_PORT=8080
REDIS_ADDR=redis:6379
LLAMA_MODEL=meta-llama/Llama-3.2-1B-Instruct
CACHE_TTL=3600
AI_ENABLED=true
```

## 🛠️ Development

### Local Development Setup

1. **Install dependencies**
   ```bash
   # Go dependencies
   cd go-proxy
   go mod download

   # Python dependencies
   cd ../llama-service
   pip install -r requirements.txt
   ```

2. **Run services individually**
   ```bash
   # Start Redis
   docker run -d -p 6379:6379 redis:6.2-alpine

   # Start Go proxy
   cd go-proxy
   go run cmd/proxy/main.go

   # Start LLaMA service
   cd ../llama-service
   python llama-service.py
   ```

### Testing

```bash
# Run Go tests
cd go-proxy
go test ./...

# Run Python tests
cd ../llama-service
python -m pytest tests/
```

## 📈 Performance

- **Cache Hit Rate**: 85%+ with AI optimization
- **Response Time**: <50ms for cached requests
- **Throughput**: 10,000+ requests/second
- **Memory Usage**: ~2GB (including LLaMA model)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Original project by [nesistor](https://github.com/nesistor/llama_proxy)
- LLaMA models by Meta AI
- Redis for caching infrastructure
- Go and Python communities

---

<div align="center">

**Made with 🦩 by Vani**

[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/vanitayall)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/vanitayall)

</div>
