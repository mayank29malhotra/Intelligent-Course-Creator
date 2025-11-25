"""
Intelligent Course Creator - Hugging Face Spaces App

Main entry point for the Intelligent Course Creator running on Hugging Face Spaces.
Uses Google Gemini API for course generation with Gradio web interface.

Environment Variables:
    GEMINI_API_KEY: Google Gemini API key (required)
    GOOGLE_API_KEY: Alternative to GEMINI_API_KEY
    GRADIO_SHARE: Whether to share the link (default: False)
    QUALITY_THRESHOLD: Default quality threshold (default: 75.0)
    MAX_ITERATIONS: Maximum refinement iterations (default: 3)
"""

"""Patched app for Hugging Face Spaces - Option B (HuggingFace-Safe Fix)
* Forces share=True on Spaces
* Forces server_name=0.0.0.0
* Removes deprecated / unsupported launch args
* Tries to minimize Gradio API schema exposure by disabling show_api and using share mode
"""

import asyncio
import gradio as gr
import json
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(override=True)

os.environ.setdefault("GRADIO_SERVER_NAME", "0.0.0.0")
os.environ.setdefault("GRADIO_SHARE", "True")
os.environ.setdefault("GRADIO_SHOW_API", "False")

from coordinator_agent import CourseCreationCoordinator
from models import CourseCompletion
from tools.docx_exporter import export_markdown_to_docx
from datetime import datetime

class CourseCreatorApp:
    def __init__(self):
        self.coordinator = None
        self._initialize_coordinator()

    def _initialize_coordinator(self):
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

    def export_to_pdf(self, markdown_content: str, course_title: str) -> tuple[str, str]:
        return "❌ PDF export is no longer supported. Use DOCX export instead.", None

    def export_to_docx(self, markdown_content: str, course_title: str) -> tuple[str, str]:
        if not markdown_content or not markdown_content.strip():
            return "❌ No course content to export", None
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

    async def create_course(
        self,
        topic: str,
        audience: str,
        hours: int,
        quality_threshold: float,
        progress=gr.Progress()
    ) -> tuple[str, str]:
        if not topic or not topic.strip():
            return "❌ Error: Course topic is required", ""
        if not audience or not audience.strip():
            return "❌ Error: Target audience is required", ""
        if hours is None:
            return "❌ Error: Course duration is required", ""
        try:
            hours = float(hours)
            if hours < 0.5 or hours > 5.0:
                return "❌ Error: Course hours must be between 0.5 and 5", ""
        except (ValueError, TypeError):
            return "❌ Error: Course hours must be a valid number", ""
        if quality_threshold is None:
            quality_threshold = 75.0
        try:
            quality_threshold = float(quality_threshold)
            if quality_threshold < 50 or quality_threshold > 100:
                return "❌ Error: Quality threshold must be between 50 and 100", ""
        except (ValueError, TypeError):
            return "❌ Error: Quality threshold must be a valid number", ""

        try:
            self.coordinator.quality_threshold = quality_threshold
            progress(0.0, desc="🚀 Initializing course creation (0/4)...")

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

            course = await self.coordinator.create_course(
                course_topic=topic,
                target_audience=audience,
                duration_hours=hours,
                verbose=True,
                progress_callback=stage_progress_callback
            )

            course_data = {
                "course_id": course.course_id,
                "course_title": course.course_title,
                "total_iterations": course.total_iterations,
                "quality_score": course.quality_assessment.overall_quality_score,
                "creation_timestamp": course.creation_timestamp
            }
            course_json = json.dumps(course_data, indent=2)

            safe_topic = "".join(c if c.isalnum() or c in " _-" else "" for c in topic)
            safe_topic = safe_topic.lower().replace(" ", "_")[:50]
            md_output_file = f"course_{safe_topic}.md"

            try:
                md_output_path = Path(md_output_file)
                md_output_path.write_text(course.full_markdown_content)
                saved_msg = f"📁 Saved to: `{md_output_file}`"
            except Exception as e:
                saved_msg = f"⚠️ Could not save file: {str(e)}"

            summary = (
                "\n✅ **Course Created Successfully!**\n\n"
                "📋 **Course Overview:**\n"
                f"- **Title:** {course.course_title}\n"
                f"- **Course ID:** {course.course_id}\n\n"
                "📊 **Quality Assessment:**\n"
                f"- **Overall Score:** {course.quality_assessment.overall_quality_score:.1f}% \n  (Threshold: {quality_threshold:.0f}%)\n"
                f"- **Curriculum Alignment:** {course.quality_assessment.curriculum_alignment:.1f}%\n"
                f"- **Completeness:** {course.quality_assessment.completeness_score:.1f}%\n"
                f"- **Accuracy:** {course.quality_assessment.accuracy_score:.1f}%\n"
                f"- **Clarity:** {course.quality_assessment.clarity_score:.1f}%\n\n"
                "🔄 **Generation Stats:**\n"
                f"- **Iterations:** {course.total_iterations}\n"
                f"- **Status:** {'✅ PASSED' if course.quality_assessment.passes_quality_threshold else '⚠️ COMPLETED (Quality below threshold)'}\n\n"
                f"{saved_msg}\n\n---\n\n📚 **Course Structure:**\n"
                "✓ Complete curriculum with modules and lessons\n"
                "✓ Detailed instruction materials  \n"
                "✓ Practice exercises and assessments\n"
                "✓ Quality assurance validation\n"
            )

            progress(1.0, desc="🎉 Course generation complete (4/4). Ready to export DOCX.")

            return summary, course.full_markdown_content

        except Exception as e:
            error_msg = (
                "\n❌ **Error Creating Course:**\n\n"
                "**Troubleshooting:**\n"
                "1. Verify all required fields are filled\n"
                "2. Check API key is valid\n"
                "3. Try a simpler course topic\n"
                "4. Reduce course duration\n"
            )
            return error_msg, ""

    def create_interface(self) -> gr.Blocks:
        with gr.Blocks(title="Intelligent Course Creator", theme=gr.themes.Soft(), css=""" .header-text { text-align: center; margin: 20px 0; } """) as interface:
            gr.Markdown("# 🎓 Intelligent Course Creator")
            gr.Markdown("""
**Create comprehensive, high-quality courses powered by Google Gemini AI.**

Simply provide your course topic, target audience, and duration. 
The system will automatically generate a complete course structure with curriculum, 
instruction materials, practice exercises, and quality validation.
""")

            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### 📝 Course Configuration")
                    topic_input = gr.Textbox(label="📚 Course Topic", placeholder="e.g., Python Programming for Beginners", lines=1, info="What is the main subject of your course?", scale=1)
                    audience_input = gr.Textbox(label="👥 Target Audience", placeholder="e.g., High school students with no programming experience", lines=1, info="Who is this course designed for?", scale=1)
                    hours_input = gr.Number(label="⏱️ Course Duration (hours)", value=0.5, minimum=0.5, maximum=5, step=0.5, info="Total hours available for the complete course (1-5)", scale=1)
                    quality_input = gr.Slider(label="✅ Quality Threshold (%)", minimum=50, maximum=100, value=75, step=5, info="Minimum acceptable quality score (75% = good balance, 85%+ = very strict)", scale=1)
                with gr.Column(scale=1):
                    gr.Markdown("### 📊 Course Summary")
                    gr.Markdown("_Course creation runs through 4 stages (Curriculum, Instruction, Practice, QA)._  This may take some minutes depending on topic complexity.")
                    status_output = gr.Textbox(label="Status & Summary", lines=18, interactive=False, show_copy_button=True, scale=1)

            with gr.Row():
                with gr.Column(scale=1):
                    create_btn = gr.Button("🚀 Create Course", variant="primary", size="lg")
                with gr.Column(scale=1):
                    clear_btn = gr.Button("🔄 Clear All", size="lg")

            with gr.Group():
                gr.Markdown("### 📥 Export Course")
                markdown_output = gr.State(value="")
                with gr.Row():
                    with gr.Column(scale=2):
                        export_status = gr.Textbox(label="Export Status", lines=2, interactive=False, placeholder="Waiting for course generation to finish (4/4)...", show_label=True)
                    with gr.Column(scale=1):
                        docx_btn = gr.Button("📘 Download DOCX", variant="secondary", size="lg", visible=False)
                        docx_download = gr.File(label="Download DOCX", visible=False)

            course_title_state = gr.State(value="")

            async def create_course_wrapper(topic, audience, hours, quality):
                status, markdown = await self.create_course(topic, audience, hours, quality)
                title = topic or "course"
                docx_btn_update = gr.update(visible=bool(markdown and markdown.strip()))
                return status, markdown, title, docx_btn_update

            create_btn.click(fn=create_course_wrapper, inputs=[topic_input, audience_input, hours_input, quality_input], outputs=[status_output, markdown_output, course_title_state, docx_btn], show_progress=True)

            def export_docx_wrapper(markdown_content, course_title):
                if not markdown_content:
                    return "❌ Please generate a course first", None, gr.update(visible=False)
                status, docx_path = self.export_to_docx(markdown_content, course_title or "course")
                if docx_path:
                    return status, docx_path, gr.update(visible=True, value=docx_path)
                else:
                    return status, None, gr.update(visible=False)

            docx_btn.click(fn=export_docx_wrapper, inputs=[markdown_output, course_title_state], outputs=[export_status, docx_download, docx_download])

            def clear_all():
                return "", "", 5, 75, "", "", "", "", gr.update(visible=False), gr.update(visible=False)

            clear_btn.click(fn=clear_all, outputs=[topic_input, audience_input, hours_input, quality_input, status_output, markdown_output, course_title_state, export_status, docx_download, docx_btn])

        return interface

def main():
    print("\n" + "="*70)
    print("🎓 Intelligent Course Creator (Patched - Spaces-safe)")
    print("="*70)
    print("Starting Gradio interface for Hugging Face Spaces...\n")
    try:
        app = CourseCreatorApp()
        interface = app.create_interface()

        share_env = os.getenv("GRADIO_SHARE", "True").lower() == "true"
        server_name = os.getenv("GRADIO_SERVER_NAME", "0.0.0.0")
        server_port = int(os.getenv("GRADIO_SERVER_PORT", "7860"))

        print("✅ Server configuration:")
        print("   - Address: {}:{}".format(server_name, server_port))
        print("   - Share: {}".format(share_env))
        print("   - Quality Threshold: {}%".format(os.getenv('QUALITY_THRESHOLD', '75.0')))
        print("   - Max Iterations: {}".format(os.getenv('MAX_ITERATIONS', '3')))
        print("\n" + "="*70 + "\n")

        interface.launch(
            share=True,
            server_name=server_name,
            server_port=server_port,
            show_error=True,
            show_api=False,
            inbrowser=False,
        )

    except KeyboardInterrupt:
        print("\n\n⚠️ Application interrupted by user")
    except Exception as e:
        print("\n\n❌ Fatal error: {}".format(str(e)))
        raise

if __name__ == "__main__":
    main()
