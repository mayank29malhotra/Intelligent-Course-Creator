"""
Simplified Gradio Interface - HF Spaces Compatible
No complex Pydantic models exposed to Gradio - only basic types (str, int, float)
"""

import gradio as gr
import asyncio
import json
import os
"""
This file is intentionally not used. The main UI is `app.py`.
Keeping this file minimal to avoid duplicate entry points.
"""

print("Note: Use app.py as the main UI entry point.")
from coordinator_agent import CourseCreationCoordinator
