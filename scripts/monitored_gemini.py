#!/usr/bin/env python3
"""
Monitored Gemini API Wrapper
Automatically logs ALL Gemini API calls with full transparency.
Drop-in replacement for direct Gemini usage.
"""

import os
import sys
from typing import Optional, Dict, Any, List

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.ai_transparency_logger import get_logger


class MonitoredGeminiAPI:
    """
    Wrapper around Google Gemini API that logs all interactions.

    Usage:
        # Instead of:
        from google.generativeai import GenerativeModel

        # Use:
        from scripts.monitored_gemini import MonitoredGeminiAPI
        model = MonitoredGeminiAPI(model_name="gemini-2.5-flash")
    """

    def __init__(self, model_name: str = "gemini-2.5-flash", api_key: Optional[str] = None):
        """
        Initialize monitored Gemini client.

        Args:
            model_name: Gemini model name
            api_key: API key (will use GEMINI_API_KEY env var if not provided)
        """
        self.model_name = model_name
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("API_KEY")
        self.logger = get_logger()

        if not self.api_key:
            print("⚠️  WARNING: No Gemini API key found. Set GEMINI_API_KEY env var.")

        # Import actual Gemini SDK
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(model_name)
            self.genai = genai
            print(f"✅ Monitored Gemini API initialized: {model_name}")
        except ImportError:
            print("❌ google-generativeai not installed. Run: pip install google-generativeai")
            self.model = None
            self.genai = None

    def generate_content(
        self,
        prompt: str,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Any:
        """
        Generate content and log the interaction.

        Args:
            prompt: Text prompt
            metadata: Additional context to log
            **kwargs: Passed to underlying API

        Returns:
            Response object from Gemini
        """
        if not self.model:
            raise RuntimeError("Gemini model not initialized")

        # Make actual API call
        response = self.model.generate_content(prompt, **kwargs)

        # Extract text response
        response_text = response.text if hasattr(response, 'text') else str(response)

        # Get token counts if available
        input_tokens = None
        output_tokens = None

        if hasattr(response, 'usage_metadata'):
            usage = response.usage_metadata
            input_tokens = getattr(usage, 'prompt_token_count', None)
            output_tokens = getattr(usage, 'candidates_token_count', None)

        # Log the interaction
        self.logger.log_interaction(
            model=self.model_name,
            provider="google",
            prompt=prompt,
            response=response_text,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            metadata=metadata or {}
        )

        return response

    def send_message(
        self,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Send a message in chat context.

        Args:
            message: Message text
            metadata: Additional context

        Returns:
            Response text
        """
        response = self.generate_content(message, metadata=metadata)
        return response.text

    def analyze_video(
        self,
        video_url: str,
        prompt: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Analyze a video with Gemini.

        Args:
            video_url: URL to video
            prompt: Analysis prompt
            metadata: Additional context

        Returns:
            Analysis result
        """
        full_prompt = f"Video: {video_url}\n\n{prompt}"
        response = self.generate_content(full_prompt, metadata=metadata or {})
        return response.text

    def analyze_image(
        self,
        image_data: bytes,
        prompt: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Analyze an image with Gemini.

        Args:
            image_data: Image bytes
            prompt: Analysis prompt
            metadata: Additional context

        Returns:
            Analysis result
        """
        # This would use Gemini's vision capabilities
        # For now, logging the attempt
        self.logger.log_interaction(
            model=self.model_name,
            provider="google",
            prompt=f"[IMAGE ANALYSIS] {prompt}",
            response="[Image analysis - implementation needed]",
            metadata={**(metadata or {}), "type": "image_analysis"}
        )
        return "[Image analysis placeholder]"


class MonitoredClaudeAPI:
    """
    Wrapper for Claude API (when used via SDK, not this interface).
    For logging purposes.
    """

    def __init__(self, model_name: str = "claude-sonnet-4-5", api_key: Optional[str] = None):
        self.model_name = model_name
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.logger = get_logger()

        if not self.api_key:
            print("⚠️  WARNING: No Claude API key found. Set ANTHROPIC_API_KEY env var.")

        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=self.api_key)
            print(f"✅ Monitored Claude API initialized: {model_name}")
        except ImportError:
            print("❌ anthropic not installed. Run: pip install anthropic")
            self.client = None

    def send_message(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Send message and log."""
        if not self.client:
            raise RuntimeError("Claude client not initialized")

        full_prompt = f"{system_prompt}\n\n{message}" if system_prompt else message

        response = self.client.messages.create(
            model=self.model_name,
            max_tokens=4096,
            messages=[{"role": "user", "content": message}],
            system=system_prompt or ""
        )

        response_text = response.content[0].text

        # Log interaction
        self.logger.log_interaction(
            model=self.model_name,
            provider="anthropic",
            prompt=full_prompt,
            response=response_text,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            metadata=metadata or {}
        )

        return response_text


# Convenience function for quick logging without class instantiation
def log_manual_ai_call(
    model: str,
    provider: str,
    prompt: str,
    response: str,
    cost: float = 0.0,
    metadata: Optional[Dict] = None
):
    """
    Manually log an AI call (for non-SDK usage, like web UI calls).

    Example:
        log_manual_ai_call(
            model="gemini-2.5-flash",
            provider="google",
            prompt="User asked about video",
            response="I analyzed the video...",
            metadata={"source": "web_ui", "user": "michael"}
        )
    """
    logger = get_logger()
    logger.log_interaction(
        model=model,
        provider=provider,
        prompt=prompt,
        response=response,
        metadata=metadata or {}
    )


if __name__ == "__main__":
    # Demo
    print("=== Monitored Gemini API Demo ===\n")

    # Example: Using monitored Gemini
    gemini = MonitoredGeminiAPI(model_name="gemini-2.5-flash")

    response = gemini.send_message(
        "What is the capital of France?",
        metadata={"test": "demo", "user": "system"}
    )

    print(f"Response: {response}\n")

    # Show dashboard
    from scripts.ai_dashboard import print_dashboard
    print_dashboard()
