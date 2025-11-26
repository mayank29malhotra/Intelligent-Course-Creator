"""
Simplified Gradio Interface - HF Spaces Compatible
No complex Pydantic models exposed to Gradio - only basic types (str, int, float)
"""

import gradio as gr
import asyncio
import json
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(override=True)

from coordinator_agent import CourseCreationCoordinator
from tools.docx_exporter import export_markdown_to_docx


class SimpleCourseCreatorApp:
    """Simplified app that exposes only basic types to Gradio."""
    
    def __init__(self):
        self.coordinator = None
        self._initialize_coordinator()
    
    def _initialize_coordinator(self):
        """Initialize the coordinator."""
        try:
            quality_threshold = float(os.getenv("QUALITY_THRESHOLD", "75.0"))
            max_iterations = int(os.getenv("MAX_ITERATIONS", "3"))
            
            self.coordinator = CourseCreationCoordinator(
                quality_threshold=quality_threshold,
                max_iterations=max_iterations
            )
            print("✅ Coordinator initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize coordinator: {str(e)}")
            raise
    
    def create_course_sync(
        self,
        topic: str,
        audience: str,
        hours: float,
        quality_threshold: float,
        progress=gr.Progress()
    ):
        """Synchronous wrapper for async course creation.
        
        Returns: tuple of (status_message: str, markdown_content: str, course_title: str)
        All return types are basic Python types - no Pydantic models!
        """
        # Validate inputs
        if not topic or not topic.strip():
            return "❌ Error: Course topic is required", "", ""
        if not audience or not audience.strip():
            return "❌ Error: Target audience is required", "", ""
        
        try:
            hours = float(hours)
            if hours < 0.5 or hours > 5.0:
                return "❌ Error: Course hours must be between 0.5 and 5", "", ""
        except (ValueError, TypeError):
            return "❌ Error: Course hours must be a valid number", "", ""
        
        try:
            quality_threshold = float(quality_threshold)
            if quality_threshold < 50 or quality_threshold > 100:
                return "❌ Error: Quality threshold must be between 50 and 100", "", ""
        except (ValueError, TypeError):
            return "❌ Error: Quality threshold must be a valid number", "", ""
        
        # Run async function in sync context
        try:
            # Update quality threshold
            self.coordinator.quality_threshold = quality_threshold
            
            # Initial progress
            progress(0.0, desc="🚀 Initializing course creation...")
            
            def stage_progress_callback(fraction: float, desc: str = ""):
                if fraction <= 0.1:
                    progress(0.1, desc="📚 [1/4] Curriculum Designer – Creating course structure...")
                elif fraction <= 0.4:
                    progress(0.35, desc="✍️ [2/4] Instruction Designer – Writing teaching materials...")
                elif fraction <= 0.7:
                    progress(0.6, desc="💪 [3/4] Practice Designer – Building exercises & assessments...")
                elif fraction < 1.0:
                    progress(0.85, desc="✅ [4/4] QA Agent – Checking quality & consistency...")
                else:
                    progress(1.0, desc="🎉 Course ready! You can now export the DOCX.")
            
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # Run async course creation
                course = loop.run_until_complete(
                    self.coordinator.create_course(
                        course_topic=topic,
                        target_audience=audience,
                        duration_hours=hours,
                        verbose=True,
                        progress_callback=stage_progress_callback
                    )
                )
            finally:
                loop.close()
            
            # Extract data from Pydantic model and convert to basic types
            course_title = str(course.course_title)
            markdown_content = str(course.full_markdown_content)
            quality_score = float(course.quality_assessment.overall_quality_score)
            total_iterations = int(course.total_iterations)
            course_id = str(course.course_id)
            
            # Create summary message
            summary = f"""
✅ **Course Created Successfully!**

📋 **Course Overview:**
- **Title:** {course_title}
- **Course ID:** {course_id}

📊 **Quality Assessment:**
- **Overall Score:** {quality_score:.1f}% (Threshold: {quality_threshold:.0f}%)
- **Curriculum Alignment:** {course.quality_assessment.curriculum_alignment:.1f}%
- **Completeness:** {course.quality_assessment.completeness_score:.1f}%
- **Accuracy:** {course.quality_assessment.accuracy_score:.1f}%
- **Clarity:** {course.quality_assessment.clarity_score:.1f}%

🔄 **Generation Stats:**
- **Iterations:** {total_iterations}
- **Status:** {'✅ PASSED' if course.quality_assessment.passes_quality_threshold else '⚠️ COMPLETED'}

---

📚 **Course Structure:**
✓ Complete curriculum with modules and lessons
✓ Detailed instruction materials  
✓ Practice exercises and assessments
✓ Quality assurance validation

**All content is ready for DOCX export!**
            """
            
            progress(1.0, desc="🎉 Course generation complete!")
            
            # Return only basic types: (str, str, str)
            return summary, markdown_content, course_title
        
        except Exception as e:
            error_msg = f"""
❌ **Error Creating Course:**

**Error Details:**
```
{type(e).__name__}: {str(e)}
```

**Troubleshooting:**
1. Verify all required fields are filled
2. Check API key is valid
3. Try a simpler course topic
4. Reduce course duration
            """
            return error_msg, "", ""
    
    def export_to_docx_simple(self, markdown_content: str, course_title: str):
        """Export markdown to DOCX.
        
        Returns: tuple of (status_message: str, docx_file_path: str or None)
        """
        if not markdown_content or not markdown_content.strip():
            return "❌ Please generate a course first", None
        
        try:
            outputs_dir = Path("outputs")
            outputs_dir.mkdir(exist_ok=True)
            
            safe_title = "".join(c if c.isalnum() or c in " _-" else "" for c in course_title)
            safe_title = safe_title.lower().replace(" ", "_")[:50] or "course"
            docx_filename = f"{safe_title}.docx"
            docx_path = outputs_dir / docx_filename
            
            final_path = export_markdown_to_docx(markdown_content, str(docx_path))
            
            return f"✅ DOCX ready: {docx_filename}", str(final_path)
        
        except Exception as e:
            return f"❌ Error exporting DOCX: {str(e)}", None
    
    def create_interface(self):
        """Create simplified Gradio interface with only basic types."""
        
        with gr.Blocks(title="Intelligent Course Creator", theme=gr.themes.Soft()) as interface:
            
            # Header
            gr.Markdown("# 🎓 Intelligent Course Creator")
            gr.Markdown("""
            **Create comprehensive, high-quality courses powered by Google Gemini AI.**
            
            Simply provide your course topic, target audience, and duration.
            The system will automatically generate a complete course structure.
            """)
            
            # Main content
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### 📝 Course Configuration")
                    
                    topic_input = gr.Textbox(
                        label="📚 Course Topic",
                        placeholder="e.g., Python Programming for Beginners",
                        lines=1
                    )
                    
                    audience_input = gr.Textbox(
                        label="👥 Target Audience",
                        placeholder="e.g., High school students with no programming experience",
                        lines=1
                    )
                    
                    hours_input = gr.Number(
                        label="⏱️ Course Duration (hours)",
                        value=0.5,
                        minimum=0.5,
                        maximum=5,
                        step=0.5
                    )
                    
                    quality_input = gr.Slider(
                        label="✅ Quality Threshold (%)",
                        minimum=50,
                        maximum=100,
                        value=75,
                        step=5
                    )
                
                with gr.Column(scale=1):
                    gr.Markdown("### 📊 Course Summary")
                    
                    status_output = gr.Textbox(
                        label="Status & Summary",
                        lines=18,
                        interactive=False,
                        show_copy_button=True
                    )
            
            # Buttons
            with gr.Row():
                create_btn = gr.Button("🚀 Create Course", variant="primary", size="lg")
                clear_btn = gr.Button("🔄 Clear All", size="lg")
            
            # Hidden state variables (basic types only!)
            markdown_state = gr.State(value="")
            course_title_state = gr.State(value="")
            
            # Export section
            with gr.Group():
                gr.Markdown("### 📥 Export Course")
                
                with gr.Row():
                    with gr.Column(scale=2):
                        export_status = gr.Textbox(
                            label="Export Status",
                            lines=2,
                            interactive=False
                        )
                    with gr.Column(scale=1):
                        docx_btn = gr.Button("📘 Download DOCX", variant="secondary", size="lg")
                        docx_download = gr.File(label="Download DOCX", visible=False)
            
            # Event handlers - all using basic types only!
            def create_course_handler(topic, audience, hours, quality):
                """Handler that returns only basic types."""
                summary, markdown, title = self.create_course_sync(topic, audience, hours, quality)
                # Show download button only if we have content
                return summary, markdown, title, gr.update(visible=bool(markdown))
            
            create_btn.click(
                fn=create_course_handler,
                inputs=[topic_input, audience_input, hours_input, quality_input],
                outputs=[status_output, markdown_state, course_title_state, docx_btn],
                show_progress=True
            )
            
            def export_handler(markdown, title):
                """Handler for DOCX export."""
                status, path = self.export_to_docx_simple(markdown, title)
                if path:
                    return status, path, gr.update(visible=True, value=path)
                else:
                    return status, None, gr.update(visible=False)
            
            docx_btn.click(
                fn=export_handler,
                inputs=[markdown_state, course_title_state],
                outputs=[export_status, docx_download, docx_download]
            )
            
            def clear_handler():
                """Clear all fields."""
                return "", "", 0.5, 75, "", "", "", "", None, gr.update(visible=False)
            
            clear_btn.click(
                fn=clear_handler,
                outputs=[topic_input, audience_input, hours_input, quality_input,
                        status_output, markdown_state, course_title_state, 
                        export_status, docx_download, docx_btn]
            )
        
        return interface


def main():
    """Main entry point."""
    
    print("\n" + "="*70)
    print("🎓 Intelligent Course Creator")
    print("="*70)
    print("Starting Gradio interface for Hugging Face Spaces...")
    print("="*70 + "\n")
    
    try:
        # Initialize app
        app = SimpleCourseCreatorApp()
        
        # Create interface
        interface = app.create_interface()
        
        # Get configuration
        is_huggingface_space = os.getenv("SPACE_ID") is not None
        
        if is_huggingface_space:
            share = True
            server_name = "0.0.0.0"
            server_port = 7860
            print("🤗 Running in Hugging Face Space environment")
        else:
            share = os.getenv("GRADIO_SHARE", "False").lower() == "true"
            server_name = os.getenv("GRADIO_SERVER_NAME", "127.0.0.1")
            server_port = int(os.getenv("GRADIO_SERVER_PORT", "7860"))
        
        print(f"✅ Server configuration:")
        print(f"   - Address: {server_name}:{server_port}")
        print(f"   - Share: {share}")
        print("\n" + "="*70 + "\n")
        
        # Launch Gradio interface
        interface.launch(
            share=share,
            server_name=server_name,
            server_port=server_port,
            show_error=True,
            show_api=True  # Enable API but Gradio won't parse complex schemas
        )
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Application interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {str(e)}")
        raise


if __name__ == "__main__":
    main()
