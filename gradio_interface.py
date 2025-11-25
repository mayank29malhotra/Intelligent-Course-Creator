"""Gradio entrypoint for Intelligent Course Creator (Hugging Face friendly).

This module simply reuses the main `CourseCreatorApp` UI defined in `app.py`
so there is a single, professional interface to maintain.
"""
"""Gradio entrypoint for Intelligent Course Creator (Hugging Face friendly).

This module simply reuses the main `CourseCreatorApp` UI defined in `app.py`
so there is a single, professional interface to maintain.
"""

import os
from dotenv import load_dotenv

from app import CourseCreatorApp


# Load environment (Hugging Face Spaces compatible)
load_dotenv(override=True)


def main() -> None:
    """Main entry point when running on Hugging Face or locally."""

    app = CourseCreatorApp()
    interface = app.create_interface()

    share = os.getenv("GRADIO_SHARE", "True").lower() == "true"
    server_name = os.getenv("GRADIO_SERVER_NAME", "0.0.0.0")
    server_port = int(os.getenv("GRADIO_SERVER_PORT", "7860"))

    interface.launch(
        share=share,
        server_name=server_name,
        server_port=server_port,
        show_error=True,
        show_api=False,
    )


if __name__ == "__main__":
    main()
