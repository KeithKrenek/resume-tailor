"""
Multi-Model Provider Support

Abstracts LLM provider implementations to support multiple models
(Anthropic Claude, OpenAI GPT, Google Gemini, etc.)
"""

import os
from typing import Optional, Dict, Any, List
from enum import Enum
from dataclasses import dataclass
from abc import ABC, abstractmethod
from utils.logging_config import get_logger

logger = get_logger(__name__)


class ModelProvider(Enum):
    """Supported model providers."""
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GOOGLE = "google"


@dataclass
class ModelConfig:
    """Configuration for a specific model."""
    provider: ModelProvider
    model_id: str
    display_name: str
    max_tokens: int
    supports_system_prompt: bool = True
    cost_per_1k_input: float = 0.0  # USD
    cost_per_1k_output: float = 0.0  # USD
    context_window: int = 100000


class AvailableModels:
    """Available model configurations."""

    # Anthropic Claude Models
    CLAUDE_SONNET_4 = ModelConfig(
        provider=ModelProvider.ANTHROPIC,
        model_id="claude-sonnet-4-20250514",
        display_name="Claude Sonnet 4.5 (Recommended)",
        max_tokens=8000,
        cost_per_1k_input=0.003,
        cost_per_1k_output=0.015,
        context_window=200000
    )

    CLAUDE_OPUS_4 = ModelConfig(
        provider=ModelProvider.ANTHROPIC,
        model_id="claude-opus-4-20250514",
        display_name="Claude Opus 4 (Highest Quality)",
        max_tokens=8000,
        cost_per_1k_input=0.015,
        cost_per_1k_output=0.075,
        context_window=200000
    )

    CLAUDE_HAIKU = ModelConfig(
        provider=ModelProvider.ANTHROPIC,
        model_id="claude-3-5-haiku-20241022",
        display_name="Claude Haiku (Fast & Affordable)",
        max_tokens=8000,
        cost_per_1k_input=0.001,
        cost_per_1k_output=0.005,
        context_window=200000
    )

    # OpenAI GPT Models
    GPT_4_TURBO = ModelConfig(
        provider=ModelProvider.OPENAI,
        model_id="gpt-4-turbo-preview",
        display_name="GPT-4 Turbo",
        max_tokens=4096,
        cost_per_1k_input=0.01,
        cost_per_1k_output=0.03,
        context_window=128000
    )

    GPT_4 = ModelConfig(
        provider=ModelProvider.OPENAI,
        model_id="gpt-4",
        display_name="GPT-4",
        max_tokens=8000,
        cost_per_1k_input=0.03,
        cost_per_1k_output=0.06,
        context_window=8192
    )

    GPT_35_TURBO = ModelConfig(
        provider=ModelProvider.OPENAI,
        model_id="gpt-3.5-turbo",
        display_name="GPT-3.5 Turbo (Affordable)",
        max_tokens=4096,
        cost_per_1k_input=0.0005,
        cost_per_1k_output=0.0015,
        context_window=16385
    )

    # Google Gemini Models
    GEMINI_PRO = ModelConfig(
        provider=ModelProvider.GOOGLE,
        model_id="gemini-pro",
        display_name="Gemini Pro",
        max_tokens=8000,
        cost_per_1k_input=0.00025,
        cost_per_1k_output=0.0005,
        context_window=32000
    )

    @classmethod
    def get_all(cls) -> List[ModelConfig]:
        """Get all available models."""
        return [
            cls.CLAUDE_SONNET_4,
            cls.CLAUDE_OPUS_4,
            cls.CLAUDE_HAIKU,
            cls.GPT_4_TURBO,
            cls.GPT_4,
            cls.GPT_35_TURBO,
            cls.GEMINI_PRO
        ]

    @classmethod
    def get_by_id(cls, model_id: str) -> Optional[ModelConfig]:
        """Get model config by ID."""
        for model in cls.get_all():
            if model.model_id == model_id:
                return model
        return None

    @classmethod
    def get_by_provider(cls, provider: ModelProvider) -> List[ModelConfig]:
        """Get all models for a provider."""
        return [m for m in cls.get_all() if m.provider == provider]


class BaseLLMProvider(ABC):
    """Base class for LLM providers."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize provider with API key."""
        self.api_key = api_key
        self.client = None

    @abstractmethod
    def complete(
        self,
        messages: List[Dict[str, str]],
        model_id: str,
        max_tokens: int = 4000,
        temperature: float = 0.5,
        system_prompt: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate a completion.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model_id: Model identifier
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            system_prompt: Optional system prompt

        Returns:
            Generated text or None on error
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available (API key set, library installed)."""
        pass


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude provider."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Anthropic provider."""
        super().__init__(api_key or os.getenv('ANTHROPIC_API_KEY'))

        try:
            from anthropic import Anthropic
            if self.api_key:
                self.client = Anthropic(api_key=self.api_key)
                logger.info("Anthropic provider initialized")
        except ImportError:
            logger.warning("Anthropic library not available")
            self.client = None

    def complete(
        self,
        messages: List[Dict[str, str]],
        model_id: str,
        max_tokens: int = 4000,
        temperature: float = 0.5,
        system_prompt: Optional[str] = None
    ) -> Optional[str]:
        """Generate completion using Claude."""
        if not self.client:
            logger.error("Anthropic client not initialized")
            return None

        try:
            # Anthropic uses 'system' parameter separately
            response = self.client.messages.create(
                model=model_id,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt or "",
                messages=messages
            )

            return response.content[0].text

        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            return None

    def is_available(self) -> bool:
        """Check if Anthropic is available."""
        return self.client is not None


class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT provider."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenAI provider."""
        super().__init__(api_key or os.getenv('OPENAI_API_KEY'))

        try:
            from openai import OpenAI
            if self.api_key:
                self.client = OpenAI(api_key=self.api_key)
                logger.info("OpenAI provider initialized")
        except ImportError:
            logger.warning("OpenAI library not available. Install with: pip install openai")
            self.client = None

    def complete(
        self,
        messages: List[Dict[str, str]],
        model_id: str,
        max_tokens: int = 4000,
        temperature: float = 0.5,
        system_prompt: Optional[str] = None
    ) -> Optional[str]:
        """Generate completion using GPT."""
        if not self.client:
            logger.error("OpenAI client not initialized")
            return None

        try:
            # OpenAI includes system prompt as a message
            all_messages = []

            if system_prompt:
                all_messages.append({
                    "role": "system",
                    "content": system_prompt
                })

            all_messages.extend(messages)

            response = self.client.chat.completions.create(
                model=model_id,
                messages=all_messages,
                max_tokens=max_tokens,
                temperature=temperature
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return None

    def is_available(self) -> bool:
        """Check if OpenAI is available."""
        return self.client is not None


class GoogleProvider(BaseLLMProvider):
    """Google Gemini provider."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Google provider."""
        super().__init__(api_key or os.getenv('GOOGLE_API_KEY'))

        try:
            import google.generativeai as genai
            if self.api_key:
                genai.configure(api_key=self.api_key)
                self.client = genai
                logger.info("Google provider initialized")
        except ImportError:
            logger.warning("Google generativeai library not available. Install with: pip install google-generativeai")
            self.client = None

    def complete(
        self,
        messages: List[Dict[str, str]],
        model_id: str,
        max_tokens: int = 4000,
        temperature: float = 0.5,
        system_prompt: Optional[str] = None
    ) -> Optional[str]:
        """Generate completion using Gemini."""
        if not self.client:
            logger.error("Google client not initialized")
            return None

        try:
            model = self.client.GenerativeModel(model_id)

            # Convert messages to Gemini format
            # Gemini uses a chat format with history
            chat = model.start_chat(history=[])

            # Add system prompt if provided
            full_prompt = ""
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n"

            # Add messages
            for msg in messages:
                if msg['role'] == 'user':
                    full_prompt += msg['content']

            response = chat.send_message(
                full_prompt,
                generation_config={
                    'max_output_tokens': max_tokens,
                    'temperature': temperature
                }
            )

            return response.text

        except Exception as e:
            logger.error(f"Google API error: {e}")
            return None

    def is_available(self) -> bool:
        """Check if Google is available."""
        return self.client is not None


class ModelManager:
    """Manages model providers and provides unified interface."""

    def __init__(self):
        """Initialize model manager with all providers."""
        self.providers = {
            ModelProvider.ANTHROPIC: AnthropicProvider(),
            ModelProvider.OPENAI: OpenAIProvider(),
            ModelProvider.GOOGLE: GoogleProvider()
        }

    def get_provider(self, provider: ModelProvider) -> Optional[BaseLLMProvider]:
        """Get provider instance."""
        return self.providers.get(provider)

    def get_available_providers(self) -> List[ModelProvider]:
        """Get list of available providers."""
        return [
            provider
            for provider, instance in self.providers.items()
            if instance.is_available()
        ]

    def get_available_models(self) -> List[ModelConfig]:
        """Get all available models from available providers."""
        available_providers = self.get_available_providers()
        return [
            model
            for model in AvailableModels.get_all()
            if model.provider in available_providers
        ]

    def complete(
        self,
        messages: List[Dict[str, str]],
        model_config: ModelConfig,
        temperature: float = 0.5,
        system_prompt: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate completion using specified model.

        Args:
            messages: List of message dicts
            model_config: Model configuration to use
            temperature: Sampling temperature
            system_prompt: Optional system prompt

        Returns:
            Generated text or None on error
        """
        provider = self.get_provider(model_config.provider)

        if not provider or not provider.is_available():
            logger.error(f"Provider {model_config.provider.value} not available")
            return None

        return provider.complete(
            messages=messages,
            model_id=model_config.model_id,
            max_tokens=model_config.max_tokens,
            temperature=temperature,
            system_prompt=system_prompt
        )

    def estimate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        model_config: ModelConfig
    ) -> float:
        """
        Estimate cost for a completion.

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            model_config: Model configuration

        Returns:
            Estimated cost in USD
        """
        input_cost = (input_tokens / 1000) * model_config.cost_per_1k_input
        output_cost = (output_tokens / 1000) * model_config.cost_per_1k_output
        return input_cost + output_cost


# Global instance
_model_manager = None


def get_model_manager() -> ModelManager:
    """Get global model manager instance."""
    global _model_manager
    if _model_manager is None:
        _model_manager = ModelManager()
    return _model_manager


def get_available_models() -> List[ModelConfig]:
    """Get all available models."""
    return get_model_manager().get_available_models()


def complete(
    messages: List[Dict[str, str]],
    model_config: ModelConfig,
    temperature: float = 0.5,
    system_prompt: Optional[str] = None
) -> Optional[str]:
    """Generate a completion using specified model."""
    return get_model_manager().complete(
        messages=messages,
        model_config=model_config,
        temperature=temperature,
        system_prompt=system_prompt
    )
