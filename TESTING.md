# 🧪 Testing Instructions - AI Sales Call Analysis Platform

This document provides comprehensive testing instructions for evaluating the AI Sales Call Analysis Platform submission for the hackathon.

## 🎯 Quick Test Overview

The platform analyzes sales call transcripts using 14 parallel AI agents to provide coaching insights. Testing covers:
- File upload and processing
- AI analysis pipeline execution
- Real-time progress monitoring
- Results generation and download
- Learning system functionality

## 🚀 Prerequisites for Testing

### Required Setup
```bash
# 1. Python 3.8+ and Node.js 18+
python --version  # Should be 3.8+
node --version    # Should be 18+

# 2. Google AI API Key (Gemini)
# Get your free API key at: https://ai.google.dev/
export GOOGLE_API_KEY="your_gemini_api_key_here"
```

### Environment Configuration
```bash
# Backend setup
cd backend
pip install -r requirements.txt
echo "GOOGLE_API_KEY=your_key_here" > .env

# Frontend setup  
cd ../frontend
npm install
```

## 🧪 Test Suite Execution

### 1. Automated Unit Tests

Run the comprehensive test suite to validate core functionality:

```bash
cd tests

# Test 1: Pipeline and ADK Integration
python test_pipeline.py
# Expected: All 14 AI agents initialize correctly
# Expected: Parallel processing capabilities verified
# Expected: Error handling and recovery tested

# Test 2: Learning System Validation
python test_lessons_system.py  
# Expected: Lesson extraction and deduplication working
# Expected: Plateau detection algorithms functional
# Expected: Audit trail recording properly

# Test 3: File Validation and Processing
python test_validation.py
# Expected: PDF text extraction working
# Expected: Output file structure validation
# Expected: Error handling for corrupted files
```

### 2. Integration Testing

```bash
# Start backend server
cd backend
python api_server.py
# Server should start on http://localhost:5000

# In new terminal, start frontend
cd frontend  
npm run dev
# Frontend should start on http://localhost:3000
```

## 📁 Test Data Provided

The system includes sample test data for evaluation:

### Sample Sales Call Transcripts
Located in `sample_data/` directory:
- `sample_call_1.pdf` - Discovery call transcript
- `sample_call_2.pdf` - Product demo transcript  
- `sample_call_3.pdf` - Closing meeting transcript

## 🔍 Manual Testing Workflow

### Test Case 1: File Upload and Analysis

1. **Navigate to Platform**
   - Open browser to `http://localhost:3000`
   - Verify dashboard loads with upload interface

2. **Upload Test File**
   ```bash
   # Use provided sample or create test PDF
   # File should be <10MB with extractable text
   ```
   - Click "Upload Transcript" button
   - Select `sample_data/sample_call_1.pdf`
   - Verify file upload success message

3. **Start Analysis**
   - Click "Start Analysis" button
   - Verify job ID is generated
   - Confirm analysis initiated message

4. **Monitor Real-time Progress**
   - Watch progress bar update in real-time
   - Verify individual agent completion notifications
   - Check WebSocket connection status
   - Expected: All 14 agents complete within 2-5 minutes

### Test Case 2: Results Validation

1. **View Analysis Results**
   - Navigate to results page after completion
   - Verify comprehensive analysis display
   - Check individual agent insights are shown

2. **Download Generated Files**
   ```bash
   # Expected output files:
   # - sample_call_1_comprehensive_analysis.json
   # - sample_call_1_objection_specialist.json
   # - sample_call_1_opening_gambit.json
   # ... (one file per agent)
   # - sample_call_1_enhanced_prompt.txt
   ```

3. **Validate File Contents**
   ```bash
   # Check file structure
   cd comprehensive_results/
   ls -la sample_call_1_*
   
   # Verify JSON structure
   python -m json.tool sample_call_1_comprehensive_analysis.json
   ```

### Test Case 3: Learning System

1. **Check Learning Metrics**
   - Visit `/lessons/metrics` endpoint
   - Verify lesson extraction statistics
   - Check deduplication rates

2. **Plateau Detection Test**
   ```bash
   # API endpoint test
   curl http://localhost:5000/lessons/plateau-status
   # Expected: JSON response with plateau analysis
   ```

3. **Audit Trail Verification**
   - Navigate to audit trail in dashboard
   - Verify processing events are logged
   - Check timestamp accuracy

## 🎯 Expected Test Results

### Performance Benchmarks
- **File Upload**: <5 seconds for 10MB files
- **Analysis Completion**: 2-5 minutes for typical sales calls
- **Real-time Updates**: <1 second WebSocket latency
- **Parallel Processing**: All 14 agents execute simultaneously

### Quality Metrics
- **Text Extraction**: 95%+ accuracy from PDF transcripts
- **AI Analysis**: Comprehensive insights from all 14 specialized agents
- **Learning System**: Automatic lesson extraction and deduplication
- **Error Handling**: Graceful failure recovery and user notifications

## 🚨 Troubleshooting Common Issues

### Issue 1: API Key Problems
```bash
# Symptom: AI analysis fails to start
# Solution: Verify API key configuration
echo $GOOGLE_API_KEY
# Ensure key is valid at https://ai.google.dev/
```

### Issue 2: Port Conflicts
```bash
# Symptom: Server won't start
# Solution: Check port availability
lsof -i :5000  # Backend port
lsof -i :3000  # Frontend port
# Kill conflicting processes if needed
```

### Issue 3: PDF Processing Errors
```bash
# Symptom: File upload fails
# Solution: Verify PDF has extractable text
# Use simple text-based PDFs, not scanned images
```

## 📊 Success Criteria

### ✅ Must Pass Tests
- [ ] All unit tests pass without errors
- [ ] File upload and processing works end-to-end
- [ ] AI analysis completes successfully 
- [ ] Real-time progress updates function
- [ ] Results download and validation successful
- [ ] Learning system metrics accessible

### 🎯 Performance Goals
- [ ] Analysis completes in under 5 minutes
- [ ] WebSocket updates in real-time
- [ ] All 14 AI agents execute in parallel
- [ ] Comprehensive coaching insights generated

### 🌟 Bonus Features to Test
- [ ] Plateau detection algorithm working
- [ ] Audit trail complete and accurate
- [ ] Multiple file processing capability
- [ ] Error recovery and user notifications

## 🔬 Advanced Testing (Optional)

### Load Testing
```bash
# Test multiple concurrent analyses
for i in {1..3}; do
  curl -X POST http://localhost:5000/upload \
    -F "file=@sample_data/sample_call_$i.pdf" &
done
```

### API Endpoint Testing
```bash
# Test all major endpoints
curl http://localhost:5000/jobs
curl http://localhost:5000/lessons/metrics
curl http://localhost:5000/lessons/categories
```

## 📝 Test Results Documentation

### Recording Test Outcomes
1. **Screenshot Evidence**: Capture key interface states
2. **Log Analysis**: Review console outputs for errors
3. **Performance Metrics**: Document processing times
4. **Output Validation**: Verify generated file quality

### Expected Deliverables After Testing
- All sample analyses completed successfully
- Generated JSON and text files with valid structure
- Learning system populated with extracted lessons
- Audit trail showing complete processing history

## 🏆 Hackathon Evaluation Points

This testing demonstrates:
- **Innovation**: 14 parallel AI agents for comprehensive analysis
- **Technical Excellence**: ADK integration and real-time processing
- **User Experience**: Intuitive interface with live progress
- **Scalability**: Parallel processing and learning system
- **Robustness**: Comprehensive error handling and validation

---

**Testing Support**: Refer to individual test files in `/tests/` directory for detailed technical validation procedures. 