# 🎯 AI Sales Call Analysis Platform

An advanced AI-powered platform that analyzes sales call transcripts using Google's Agent Development Kit (ADK) to provide comprehensive coaching insights and performance optimization for sales professionals.

## 🌟 Overview

This platform transforms sales call analysis by leveraging 14 specialized AI agents running in parallel to extract actionable insights from sales conversation transcripts. Built with a modern tech stack combining Python/Flask backend and Next.js frontend, it provides real-time analysis, learning system tracking, and comprehensive coaching recommendations.

### Key Features

- **🤖 AI-Powered Analysis**: 14 specialized agents analyze different aspects of sales calls
- **⚡ Parallel Processing**: ADK-based orchestration for high-performance analysis
- **📊 Real-time Dashboard**: Live progress tracking with WebSocket connections
- **🧠 Self-Learning System**: Continuous improvement through lessons extraction
- **📈 Plateau Detection**: Smart analytics to optimize data collection
- **🎯 Comprehensive Coaching**: Detailed recommendations for sales improvement

## 🏗️ Architecture

### Backend Components
- **Flask API Server** (`api_server.py`) - RESTful API with WebSocket support
- **ADK Orchestration** (`pipeline.py`) - Parallel AI agent coordination
- **Learning System** (`lessons_audit_trail.py`) - Self-improving knowledge base
- **File Processing** - PDF transcript extraction and validation

### Frontend Components
- **Next.js Dashboard** - Modern React-based user interface
- **Real-time Updates** - Socket.io integration for live progress
- **Responsive Design** - Built with Tailwind CSS and shadcn/ui

### AI Analysis Pipeline

The system employs a sophisticated 3-phase analysis approach:

#### Phase 1: Core Analysis (8 Parallel Agents)
1. **Objection Specialist** - Customer objections and handling techniques
2. **Opening Gambit** - Call openings and first impressions
3. **Needs Assessment** - Discovery questions and customer profiling
4. **Rapport Building** - Relationship establishment techniques
5. **Pattern Recognition** - Conversation patterns and behaviors
6. **Emotional Intelligence** - Emotional cues and responses
7. **Language Optimizer** - Communication effectiveness
8. **Client Profiling** - Customer characterization and segmentation

#### Phase 2: Advanced Analysis (6 Parallel Agents)
9. **Micro Commitments** - Small agreement and buy-in techniques
10. **Conversation Flow** - Dialogue structure and transitions
11. **Budget Handling** - Financial discussions and objections
12. **Urgency Builder** - Time-sensitive motivation techniques
13. **Technical Navigation** - Product complexity management
14. **Cross-selling** - Additional opportunity identification

#### Phase 3: Synthesis
- **Comprehensive Analysis** - Unified insights and recommendations
- **Learning Extraction** - Knowledge base enhancement
- **Coaching Prompts** - Actionable improvement suggestions

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- Google AI API Key (Gemini)

### Backend Setup

1. **Clone and navigate to backend**:
```bash
git clone <repository-url>
cd backend
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure environment**:
```bash
# Create .env file
echo "GOOGLE_API_KEY=your_gemini_api_key_here" > .env
```

4. **Start the server**:
```bash
python api_server.py
```
Server will run on `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend**:
```bash
cd frontend
```

2. **Install dependencies**:
```bash
npm install
```

3. **Start development server**:
```bash
npm run dev
```
Frontend will run on `http://localhost:3000`

## 📋 Usage

### 1. Upload Sales Call Transcript
- Upload PDF files containing sales call transcripts
- Supported format: PDF with extractable text
- File size limit: 10MB

### 2. Start Analysis
- Initiate analysis through the web interface
- Monitor real-time progress via the dashboard
- View individual agent results as they complete

### 3. Review Results
- Access comprehensive analysis reports
- Download individual agent analyses
- Review coaching recommendations
- Track learning system metrics

### 4. Download Outputs
The system generates multiple output files:
- **Individual Agent Reports**: `{filename}_{agent_name}.json`
- **Comprehensive Analysis**: `{filename}_comprehensive_analysis.json`
- **Enhanced Prompts**: `{filename}_enhanced_prompt.txt`
- **Synthesized Learnings**: `synthesized_learnings.json`

## 🛠️ API Endpoints

### Core Analysis
- `POST /upload` - Upload transcript files
- `POST /analyze/{job_id}` - Start analysis job
- `GET /status/{job_id}` - Check analysis progress
- `GET /results/{job_id}` - Retrieve analysis results

### Learning System
- `GET /lessons/metrics` - Learning system statistics
- `GET /lessons/plateau-status` - Plateau detection status
- `GET /lessons/categories` - Lessons by category
- `GET /lessons/audit-trail` - Processing event history

### File Management
- `GET /download/{job_id}/{file_type}` - Download specific result files
- `GET /validate/{job_id}` - Validate output file structure
- `GET /jobs` - List all processing jobs

## 🧪 Testing

Run the test suite to validate system functionality:

```bash
cd tests
python test_pipeline.py      # Test ADK orchestration
python test_lessons_system.py # Test learning system
python test_validation.py    # Test file validation
```

## 📊 Learning System Features

### Plateau Detection
- Monitors lesson extraction efficiency
- Detects diminishing returns in data collection
- Provides recommendations for optimization

### Quality Metrics
- Deduplication rate tracking
- Lesson uniqueness scoring
- Category saturation analysis

### Audit Trail
- Complete processing event history
- Performance trend analysis
- Business intelligence insights

## 🔧 Configuration

### Environment Variables
```bash
GOOGLE_API_KEY=your_gemini_api_key
FLASK_ENV=development
LOG_LEVEL=INFO
```

### System Parameters
- **Upload Directory**: `uploads/`
- **Results Directory**: `comprehensive_results/`
- **Max File Size**: 10MB
- **Parallel Agents**: 14 simultaneous
- **Plateau Window**: 7 days

## 📁 Project Structure

```
hammer_adk_submission/
├── backend/
│   ├── api_server.py           # Flask API server
│   ├── pipeline.py             # ADK orchestration
│   ├── lessons_audit_trail.py  # Learning system
│   └── generate_prompt.py      # Prompt generation
├── frontend/
│   ├── src/
│   │   ├── app/                # Next.js app directory
│   │   └── components/         # React components
│   └── package.json
├── tests/
│   ├── test_pipeline.py        # Pipeline tests
│   ├── test_lessons_system.py  # Learning tests
│   └── test_validation.py      # Validation tests
└── requirements.txt            # Python dependencies
```

## 🚀 Performance Optimizations

- **Parallel Processing**: 14 agents run simultaneously
- **ADK Integration**: Google's optimized agent orchestration
- **WebSocket Updates**: Real-time progress without polling
- **Intelligent Caching**: Results stored for quick retrieval
- **File Validation**: Comprehensive output verification

## 📈 Monitoring & Analytics

### Real-time Metrics
- Processing speed and throughput
- Agent execution times
- Success/failure rates
- Memory and CPU usage

### Learning Analytics
- Lesson extraction rates
- Quality score trends
- Category saturation levels
- Plateau detection status

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is part of a research submission and is provided for evaluation purposes.

## 🔗 Related Technologies

- [Google ADK (Agent Development Kit)](https://ai.google.dev/adk)
- [Google Gemini AI](https://ai.google.dev/gemini-api)
- [Next.js](https://nextjs.org/)
- [Flask](https://flask.palletsprojects.com/)
- [Socket.IO](https://socket.io/)
- [Tailwind CSS](https://tailwindcss.com/)

## 📞 Support

For technical questions or issues, please refer to the test files and documentation within the codebase.

---

**Note**: This system is designed for sales call analysis and coaching. Ensure all uploaded transcripts comply with privacy regulations and company policies. 