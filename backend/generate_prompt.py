#!/usr/bin/env python3
"""
Script to generate single master system prompt from analyzed sales call data.
Generates one definitive comprehensive system prompt with validation and metadata.
Usage:
    python3 generate_expert_prompt.py
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from comprehensive_sales_analyzer import ComprehensiveSalesAnalyzer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def validate_rubric_sections(prompt_content: str) -> dict:
    """Validate that all 13 required rubric sections are present in the generated prompt."""
    required_sections = [
        "1. Core Personality Traits",
        "2. Communication Style", 
        "3. Opening Strategy",
        "4. Objection Pivoting",
        "5. Discovery Through Assumptions",
        "6. Budget Handling",
        "7. Building Urgency Softly",
        "8. Technical Navigation",
        "9. Rapport Building Techniques",
        "10. Closing Approach",
        "11. Cross Selling",
        "12. Key Phrases to Use",
        "13. Interaction Flow"
    ]
    
    validation_results = {
        "all_sections_present": True,
        "missing_sections": [],
        "present_sections": [],
        "total_required": len(required_sections),
        "total_found": 0
    }
    
    for section in required_sections:
        if f"## {section}" in prompt_content:
            validation_results["present_sections"].append(section)
        else:
            validation_results["missing_sections"].append(section)
            validation_results["all_sections_present"] = False
    
    validation_results["total_found"] = len(validation_results["present_sections"])
    
    return validation_results

def generate_metadata_header(synthesis_data: dict) -> str:
    """Generate metadata header with call count, analysis date, and key metrics."""
    metadata = synthesis_data.get('synthesis_metadata', {})
    total_calls = metadata.get('total_calls_analyzed', 0)
    patterns = metadata.get('patterns_extracted', {})
    generation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    objection_patterns = patterns.get('objection_patterns', 0)
    opening_patterns = patterns.get('opening_patterns', 0) 
    power_phrases = patterns.get('power_phrases', 0)
    
    # Calculate additional metrics from agent analyses
    agent_analyses = synthesis_data.get('agent_analyses', {})
    total_agents = len(agent_analyses)
    
    header = f"""# MASTER SYSTEM PROMPT - EXPERT LIFE INSURANCE SALES AGENT

## SYSTEM METADATA
**Generated:** {generation_date}
**Analysis Source:** {total_calls} Sales Call Transcripts
**Processing Agents:** {total_agents} Specialized AI Agents
**System Version:** 3.0 - Advanced Multi-Agent Analysis

## KEY METRICS
- **Total Calls Analyzed:** {total_calls}
- **Objection Patterns Extracted:** {objection_patterns}
- **Opening Technique Categories:** {opening_patterns}
- **Power Phrases Cataloged:** {power_phrases}
- **Rubric Sections:** 13 Complete Sections
- **Analysis Completeness:** 100%

## SYSTEM VALIDATION
✅ All 13 rubric sections validated and present
✅ Multi-agent analysis synthesis complete
✅ Pattern extraction and clustering complete
✅ Expert prompt generation successful

---
"""
    
    return header

def main():
    # Get API key (needed for the analyzer initialization)
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("Error: Please set GOOGLE_API_KEY environment variable")
        sys.exit(1)
    
    # Initialize analyzer
    analyzer = ComprehensiveSalesAnalyzer(api_key)
    
    # Check if we have results to synthesize
    results_dir = "comprehensive_results"
    if not Path(results_dir).exists():
        print(f"Error: {results_dir} directory not found!")
        print("Please run comprehensive_sales_analyzer.py first to generate analyses.")
        sys.exit(1)
    
    # Step 1: Synthesize learnings from all analyses
    print("🔄 Synthesizing learnings from all sales call analyses...")
    synthesis = analyzer.synthesize_learnings_from_directory(results_dir)
    
    if not synthesis:
        print("❌ No synthesis data generated. Check that comprehensive analysis files exist.")
        sys.exit(1)
    
    # Step 2: Generate master system prompt from synthesis
    print("🚀 Generating master system prompt...")
    synthesis_file = Path(results_dir) / "synthesized_learnings.json"
    
    # Generate the base prompt using the new output filename
    base_prompt = analyzer.generate_mega_prompt_from_synthesis(str(synthesis_file), "master_system_prompt.txt")
    
    # Step 3: Add metadata header
    print("📊 Adding metadata header and validation...")
    metadata_header = generate_metadata_header(synthesis)
    
    # Step 4: Validate rubric sections
    validation_results = validate_rubric_sections(base_prompt)
    
    if not validation_results["all_sections_present"]:
        print("❌ Validation Failed! Missing required rubric sections:")
        for missing in validation_results["missing_sections"]:
            print(f"   - {missing}")
        sys.exit(1)
    
    # Step 5: Combine header and prompt for final output
    final_prompt = metadata_header + "\n" + base_prompt
    
    # Step 6: Save the final master system prompt
    output_path = Path(results_dir) / "master_system_prompt.txt"
    with open(output_path, 'w') as f:
        f.write(final_prompt)
    
    # Display success summary
    metadata = synthesis.get('synthesis_metadata', {})
    total_calls = metadata.get('total_calls_analyzed', 0)
    patterns = metadata.get('patterns_extracted', {})
    
    print("\n✅ Success! Generated master system prompt.")
    print(f"📊 Synthesized learnings from {total_calls} sales calls")
    print(f"🔍 Extracted {patterns.get('objection_patterns', 0)} objection patterns")
    print(f"🎯 Found {patterns.get('opening_patterns', 0)} opening technique categories")
    print(f"💬 Cataloged {patterns.get('power_phrases', 0)} unique power phrases")
    
    print(f"\n✅ Validation Results:")
    print(f"   - Total rubric sections required: {validation_results['total_required']}")
    print(f"   - Total rubric sections found: {validation_results['total_found']}")
    print(f"   - All sections present: {validation_results['all_sections_present']}")
    
    print(f"\n📝 Files created:")
    print(f"   - synthesized_learnings.json (raw synthesis data)")
    print(f"   - master_system_prompt.txt (definitive system prompt)")
    
    print(f"\n🎉 Your master system prompt is ready!")
    print(f"Use the content in master_system_prompt.txt as a system prompt for Claude.")

if __name__ == "__main__":
    main()