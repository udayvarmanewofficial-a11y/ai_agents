"""
API endpoints for fetching available LLM models dynamically.
"""

from typing import Dict, List

import google.generativeai as genai
import openai
from app.core.config import settings
from app.core.logging import app_logger
from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/models/available")
async def get_available_models() -> Dict[str, List[Dict[str, str]]]:
    """
    Fetch available models from both OpenAI and Gemini APIs.
    Returns a dictionary with provider names as keys and model lists as values.
    """
    models = {
        "openai": [],
        "gemini": []
    }
    
    # Fetch OpenAI models
    if settings.openai_api_key:
        try:
            client = openai.OpenAI(api_key=settings.openai_api_key)
            openai_models = client.models.list()
            
            # Filter for chat/completion models only
            chat_models = [
                {
                    "id": model.id,
                    "name": model.id,
                    "provider": "openai",
                    "description": f"OpenAI {model.id}"
                }
                for model in openai_models.data
                if any(prefix in model.id for prefix in ["gpt-4", "gpt-3.5", "gpt-4o"])
            ]
            
            # Sort by name, prioritize latest models
            chat_models.sort(key=lambda x: (
                "gpt-4o" not in x["id"],
                "turbo" not in x["id"],
                x["id"]
            ))
            
            models["openai"] = chat_models[:10]  # Limit to top 10 relevant models
            app_logger.info(f"Fetched {len(models['openai'])} OpenAI models")
            
        except Exception as e:
            app_logger.error(f"Error fetching OpenAI models: {e}")
            # Fallback to default models
            models["openai"] = [
                {
                    "id": "gpt-4o-mini",
                    "name": "GPT-4o Mini",
                    "provider": "openai",
                    "description": "Fast and affordable model"
                },
                {
                    "id": "gpt-4o",
                    "name": "GPT-4o",
                    "provider": "openai",
                    "description": "Most capable model"
                },
                {
                    "id": "gpt-4-turbo",
                    "name": "GPT-4 Turbo",
                    "provider": "openai",
                    "description": "High performance"
                },
                {
                    "id": "gpt-3.5-turbo",
                    "name": "GPT-3.5 Turbo",
                    "provider": "openai",
                    "description": "Cost-effective option"
                }
            ]
    
    # Fetch Gemini models
    if settings.google_api_key:
        try:
            genai.configure(api_key=settings.google_api_key)
            gemini_models = genai.list_models()
            
            # Filter for generative models
            generative_models = [
                {
                    "id": model.name.split('/')[-1],
                    "name": model.display_name if hasattr(model, 'display_name') else model.name.split('/')[-1],
                    "provider": "gemini",
                    "description": model.description if hasattr(model, 'description') else f"Google Gemini {model.name.split('/')[-1]}"
                }
                for model in gemini_models
                if 'generateContent' in (model.supported_generation_methods if hasattr(model, 'supported_generation_methods') else [])
            ]
            
            # Sort by name, prioritize latest models
            generative_models.sort(key=lambda x: (
                "2.5" not in x["id"],
                "2.0" not in x["id"],
                "flash" not in x["id"],
                "exp" not in x["id"],
                x["id"]
            ), reverse=True)
            
            models["gemini"] = generative_models[:10]  # Limit to top 10
            app_logger.info(f"Fetched {len(models['gemini'])} Gemini models")
            
        except Exception as e:
            app_logger.error(f"Error fetching Gemini models: {e}")
            # Fallback to default models
            models["gemini"] = [
                {
                    "id": "gemini-2.5-pro",
                    "name": "Gemini 2.5 Pro",
                    "provider": "gemini",
                    "description": "Most capable model"
                },
                {
                    "id": "gemini-2.5-flash",
                    "name": "Gemini 2.5 Flash",
                    "provider": "gemini",
                    "description": "Fast and efficient"
                }
            ]
    
    return models


@router.get("/models/default")
async def get_default_model() -> Dict[str, str]:
    """
    Get the default LLM provider and model from configuration.
    """
    provider = settings.default_llm_provider
    
    if provider == "openai":
        model = settings.openai_model
    elif provider == "gemini":
        model = settings.gemini_model
    else:
        raise HTTPException(status_code=400, detail=f"Invalid provider: {provider}")
    
    return {
        "provider": provider,
        "model": model,
        "temperature": settings.openai_temperature if provider == "openai" else settings.gemini_temperature,
        "max_tokens": settings.openai_max_tokens if provider == "openai" else settings.gemini_max_tokens
    }


@router.get("/models/recommended")
async def get_recommended_models() -> List[Dict[str, str]]:
    """
    Get recommended models for planning tasks.
    These are curated based on performance, cost, and capability.
    """
    return [
        {
            "id": "gemini-2.5-flash",
            "name": "Gemini 2.5 Flash (Recommended)",
            "provider": "gemini",
            "description": "Latest model with excellent reasoning and planning capabilities",
            "recommended": True,
            "best_for": "Complex planning, detailed schedules"
        },
        {
            "id": "gpt-4o-mini",
            "name": "GPT-4o Mini",
            "provider": "openai",
            "description": "Fast, cost-effective, great for most planning tasks",
            "recommended": True,
            "best_for": "Quick plans, general use"
        },
        {
            "id": "gemini-2.5-pro",
            "name": "Gemini 2.5 Pro",
            "provider": "gemini",
            "description": "High capability for complex, long-term planning",
            "recommended": False,
            "best_for": "Comprehensive research, detailed analysis"
        },
        {
            "id": "gpt-4o",
            "name": "GPT-4o",
            "provider": "openai",
            "description": "Most capable OpenAI model",
            "recommended": False,
            "best_for": "Maximum quality, critical planning"
        }
    ]
