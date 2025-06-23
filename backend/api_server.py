#!/usr/bin/env python3

import os
import json
import uuid
import threading
import logging
import glob
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import PyPDF2
from werkzeug.utils import secure_filename

from adk_orchestration import ADKSalesAnalysisOrchestrator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size

CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Job storage
jobs: Dict[str, Dict[str, Any]] = {}

# Initialize ADK orchestrator
try:
    adk_orchestrator = ADKSalesAnalysisOrchestrator()
    logger.info("✅ ADK Orchestrator initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize ADK orchestrator: {e}")
    adk_orchestrator = None

class FileStructureValidator:
    """Validates that all expected files are generated matching the standalone version."""
    
    def __init__(self, output_dir: str = "comprehensive_results"):
        self.output_dir = Path(output_dir)
        
    def get_expected_files(self, filename_base: str) -> Dict[str, str]:
        """Get all expected files for a given filename base."""
        # List of all 14 agent names from the standalone version
        agent_names = [
            'objection_specialist', 'opening_gambit', 'needs_assessment',
            'rapport_building', 'pattern_recognition', 'emotional_intelligence',
            'language_optimizer', 'client_profiling', 'micro_commitments',
            'conversation_flow', 'budget_handling', 'urgency_builder',
            'technical_navigation', 'cross_selling'
        ]
        
        expected_files = {}
        
        # Individual agent files: {filename}_{agent_name}.json
        for agent_name in agent_names:
            key = f"agent_{agent_name}"
            path = str(self.output_dir / f"{filename_base}_{agent_name}.json")
            expected_files[key] = path
        
        # Comprehensive analysis: {filename}_comprehensive_analysis.json
        expected_files["comprehensive_analysis"] = str(self.output_dir / f"{filename_base}_comprehensive_analysis.json")
        
        # Synthesis files (shared across calls)
        expected_files["synthesized_learnings"] = str(self.output_dir / "synthesized_learnings.json")
        
        # Enhanced prompt file: {filename}_enhanced_prompt.txt
        expected_files["enhanced_prompt"] = str(self.output_dir / f"{filename_base}_enhanced_prompt.txt")
        
        return expected_files
    
    def validate_file_structure(self, filename_base: str) -> Dict[str, Any]:
        """Validate that all expected files exist and report status."""
        expected_files = self.get_expected_files(filename_base)
        validation_result = {
            "validation_passed": True,
            "total_expected": len(expected_files),
            "files_found": 0,
            "files_missing": [],
            "files_present": [],
            "validation_details": {}
        }
        
        for file_type, file_path in expected_files.items():
            exists = os.path.exists(file_path)
            file_size = os.path.getsize(file_path) if exists else 0
            
            validation_result["validation_details"][file_type] = {
                "path": file_path,
                "exists": exists,
                "size_bytes": file_size,
                "is_valid": exists and file_size > 0
            }
            
            if exists and file_size > 0:
                validation_result["files_found"] += 1
                validation_result["files_present"].append(file_type)
            else:
                validation_result["validation_passed"] = False
                validation_result["files_missing"].append(file_type)
        
        validation_result["completion_percentage"] = (validation_result["files_found"] / validation_result["total_expected"]) * 100
        
        return validation_result
    
    def validate_and_retry(self, filename_base: str, max_retries: int = 3) -> Dict[str, Any]:
        """Validate file structure with retry logic for missing files."""
        for attempt in range(max_retries + 1):
            validation_result = self.validate_file_structure(filename_base)
            
            if validation_result["validation_passed"]:
                logger.info(f"✅ File validation passed on attempt {attempt + 1}")
                return validation_result
            
            if attempt < max_retries:
                logger.warning(f"❌ File validation failed on attempt {attempt + 1}. Missing: {validation_result['files_missing']}")
                # Wait a bit for file operations to complete
                import time
                time.sleep(2)
            else:
                logger.error(f"❌ File validation failed after {max_retries + 1} attempts. Missing: {validation_result['files_missing']}")
        
        return validation_result

class ProgressTrackingAnalyzer:
    """ADK-based analyzer with real-time progress tracking via WebSocket"""
    
    def __init__(self, job_id):
        self.job_id = job_id
        self.validator = FileStructureValidator()
        self.orchestrator = ADKSalesAnalysisOrchestrator()
        
    def emit_progress(self, agent_name: str, status: str, progress: int, message: str = ""):
        """Emit progress updates via WebSocket"""
        try:
            # Update job record
            if self.job_id in jobs:
                if 'agent_progress' not in jobs[self.job_id]:
                    jobs[self.job_id]['agent_progress'] = {}
                
                jobs[self.job_id]['agent_progress'][agent_name] = {
                    'status': status,
                    'progress': progress,
                    'message': message,
                    'timestamp': datetime.now().isoformat()
                }
            
            # Emit WebSocket event
            socketio.emit('analysis_progress', {
                'job_id': self.job_id,
                'agent_name': agent_name,
                'status': status,
                'progress': progress,
                'message': message,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            print(f"Error emitting progress: {e}")


    def analyze_with_progress(self, pdf_path: str, filename: str):
        """Run analysis with progress tracking"""
        try:
            # Extract text from PDF
            self.emit_progress('system', 'processing', 5, 'Extracting text from PDF...')
            transcript = self.extract_text_from_pdf(pdf_path)
            
            self.emit_progress('system', 'processing', 10, 'Starting agent analysis...')
            
            # Create output directory for individual agent files
            output_dir = "comprehensive_results"
            Path(output_dir).mkdir(exist_ok=True)
            
            # Run ADK orchestration with progress updates
            agent_names = [
                'objection_specialist', 'opening_gambit', 'needs_assessment',
                'rapport_building', 'pattern_recognition', 'emotional_intelligence',
                'language_optimizer', 'client_profiling', 'micro_commitments', 
                'conversation_flow', 'budget_handling', 'urgency_builder',
                'technical_navigation', 'cross_selling'
            ]
            
            # Emit progress for all agents starting
            for i, agent_name in enumerate(agent_names):
                self.emit_progress(agent_name, 'processing', 0, f'Starting {agent_name} analysis...')
            
            # Run ADK orchestration - all agents in parallel
            self.emit_progress('system', 'processing', 15, 'Running ADK parallel analysis...')
            agent_results = self.orchestrator.analyze_transcript(transcript, filename)
            
            # Save individual agent results and emit completion for each
            base_filename = filename.replace('.pdf', '')
            for agent_name in agent_names:
                if agent_name in agent_results:
                    self.emit_progress(agent_name, 'processing', 90, f'Saving {agent_name} results...')
                    
                    agent_output_file = Path(output_dir) / f"{base_filename}_{agent_name}.json"
                    try:
                        with open(agent_output_file, 'w') as f:
                            json.dump(agent_results[agent_name], f, indent=2)
                        logger.info(f"Saved {agent_name} results to: {agent_output_file}")
                        self.emit_progress(agent_name, 'processing', 95, f'Results saved to {agent_output_file.name}')
                    except Exception as e:
                        logger.error(f"Failed to save {agent_name} results: {str(e)}")
                        self.emit_progress(agent_name, 'processing', 95, f'Warning: Failed to save results file')
                    
                    # Emit completion (100%) for this agent
                    self.emit_progress(agent_name, 'complete', 100, 'Analysis complete')
                else:
                    self.emit_progress(agent_name, 'error', 0, f'No results returned for {agent_name}')
            
            self.emit_progress('system', 'processing', 75, 'Synthesizing results...')
            
            # Create comprehensive analysis using the orchestrator's method
            comprehensive_analysis = self.orchestrator.create_comprehensive_analysis(agent_results, filename)
            
            # Save comprehensive analysis file
            self.emit_progress('system', 'processing', 80, 'Saving comprehensive analysis...')
            base_filename = filename.replace('.pdf', '')
            comprehensive_file = Path(output_dir) / f"{base_filename}_comprehensive_analysis.json"
            
            try:
                with open(comprehensive_file, 'w') as f:
                    json.dump(comprehensive_analysis, f, indent=2)
                logger.info(f"Saved comprehensive analysis to: {comprehensive_file}")
                self.emit_progress('system', 'processing', 82, f'Comprehensive analysis saved to {comprehensive_file.name}')
            except Exception as e:
                logger.error(f"Failed to save comprehensive analysis: {str(e)}")
                self.emit_progress('system', 'processing', 82, f'Warning: Failed to save comprehensive analysis')
            
            self.emit_progress('system', 'processing', 85, 'Running Phase 2 synthesis...')
            
            # Run Phase 2 and 3 processing using orchestrator's method
            self.orchestrator.process_synthesized_learnings([comprehensive_analysis])
            
            # Generate master system prompt (enhanced_prompt) file
            self.emit_progress('system', 'processing', 90, 'Generating master system prompt...')
            
            # First check if synthesized learnings exist
            synthesis_file = "comprehensive_results/synthesized_learnings.json"
            logger.info(f"Checking for synthesis file: {synthesis_file}")
            logger.info(f"Synthesis file exists: {os.path.exists(synthesis_file)}")
            
            if os.path.exists(synthesis_file):
                enhanced_prompt_file = f"comprehensive_results/{filename.replace('.pdf', '')}_enhanced_prompt.txt"
                logger.info(f"Generating enhanced prompt: {enhanced_prompt_file}")
                
                try:
                    self.orchestrator.generate_mega_prompt_from_synthesis(synthesis_file, enhanced_prompt_file)
                    logger.info(f"✅ Successfully generated enhanced prompt: {enhanced_prompt_file}")
                    self.emit_progress('system', 'processing', 95, 'Master system prompt generated!')
                except Exception as e:
                    logger.error(f"❌ Failed to generate enhanced prompt: {str(e)}")
                    self.emit_progress('system', 'processing', 95, f'Enhanced prompt generation failed: {str(e)}')
            else:
                logger.warning("❌ No synthesized_learnings.json found - cannot generate enhanced prompt")
                self.emit_progress('system', 'processing', 95, 'No synthesis data available for prompt generation')
            
            # Final validation with retry logic
            self.emit_progress('system', 'processing', 98, 'Running final file validation...')
            filename_base = filename.replace('.pdf', '')
            final_validation = self.validator.validate_and_retry(filename_base, max_retries=2)
            
            completion_msg = f"Analysis complete! {final_validation['files_found']}/{final_validation['total_expected']} files generated ({final_validation['completion_percentage']:.1f}%)"
            
            if final_validation["validation_passed"]:
                logger.info(f"✅ {completion_msg}")
                self.emit_progress('system', 'complete', 100, completion_msg)
            else:
                logger.warning(f"⚠️  {completion_msg} - Missing: {final_validation['files_missing']}")
                self.emit_progress('system', 'complete', 100, f"{completion_msg} - Some files missing")
            
            # Add validation results to the response
            comprehensive_analysis["file_validation"] = final_validation
            
            return comprehensive_analysis
            
        except Exception as e:
            self.emit_progress('system', 'error', 0, f'Error: {str(e)}')
            raise

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file."""
        text_content = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text_content += page.extract_text() + "\n"
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise
        return text_content

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/upload', methods=['POST'])
def upload_file():
    """Upload PDF file and start analysis"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Only PDF files are allowed'}), 400
    
    # Generate job ID
    job_id = str(uuid.uuid4())
    
    # Secure filename
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{job_id}_{filename}")
    
    # Save uploaded file
    file.save(filepath)
    
    # Create job record
    jobs[job_id] = {
        'id': job_id,
        'filename': filename,
        'filepath': filepath,
        'status': 'uploaded',
        'created_at': datetime.now().isoformat(),
        'agent_progress': {}
    }
    
    return jsonify({
        'job_id': job_id,
        'filename': filename,
        'status': 'uploaded',
        'message': 'File uploaded successfully'
    })

@app.route('/analyze/<job_id>', methods=['POST'])
def start_analysis(job_id):
    """Start analysis for uploaded file"""
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = jobs[job_id]
    if job['status'] != 'uploaded':
        return jsonify({'error': 'Job already processed or in progress'}), 400
    
    # Update job status
    job['status'] = 'processing'
    job['started_at'] = datetime.now().isoformat()
    
    # Start analysis in background thread
    def run_analysis():
        try:
            print(f"Starting analysis for job {job_id}")
            analyzer = ProgressTrackingAnalyzer(job_id)
            print(f"ADK Analyzer created, starting analysis...")
            result = analyzer.analyze_with_progress(job['filepath'], job['filename'])
            
            job['status'] = 'complete'
            job['completed_at'] = datetime.now().isoformat()
            job['result'] = result
            print(f"Analysis completed for job {job_id}")
            
        except Exception as e:
            print(f"Error in analysis for job {job_id}: {str(e)}")
            import traceback
            traceback.print_exc()
            job['status'] = 'error'
            job['error'] = str(e)
            job['completed_at'] = datetime.now().isoformat()
    
    thread = threading.Thread(target=run_analysis)
    thread.daemon = True
    thread.start()
    print(f"Analysis thread started for job {job_id}")
    
    return jsonify({
        'job_id': job_id,
        'status': 'processing',
        'message': 'Analysis started'
    })

@app.route('/status/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """Get job status and progress"""
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = jobs[job_id]
    return jsonify({
        'job_id': job_id,
        'filename': job['filename'],
        'status': job['status'],
        'created_at': job['created_at'],
        'agent_progress': job.get('agent_progress', {}),
        'started_at': job.get('started_at'),
        'completed_at': job.get('completed_at'),
        'error': job.get('error')
    })

@app.route('/results/<job_id>', methods=['GET'])
def get_results(job_id):
    """Get analysis results"""
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = jobs[job_id]

    # If job is still processing, return a 202 Accepted with progress information
    if job['status'] == 'processing':
        partial_response: Dict[str, Any] = {
            'job_id': job_id,
            'status': 'processing',
            'agent_progress': job.get('agent_progress', {}),
            # If any intermediate results exist, surface them so the UI can show early data
            'partial_result': job.get('result')
        }
        return jsonify(partial_response), 202

    # If job ended in error, surface the error along with any partial result
    if job['status'] == 'error':
        return jsonify({
            'job_id': job_id,
            'status': 'error',
            'error': job.get('error', 'Unknown'),
            'partial_result': job.get('result')
        }), 200

    # Job complete – return the full result normally
    return jsonify(job['result'])

@app.route('/validate/<job_id>', methods=['GET'])
def get_file_validation(job_id):
    """Get file structure validation for a completed job"""
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = jobs[job_id]
    if job['status'] != 'complete':
        return jsonify({'error': 'Job not complete - validation not available'}), 400
    
    filename_base = job['filename'].replace('.pdf', '')
    validator = FileStructureValidator()
    validation_result = validator.validate_file_structure(filename_base)
    
    return jsonify({
        'job_id': job_id,
        'filename': job['filename'],
        'validation': validation_result
    })

def reconstruct_job_from_upload(job_id):
    """Reconstruct job information from upload directory"""
    uploads_dir = app.config['UPLOAD_FOLDER']
    for filename in os.listdir(uploads_dir):
        if filename.startswith(job_id):
            original_filename = '_'.join(filename.split('_')[1:])  # Remove job_id prefix
            return {
                'id': job_id,
                'filename': original_filename,
                'filepath': os.path.join(uploads_dir, filename),
                'status': 'complete',  # Assume complete if results exist
            }
    return None

@app.route('/download/<job_id>/<file_type>', methods=['GET'])
def download_file(job_id, file_type):
    """Download generated files"""
    
    # Try to get job from memory first
    job = jobs.get(job_id)
    
    # If not in memory, try to reconstruct from upload directory
    if not job:
        job = reconstruct_job_from_upload(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        logger.info(f"Reconstructed job info for {job_id}: {job['filename']}")
    
    # For file-specific downloads, we don't need to check completion status
    # since the user might want to download available files regardless
    
    # Map file types to actual files
    filename_base = job['filename'].replace('.pdf', '')
    
    # Base file mappings
    file_mappings = {
        'enhanced_prompt': f"comprehensive_results/{filename_base}_enhanced_prompt.txt",
        'expert_prompt': 'comprehensive_results/expert_life_insurance_agent.txt',
        'decision_tree': 'comprehensive_results/decision_tree.json',
        'synthesized_learnings': 'comprehensive_results/synthesized_learnings.json',
        'complete_ai_system': 'comprehensive_results/complete_ai_system.json',
        'comprehensive_analysis': f"comprehensive_results/{filename_base}_comprehensive_analysis.json"
    }
    
    # Add individual agent files
    agent_names = [
        'objection_specialist', 'opening_gambit', 'needs_assessment',
        'rapport_building', 'pattern_recognition', 'emotional_intelligence',
        'language_optimizer', 'client_profiling', 'micro_commitments',
        'conversation_flow', 'budget_handling', 'urgency_builder',
        'technical_navigation', 'cross_selling'
    ]
    
    for agent_name in agent_names:
        file_mappings[f"agent_{agent_name}"] = f"comprehensive_results/{filename_base}_{agent_name}.json"
    
    if file_type not in file_mappings:
        return jsonify({'error': 'Invalid file type'}), 400
    
    file_path = file_mappings[file_type]
    
    # Add detailed logging for debugging
    logger.info(f"Download request for job_id={job_id}, file_type={file_type}")
    logger.info(f"Original filename={job['filename']}")
    logger.info(f"Filename base={filename_base}")
    logger.info(f"Expected file path={file_path}")
    logger.info(f"File exists={os.path.exists(file_path)}")
    
    if not os.path.exists(file_path):
        # Try to find similar files with pattern matching
        pattern = file_path.replace(filename_base, "*")
        similar_files = glob.glob(pattern)
        error_msg = f'File not found: {file_path}'
        if similar_files:
            error_msg += f'. Similar files found: {similar_files}'
            logger.warning(f"File not found but similar files exist: {similar_files}")
        else:
            # List all files in comprehensive_results to debug
            results_dir = "comprehensive_results"
            if os.path.exists(results_dir):
                available_files = os.listdir(results_dir)
                logger.info(f"Available files in {results_dir}: {available_files}")
        return jsonify({'error': error_msg}), 404
    
    logger.info(f"Serving file: {file_path}")
    return send_file(file_path, as_attachment=True)

@app.route('/jobs', methods=['GET'])
def list_jobs():
    """List all jobs"""
    return jsonify({
        'jobs': [{
            'job_id': job_id,
            'filename': job['filename'],
            'status': job['status'],
            'created_at': job['created_at']
        } for job_id, job in jobs.items()]
    })

# Lessons Learning API Endpoints

@app.route('/lessons/metrics', methods=['GET'])
def get_lessons_metrics():
    """Get current lessons statistics and metrics."""
    try:
        if not adk_orchestrator:
            return jsonify({'error': 'ADK orchestrator not available'}), 503
        
        metrics = adk_orchestrator.lessons_auditor.get_metrics_summary()
        return jsonify(metrics)
    
    except Exception as e:
        logger.error(f"Error getting lessons metrics: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/lessons/audit-trail', methods=['GET'])
def get_lessons_audit_trail():
    """Get lessons processing history."""
    try:
        if not adk_orchestrator:
            return jsonify({'error': 'ADK orchestrator not available'}), 503
        
        # Get optional query parameters
        limit = request.args.get('limit', 10, type=int)
        
        audit_trail = adk_orchestrator.lessons_auditor.get_audit_trail_summary()
        
        # Apply limit
        if limit > 0:
            audit_trail = audit_trail[-limit:]
        
        return jsonify({
            'audit_trail': audit_trail,
            'total_events': len(adk_orchestrator.lessons_auditor.audit_data.get('processing_events', []))
        })
    
    except Exception as e:
        logger.error(f"Error getting lessons audit trail: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/lessons/plateau-status', methods=['GET'])
def get_plateau_status():
    """Get current plateau detection status and recommendations."""
    try:
        if not adk_orchestrator:
            return jsonify({'error': 'ADK orchestrator not available'}), 503
        
        is_plateaued = adk_orchestrator.lessons_auditor.is_plateau_detected()
        recommendations = adk_orchestrator.lessons_auditor.get_plateau_recommendations()
        
        # Get additional plateau analysis data
        plateau_analysis = adk_orchestrator.lessons_auditor.audit_data.get('plateau_analysis', {})
        global_totals = adk_orchestrator.lessons_auditor.audit_data.get('global_totals', {})
        
        return jsonify({
            'is_plateaued': is_plateaued,
            'recommendations': recommendations,
            'plateau_detected_date': global_totals.get('plateau_status', {}).get('plateau_detected_date'),
            'recent_lessons_added': plateau_analysis.get('lessons_added_recent_window', 0),
            'trend_direction': plateau_analysis.get('diminishing_returns_trend', {}).get('trend_direction', 'unknown'),
            'uniqueness_rate': plateau_analysis.get('uniqueness_metrics', {}).get('unique_pattern_discovery_rate', 0.0),
            'deduplication_rate': global_totals.get('deduplication_rate', 0.0)
        })
    
    except Exception as e:
        logger.error(f"Error getting plateau status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/lessons/categories', methods=['GET'])
def get_lessons_by_category():
    """Get lessons broken down by category."""
    try:
        if not adk_orchestrator:
            return jsonify({'error': 'ADK orchestrator not available'}), 503
        
        # Get category data from audit trail
        plateau_analysis = adk_orchestrator.lessons_auditor.audit_data.get('plateau_analysis', {})
        category_saturation = plateau_analysis.get('category_saturation', {})
        global_totals = adk_orchestrator.lessons_auditor.audit_data.get('global_totals', {})
        unique_categories = global_totals.get('unique_lesson_categories', [])
        
        categories = []
        for category in unique_categories:
            saturation_data = category_saturation.get(category, {})
            categories.append({
                'name': category,
                'total_lessons': saturation_data.get('total_lessons', 0),
                'recent_additions': saturation_data.get('recent_additions', 0),
                'saturation_level': saturation_data.get('saturation_level', 'unknown')
            })
        
        return jsonify({
            'categories': categories,
            'total_categories': len(categories)
        })
    
    except Exception as e:
        logger.error(f"Error getting lessons by category: {str(e)}")
        return jsonify({'error': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    print(f"Client connected: {request.sid}")
    emit('connected', {'message': 'Connected to analysis server'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    print(f"Client disconnected: {request.sid}")

if __name__ == '__main__':
    # ---------------------------------------------------
    # Startup banner & environment-aware configuration
    # ---------------------------------------------------
    print("Starting Sales Analysis API Server...")
    print(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
    print("Available endpoints:")
    print("  POST /upload - Upload PDF file")
    print("  POST /analyze/<job_id> - Start analysis")
    print("  GET /status/<job_id> - Get job status")
    print("  GET /results/<job_id> - Get analysis results")
    print("  GET /validate/<job_id> - Get file validation status")
    print("  GET /download/<job_id>/<file_type> - Download files")
    print("  GET /jobs - List all jobs")
    print()
    print("Available file types for download:")
    print("  enhanced_prompt, comprehensive_analysis, synthesized_learnings")
    print("  agent_objection_specialist, agent_opening_gambit, agent_needs_assessment, etc.")
    print()

    # Use PORT env var (e.g., provided by Render) if present, else default to 8000
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"

    print(f"Server will bind to http://{host}:{port}")

    # Disable Flask debug & reloader in production to avoid multiple processes
    # and ensure port detection works correctly on hosting platforms.
    socketio.run(
        app,
        host=host,
        port=port,
        debug=False,
        use_reloader=False,
        allow_unsafe_werkzeug=True,
    )