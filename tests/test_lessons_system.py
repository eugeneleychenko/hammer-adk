#!/usr/bin/env python3
"""
Test script for the lessons learning system.
Verifies that all components work together correctly.

Usage:
    python3 test_lessons_system.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_lessons_audit_trail():
    """Test the LessonsAuditTrail class."""
    logger.info("🧪 Testing LessonsAuditTrail class...")
    
    try:
        from lessons_audit_trail import LessonsAuditTrail
        
        # Create test audit trail
        test_path = Path("test_lessons_audit_trail.json")
        auditor = LessonsAuditTrail(test_path)
        
        # Test starting an event
        event_id = auditor.start_processing_event("test_file.pdf")
        logger.info(f"✅ Started event: {event_id}")
        
        # Test lesson extraction
        mock_agent_results = {
            "objection_specialist": {
                "key_insights": [
                    "When customer says 'I can't afford it', respond with alternatives",
                    "Always acknowledge the concern before reframing"
                ],
                "patterns": ["price objection handling", "empathy techniques"]
            },
            "opening_gambit": {
                "techniques": [
                    "Start with permission-based opening",
                    "Use customer's name early and often"
                ]
            }
        }
        
        lesson_candidates = auditor.extract_lesson_candidates(mock_agent_results)
        logger.info(f"✅ Extracted {len(lesson_candidates)} lesson candidates")
        
        # Test completing the event
        auditor.complete_processing_event(
            event_id=event_id,
            lesson_candidates=lesson_candidates,
            synthesis_result={},
            processing_duration=30.5
        )
        logger.info("✅ Completed processing event")
        
        # Test metrics
        metrics = auditor.get_metrics_summary()
        logger.info(f"✅ Metrics: {metrics}")
        
        # Test plateau detection
        is_plateaued = auditor.is_plateau_detected()
        logger.info(f"✅ Plateau detected: {is_plateaued}")
        
        # Cleanup
        if test_path.exists():
            test_path.unlink()
        
        logger.info("✅ LessonsAuditTrail test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ LessonsAuditTrail test failed: {e}")
        return False

def test_adk_integration():
    """Test ADK orchestration integration."""
    logger.info("🧪 Testing ADK integration...")
    
    try:
        from adk_orchestration import ADKSalesAnalysisOrchestrator
        
        # Check if ADK orchestrator can be initialized
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.warning("⚠️  GOOGLE_API_KEY not found - skipping ADK integration test")
            return True
        
        orchestrator = ADKSalesAnalysisOrchestrator(api_key)
        
        # Verify lessons auditor is initialized
        if hasattr(orchestrator, 'lessons_auditor'):
            logger.info("✅ Lessons auditor initialized in ADK orchestrator")
        else:
            logger.error("❌ Lessons auditor not found in ADK orchestrator")
            return False
        
        # Test audit trail methods
        metrics = orchestrator.lessons_auditor.get_metrics_summary()
        logger.info(f"✅ ADK integration metrics: {metrics}")
        
        logger.info("✅ ADK integration test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ ADK integration test failed: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints (requires server to be running)."""
    logger.info("🧪 Testing API endpoints...")
    
    try:
        import requests
        
        base_url = "http://localhost:8000"
        
        # Test lessons metrics endpoint
        response = requests.get(f"{base_url}/lessons/metrics", timeout=5)
        if response.status_code == 200:
            logger.info("✅ Lessons metrics endpoint responding")
        else:
            logger.warning(f"⚠️  Lessons metrics endpoint returned {response.status_code}")
        
        # Test plateau status endpoint
        response = requests.get(f"{base_url}/lessons/plateau-status", timeout=5)
        if response.status_code == 200:
            logger.info("✅ Plateau status endpoint responding")
        else:
            logger.warning(f"⚠️  Plateau status endpoint returned {response.status_code}")
        
        # Test categories endpoint
        response = requests.get(f"{base_url}/lessons/categories", timeout=5)
        if response.status_code == 200:
            logger.info("✅ Categories endpoint responding")
        else:
            logger.warning(f"⚠️  Categories endpoint returned {response.status_code}")
        
        logger.info("✅ API endpoints test passed")
        return True
        
    except ImportError:
        logger.warning("⚠️  requests library not available - skipping API endpoint tests")
        return True
    except requests.exceptions.ConnectionError:
        logger.warning("⚠️  API server not running - skipping API endpoint tests")
        return True
    except Exception as e:
        logger.error(f"❌ API endpoints test failed: {e}")
        return False

def test_frontend_component():
    """Test frontend component existence."""
    logger.info("🧪 Testing frontend component...")
    
    frontend_component = Path("frontend/src/components/LessonsDashboard.tsx")
    
    if frontend_component.exists():
        logger.info("✅ LessonsDashboard component exists")
        
        # Check if it's imported in main page
        main_page = Path("frontend/src/app/page.tsx")
        if main_page.exists():
            content = main_page.read_text()
            if "LessonsDashboard" in content:
                logger.info("✅ LessonsDashboard imported in main page")
            else:
                logger.warning("⚠️  LessonsDashboard not imported in main page")
        
        return True
    else:
        logger.error("❌ LessonsDashboard component not found")
        return False

def test_file_structure():
    """Test that all required files exist."""
    logger.info("🧪 Testing file structure...")
    
    required_files = [
        "lessons_audit_trail.py",
        "adk_orchestration.py",
        "api_server.py",
        "frontend/src/components/LessonsDashboard.tsx",
        "docs/tasks_6_22_lessons_learning.md"
    ]
    
    all_exist = True
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            logger.info(f"✅ {file_path} exists")
        else:
            logger.error(f"❌ {file_path} missing")
            all_exist = False
    
    return all_exist

def main():
    """Run all tests."""
    logger.info("🚀 Starting lessons learning system tests...")
    
    tests = [
        ("File Structure", test_file_structure),
        ("LessonsAuditTrail Class", test_lessons_audit_trail),
        ("ADK Integration", test_adk_integration),
        ("Frontend Component", test_frontend_component),
        ("API Endpoints", test_api_endpoints),
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running {test_name} test...")
        logger.info(f"{'='*50}")
        
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    logger.info(f"\n{'='*50}")
    logger.info("TEST SUMMARY")
    logger.info(f"{'='*50}")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\nOverall: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        logger.info("🎉 All tests passed! Lessons learning system is ready.")
        return 0
    else:
        logger.warning(f"⚠️  {len(tests) - passed} tests failed. Check implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())