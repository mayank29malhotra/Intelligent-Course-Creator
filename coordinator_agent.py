"""
Coordinator Agent - Markdown-Based Workflow

This is the main orchestrator that manages the entire course creation pipeline,
using Markdown for all content generation. Final output is a complete Markdown document
ready for PDF export.
"""

import asyncio
import os
from datetime import datetime
from typing import Tuple, Optional, Callable
import uuid

from models import CourseCompletion, QualityAssessment
from tools import design_curriculum, design_instruction, design_practice, assess_quality
from tools.course_tools import extract_curriculum_metadata
from config import gemini_config


class CourseCreationCoordinator:
    """
    Orchestrates the entire course creation workflow with feedback loops,
    quality assurance validation, and Markdown-based content generation.
    """
    
    # 30-second delay between API calls for free tier rate limiting
    DELAY_BETWEEN_STEPS = 30  # seconds
    
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
        Wait DELAY_BETWEEN_STEPS seconds between API calls with countdown progress.
        
        Args:
            progress_callback: Optional Gradio progress callback
            step_name: Name of the step that just completed
        """
        if step_name:
            print(f"\n⏳ Rate limiting: Waiting {self.DELAY_BETWEEN_STEPS}s before next step...")

        for remaining in range(self.DELAY_BETWEEN_STEPS, 0, -1):
            # Keep countdown logs for debugging, but let the UI progress
            # be controlled entirely by the outer Gradio app.
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
        All content is generated as Markdown for easy PDF export.
        
        Args:
            course_topic: The main topic/subject of the course
            target_audience: Who the course is designed for
            duration_hours: Total hours available for the course
            verbose: Whether to print progress updates
            progress_callback: Optional callback for progress updates (Gradio)
        
        Returns:
            CourseCompletion: Complete course in Markdown format
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
                if verbose:
                    print(f"{'▌'*70}")
                    print(f"📚 STEP 1/4: CURRICULUM DESIGNER AGENT")
                    print(f"{'▌'*70}")
                    print(f"⏳ Analyzing topic and creating course structure...")
                
                if progress_callback:
                    try:
                        progress_callback(0.1, desc=f"📚 [1/4] Curriculum Designer - Analyzing course structure...")
                    except:
                        pass
                
                try:
                    curriculum_markdown = await design_curriculum(
                        course_topic=course_topic,
                        target_audience=target_audience,
                        course_duration_hours=duration_hours
                    )
                    
                    # Extract metadata for logging
                    metadata = extract_curriculum_metadata(curriculum_markdown)
                    
                    if verbose:
                        print(f"\n✅ CURRICULUM GENERATED")
                        print(f"   • Title: {metadata['course_title']}")
                        print(f"   • Markdown length: {len(curriculum_markdown)} characters")
                    
                    # Wait before next step
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
                if verbose:
                    print(f"\n{'▌'*70}")
                    print(f"✍️  STEP 2/4: INSTRUCTION DESIGNER AGENT")
                    print(f"{'▌'*70}")
                    print(f"⏳ Creating teaching materials and engagement strategies...")
                
                if progress_callback:
                    try:
                        progress_callback(0.35, desc=f"✍️  [2/4] Instruction Designer - Creating teaching materials...")
                    except:
                        pass
                
                try:
                    instruction_markdown = await design_instruction(curriculum_markdown)
                    
                    if verbose:
                        print(f"\n✅ INSTRUCTION MATERIALS GENERATED")
                        print(f"   • Markdown length: {len(instruction_markdown)} characters")
                    
                    # Wait before next step
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
                if verbose:
                    print(f"\n{'▌'*70}")
                    print(f"💪 STEP 3/4: PRACTICE DESIGNER AGENT")
                    print(f"{'▌'*70}")
                    print(f"⏳ Generating exercises, quizzes, and assessments...")
                
                if progress_callback:
                    try:
                        progress_callback(0.6, desc=f"💪 [3/4] Practice Designer - Creating exercises & assessments...")
                    except:
                        pass
                
                try:
                    practice_markdown = await design_practice(curriculum_markdown, instruction_markdown)
                    
                    if verbose:
                        print(f"\n✅ PRACTICE MATERIALS GENERATED")
                        print(f"   • Markdown length: {len(practice_markdown)} characters")
                    
                    # Wait before QA step
                    if iteration < self.max_iterations + 1:
                        await self._wait_between_steps(progress_callback, "Practice Designer")
                
                except Exception as e:
                    if verbose:
                        print(f"❌ PRACTICE DESIGN FAILED: {str(e)}")
                    raise
            
            # ============================================================
            # STEP 4: Quality Assurance
            # ============================================================
            if verbose:
                print(f"\n{'▌'*70}")
                print(f"✅ STEP 4/4: QA VALIDATION AGENT")
                print(f"{'▌'*70}")
                print(f"⏳ Evaluating quality across all dimensions...")
            
            if progress_callback:
                try:
                    progress_callback(0.8, desc=f"✅ [4/4] QA Agent - Validating course quality...")
                except:
                    pass
            
            try:
                quality_assessment = await assess_quality(
                    curriculum_markdown=curriculum_markdown,
                    instruction_markdown=instruction_markdown,
                    practice_markdown=practice_markdown,
                    quality_threshold=self.quality_threshold
                )
                
                if verbose:
                    print(f"\n📊 QUALITY ASSESSMENT RESULTS:")
                    print(f"   • Overall Score: {quality_assessment.overall_quality_score:.1f}%")
                    print(f"   • Curriculum Alignment: {quality_assessment.curriculum_alignment:.1f}%")
                    print(f"   • Completeness: {quality_assessment.completeness_score:.1f}%")
                    print(f"   • Accuracy: {quality_assessment.accuracy_score:.1f}%")
                    print(f"   • Clarity: {quality_assessment.clarity_score:.1f}%")
                
                # Check if quality threshold is met
                if quality_assessment.passes_quality_threshold:
                    if verbose:
                        print(f"\n✅ QUALITY THRESHOLD MET!")
                        print(f"   Score: {quality_assessment.overall_quality_score:.1f}% >= {self.quality_threshold}%")
                    
                    if progress_callback:
                        try:
                            progress_callback(1.0, desc="✅ Course generation complete! All quality checks passed.")
                        except:
                            pass
                    
                    # Create final course completion object
                    metadata = extract_curriculum_metadata(curriculum_markdown)
                    
                    # Combine all Markdown content
                    full_markdown = self._combine_markdown_content(
                        curriculum_markdown,
                        instruction_markdown,
                        practice_markdown,
                        quality_assessment.markdown_report
                    )
                    
                    course = CourseCompletion(
                        course_id=f"{course_topic.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        course_title=metadata['course_title'],
                        full_markdown_content=full_markdown,
                        curriculum_markdown=curriculum_markdown,
                        instruction_markdown=instruction_markdown,
                        practice_markdown=practice_markdown,
                        quality_report_markdown=quality_assessment.markdown_report,
                        quality_assessment=quality_assessment,
                        creation_timestamp=datetime.now().isoformat(),
                        total_iterations=iteration
                    )
                    
                    if verbose:
                        print(f"\n{'='*70}")
                        print(f"🎉 COURSE CREATION COMPLETED SUCCESSFULLY!")
                        print(f"{'='*70}")
                        print(f"Course ID: {course.course_id}")
                        print(f"Iterations: {iteration}/{self.max_iterations}")
                        print(f"Final Quality Score: {quality_assessment.overall_quality_score:.1f}%")
                        print(f"{'='*70}\n")
                    
                    # Export to PDF
                    try:
                        outputs_dir = os.path.join(os.path.dirname(__file__), "outputs")
                        os.makedirs(outputs_dir, exist_ok=True)
                        pdf_path = os.path.join(outputs_dir, f"{course.course_id}.pdf")
                        export_markdown_to_pdf(full_markdown, pdf_path)
                        print(f"📥 PDF exported to: {pdf_path}")
                    except Exception as e:
                        print(f"⚠️  Failed to export PDF: {e}")
                    
                    return course
                else:
                    # Quality not met
                    if verbose:
                        print(f"\n⚠️  QUALITY THRESHOLD NOT MET")
                        print(f"   Score: {quality_assessment.overall_quality_score:.1f}% < {self.quality_threshold}%")
                        
                        if quality_assessment.recommendations:
                            print(f"\n   💡 Recommendations:")
                            for rec in quality_assessment.recommendations:
                                print(f"   • {rec}")
                    
                    # Determine which components to retry
                    failed_components = self._determine_failed_components(quality_assessment)
                    
                    if iteration >= self.max_iterations:
                        if verbose:
                            print(f"\n❌ MAX ITERATIONS REACHED ({self.max_iterations})")
                            print(f"   Final Score: {quality_assessment.overall_quality_score:.1f}%")
                            print(f"   Returning course with best attempt...")
                        
                        if progress_callback:
                            try:
                                progress_callback(1.0, desc=f"⚠️  Max iterations reached. Quality: {quality_assessment.overall_quality_score:.1f}%")
                            except:
                                pass
                        
                        # Return course even if quality not met
                        metadata = extract_curriculum_metadata(curriculum_markdown)
                        full_markdown = self._combine_markdown_content(
                            curriculum_markdown,
                            instruction_markdown,
                            practice_markdown,
                            quality_assessment.markdown_report
                        )
                        
                        course = CourseCompletion(
                            course_id=f"{course_topic.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                            course_title=metadata['course_title'],
                            full_markdown_content=full_markdown,
                            curriculum_markdown=curriculum_markdown,
                            instruction_markdown=instruction_markdown,
                            practice_markdown=practice_markdown,
                            quality_report_markdown=quality_assessment.markdown_report,
                            quality_assessment=quality_assessment,
                            creation_timestamp=datetime.now().isoformat(),
                            total_iterations=iteration
                        )
                        
                        # Export best-effort PDF
                        try:
                            outputs_dir = os.path.join(os.path.dirname(__file__), "outputs")
                            os.makedirs(outputs_dir, exist_ok=True)
                            pdf_path = os.path.join(outputs_dir, f"{course.course_id}.pdf")
                            export_markdown_to_pdf(full_markdown, pdf_path)
                            print(f"📥 PDF exported to: {pdf_path}")
                        except Exception as e:
                            print(f"⚠️  Failed to export PDF: {e}")
                        
                        return course
                    
                    if verbose:
                        print(f"\n🔄 Retrying: {', '.join(failed_components).upper()}")
                        print(f"   Next iteration will regenerate failed components...")
                        await self._wait_between_steps(progress_callback, f"Iteration {iteration} complete")
            
            except Exception as e:
                if verbose:
                    print(f"❌ QUALITY ASSESSMENT FAILED: {str(e)}")
                raise
    
    def _combine_markdown_content(
        self,
        curriculum: str,
        instruction: str,
        practice: str,
        qa_report: str
    ) -> str:
        """
        Combine all Markdown content into a single document.
        
        Args:
            curriculum: Curriculum markdown
            instruction: Instruction materials markdown
            practice: Practice materials markdown
            qa_report: Quality assessment report markdown
        
        Returns:
            Combined markdown document
        """
        combined = f"""
{curriculum}

---

{instruction}

---

{practice}

---

# QUALITY ASSURANCE REPORT

{qa_report}

---

*Course generated by Intelligent Course Creator*
*Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        return combined
    
    def _determine_failed_components(self, quality_assessment: QualityAssessment) -> list:
        """
        Determine which components failed quality checks.
        
        Args:
            quality_assessment: The quality assessment report
        
        Returns:
            List of component names to retry
        """
        failed_components = []
        
        # If alignment is low, curriculum failed
        if quality_assessment.curriculum_alignment < self.quality_threshold:
            failed_components.append("curriculum")
        
        # If clarity or accuracy is low, instruction failed
        if quality_assessment.clarity_score < self.quality_threshold or \
           quality_assessment.accuracy_score < self.quality_threshold:
            failed_components.append("instruction")
        
        # If completeness is low, practice failed
        if quality_assessment.completeness_score < self.quality_threshold:
            failed_components.append("practice")
        
        # If nothing specific, retry all
        if not failed_components:
            failed_components = ["curriculum", "instruction", "practice"]
        
        return failed_components


# Convenience function for direct use
coordinator = CourseCreationCoordinator()
