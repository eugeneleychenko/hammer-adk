#!/usr/bin/env python3
"""
Lessons Audit Trail System for Self-Improving Prompt Learning

This module tracks the evolution of lessons extracted from sales call analysis,
providing comprehensive auditing, plateau detection, and quality metrics.

Author: System Generated
Date: 2025-06-22
"""

import json
import logging
import uuid
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class LessonsAuditTrail:
    """
    Comprehensive audit trail system for tracking lesson learning evolution.
    
    Provides:
    - Processing event tracking
    - Plateau detection
    - Quality metrics
    - Deduplication analysis
    - Business intelligence recommendations
    """
    
    def __init__(self, audit_file_path: Path):
        """Initialize the audit trail system."""
        self.audit_file_path = Path(audit_file_path)
        self.audit_data = {}
        
        # Configuration - set before loading
        self.PLATEAU_WINDOW_DAYS = 7
        self.MIN_ADDITIONS_THRESHOLD = 3
        self.HIGH_DEDUP_THRESHOLD = 0.8
        self.LOW_UNIQUENESS_THRESHOLD = 0.2
        self.SIMILARITY_THRESHOLD = 0.85
        
        self.load_or_create_audit_trail()
        
    def load_or_create_audit_trail(self) -> None:
        """Load existing audit trail or create new one."""
        if self.audit_file_path.exists():
            try:
                with open(self.audit_file_path, 'r') as f:
                    self.audit_data = json.load(f)
                logger.info(f"Loaded existing audit trail from {self.audit_file_path}")
            except Exception as e:
                logger.error(f"Failed to load audit trail: {e}")
                self.audit_data = self._create_empty_audit_trail()
        else:
            self.audit_data = self._create_empty_audit_trail()
            self._save_audit_trail()
            logger.info(f"Created new audit trail at {self.audit_file_path}")
    
    def _create_empty_audit_trail(self) -> Dict[str, Any]:
        """Create empty audit trail structure."""
        return {
            "audit_metadata": {
                "version": "1.0.0",
                "created_date": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "system_version": "ADK-v2.0",
                "tracking_started": datetime.now().isoformat()
            },
            "global_totals": {
                "total_pdfs_processed": 0,
                "total_lessons_extracted_raw": 0,
                "total_lessons_added_net": 0,
                "total_lessons_deduplicated": 0,
                "deduplication_rate": 0.0,
                "unique_lesson_categories": [],
                "plateau_status": {
                    "is_plateaued": False,
                    "plateau_detected_date": None,
                    "plateau_threshold_days": self.PLATEAU_WINDOW_DAYS,
                    "plateau_threshold_additions": self.MIN_ADDITIONS_THRESHOLD
                }
            },
            "processing_events": [],
            "plateau_analysis": {
                "recent_window_days": 14,
                "lessons_added_recent_window": 0,
                "diminishing_returns_trend": {
                    "trend_direction": "increasing",
                    "trend_coefficient": 1.0,
                    "confidence_level": 1.0
                },
                "category_saturation": {},
                "uniqueness_metrics": {
                    "average_similarity_threshold": self.SIMILARITY_THRESHOLD,
                    "unique_pattern_discovery_rate": 1.0,
                    "content_diversity_index": 1.0
                }
            },
            "insights_and_recommendations": {
                "data_collection_status": "active_learning",
                "recommended_actions": ["Continue processing PDFs", "Monitor for emerging patterns"],
                "next_milestone_target": 100,
                "estimated_completion_percentage": 0.0
            }
        }
    
    def _save_audit_trail(self) -> None:
        """Save audit trail to disk."""
        try:
            # Create backup if file exists
            if self.audit_file_path.exists():
                backup_path = self.audit_file_path.with_suffix(f'.backup_{int(datetime.now().timestamp())}.json')
                self.audit_file_path.rename(backup_path)
                logger.debug(f"Created backup at {backup_path}")
            
            # Ensure directory exists
            self.audit_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Update metadata
            self.audit_data["audit_metadata"]["last_updated"] = datetime.now().isoformat()
            
            # Save with proper formatting
            with open(self.audit_file_path, 'w') as f:
                json.dump(self.audit_data, f, indent=2)
                
            logger.debug(f"Saved audit trail to {self.audit_file_path}")
            
        except Exception as e:
            logger.error(f"Failed to save audit trail: {e}")
            raise
    
    def start_processing_event(self, pdf_filename: str) -> str:
        """Initialize a new processing event and return event ID."""
        event_id = f"evt_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
        
        event = {
            "event_id": event_id,
            "timestamp": datetime.now().isoformat(),
            "pdf_filename": Path(pdf_filename).name,
            "pdf_file_path": str(pdf_filename),
            "processing_duration_seconds": 0.0,
            "lesson_extraction": {
                "candidate_lessons_extracted": 0,
                "lessons_added_after_deduplication": 0,
                "lessons_rejected_duplicates": 0,
                "lesson_categories_found": [],
                "lesson_quality_scores": {
                    "objection_handling_score": 0.0,
                    "opening_technique_score": 0.0,
                    "power_phrase_relevance": 0.0,
                    "overall_lesson_value": 0.0
                }
            },
            "running_totals": {
                "cumulative_pdfs_processed": 0,
                "cumulative_lessons_raw": 0,
                "cumulative_lessons_net": 0,
                "cumulative_deduplication_rate": 0.0
            },
            "change_deltas": {
                "new_lessons_this_event": 0,
                "new_categories_discovered": [],
                "improvement_over_previous": 0.0,
                "uniqueness_contribution": 0.0
            },
            "lesson_samples": []
        }
        
        # Store event in progress
        self.current_event = event
        logger.info(f"Started processing event {event_id} for {pdf_filename}")
        
        return event_id
    
    def extract_lesson_candidates(self, agent_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract potential lessons from agent analysis results."""
        lesson_candidates = []
        
        # Extract lessons from each agent's results
        for agent_name, result in agent_results.items():
            if not isinstance(result, dict):
                continue
                
            # Look for key insights, patterns, or learnings in the result
            agent_lessons = self._extract_lessons_from_agent_result(agent_name, result)
            lesson_candidates.extend(agent_lessons)
        
        logger.info(f"Extracted {len(lesson_candidates)} candidate lessons from {len(agent_results)} agents")
        return lesson_candidates
    
    def _extract_lessons_from_agent_result(self, agent_name: str, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract lessons from a single agent's result."""
        lessons = []
        
        # Keys that contain valuable insights from actual agent structure
        insight_keys = [
            # Generic lesson keys
            'key_insights', 'insights', 'learnings', 'patterns', 'techniques',
            'recommendations', 'best_practices', 'power_phrases', 'strategies',
            'observations', 'findings', 'analysis_points',
            # Actual agent result keys
            'improvement_recommendations', 'improvement_opportunities', 'missed_opportunities',
            'handling_techniques', 'rapport_techniques', 'power_phrases_identified',
            'optimization_recommendations', 'effectiveness_tips', 'strategic_insights'
        ]
        
        for key in insight_keys:
            if key in result:
                value = result[key]
                if isinstance(value, list):
                    for item in value:
                        if isinstance(item, str) and len(item.strip()) > 10:
                            lessons.append({
                                "lesson_type": agent_name.lower().replace('agent', ''),
                                "lesson_content": item.strip(),
                                "source_agent": agent_name,
                                "extraction_key": key,
                                "quality_score": self._estimate_lesson_quality(item.strip())
                            })
                        elif isinstance(item, dict):
                            # Handle structured items like handling_techniques
                            lesson_text = self._extract_lesson_from_dict(item)
                            if lesson_text and len(lesson_text.strip()) > 10:
                                lessons.append({
                                    "lesson_type": agent_name.lower().replace('agent', ''),
                                    "lesson_content": lesson_text.strip(),
                                    "source_agent": agent_name,
                                    "extraction_key": key,
                                    "quality_score": self._estimate_lesson_quality(lesson_text.strip())
                                })
                elif isinstance(value, str) and len(value.strip()) > 10:
                    lessons.append({
                        "lesson_type": agent_name.lower().replace('agent', ''),
                        "lesson_content": value.strip(),
                        "source_agent": agent_name,
                        "extraction_key": key,
                        "quality_score": self._estimate_lesson_quality(value.strip())
                    })
        
        return lessons
    
    def _extract_lesson_from_dict(self, item_dict: Dict[str, Any]) -> str:
        """Extract lesson text from structured dictionary items."""
        # Common patterns in agent results
        lesson_patterns = [
            'agent_response', 'response_text', 'technique_description',
            'recommendation', 'suggestion', 'insight', 'observation',
            'strategy', 'approach', 'method', 'phrase', 'example'
        ]
        
        for pattern in lesson_patterns:
            if pattern in item_dict and isinstance(item_dict[pattern], str):
                return item_dict[pattern]
        
        # If no direct pattern, try to construct from multiple fields
        if 'technique_used' in item_dict and 'agent_response' in item_dict:
            return f"Technique: {item_dict['technique_used']} - Response: {item_dict['agent_response']}"
        
        # Fallback: convert entire dict to readable lesson
        if len(item_dict) <= 3:  # Small dicts only
            return " | ".join([f"{k}: {v}" for k, v in item_dict.items() if isinstance(v, str)])
        
        return ""
    
    def _estimate_lesson_quality(self, lesson_content: str) -> float:
        """Estimate the quality of a lesson based on content characteristics."""
        score = 5.0  # Base score
        
        # Length bonus (but not too long)
        if 20 <= len(lesson_content) <= 200:
            score += 1.0
        elif len(lesson_content) > 200:
            score += 0.5
        
        # Specific technique indicators
        quality_indicators = [
            'when customer says', 'respond with', 'technique', 'strategy',
            'objection', 'close', 'rapport', 'phrase', 'approach', 'method'
        ]
        
        for indicator in quality_indicators:
            if indicator.lower() in lesson_content.lower():
                score += 0.5
        
        # Actionable content bonus
        action_words = ['use', 'say', 'ask', 'respond', 'handle', 'build', 'create']
        for word in action_words:
            if word.lower() in lesson_content.lower():
                score += 0.3
        
        return min(10.0, score)
    
    def complete_processing_event(self, event_id: str, lesson_candidates: List[Dict], 
                                 synthesis_result: Dict[str, Any], processing_duration: float):
        """Complete the processing event with lesson analysis and deduplication."""
        if not hasattr(self, 'current_event') or self.current_event["event_id"] != event_id:
            logger.error(f"No active event found for {event_id}")
            return
        
        # Load existing lessons for deduplication
        existing_lessons = self._load_existing_lessons()
        
        # Perform deduplication
        new_lessons, duplicates = self._deduplicate_lessons(lesson_candidates, existing_lessons)
        
        # Update event data
        event = self.current_event
        event["processing_duration_seconds"] = processing_duration
        event["lesson_extraction"]["candidate_lessons_extracted"] = len(lesson_candidates)
        event["lesson_extraction"]["lessons_added_after_deduplication"] = len(new_lessons)
        event["lesson_extraction"]["lessons_rejected_duplicates"] = len(duplicates)
        
        # Extract lesson categories
        categories = list(set(lesson["lesson_type"] for lesson in lesson_candidates))
        event["lesson_extraction"]["lesson_categories_found"] = categories
        
        # Calculate quality scores
        if lesson_candidates:
            quality_scores = [lesson["quality_score"] for lesson in lesson_candidates]
            event["lesson_extraction"]["lesson_quality_scores"]["overall_lesson_value"] = sum(quality_scores) / len(quality_scores)
        
        # Update running totals
        totals = self.audit_data["global_totals"]
        totals["total_pdfs_processed"] += 1
        totals["total_lessons_extracted_raw"] += len(lesson_candidates)
        totals["total_lessons_added_net"] += len(new_lessons)
        totals["total_lessons_deduplicated"] += len(duplicates)
        
        if totals["total_lessons_extracted_raw"] > 0:
            totals["deduplication_rate"] = totals["total_lessons_deduplicated"] / totals["total_lessons_extracted_raw"]
        
        # Update unique categories
        all_categories = set(totals.get("unique_lesson_categories", []))
        all_categories.update(categories)
        totals["unique_lesson_categories"] = list(all_categories)
        
        # Update event running totals
        event["running_totals"]["cumulative_pdfs_processed"] = totals["total_pdfs_processed"]
        event["running_totals"]["cumulative_lessons_raw"] = totals["total_lessons_extracted_raw"]
        event["running_totals"]["cumulative_lessons_net"] = totals["total_lessons_added_net"]
        event["running_totals"]["cumulative_deduplication_rate"] = totals["deduplication_rate"]
        
        # Calculate change deltas
        event["change_deltas"]["new_lessons_this_event"] = len(new_lessons)
        event["change_deltas"]["uniqueness_contribution"] = len(new_lessons) / len(lesson_candidates) if lesson_candidates else 0.0
        
        # Add lesson samples
        event["lesson_samples"] = [
            {
                "lesson_type": lesson["lesson_type"],
                "lesson_excerpt": lesson["lesson_content"][:100] + "..." if len(lesson["lesson_content"]) > 100 else lesson["lesson_content"],
                "quality_score": lesson["quality_score"],
                "is_new_pattern": True
            }
            for lesson in new_lessons[:3]  # Top 3 samples
        ]
        
        # Add event to audit trail
        self.audit_data["processing_events"].append(event)
        
        # Save new lessons to synthesized_learnings.json
        self._save_new_lessons(new_lessons)
        
        # Update plateau analysis
        self._update_plateau_analysis()
        
        # Save audit trail
        self._save_audit_trail()
        
        logger.info(f"Completed processing event {event_id}: {len(new_lessons)} new lessons added, {len(duplicates)} duplicates removed")
        
        # Clean up
        delattr(self, 'current_event')
    
    def _load_existing_lessons(self) -> List[str]:
        """Load existing lessons from synthesized_learnings.json."""
        synthesized_path = self.audit_file_path.parent / "synthesized_learnings.json"
        
        if not synthesized_path.exists():
            return []
        
        try:
            with open(synthesized_path, 'r') as f:
                data = json.load(f)
            
            # Extract lessons from structured format
            lessons = []
            
            # Look for lessons in various parts of the structure
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, dict) and 'techniques_used' in value:
                        # Extract from objection handling playbook format
                        for technique_category in value['techniques_used'].values():
                            if isinstance(technique_category, list):
                                for item in technique_category:
                                    if isinstance(item, dict) and 'response_text' in item:
                                        lessons.append(item['response_text'])
                    elif isinstance(value, list):
                        # Direct list of lessons
                        lessons.extend([str(item) for item in value if isinstance(item, str)])
                    elif isinstance(value, str):
                        lessons.append(value)
            
            logger.debug(f"Loaded {len(lessons)} existing lessons for deduplication")
            return lessons
            
        except Exception as e:
            logger.error(f"Failed to load existing lessons: {e}")
            return []
    
    def _deduplicate_lessons(self, candidates: List[Dict], existing: List[str]) -> Tuple[List[Dict], List[Dict]]:
        """Deduplicate lesson candidates against existing lessons."""
        new_lessons = []
        duplicates = []
        
        for candidate in candidates:
            lesson_content = candidate["lesson_content"]
            is_duplicate = False
            
            # Check against existing lessons
            for existing_lesson in existing:
                similarity = SequenceMatcher(None, lesson_content.lower(), existing_lesson.lower()).ratio()
                if similarity > self.SIMILARITY_THRESHOLD:
                    is_duplicate = True
                    break
            
            # Check against already processed new lessons in this batch
            if not is_duplicate:
                for new_lesson in new_lessons:
                    similarity = SequenceMatcher(None, lesson_content.lower(), new_lesson["lesson_content"].lower()).ratio()
                    if similarity > self.SIMILARITY_THRESHOLD:
                        is_duplicate = True
                        break
            
            if is_duplicate:
                duplicates.append(candidate)
            else:
                new_lessons.append(candidate)
        
        return new_lessons, duplicates
    
    def _save_new_lessons(self, new_lessons: List[Dict]) -> None:
        """Save new lessons to synthesized_learnings.json."""
        if not new_lessons:
            return
        
        synthesized_path = self.audit_file_path.parent / "synthesized_learnings.json"
        
        # Load existing data
        if synthesized_path.exists():
            try:
                with open(synthesized_path, 'r') as f:
                    data = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load synthesized_learnings.json: {e}")
                data = {}
        else:
            data = {}
        
        # Add new lessons section if not exists
        if "new_lessons_from_audit" not in data:
            data["new_lessons_from_audit"] = []
        
        # Add new lessons with metadata
        for lesson in new_lessons:
            lesson_entry = {
                "content": lesson["lesson_content"],
                "type": lesson["lesson_type"],
                "quality_score": lesson["quality_score"],
                "source_agent": lesson["source_agent"],
                "added_date": datetime.now().isoformat()
            }
            data["new_lessons_from_audit"].append(lesson_entry)
        
        # Save updated data
        try:
            with open(synthesized_path, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved {len(new_lessons)} new lessons to synthesized_learnings.json")
        except Exception as e:
            logger.error(f"Failed to save new lessons: {e}")
    
    def _update_plateau_analysis(self) -> None:
        """Update plateau analysis based on recent events."""
        events = self.audit_data["processing_events"]
        if not events:
            return
        
        # Analyze recent window
        cutoff_date = datetime.now() - timedelta(days=self.PLATEAU_WINDOW_DAYS)
        recent_events = [
            event for event in events
            if datetime.fromisoformat(event["timestamp"]) > cutoff_date
        ]
        
        recent_additions = sum(
            event["lesson_extraction"]["lessons_added_after_deduplication"]
            for event in recent_events
        )
        
        # Update plateau analysis
        plateau_analysis = self.audit_data["plateau_analysis"]
        plateau_analysis["lessons_added_recent_window"] = recent_additions
        
        # Calculate trend
        if len(events) >= 2:
            last_event = events[-1]
            prev_event = events[-2]
            
            last_uniqueness = last_event["change_deltas"]["uniqueness_contribution"]
            prev_uniqueness = prev_event["change_deltas"]["uniqueness_contribution"]
            
            trend_change = last_uniqueness - prev_uniqueness
            
            if trend_change > 0.1:
                trend_direction = "increasing"
            elif trend_change < -0.1:
                trend_direction = "decreasing"
            else:
                trend_direction = "stable"
            
            plateau_analysis["diminishing_returns_trend"]["trend_direction"] = trend_direction
            plateau_analysis["diminishing_returns_trend"]["trend_coefficient"] = trend_change
        
        # Update uniqueness metrics
        if events:
            latest_event = events[-1]
            uniqueness_rate = latest_event["change_deltas"]["uniqueness_contribution"]
            plateau_analysis["uniqueness_metrics"]["unique_pattern_discovery_rate"] = uniqueness_rate
        
        # Check for plateau
        is_plateaued = self._detect_plateau()
        if is_plateaued and not self.audit_data["global_totals"]["plateau_status"]["is_plateaued"]:
            self.audit_data["global_totals"]["plateau_status"]["is_plateaued"] = True
            self.audit_data["global_totals"]["plateau_status"]["plateau_detected_date"] = datetime.now().isoformat()
            logger.warning("⚠️  Learning plateau detected!")
        
        # Update recommendations
        self._update_recommendations()
    
    def _detect_plateau(self) -> bool:
        """Detect if the lesson learning system has reached a plateau."""
        recent_events = self._get_recent_events(self.PLATEAU_WINDOW_DAYS)
        
        if len(recent_events) < 3:  # Need minimum events for trend analysis
            return False
        
        # Criterion 1: Low addition rate
        recent_additions = sum(
            event["lesson_extraction"]["lessons_added_after_deduplication"]
            for event in recent_events
        )
        low_addition_rate = recent_additions < self.MIN_ADDITIONS_THRESHOLD
        
        # Criterion 2: High deduplication rate
        global_dedup_rate = self.audit_data["global_totals"]["deduplication_rate"]
        high_dedup_rate = global_dedup_rate > self.HIGH_DEDUP_THRESHOLD
        
        # Criterion 3: Declining uniqueness trend
        plateau_analysis = self.audit_data["plateau_analysis"]
        uniqueness_rate = plateau_analysis["uniqueness_metrics"]["unique_pattern_discovery_rate"]
        low_uniqueness = uniqueness_rate < self.LOW_UNIQUENESS_THRESHOLD
        
        # Plateau detected if 2+ criteria met
        plateau_indicators = [low_addition_rate, high_dedup_rate, low_uniqueness]
        return sum(plateau_indicators) >= 2
    
    def _get_recent_events(self, days: int) -> List[Dict[str, Any]]:
        """Get events from the recent window."""
        cutoff_date = datetime.now() - timedelta(days=days)
        return [
            event for event in self.audit_data["processing_events"]
            if datetime.fromisoformat(event["timestamp"]) > cutoff_date
        ]
    
    def _update_recommendations(self) -> None:
        """Update insights and recommendations based on current state."""
        totals = self.audit_data["global_totals"]
        is_plateaued = totals["plateau_status"]["is_plateaued"]
        dedup_rate = totals["deduplication_rate"]
        
        recommendations = []
        
        if is_plateaued:
            status = "plateau_reached"
            recommendations = [
                "Consider expanding to new call types or industries",
                "Implement advanced pattern recognition for subtle variations", 
                "Focus on quality refinement rather than quantity"
            ]
        elif dedup_rate > 0.6:
            status = "diminishing_returns"
            recommendations = [
                "Monitor for plateau signs",
                "Consider diversifying data sources",
                "Review lesson extraction techniques"
            ]
        else:
            status = "active_learning"
            recommendations = [
                "Continue processing PDFs",
                "Monitor for emerging patterns"
            ]
        
        # Estimate completion percentage
        if totals["total_lessons_added_net"] > 0:
            completion = min(95.0, (dedup_rate * 100))
        else:
            completion = 0.0
        
        self.audit_data["insights_and_recommendations"] = {
            "data_collection_status": status,
            "recommended_actions": recommendations,
            "next_milestone_target": totals["total_lessons_added_net"] + 50,
            "estimated_completion_percentage": completion
        }
    
    def is_plateau_detected(self) -> bool:
        """Check if learning has plateaued based on recent trends."""
        return self.audit_data["global_totals"]["plateau_status"]["is_plateaued"]
    
    def get_plateau_recommendations(self) -> List[str]:
        """Get actionable recommendations when plateau is detected."""
        return self.audit_data["insights_and_recommendations"]["recommended_actions"]
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary metrics for API/UI consumption."""
        totals = self.audit_data["global_totals"]
        recent_events = self._get_recent_events(7)
        
        return {
            "total_pdfs_processed": totals["total_pdfs_processed"],
            "total_lessons": totals["total_lessons_added_net"],
            "deduplication_rate": round(totals["deduplication_rate"], 3),
            "plateau_status": totals["plateau_status"]["is_plateaued"],
            "recent_lessons_added": sum(
                event["lesson_extraction"]["lessons_added_after_deduplication"]
                for event in recent_events
            ),
            "unique_categories": len(totals["unique_lesson_categories"]),
            "data_collection_status": self.audit_data["insights_and_recommendations"]["data_collection_status"],
            "estimated_completion": round(self.audit_data["insights_and_recommendations"]["estimated_completion_percentage"], 1)
        }
    
    def get_audit_trail_summary(self) -> List[Dict[str, Any]]:
        """Get processing history for UI display."""
        return [
            {
                "timestamp": event["timestamp"],
                "pdf_filename": event["pdf_filename"],
                "candidate_lessons": event["lesson_extraction"]["candidate_lessons_extracted"],
                "new_lessons": event["lesson_extraction"]["lessons_added_after_deduplication"],
                "duplicates": event["lesson_extraction"]["lessons_rejected_duplicates"],
                "quality_score": event["lesson_extraction"]["lesson_quality_scores"]["overall_lesson_value"],
                "processing_time": event["processing_duration_seconds"]
            }
            for event in self.audit_data["processing_events"][-10:]  # Last 10 events
        ]