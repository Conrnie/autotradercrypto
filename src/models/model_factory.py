"""
Model Factory - DeepSeek Only

This module manages DeepSeek AI models only.
"""

import os
from typing import Optional
from termcolor import cprint
from dotenv import load_dotenv
from pathlib import Path
from .base_model import BaseModel
from .deepseek_model import DeepSeekModel

class ModelFactory:
    """Factory for creating and managing DeepSeek AI models"""

    # Only DeepSeek is supported
    MODEL_IMPLEMENTATIONS = {
        "deepseek": DeepSeekModel,
    }

    # Default DeepSeek model
    DEFAULT_MODELS = {
        "deepseek": "deepseek-reasoner",     # Enhanced reasoning model
    }
    
    def __init__(self):
        cprint("\n🏗️ Creating new ModelFactory instance (DeepSeek only)...", "cyan")

        # Load environment variables first
        project_root = Path(__file__).parent.parent.parent
        env_path = project_root / '.env'
        cprint(f"\n🔍 Loading environment from: {env_path}", "cyan")
        load_dotenv(dotenv_path=env_path)
        cprint("✨ Environment loaded", "green")

        self._model: Optional[BaseModel] = None
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize DeepSeek model"""
        cprint("\n🏭 Model Factory Initialization (DeepSeek Only)", "cyan")
        cprint("═" * 50, "cyan")

        # Check for DeepSeek API key
        api_key = os.getenv("DEEPSEEK_KEY")

        if not api_key:
            cprint("\n❌ DEEPSEEK_KEY not found in environment!", "red")
            cprint("  └─ Add DEEPSEEK_KEY to your .env file", "yellow")
            return

        cprint(f"\n✅ Found DEEPSEEK_KEY ({len(api_key)} chars)", "green")

        # Initialize DeepSeek model
        try:
            cprint("\n🔄 Initializing DeepSeek model...", "cyan")
            model_name = self.DEFAULT_MODELS["deepseek"]
            cprint(f"  ├─ Model: {model_name}", "cyan")

            self._model = DeepSeekModel(api_key, model_name=model_name)

            if self._model.is_available():
                cprint(f"  └─ ✨ Successfully initialized DeepSeek!", "green")
            else:
                cprint(f"  └─ ⚠️ DeepSeek model created but not available", "yellow")
                self._model = None

        except Exception as e:
            cprint(f"\n❌ Failed to initialize DeepSeek model", "red")
            cprint(f"  ├─ Error: {str(e)}", "red")
            import traceback
            cprint(f"  └─ Traceback:\n{traceback.format_exc()}", "red")
            self._model = None

        cprint("\n" + "═" * 50, "cyan")
        if self._model:
            cprint("🤖 DeepSeek AI Model Ready!", "green")
        else:
            cprint("⚠️ DeepSeek not available - check your API key", "yellow")
    
    def get_model(self, model_type: str = "deepseek", model_name: Optional[str] = None) -> Optional[BaseModel]:
        """Get DeepSeek model instance"""
        if model_type != "deepseek":
            cprint(f"⚠️ Only DeepSeek is supported. Returning DeepSeek model.", "yellow")

        if not self._model:
            cprint(f"❌ DeepSeek model not available - check DEEPSEEK_KEY in .env", "red")
            return None

        # If specific model name requested, reinitialize
        if model_name and self._model.model_name != model_name:
            cprint(f"🔄 Reinitializing DeepSeek with model {model_name}...", "cyan")
            try:
                api_key = os.getenv("DEEPSEEK_KEY")
                if not api_key:
                    cprint(f"❌ DEEPSEEK_KEY not found", "red")
                    return None

                self._model = DeepSeekModel(api_key, model_name=model_name)
                cprint(f"✨ Successfully reinitialized with {model_name}", "green")
            except Exception as e:
                cprint(f"❌ Failed to reinitialize DeepSeek with {model_name}", "red")
                cprint(f"  └─ Error: {str(e)}", "red")
                return None

        return self._model
    
    def is_model_available(self, model_type: str = "deepseek") -> bool:
        """Check if DeepSeek model is available"""
        return self._model is not None and self._model.is_available()

# Create a singleton instance
model_factory = ModelFactory() 