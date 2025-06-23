# 🧪 UAT Test - Core File Analysis

## Test Overview
**Test Name**: Basic Sales Call Analysis  
**Duration**: 10 minutes  
**Objective**: Verify core upload and AI analysis functionality works end-to-end

## Prerequisites
```bash
# 1. Set API key
export GOOGLE_API_KEY="your_gemini_api_key"

# 2. Start backend
cd backend && python api_server.py

# 3. Start frontend (new terminal)
cd frontend && npm run dev
```

## Test Steps

### Step 1: Upload File
1. Open browser to `http://localhost:3000`
2. Click "Upload Transcript" button
3. Select `sample_data/sample_call_1.txt`
4. **Expected**: File uploads successfully, shows file name

### Step 2: Start Analysis
1. Click "Start Analysis" button
2. **Expected**: 
   - Job ID appears (e.g., `job_12345`)
   - Progress bar shows 0%
   - Status shows "Starting analysis..."

### Step 3: Monitor Progress
1. Watch the progress bar
2. **Expected**:
   - Progress updates in real-time (0% → 100%)
   - Individual agent completions show (14 total)
   - Takes 2-5 minutes to complete

### Step 4: View Results
1. When analysis completes, view results
2. **Expected**:
   - "Analysis Complete" message
   - Download links for result files
   - Summary of insights displayed

### Step 5: Download Files
1. Click download link for "Comprehensive Analysis"
2. **Expected**:
   - JSON file downloads successfully
   - File contains AI analysis data
   - No errors in browser console

## Success Criteria
- ✅ File uploads without errors
- ✅ Analysis starts and progresses to 100%
- ✅ All 14 AI agents complete successfully
- ✅ Results are generated and downloadable
- ✅ No critical errors in browser console

## Quick Validation
```bash
# Check if output file exists and is valid JSON
ls -la comprehensive_results/
python -m json.tool comprehensive_results/sample_call_1_comprehensive_analysis.json
```

## Pass/Fail
**Test Result**: [ ] PASS [ ] FAIL  
**Notes**: _________________________________  
**Tester**: _________________________________  
**Date**: ___________________________________ 