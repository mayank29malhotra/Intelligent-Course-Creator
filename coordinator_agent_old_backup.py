"""
Coordinator Agent

This is the main orchestrator that manages the entire course creation pipeline,
including feedback loops and quality assurance iterations using Google Gemini.
Includes 60-second delays between steps for Gemini free tier rate limiting.
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Tuple, Optional, Callable
import uuid

from models import Curriculum, Instruction, Practice, QualityAssurance, CourseCompletion
from tools import design_curriculum, design_instruction, design_practice, assess_quality
from tools.pdf_exporter import export_course_to_pdf
from config import gemini_config


class CourseCreationCoordinator:
    """
    Orchestrates the entire course creation workflow with feedback loops,
    quality assurance validation, and 60-second delays for Gemini API free tier.
    """
    
    # 60-second delay between API calls for free tier rate limiting
    DELAY_BETWEEN_STEPS = 60  # seconds
    
    def __init__(self, quality_threshold: float = 75.0, max_iterations: int = 3):
        """
        Initialize the coordinator.
        
        Args:
            quality_threshold: Minimum quality score required (0-100)
            max_iterations: Maximum number of refinement iterations
        """
        self.quality_threshold = quality_threshold
        self.max_iterations = max_iterations
        self.trace_id = str(uuid.uuid4())
        # Quick validation: ensure Gemini is configured
        try:
            _ = gemini_config.GEMINI_API_KEY
            _ = gemini_config.GEMINI_MODEL
        except Exception as e:
            print(f"⚠️  Warning: Gemini configuration may be missing or invalid: {e}")
    
    async def _wait_between_steps(self, progress_callback: Optional[Callable] = None, 
                                   step_name: str = ""):
        """
        Wait 60 seconds between API calls with countdown progress.
        
        Args:
            progress_callback: Optional Gradio progress callback
            step_name: Name of the step that just completed
        """
        if step_name:
            print(f"\n⏳ Rate limiting: Waiting {self.DELAY_BETWEEN_STEPS}s before next step...")
        
        for remaining in range(self.DELAY_BETWEEN_STEPS, 0, -1):
            if progress_callback:
                desc = f"⏳ Waiting {remaining}s before next step ({step_name})"
                try:
                    progress_callback(0.5, desc=desc)
                except:
                    pass
            
            if remaining % 10 == 0 or remaining <= 5:
                print(f"   {remaining}s remaining...", end="\r")
            
            await asyncio.sleep(1)
        
        print("   ✓ Ready to proceed           ")
    
    async def create_course(
        self,
        course_topic: str,
        target_audience: str,
        duration_hours: int,
        verbose: bool = True,
        progress_callback: Optional[Callable] = None
    ) -> CourseCompletion:
        """
        Create a complete course through the full pipeline with quality assurance.
        Includes 60-second delays between steps for Gemini free tier.
        
        Args:
            course_topic: The main topic/subject of the course
            target_audience: Who the course is designed for
            duration_hours: Total hours available for the course
            verbose: Whether to print progress updates
            progress_callback: Optional callback for progress updates (Gradio)
        
        Returns:
            CourseCompletion: Complete course with all materials and QA report
        """
        if verbose:
            print(f"\n{'='*70}")
            print(f"🎓 INTELLIGENT COURSE CREATOR - PIPELINE EXECUTION")
            print(f"{'='*70}")
            print(f"\n📋 Course Configuration:")
            print(f"   Topic: {course_topic}")
            print(f"   Audience: {target_audience}")
            print(f"   Duration: {duration_hours} hours")
            print(f"   Quality Threshold: {self.quality_threshold}%")
            print(f"   Max Iterations: {self.max_iterations}")
            print(f"\n   Trace ID: {self.trace_id}")
            print(f"{'='*70}\n")
        
        iteration = 0
        failed_components = None
        total_progress = 0
        
        while iteration <= self.max_iterations:
            iteration += 1
            
            if verbose:
                print(f"\n{'█'*70}")
                print(f"🔄 ITERATION {iteration}/{self.max_iterations + 1}")
                print(f"{'█'*70}\n")
            
            # ============================================================
            # STEP 1: Design Curriculum
            # ============================================================
            if failed_components is None or "curriculum" in failed_components:
                step_num = 1
                
                if verbose:
                    print(f"{'▌'*70}")
                    print(f"📚 STEP {step_num}/4: CURRICULUM DESIGNER AGENT")
                    print(f"{'▌'*70}")
                    print(f"⏳ Analyzing topic and creating course structure...")
                
                if progress_callback:
                    try:
                        progress_callback(0.1, desc=f"📚 [1/4] Curriculum Designer - Analyzing course structure...")
                    except:
                        pass
                
                try:
                    curriculum = await design_curriculum(
                        course_topic=course_topic,
                        target_audience=target_audience,
                        course_duration_hours=duration_hours
                    )
                    
                    if verbose:
                        print(f"\n✅ CURRICULUM GENERATED")
                        print(f"   • Title: {curriculum.course_title}")
                        print(f"   • Modules: {len(curriculum.modules)}")
                        print(f"   • Total Lessons: {sum(len(m.lessons) for m in curriculum.modules)}")
                        total_objectives = sum(len(lesson.learning_objectives) for module in curriculum.modules for lesson in module.lessons)
                        print(f"   • Learning Objectives: {total_objectives}")
                    
                    # Wait 60 seconds before next step
                    if iteration < self.max_iterations + 1:
                        await self._wait_between_steps(progress_callback, "Curriculum Designer")
                
                except Exception as e:
                    if verbose:
                        print(f"❌ CURRICULUM DESIGN FAILED: {str(e)}")
                    raise
            
            # ============================================================
            # STEP 2: Design Instruction Materials
            # ============================================================
            if failed_components is None or "instruction" in failed_components:
                step_num = 2
                
                if verbose:
                    print(f"\n{'▌'*70}")
                    print(f"✍️  STEP {step_num}/4: INSTRUCTION DESIGNER AGENT")
                    print(f"{'▌'*70}")
                    print(f"⏳ Creating teaching materials and engagement strategies...")
                
                if progress_callback:
                    try:
                        progress_callback(0.35, desc=f"✍️  [2/4] Instruction Designer - Creating teaching materials...")
                    except:
                        pass
                
                try:
                    instructions = await design_instruction(curriculum)
                    
                    if verbose:
                        print(f"\n✅ INSTRUCTION MATERIALS GENERATED")
                        print(f"   • Instruction Sets: {len(instructions)}")
                        total_content = sum(len(i.overview) for i in instructions)
                        print(f"   • Teaching Strategies: {sum(1 for i in instructions if i.teaching_strategies)}")
                        print(f"   • Engagement Strategies: {sum(len(i.engagement_strategies) for i in instructions)}")
                    
                    # Wait 60 seconds before next step
                    if iteration < self.max_iterations + 1:
                        await self._wait_between_steps(progress_callback, "Instruction Designer")
                
                except Exception as e:
                    if verbose:
                        print(f"❌ INSTRUCTION DESIGN FAILED: {str(e)}")
                    raise
            
            # ============================================================
            # STEP 3: Design Practice Materials
            # ============================================================
            if failed_components is None or "practice" in failed_components:
                step_num = 3
                
                if verbose:
                    print(f"\n{'▌'*70}")
                    print(f"💪 STEP {step_num}/4: PRACTICE DESIGNER AGENT")
                    print(f"{'▌'*70}")
                    print(f"⏳ Generating exercises, quizzes, and assessments...")
                
                if progress_callback:
                    try:
                        progress_callback(0.6, desc=f"💪 [3/4] Practice Designer - Creating exercises & assessments...")
                    except:
                        pass
                
                try:
                    practice_sets = await design_practice(curriculum, instructions)
                    
                    if verbose:
                        print(f"\n✅ PRACTICE MATERIALS GENERATED")
                        print(f"   • Practice Sets: {len(practice_sets)}")
                        print(f"   • Total Exercises: {sum(len(p.exercises) for p in practice_sets)}")
                        print(f"   • Quizzes: {sum(len(p.quiz_questions) for p in practice_sets)}")
                        print(f"   • Assessments: {sum(len(p.assessment_criteria) for p in practice_sets)}")
                    
                    # Wait 60 seconds before QA step
                    if iteration < self.max_iterations + 1:
                        await self._wait_between_steps(progress_callback, "Practice Designer")
                
                except Exception as e:
                    if verbose:
                        print(f"❌ PRACTICE DESIGN FAILED: {str(e)}")
                    raise
            
            # ============================================================
            # STEP 4: Quality Assurance
            # ============================================================
            step_num = 4
            
            if verbose:
                print(f"\n{'▌'*70}")
                print(f"✅ STEP {step_num}/4: QA VALIDATION AGENT")
                print(f"{'▌'*70}")
                print(f"⏳ Evaluating quality across all dimensions...")
            
            if progress_callback:
                try:
                    progress_callback(0.8, desc=f"✅ [4/4] QA Agent - Validating course quality...")
                except:
                    pass
            
            try:
                quality_report = await assess_quality(
                    curriculum=curriculum,
                    instructions=instructions,
                    practice_sets=practice_sets,
                    quality_threshold=self.quality_threshold
                )
                
                if verbose:
                    print(f"\n📊 QUALITY ASSESSMENT RESULTS:")
                    print(f"   • Overall Score: {quality_report.overall_quality_score:.1f}%")
                    print(f"   • Curriculum Alignment: {quality_report.curriculum_alignment:.1f}%")
                    print(f"   • Completeness: {quality_report.completeness_score:.1f}%")
                    print(f"   • Accuracy: {quality_report.accuracy_score:.1f}%")
                    print(f"   • Clarity: {quality_report.clarity_score:.1f}%")
                
                # Check if quality threshold is met
                if quality_report.passes_quality_threshold:
                    if verbose:
                        print(f"\n✅ QUALITY THRESHOLD MET!")
                        print(f"   Score: {quality_report.overall_quality_score:.1f}% >= {self.quality_threshold}%")
                    
                    if progress_callback:
                        try:
                            progress_callback(1.0, desc="✅ Course generation complete! All quality checks passed.")
                        except:
                            pass
                    
                    # Create final course completion object
                    course = CourseCompletion(
                        course_id=f"{course_topic.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        curriculum=curriculum,
                        instructions=instructions,
                        practice_sets=practice_sets,
                        quality_report=quality_report,
                        creation_timestamp=datetime.now().isoformat(),
                        total_iterations=iteration
                    )
                    
                    if verbose:
                        print(f"\n{'='*70}")
                        print(f"🎉 COURSE CREATION COMPLETED SUCCESSFULLY!")
                        print(f"{'='*70}")
                        print(f"Course ID: {course.course_id}")
                        print(f"Iterations: {iteration}/{self.max_iterations}")
                        print(f"Final Quality Score: {quality_report.overall_quality_score:.1f}%")
                        print(f"{'='*70}\n")
                    
                    # Export to PDF for easy download
                    try:
                        outputs_dir = os.path.join(os.path.dirname(__file__), "outputs")
                        os.makedirs(outputs_dir, exist_ok=True)
                        pdf_path = os.path.join(outputs_dir, f"{course.course_id}.pdf")
                        export_course_to_pdf(course, pdf_path)
                        print(f"📥 PDF exported to: {pdf_path}")
                    except Exception as e:
                        print(f"⚠️  Failed to export PDF: {e}")

                    return course
                else:
                    # Quality not met
                    if verbose:
                        print(f"\n⚠️  QUALITY THRESHOLD NOT MET")
                        print(f"   Score: {quality_report.overall_quality_score:.1f}% < {self.quality_threshold}%")
                        
                        if quality_report.issues:
                            print(f"\n   🔍 Issues Identified:")
                            for issue in quality_report.issues:
                                print(f"   • [{issue.severity.upper()}] {issue.category}")
                                print(f"     → {issue.description}")
                        
                        if quality_report.recommendations:
                            print(f"\n   💡 Recommendations:")
                            for rec in quality_report.recommendations:
                                print(f"   • {rec}")
                    
                    # Determine which components to retry
                    failed_components = self._determine_failed_components(quality_report)
                    
                    if iteration >= self.max_iterations:
                        if verbose:
                            print(f"\n❌ MAX ITERATIONS REACHED ({self.max_iterations})")
                            print(f"   Final Score: {quality_report.overall_quality_score:.1f}%")
                            print(f"   Returning course with best attempt...")
                        
                        if progress_callback:
                            try:
                                progress_callback(1.0, desc=f"⚠️  Max iterations reached. Quality: {quality_report.overall_quality_score:.1f}%")
                            except:
                                pass
                        
                        # Return course even if quality not met
                        course = CourseCompletion(
                            course_id=f"{course_topic.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                            curriculum=curriculum,
                            instructions=instructions,
                            practice_sets=practice_sets,
                            quality_report=quality_report,
                            creation_timestamp=datetime.now().isoformat(),
                            total_iterations=iteration
                        )
                        # Export best-effort PDF even if quality threshold not met
                        try:
                            outputs_dir = os.path.join(os.path.dirname(__file__), "outputs")
                            os.makedirs(outputs_dir, exist_ok=True)
                            pdf_path = os.path.join(outputs_dir, f"{course.course_id}.pdf")
                            export_course_to_pdf(course, pdf_path)
                            print(f"📥 PDF exported to: {pdf_path}")
                        except Exception as e:
                            print(f"⚠️  Failed to export PDF: {e}")

                        return course
                    
                    if verbose:
                        print(f"\n🔄 Retrying: {', '.join(failed_components).upper()}")
                        print(f"   Next iteration will regenerate failed components...")
                        
                        # Wait 60 seconds before next iteration
                        await self._wait_between_steps(progress_callback, f"Iteration {iteration} complete")
            
            except Exception as e:
                if verbose:
                    print(f"❌ QUALITY ASSESSMENT FAILED: {str(e)}")
                raise
    
    def _determine_failed_components(self, quality_report: QualityAssurance) -> list:
        """
        Determine which components failed quality checks.
        
        Args:
            quality_report: The quality assessment report
        
        Returns:
            List of component names to retry
        """
        failed_components = []
        
        # If alignment is low, curriculum failed
        if quality_report.curriculum_alignment < self.quality_threshold:
            failed_components.append("curriculum")
        
        # If clarity or accuracy is low, instruction failed
        if quality_report.clarity_score < self.quality_threshold or \
           quality_report.accuracy_score < self.quality_threshold:
            failed_components.append("instruction")
        
        # If completeness is low, practice failed
        if quality_report.completeness_score < self.quality_threshold:
            failed_components.append("practice")
        
        # If nothing specific, retry all
        if not failed_components:
            failed_components = ["curriculum", "instruction", "practice"]
        
        return failed_components


# Convenience function for direct use
coordinator = CourseCreationCoordinator()
