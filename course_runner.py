#!/usr/bin/env python3
"""
Course Runner - Isolated subprocess for course creation

This script runs in a separate process to completely isolate
Pydantic models from Gradio's introspection.
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# Ensure the parent directory is in path for imports
sys.path.insert(0, str(Path(__file__).parent))

from coordinator_agent import CourseCreationCoordinator


async def create_course_isolated(
    course_topic: str,
    target_audience: str,
    duration_hours: int,
    quality_threshold: float = 75.0,
    max_iterations: int = 3
) -> dict:
    """
    Create course in isolated environment.
    
    Returns:
        dict with keys: success, course_title, markdown_content, error
    """
    try:
        # Initialize coordinator
        coordinator = CourseCreationCoordinator(
            quality_threshold=quality_threshold,
            max_iterations=max_iterations
        )
        
        print(f"✅ Coordinator initialized (threshold: {quality_threshold}%)")
        
        # Create course
        course = await coordinator.create_course(
            course_topic=course_topic,
            target_audience=target_audience,
            duration_hours=int(duration_hours),
            verbose=True
        )
        
        # Convert Pydantic model to plain dict
        result = {
            "success": True,
            "course_title": str(course.course_title),
            "markdown_content": str(course.full_markdown_content),
            "error": None
        }
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "course_title": "",
            "markdown_content": "",
            "error": str(e)
        }


def main():
    """CLI entry point for subprocess execution."""
    if len(sys.argv) != 6:
        print("Usage: course_runner.py <topic> <audience> <hours> <quality> <max_iterations>")
        sys.exit(1)
    
    topic = sys.argv[1]
    audience = sys.argv[2] 
    hours = float(sys.argv[3])
    quality = float(sys.argv[4])
    max_iter = int(sys.argv[5])
    
    # Run async course creation
    result = asyncio.run(create_course_isolated(
        course_topic=topic,
        target_audience=audience, 
        duration_hours=hours,
        quality_threshold=quality,
        max_iterations=max_iter
    ))
    
    # Output result as JSON
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()