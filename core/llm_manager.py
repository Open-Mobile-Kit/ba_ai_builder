"""
LLM Manager for AI Builder
Handles multiple LLM providers (OpenAI, Ollama, Anthropic, Gemini)
"""

import os
from typing import Optional, Dict, Any
from .config_manager import config
from .logger import logger


class LLMManager:
    def __init__(self):
        self.provider = config.llm.provider
        self.model_name = config.llm.model_name
        self.temperature = config.llm.temperature
        self.max_tokens = config.llm.max_tokens
        self._client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the appropriate LLM client based on provider"""
        try:
            if self.provider.lower() == "ollama":
                self._initialize_ollama()
            elif self.provider.lower() == "openai":
                self._initialize_openai()
            elif self.provider.lower() == "anthropic":
                self._initialize_anthropic()
            elif self.provider.lower() == "gemini":
                self._initialize_gemini()
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
        except Exception as e:
            logger.log_error(e, f"Initializing {self.provider} client")
            raise
    
    def _initialize_ollama(self):
        """Initialize Ollama client"""
        try:
            import ollama
            self._client = ollama.Client(host=config.llm.base_url)
            logger.logger.info(f"Initialized Ollama client with model: {self.model_name}")
        except ImportError:
            raise ImportError("ollama package not installed. Run: pip install ollama")
    
    def _initialize_openai(self):
        """Initialize OpenAI client"""
        try:
            import openai
            self._client = openai.OpenAI(api_key=config.llm.api_key)
            logger.logger.info(f"Initialized OpenAI client with model: {self.model_name}")
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")
    
    def _initialize_anthropic(self):
        """Initialize Anthropic client"""
        try:
            import anthropic
            self._client = anthropic.Anthropic(api_key=config.llm.api_key)
            logger.logger.info(f"Initialized Anthropic client with model: {self.model_name}")
        except ImportError:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")
    
    def _initialize_gemini(self):
        """Initialize Google Gemini client"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=config.llm.api_key)
            self._client = genai.GenerativeModel(self.model_name)
            logger.logger.info(f"Initialized Gemini client with model: {self.model_name}")
        except ImportError:
            raise ImportError("google-generativeai package not installed. Run: pip install google-generativeai")
    
    def complete(self, prompt: str, system_prompt: str = "") -> str:
        """
        Generate completion from the configured LLM
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            
        Returns:
            Generated text response
        """
        try:
            if self.provider.lower() == "ollama":
                return self._complete_ollama(prompt, system_prompt)
            elif self.provider.lower() == "openai":
                return self._complete_openai(prompt, system_prompt)
            elif self.provider.lower() == "anthropic":
                return self._complete_anthropic(prompt, system_prompt)
            elif self.provider.lower() == "gemini":
                return self._complete_gemini(prompt, system_prompt)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
        except Exception as e:
            logger.log_error(e, f"LLM completion with {self.provider}")
            raise
    
    def _complete_ollama(self, prompt: str, system_prompt: str = "") -> str:
        """Complete using Ollama"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self._client.chat(
            model=self.model_name,
            messages=messages,
            options={
                "temperature": self.temperature,
                "num_predict": self.max_tokens
            }
        )
        
        result = response['message']['content']
        logger.log_llm_call(self.provider, self.model_name, len(prompt), len(result))
        return result
    
    def _complete_openai(self, prompt: str, system_prompt: str = "") -> str:
        """Complete using OpenAI"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self._client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        result = response.choices[0].message.content
        logger.log_llm_call(self.provider, self.model_name, len(prompt), len(result))
        return result
    
    def _complete_anthropic(self, prompt: str, system_prompt: str = "") -> str:
        """Complete using Anthropic Claude"""
        message_content = prompt
        if system_prompt:
            message_content = f"{system_prompt}\n\n{prompt}"
        
        response = self._client.messages.create(
            model=self.model_name,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            messages=[{"role": "user", "content": message_content}]
        )
        
        result = response.content[0].text
        logger.log_llm_call(self.provider, self.model_name, len(prompt), len(result))
        return result
    
    def _complete_gemini(self, prompt: str, system_prompt: str = "") -> str:
        """Complete using Google Gemini"""
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        
        response = self._client.generate_content(
            full_prompt,
            generation_config={
                "temperature": self.temperature,
                "max_output_tokens": self.max_tokens,
            }
        )
        
        result = response.text
        logger.log_llm_call(self.provider, self.model_name, len(prompt), len(result))
        return result


# Global LLM manager instance
llm_manager = LLMManager()
