# 🔍 AI Developer Tools Research Agent

An **agentic AI-powered API** that automatically researches, compares, and recommends developer tools using live web search and LLM analysis.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-Agentic_AI-purple.svg)
![Groq](https://img.shields.io/badge/Groq-Llama_3.3-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

<p align="center">
  <img src="https://img.shields.io/badge/Live-Demo-brightgreen?style=for-the-badge" alt="Live Demo"/>
</p>

<p align="center">
  <a href=" https://ai-agent-1-53gg.onrender.com/">🌐 Live Demo</a> •
  <a href="https://ai-agent-uw23.onrender.com/docs">📖 API Docs</a> •
  <a href="#features">✨ Features</a> •
  <a href="#tech-stack">🛠️ Tech Stack</a>
</p>

---

## 🎯 What It Does

**Input:** Any developer tool query  
**Output:** Researched tools with AI-powered recommendations

```
User: "best database for startups"
         ↓
    [Live Web Search]
         ↓
    [Extract Tool Names]
         ↓
    [Research Each Tool]
         ↓
    [AI Analysis & Recommendations]
         ↓
Output: Supabase, PlanetScale, Neon, Firebase
        + Pricing, Features, Integrations
        + AI Recommendation: "Use Supabase for..."
```

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔎 **Live Web Search** | Real-time search using Tavily API |
| 🤖 **Agentic Workflow** | Multi-step LangGraph orchestration |
| 📊 **Deep Analysis** | Extracts pricing, features, integrations |
| 💡 **AI Recommendations** | Personalized suggestions using Llama 3.3 70B |
| 📖 **Auto Documentation** | Interactive Swagger UI |
| 🌐 **Any Query** | Works with any developer tool query |

---

## 🛠️ Tech Stack

### Core Technologies

| Technology | Purpose | Why |
|------------|---------|-----|
| **FastAPI** | API Framework | Fast, modern, auto-docs |
| **LangGraph** | Agent Orchestration | Multi-step AI workflows |
| **Groq** | LLM Provider | Fast inference, free tier |
| **Llama 3.3 70B** | Language Model | Powerful, open-source |
| **Tavily** | Web Search | AI-optimized search API |
| **Pydantic** | Data Validation | Type-safe models |

### Supporting Libraries

| Library | Purpose |
|---------|---------|
| **httpx** | HTTP client for web scraping |
| **BeautifulSoup4** | HTML parsing |
| **python-dotenv** | Environment management |
| **uvicorn** | ASGI server |

### Infrastructure

| Service | Purpose |
|---------|---------|
| **Render** | Cloud deployment |
| **Docker** | Containerization |
| **GitHub** | Version control |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Server                          │
│                    (main.py + /docs)                         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   LangGraph Workflow                         │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Extract    │─▶│   Research   │─▶│   Analyze    │       │
│  │    Tools     │  │    Tools     │  │  & Recommend │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
         │                   │                   │
         ▼                   ▼                   ▼
   ┌──────────┐        ┌──────────┐        ┌──────────┐
   │  Tavily  │        │ Scraper  │        │   Groq   │
   │  Search  │        │ (httpx)  │        │   LLM    │
   └──────────┘        └──────────┘        └──────────┘
         │                   │                   │
         ▼                   ▼                   ▼
   ┌──────────┐        ┌──────────┐        ┌──────────┐
   │   Web    │        │ Websites │        │Llama 3.3 │
   │ Results  │        │   HTML   │        │   70B    │
   └──────────┘        └──────────┘        └──────────┘
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Landing page |
| `GET` | `/health` | Health check |
| `GET` | `/docs` | Swagger UI documentation |
| `GET` | `/examples` | Example queries |
| `POST` | `/research` | **Main endpoint** - Research tools |
| `GET` | `/research/{id}` | Get cached research |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- [Groq API Key](https://console.groq.com) (free)
- [Tavily API Key](https://app.tavily.com) (free)

### Installation

```bash
# Clone the repository
git clone https://github.com/EmonKarmaker/AI-agent.git
cd AI-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your API keys
```

### Run Locally

```bash
uvicorn main:app --reload
```

Open: http://127.0.0.1:8000/docs

### Test the API

```bash
curl -X POST "http://127.0.0.1:8000/research" \
  -H "Content-Type: application/json" \
  -d '{"query": "best database for startups"}'
```

---

## 📋 Example Queries

```json
{"query": "best database for startups"}
{"query": "React state management libraries"}
{"query": "AI coding assistants 2024"}
{"query": "kubernetes alternatives"}
{"query": "vector databases for machine learning"}
{"query": "payment APIs for SaaS"}
{"query": "headless CMS comparison"}
{"query": "backend as a service platforms"}
```

---

## 📦 Example Response

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "query": "best AI coding assistants 2024",
  "tools": [
    {
      "name": "GitHub Copilot",
      "website": "https://github.com/features/copilot",
      "description": "AI coding assistant that helps you write code faster",
      "pricing_model": "Freemium",
      "is_open_source": false,
      "language_support": ["Python", "JavaScript", "TypeScript"],
      "integrations": ["VS Code", "JetBrains", "Neovim"]
    },
    {
      "name": "Cursor",
      "website": "https://cursor.sh",
      "description": "AI-powered code editor built on VS Code",
      "pricing_model": "Freemium",
      "is_open_source": false,
      "language_support": ["All major languages"],
      "integrations": ["GitHub", "GitLab"]
    }
  ],
  "recommendations": "## 🏆 Top Pick\nGitHub Copilot is ideal for...",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## 🐳 Docker Deployment

```bash
# Build
docker build -t ai-agent .

# Run
docker run -p 8000:8000 \
  -e GROQ_API_KEY=your_key \
  -e TAVILY_API_KEY=your_key \
  ai-agent
```

---

## ☁️ Deploy to Render

1. Fork this repository
2. Go to [render.com](https://render.com)
3. New → Web Service → Connect repo
4. Configure:
   - **Runtime:** Docker
   - **Instance:** Free
5. Add environment variables:
   - `GROQ_API_KEY`
   - `TAVILY_API_KEY`
6. Deploy! 🚀

---

## 📁 Project Structure

```
AI-agent/
├── src/
│   ├── __init__.py       # Package exports
│   ├── models.py         # Pydantic data models
│   ├── prompts.py        # LLM prompt templates
│   ├── search.py         # Tavily search service
│   ├── scraper.py        # Web scraping service
│   ├── llm.py            # Groq LLM service
│   └── workflow.py       # LangGraph workflow
├── static/
│   └── index.html        # Landing page
├── main.py               # FastAPI application
├── requirements.txt      # Dependencies
├── Dockerfile            # Container config
├── render.yaml           # Render deployment
├── .env.example          # Environment template
└── README.md             # This file
```

---

## 🔑 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | ✅ | Groq API key for LLM |
| `TAVILY_API_KEY` | ✅ | Tavily API key for search |

---

## 💰 Cost

**$0** - This project uses only free tiers:

| Service | Free Tier |
|---------|-----------|
| Groq | 30 req/min, 14,400 req/day |
| Tavily | 1,000 searches/month |
| Render | 750 hours/month |

---

## 🔮 Future Improvements

- [ ] Add more search providers (fallback)
- [ ] Cache results with Redis
- [ ] Add authentication
- [ ] Rate limiting
- [ ] WebSocket for real-time updates
- [ ] Frontend dashboard

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open a Pull Request

---

## 📄 License

MIT License - feel free to use for your portfolio!

---

## 👨‍💻 Author

**Emon Karmaker**

- GitHub: [@EmonKarmaker](https://github.com/EmonKarmaker)

---

## 🙏 Acknowledgments

- [Groq](https://groq.com) - Fast LLM inference
- [Tavily](https://tavily.com) - AI-powered search
- [LangGraph](https://langchain-ai.github.io/langgraph/) - Agent orchestration
- [FastAPI](https://fastapi.tiangolo.com) - Modern API framework

---

<p align="center">
  <b>⭐ Star this repo if you found it useful!</b>
</p>

<p align="center">
  Built with ❤️ using 100% Free APIs
</p>

