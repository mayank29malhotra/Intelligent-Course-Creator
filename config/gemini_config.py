"""
Gemini Model Configuration

This module configures the Google Gemini API via OpenAI SDK for use with agents.
Using OpenAI SDK provides better compatibility and structured output handling.
"""

import os
import asyncio
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import Optional

# Load environment variables
load_dotenv(override=True)

# Setup Gemini API via OpenAI SDK
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY or GOOGLE_API_KEY not found in environment variables. "
        "Please set one of these in your .env file."
    )

# Initialize OpenAI client for Gemini
GEMINI_MODEL = "gemini-2.5-flash-lite"
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

def get_gemini_client():
    """Get configured OpenAI client for Gemini."""
    return OpenAI(
        api_key=GEMINI_API_KEY,
        base_url=GEMINI_BASE_URL
    )

async def call_gemini(prompt: str, return_markdown: bool = True) -> str:
    """
    Call Gemini API with given prompt via OpenAI SDK.
    
    Args:
        prompt: The input prompt
        return_markdown: Whether to expect Markdown output (default: True)
    
    Returns:
        Response text from Gemini (as Markdown)
    """
    client = get_gemini_client()
    
    # Add Markdown formatting instructions
    if return_markdown:
        prompt = f"""{prompt}

IMPORTANT: Return your response as well-formatted Markdown.
Use proper headings (##, ###), lists, code blocks, and formatting.
Make it suitable for export to PDF."""
    
    try:
        # Make synchronous call (wrap in executor for async context)
        response = client.chat.completions.create(
            model=GEMINI_MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=8000,
        )
        
        return response.choices[0].message.content
    except Exception as e:
        raise RuntimeError(f"Gemini API error: {str(e)}")

# Simple agent wrapper for Gemini with Markdown output
class GeminiAgent:
    """Wrapper for Gemini-based agents that generate Markdown."""
    
    def __init__(self, name: str, instructions: str):
        """
        Initialize Gemini agent.
        
        Args:
            name: Agent name
            instructions: System instructions for the agent
        """
        self.name = name
        self.instructions = instructions
    
    async def run(self, user_input: str) -> str:
        """
        Run the agent with user input and return Markdown.
        
        Args:
            user_input: User provided input
        
        Returns:
            Agent response as Markdown
        """
        full_prompt = f"""{self.instructions}

User Input:
{user_input}"""
        
        response = await call_gemini(full_prompt, return_markdown=True)
        return response
