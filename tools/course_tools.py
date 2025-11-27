"""
Course design tools for the Intelligent Course Creator.
These are function tools that wrap agent calls for curriculum, instruction, and practice design.
All agents now return Markdown content for easy PDF export.
"""

import asyncio
import re
from typing import Dict, Any

# Import agents
from agents.curriculum_designer_agent import curriculum_designer_agent
from agents.instruction_designer_agent import instruction_designer_agent
from agents.practice_designer_agent import practice_designer_agent
from agents.qa_agent import qa_agent

from models import QualityAssessment


def extract_curriculum_metadata(markdown: str) -> Dict[str, Any]:
    """Extract metadata from curriculum markdown."""
    metadata = {
        "course_title": "Untitled Course",
        "target_audience": "General",
        "total_duration_hours": 0.0
    }
    
    # Extract course title (first # heading)
    title_match = re.search(r'^#\s+(.+)$', markdown, re.MULTILINE)
    if title_match:
        metadata["course_title"] = title_match.group(1).strip()
    
    # Extract target audience
    audience_match = re.search(r'\*\*Target Audience\*\*:\s*(.+)', markdown)
    if audience_match:
        metadata["target_audience"] = audience_match.group(1).strip()
    
    # Extract duration
    duration_match = re.search(r'\*\*Total Duration\*\*:\s*(\d+(?:\.\d+)?)', markdown)
    if duration_match:
        metadata["total_duration_hours"] = float(duration_match.group(1))
    
    return metadata


def extract_lessons_from_curriculum(markdown: str) -> list:
    """Extract lesson information from curriculum markdown."""
    lessons = []
    
    # Find all lessons (pattern: #### or numbered lessons)
    lesson_pattern = r'(?:####|\d+\.)\s+\*\*(.+?)\*\*\s+\((\d+)\s+minutes?\)'
    matches = re.finditer(lesson_pattern, markdown, re.IGNORECASE)
    
    for match in matches:
        lessons.append({
            "title": match.group(1).strip(),
            "duration_minutes": int(match.group(2))
        })
    
    return lessons


def extract_qa_scores(markdown: str, quality_threshold: float = 75.0) -> QualityAssessment:
    """Extract QA scores from markdown report with YAML front matter.
    
    Args:
        markdown: The markdown report with YAML front matter
        quality_threshold: Minimum quality score required (0-100)
    
    Returns:
        QualityAssessment with scores extracted from markdown
    """
    # Default values
    scores = {
        "overall_quality_score": 75.0,
        "curriculum_alignment": 75.0,
        "completeness_score": 75.0,
        "accuracy_score": 75.0,
        "clarity_score": 75.0,
        "recommendations": []
    }
    
    # Extract YAML front matter
    yaml_match = re.search(r'---\s*\n(.*?)\n---', markdown, re.DOTALL)
    if yaml_match:
        yaml_content = yaml_match.group(1)
        
        # Parse YAML-like content
        for line in yaml_content.split('\n'):
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                if key in ['overall_quality_score', 'curriculum_alignment', 'completeness_score', 
                          'accuracy_score', 'clarity_score']:
                    try:
                        scores[key] = float(value)
                    except:
                        pass
                # Ignore 'passes_quality_threshold' from YAML - we calculate it ourselves
    
    # Calculate passes_quality_threshold based on actual threshold from UI
    passes_threshold = scores['overall_quality_score'] >= quality_threshold
    
    # Extract recommendations
    rec_section = re.search(r'##\s+Recommendations\s*\n(.*?)(?=\n##|\Z)', markdown, re.DOTALL | re.IGNORECASE)
    if rec_section:
        rec_text = rec_section.group(1)
        # Find bullet points or numbered lists
        recs = re.findall(r'(?:[-*]\s+|^\d+\.\s+)(.+)$', rec_text, re.MULTILINE)
        scores['recommendations'] = [r.strip() for r in recs]
    
    return QualityAssessment(
        markdown_report=markdown,
        passes_quality_threshold=passes_threshold,
        **scores
    )


async def design_curriculum(course_topic: str, target_audience: str, course_duration_hours: int) -> str:
    """
    Design a comprehensive curriculum for the given course topic.
    
    Args:
        course_topic: The main topic or subject of the course
        target_audience: Who this course is designed for
        course_duration_hours: Total hours available for the course
    
    Returns:
        str: Curriculum in Markdown format
    """
    print(f"Designing curriculum for: {course_topic}")
    
    input_prompt = f"""
Design a comprehensive curriculum for:
- Topic: {course_topic}
- Target Audience: {target_audience}
- Total Duration: {course_duration_hours} hours

Create a detailed curriculum with modules, lessons, learning objectives, and assessment strategy.
"""
    
    curriculum_markdown = await curriculum_designer_agent.run(input_prompt)
    
    # Extract metadata for logging
    metadata = extract_curriculum_metadata(curriculum_markdown)
    lessons = extract_lessons_from_curriculum(curriculum_markdown)
    
    print(f"Curriculum designed: {metadata['course_title']}")
    print(f"  - Lessons found: {len(lessons)}")
    
    return curriculum_markdown


async def design_instruction(curriculum_markdown: str) -> str:
    """
    Design detailed instruction materials for lessons in the curriculum.
    
    Args:
        curriculum_markdown: The curriculum in Markdown format
    
    Returns:
        str: Combined instruction materials in Markdown format
    """
    # Extract lessons from curriculum
    lessons = extract_lessons_from_curriculum(curriculum_markdown)
    metadata = extract_curriculum_metadata(curriculum_markdown)
    
    print(f"Designing instruction materials for {metadata['course_title']}")
    print(f"Creating instruction for {len(lessons)} lessons (parallel)...")
    
    # Create instruction for each lesson
    tasks = []
    for lesson in lessons:
        input_prompt = f"""
Create detailed instruction materials for this lesson from the course "{metadata['course_title']}":

Lesson: {lesson['title']}
Duration: {lesson['duration_minutes']} minutes
Target Audience: {metadata['target_audience']}

Provide comprehensive teaching content, tips, and engagement strategies.
"""
        task = instruction_designer_agent.run(input_prompt)
        tasks.append(task)
    
    # Run all instruction designs in parallel
    instruction_markdowns = await asyncio.gather(*tasks)
    
    # Combine all instruction materials
    combined_instructions = f"\n\n---\n\n# INSTRUCTION MATERIALS\n\n"
    for i, instr_md in enumerate(instruction_markdowns, 1):
        combined_instructions += f"\n\n## Lesson {i}\n\n{instr_md}\n\n"
    
    print(f"Instruction materials created for all lessons")
    
    return combined_instructions


async def design_practice(curriculum_markdown: str, instruction_markdown: str) -> str:
    """
    Design practice exercises and assessments for all lessons.
    
    Args:
        curriculum_markdown: The curriculum in Markdown format
        instruction_markdown: The instruction materials in Markdown format
    
    Returns:
        str: Combined practice materials in Markdown format
    """
    # Extract lessons from curriculum
    lessons = extract_lessons_from_curriculum(curriculum_markdown)
    metadata = extract_curriculum_metadata(curriculum_markdown)
    
    print(f"Designing practice materials for {metadata['course_title']}")
    print(f"Creating practice materials for {len(lessons)} lessons (parallel)...")
    
    # Create practice for each lesson
    tasks = []
    for lesson in lessons:
        input_prompt = f"""
Create practice exercises and assessments for this lesson from the course "{metadata['course_title']}":

Lesson: {lesson['title']}
Duration: {lesson['duration_minutes']} minutes
Target Audience: {metadata['target_audience']}

Design varied exercises with multiple difficulty levels and clear assessments.
"""
        task = practice_designer_agent.run(input_prompt)
        tasks.append(task)
    
    # Run all practice designs in parallel
    practice_markdowns = await asyncio.gather(*tasks)
    
    # Combine all practice materials
    combined_practice = f"\n\n---\n\n# PRACTICE MATERIALS\n\n"
    for i, practice_md in enumerate(practice_markdowns, 1):
        combined_practice += f"\n\n## Lesson {i}\n\n{practice_md}\n\n"
    
    print(f"Practice materials created for all lessons")
    
    return combined_practice


async def assess_quality(
    curriculum_markdown: str,
    instruction_markdown: str,
    practice_markdown: str,
    quality_threshold: float = 75.0
) -> QualityAssessment:
    """
    Assess the quality of the designed course materials.
    
    Args:
        curriculum_markdown: The curriculum in Markdown
        instruction_markdown: The instruction materials in Markdown
        practice_markdown: The practice materials in Markdown
        quality_threshold: Minimum quality score required (0-100)
    
    Returns:
        QualityAssessment: Quality assessment with scores and report
    """
    print(f"Assessing quality of course materials (threshold: {quality_threshold}%)")
    
    # Count sections for summary
    curriculum_metadata = extract_curriculum_metadata(curriculum_markdown)
    lessons = extract_lessons_from_curriculum(curriculum_markdown)
    
    materials_summary = f"""
Course: {curriculum_metadata['course_title']}
Target Audience: {curriculum_metadata['target_audience']}
Total Duration: {curriculum_metadata['total_duration_hours']} hours
Lessons: {len(lessons)}

CURRICULUM:
{curriculum_markdown[:1000]}...

INSTRUCTION MATERIALS (preview):
{instruction_markdown[:1000]}...

PRACTICE MATERIALS (preview):
{practice_markdown[:1000]}...
"""
    
    input_prompt = f"""
Evaluate the quality of these course materials:
{materials_summary}

Assess:
- Curriculum alignment with learning outcomes
- Completeness of instruction materials
- Accuracy and clarity of content
- Quality and variety of practice materials
- Overall course coherence and flow

Minimum quality threshold: {quality_threshold}%

Remember to include the YAML front matter with scores at the start of your response!
"""
    
    qa_markdown = await qa_agent.run(input_prompt)
    
    # Extract scores and create QualityAssessment object
    # Pass the threshold so it can be calculated correctly based on UI value
    qa_assessment = extract_qa_scores(qa_markdown, quality_threshold=quality_threshold)
    
    print(f"Quality Assessment: {qa_assessment.overall_quality_score:.1f}% (threshold: {quality_threshold}%)")
    print(f"Passes threshold: {qa_assessment.passes_quality_threshold}")
    
    return qa_assessment
