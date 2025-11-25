"""
Intelligent Course Creator - Multi-Agent Orchestration System

An end-to-end course generation platform using OpenAI SDK agents with feedback loops
and quality assurance.
"""

__version__ = "1.0.0"
__author__ = "Course Creator Team"
__license__ = "MIT"

from coordinator_agent import CourseCreationCoordinator
from models import (
    Curriculum,
    Instruction,
    Practice,
    QualityAssurance,
    CourseCompletion,
)

__all__ = [
    "CourseCreationCoordinator",
    "Curriculum",
    "Instruction",
    "Practice",
    "QualityAssurance",
    "CourseCompletion",
]

# Convenience function
async def create_course(
    topic: str,
    audience: str,
    duration_hours: int,
    quality_threshold: float = 75.0,
    max_iterations: int = 3,
    verbose: bool = True
) -> CourseCompletion:
    """
    Quick start function to create a course.
    
    Args:
        topic: Course topic/subject
        audience: Target audience
        duration_hours: Total course hours
        quality_threshold: Minimum quality score (0-100)
        max_iterations: Maximum refinement iterations
        verbose: Print progress updates
    
    Returns:
        CourseCompletion: Complete course with all materials
    """
    coordinator = CourseCreationCoordinator(
        quality_threshold=quality_threshold,
        max_iterations=max_iterations
    )
    
    return await coordinator.create_course(
        course_topic=topic,
        target_audience=audience,
        duration_hours=duration_hours,
        verbose=verbose
    )
