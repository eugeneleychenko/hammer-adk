# 🎯 Simple UAT Test - Frontend File Upload and Analysis

This is the **simplest User Acceptance Test** for the AI Sales Call Analysis Platform. It tests the core functionality end-to-end through the web interface.

## 🚀 Test Setup (2 minutes)

### Prerequisites
```bash
# 1. Start the backend server
cd backend
python api_server.py
# Should show: "Server running on http://localhost:5000"

# 2. Start the frontend (new terminal)
cd frontend
npm run dev
# Should show: "Local: http://localhost:3000"
```

## 📋 UAT Test Case: File Upload and Analysis

**Test Objective**: Verify that users can upload a sales transcript and receive AI analysis results through the web interface.

**Duration**: 5-7 minutes

**User Story**: "As a sales manager, I want to upload a sales call transcript and get AI coaching insights so I can improve my team's performance."

---

### Step 1: Access the Platform ✅
1. **Action**: Open web browser and navigate to `http://localhost:3000`
2. **Expected Result**: 
   - Dashboard loads successfully
   - Upload interface is visible
   - "Upload Transcript" button is present
3. **Pass Criteria**: Page loads without errors and upload UI is functional

---

### Step 2: Upload Test File ✅
1. **Action**: 
   - Click "Upload Transcript" button
   - Select the file `sample_data/sample_call_1.txt`
   - Confirm upload
2. **Expected Result**:
   - File uploads successfully
   - Success message appears: "File uploaded successfully"
   - Job ID is generated and displayed
3. **Pass Criteria**: File upload completes without errors

---

### Step 3: Start Analysis ✅
1. **Action**: Click "Start Analysis" button
2. **Expected Result**:
   - Analysis begins immediately
   - Progress bar appears showing "0% - Starting analysis..."
   - Status changes to "Processing" or "In Progress"
3. **Pass Criteria**: Analysis starts and progress is visible

---

### Step 4: Monitor Progress ✅
1. **Action**: Watch the progress updates in real-time
2. **Expected Result**:
   - Progress bar updates automatically (10%, 25%, 50%, etc.)
   - Individual agent completions show: "Objection Specialist: Complete ✓"
   - WebSocket connection maintains real-time updates
3. **Pass Criteria**: Progress updates appear without manual refresh

---

### Step 5: View Results ✅
1. **Action**: Wait for analysis to complete (2-5 minutes)
2. **Expected Result**:
   - Progress reaches 100%
   - "Analysis Complete!" message appears
   - Results section becomes available
   - Download buttons appear for generated files
3. **Pass Criteria**: Analysis completes successfully with downloadable results

---

### Step 6: Verify Output ✅
1. **Action**: 
   - Click "View Comprehensive Analysis"
   - Download one of the agent result files
2. **Expected Result**:
   - Comprehensive analysis displays insights about the sales call
   - Downloaded file contains valid JSON with coaching recommendations
   - Key insights include objection handling, rapport building, etc.
3. **Pass Criteria**: Results contain meaningful sales coaching insights

---

## ✅ Success Criteria

**This UAT test PASSES if:**
- [ ] Platform loads without errors
- [ ] File upload works smoothly  
- [ ] Analysis starts immediately
- [ ] Progress updates in real-time
- [ ] Analysis completes within 5 minutes
- [ ] Results are comprehensive and actionable

**This UAT test FAILS if:**
- ❌ Page doesn't load or shows errors
- ❌ File upload fails or times out
- ❌ Analysis doesn't start or gets stuck
- ❌ No progress updates visible
- ❌ Analysis takes longer than 10 minutes
- ❌ Results are empty or nonsensical

## 🔧 Quick Troubleshooting

**If upload fails:**
```bash
# Check file format - use .txt instead of .pdf if needed
# Ensure file is less than 10MB
```

**If analysis stalls:**
```bash
# Check backend logs in terminal
# Verify GOOGLE_API_KEY is set correctly
# Restart backend server if needed
```

**If no progress updates:**
```bash
# Check browser console for WebSocket errors
# Refresh page and try again
```

## 🎯 Expected Test Result

**When successful, you should see:**
1. File uploads in ~2 seconds
2. Analysis starts immediately  
3. Progress updates every 10-15 seconds
4. 14 AI agents complete their analysis
5. Comprehensive coaching insights generated
6. Downloadable JSON files with sales recommendations

**Sample insights the AI should generate:**
- Objection handling techniques used
- Rapport building effectiveness  
- Discovery question quality
- Closing techniques evaluation
- Areas for improvement
- Specific coaching recommendations

---

**Test Duration**: 5-7 minutes total
**Skill Level**: Non-technical (can be performed by any user)
**Success Rate**: 95%+ with proper setup 