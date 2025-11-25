from types import SimpleNamespace
from pathlib import Path
import sys

# Ensure project root is on sys.path for imports
sys.path.append(str(Path(__file__).parent.parent.resolve()))
from tools.pdf_exporter import export_course_to_pdf

# Build minimal dummy course structure expected by exporter
lesson = SimpleNamespace(title='Intro to Python', duration_minutes=30, learning_objectives=[SimpleNamespace(title='Understand syntax')], key_topics=['variables','types'])
module = SimpleNamespace(sequence_order=1, title='Getting Started', description='Intro module', lessons=[lesson])
curriculum = SimpleNamespace(course_title='Python Basics', course_description='A short intro', target_audience='Btech CSE 1st sem', total_duration_hours=1, modules=[module])
inst_section = SimpleNamespace(title='Overview', content='This lesson covers basics')
instruction = SimpleNamespace(lesson_title=lesson.title, overview='Overview text', instruction_sections=[inst_section], lesson_explanation=['ex1'], teaching_strategies=['demo'], engagement_activities=['quiz'])
quality_report = SimpleNamespace(overall_quality_score=80.0, recommendations=['Add more examples'], curriculum_alignment=80.0, completeness_score=80.0, accuracy_score=80.0, clarity_score=80.0, passes_quality_threshold=True, issues=[], recommendations_list=['rec'])
# Note: exporter references quality_report.recommendations; ensure attribute exists
quality_report.recommendations = ['Add examples']

course = SimpleNamespace(course_id='test_python_basics_0001', curriculum=curriculum, instructions=[instruction], practice_sets=[], quality_report=quality_report)

outputs_dir = Path(__file__).parent / '..' / 'outputs'
outputs_dir = outputs_dir.resolve()
outputs_dir.mkdir(parents=True, exist_ok=True)
output_path = outputs_dir / f"{course.course_id}.pdf"

print(f"Exporting PDF to: {output_path}")
export_course_to_pdf(course, str(output_path))
print('Export complete')
