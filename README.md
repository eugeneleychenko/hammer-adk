# Hammer ADK Submission

A comprehensive learning management system with AI-powered lesson generation and tracking capabilities.

## Project Structure

```
hammer_adk_submission/
├── backend/                 # Python backend services
│   ├── api_server.py       # Main API server
│   ├── generate_prompt.py  # AI prompt generation
│   ├── lessons_audit_trail.py # Lesson tracking
│   └── pipeline.py         # Data processing pipeline
├── frontend/               # Next.js frontend application
│   ├── src/
│   │   ├── app/           # Next.js app router
│   │   ├── components/    # React components
│   │   └── lib/           # Utility libraries
│   └── public/            # Static assets
├── tests/                  # Test suites
├── sample_data/           # Sample data files
├── docs/                  # Documentation
└── requirements.txt       # Python dependencies
```

## Features

- **AI-Powered Lesson Generation**: Automated content creation using advanced AI models
- **Progress Tracking**: Comprehensive audit trail for learning progress
- **Modern Frontend**: Built with Next.js and React for a responsive user experience
- **RESTful API**: Python-based backend with comprehensive API endpoints
- **Data Pipeline**: Robust data processing and validation

## Prerequisites

- Python 3.8+
- Node.js 18+
- npm or yarn

## Installation

### Backend Setup

1. Navigate to the project root:
   ```bash
   cd hammer_adk_submission
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the backend server:
   ```bash
   cd backend
   python api_server.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

## Usage

1. The backend API will be available at `http://localhost:8000` (or configured port)
2. The frontend application will be available at `http://localhost:3000`
3. Access the lessons dashboard through the web interface

## Testing

Run the test suite:
```bash
cd tests
python -m pytest
```

## API Documentation

The backend provides RESTful endpoints for:
- Lesson management
- Progress tracking
- Data pipeline operations
- AI prompt generation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is part of the Hammer ADK submission. 