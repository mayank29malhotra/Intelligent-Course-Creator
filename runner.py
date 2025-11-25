"""
Main runner script for the Intelligent Course Creator

This script launches the Gradio web interface for the Intelligent Course Creator.
The application is optimized for Hugging Face Spaces deployment.

Usage:
    python runner.py
"""

import argparse
import asyncio
import os
from app import main, CourseCreatorApp
from coordinator_agent import CourseCreationCoordinator


def cli_create(args):
    """Create a course via CLI using CourseCreationCoordinator."""
    coordinator = CourseCreationCoordinator(
        quality_threshold=args.quality,
        max_iterations=args.max_iterations
    )

    async def _run():
        course = await coordinator.create_course(
            course_topic=args.topic,
            target_audience=args.audience,
            duration_hours=int(args.hours),
            verbose=not args.no_verbose
        )
        # Save output JSON if provided
        out = args.output or f"course_{args.topic.lower().replace(' ', '_')}.json"
        try:
            with open(out, 'w', encoding='utf-8') as f:
                f.write(course.model_dump_json(indent=2))
            print(f"Saved course to {out}")
        except Exception as e:
            print(f"Failed to save course JSON: {e}")

    asyncio.run(_run())


def parse_args():
    p = argparse.ArgumentParser(description="Intelligent Course Creator Runner")
    p.add_argument('--web', action='store_true', help='Launch Gradio web interface')
    p.add_argument('--topic', type=str, help='Course topic (CLI mode)')
    p.add_argument('--audience', type=str, help='Target audience (CLI mode)')
    p.add_argument('--hours', type=int, help='Course duration hours (CLI mode)')
    p.add_argument('--quality', type=float, default=75.0, help='Quality threshold (CLI mode)')
    p.add_argument('--max-iterations', type=int, default=3, help='Max refinement iterations')
    p.add_argument('--output', type=str, help='Output JSON file path')
    p.add_argument('--no-verbose', action='store_true', help='Disable verbose output')
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.web:
        # Launch the Gradio app
        main()
    else:
        # Validate required CLI args
        if not (args.topic and args.audience and args.hours):
            print("Error: For CLI mode provide --topic, --audience and --hours, or use --web for the UI.")
            exit(1)

        cli_create(args)

