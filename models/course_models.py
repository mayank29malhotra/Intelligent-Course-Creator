"""
Pydantic models for the Intelligent Course Creator system.
These models define the structured data formats for each agent in the pipeline.
All agents now generate Markdown content for easy PDF export.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class CurriculumMarkdown(BaseModel):
    """Curriculum structure with Markdown content."""
    markdown_content: str = Field(description="Complete curriculum in Markdown format")
    course_title: str = Field(description="Title of the course extracted from markdown")
    target_audience: str = Field(description="Intended learners extracted from markdown")
    total_duration_hours: float = Field(description="Total estimated course duration")


class InstructionMarkdown(BaseModel):
    """Instruction materials with Markdown content."""
    markdown_content: str = Field(description="Complete instruction materials in Markdown format")
    lesson_title: str = Field(description="Title of the lesson")
    module_title: str = Field(description="Title of the module")


class PracticeMarkdown(BaseModel):
    """Practice materials with Markdown content."""
    markdown_content: str = Field(description="Complete practice materials in Markdown format")
    lesson_title: str = Field(description="Title of the lesson")


class QualityAssessment(BaseModel):
    """Quality assessment report."""
    markdown_report: str = Field(description="Quality assessment report in Markdown format")
    overall_quality_score: float = Field(description="Overall score from 0-100")
    curriculum_alignment: float = Field(description="How well curriculum aligns with objectives")
    completeness_score: float = Field(description="How complete the course materials are")
    accuracy_score: float = Field(description="How accurate the content is")
    clarity_score: float = Field(description="How clear and understandable the content is")
    passes_quality_threshold: bool = Field(description="Whether quality meets minimum threshold")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations for improvement")


class CourseCompletion(BaseModel):
    """Final compiled course ready for delivery."""
    course_id: str = Field(description="Unique identifier for the course")
    course_title: str = Field(description="Title of the course")
    full_markdown_content: str = Field(description="Complete course in Markdown format ready for PDF export")
    curriculum_markdown: str = Field(description="Curriculum section in Markdown")
    instruction_markdown: str = Field(description="Instruction materials section in Markdown")
    practice_markdown: str = Field(description="Practice materials section in Markdown")
    quality_report_markdown: str = Field(description="Quality report in Markdown")
    quality_assessment: QualityAssessment = Field(description="Structured quality assessment")
    creation_timestamp: str = Field(description="When the course was created")
    total_iterations: int = Field(description="How many iterations were needed")


# Legacy models kept for backward compatibility but deprecated
class LearningObjective(BaseModel):
    """Individual learning objective for a lesson."""
    objective_id: str = Field(description="Unique identifier for the objective")
    title: str = Field(description="Short title of the learning objective")
    description: str = Field(description="Detailed description of what students should learn")
    difficulty_level: str = Field(description="Beginner, Intermediate, or Advanced")
    measurable_outcome: str = Field(description="How to measure if the objective was achieved")


class Lesson(BaseModel):
    """Individual lesson within a module."""
    lesson_id: str = Field(description="Unique identifier for the lesson")
    title: str = Field(description="Title of the lesson")
    duration_minutes: int = Field(description="Expected duration in minutes")
    learning_objectives: List[LearningObjective] = Field(description="List of learning objectives")
    key_topics: List[str] = Field(description="Main topics covered in this lesson")


class Module(BaseModel):
    """A module containing multiple lessons."""
    module_id: str = Field(description="Unique identifier for the module")
    title: str = Field(description="Title of the module")
    description: str = Field(description="Overview of the module")
    sequence_order: int = Field(description="Order in which this module should be taught")
    estimated_hours: float = Field(description="Total estimated hours to complete the module")
    lessons: List[Lesson] = Field(description="List of lessons in this module")


class Curriculum(BaseModel):
    """Complete curriculum structure designed by the Curriculum Designer Agent."""
    course_title: str = Field(description="Title of the course")
    course_description: str = Field(description="Comprehensive course description")
    target_audience: str = Field(description="Intended learners for this course")
    prerequisites: List[str] = Field(description="What students should know before taking this course")
    total_duration_hours: float = Field(description="Total estimated course duration")
    modules: List[Module] = Field(description="All modules in the curriculum")
    learning_outcomes: List[str] = Field(description="High-level course learning outcomes")
    assessment_strategy: str = Field(description="How student progress will be assessed")


class InstructionSection(BaseModel):
    """Individual instruction section for a lesson."""
    section_id: str = Field(description="Unique identifier for the section")
    title: str = Field(description="Title of the instruction section")
    content: str = Field(description="Detailed instructional content in markdown format")
    teaching_tips: List[str] = Field(default_factory=list, description="Practical tips for instructors")
    estimated_time: int = Field(description="Time to teach this section in minutes")
    resources: List[str] = Field(default_factory=list, description="External resources or references")
    
    model_config = {"extra": "forbid", "json_schema_extra": {"additionalProperties": False}}


class Instruction(BaseModel):
    """Detailed instruction materials created by the Instruction Designer Agent."""
    lesson_id: str = Field(description="ID of the lesson this instruction is for")
    lesson_title: str = Field(description="Title of the lesson")
    module_id: str = Field(description="ID of the module containing this lesson")
    instruction_sections: List[InstructionSection] = Field(description="Individual instruction sections")
    overview: str = Field(description="Overview of the lesson instruction")
    engagement_strategies: List[str] = Field(description="Ways to engage students during instruction")
    common_misconceptions: List[str] = Field(description="Common student misconceptions to address")
    differentiation_strategies: List[str] = Field(description="Strategies for different learning levels")
    teaching_strategies: List[str] = Field(default_factory=list, description="Overall teaching strategies for the lesson")


class PracticeExercise(BaseModel):
    """Individual practice exercise or assignment."""
    exercise_id: str = Field(description="Unique identifier for the exercise")
    title: str = Field(description="Title of the exercise")
    type: str = Field(description="Type: multiple-choice, essay, coding, problem-solving, etc.")
    instructions: str = Field(description="Clear instructions for the exercise")
    difficulty_level: str = Field(description="Difficulty level relative to lesson")
    estimated_time: int = Field(description="Time to complete in minutes")
    learning_objectives: List[str] = Field(default_factory=list, description="Which objectives this exercise addresses")
    solution_rubric: Optional[str] = Field(default=None, description="Grading rubric or solution outline")
    
    model_config = {"extra": "forbid", "json_schema_extra": {"additionalProperties": False}}


class Assessment(BaseModel):
    """Assessment or quiz for evaluating student understanding."""
    assessment_id: str = Field(description="Unique identifier for the assessment")
    title: str = Field(description="Title of the assessment")
    assessment_type: str = Field(description="Type: quiz, test, project, presentation, etc.")
    duration_minutes: int = Field(description="Time allowed for assessment")
    total_points: int = Field(description="Total points possible")
    passing_score: int = Field(description="Minimum points to pass")
    questions_count: int = Field(description="Number of questions or items")
    
    model_config = {"extra": "forbid", "json_schema_extra": {"additionalProperties": False}}


class Practice(BaseModel):
    """Practice exercises and assessments designed by the Practice Designer Agent."""
    lesson_id: str = Field(description="ID of the lesson this practice is for")
    lesson_title: str = Field(description="Title of the lesson")
    module_id: str = Field(description="ID of the module")
    exercises: List[PracticeExercise] = Field(description="List of practice exercises")
    quiz_questions: List[PracticeExercise] = Field(default_factory=list, description="Quiz questions for the lesson")
    assessments: List[Assessment] = Field(description="List of assessments or quizzes")
    assessment_criteria: List[str] = Field(default_factory=list, description="Criteria for assessing student work")
    feedback_guidelines: List[str] = Field(description="Guidelines for providing feedback")
    progression_strategy: str = Field(description="How students progress through exercises")
    remediation_options: List[str] = Field(description="Options for students who need extra help")


class QualityIssue(BaseModel):
    """A quality issue identified during QA review."""
    category: str = Field(description="Category: alignment, completeness, accuracy, clarity, etc.")
    severity: str = Field(description="Severity level: critical, major, minor")
    description: str = Field(description="Description of the issue")
    location: str = Field(description="Where in the course this issue was found")
    recommendation: str = Field(description="Recommended fix or improvement")


class QualityAssurance(BaseModel):
    """Quality assurance report produced by the QA Agent."""
    overall_quality_score: float = Field(description="Overall score from 0-100")
    curriculum_alignment: float = Field(description="How well curriculum aligns with objectives")
    completeness_score: float = Field(description="How complete the course materials are")
    accuracy_score: float = Field(description="How accurate the content is")
    clarity_score: float = Field(description="How clear and understandable the content is")
    issues: List[QualityIssue] = Field(description="List of identified quality issues")
    strengths: List[str] = Field(description="Positive aspects of the course")
    recommendations: List[str] = Field(description="Overall recommendations for improvement")
    passes_quality_threshold: bool = Field(description="Whether quality meets minimum threshold (score >= 75)")
