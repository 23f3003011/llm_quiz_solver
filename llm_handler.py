"""
FILE: llm_handler.py
Integration with LLM APIs (OpenAI, Anthropic)
"""

import os
import json
import logging
import sys

logger = logging.getLogger(__name__)


class LLMHandler:
    def __init__(self):
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        self.model = os.getenv('LLM_MODEL', 'gpt-4-turbo')
        self.client = None
        self.provider = None
        
        # Try OpenAI first
        if self.openai_key:
            try:
                # Uninstall old version and use requests directly
                import requests
                self.client = self._create_openai_client()
                self.provider = 'openai'
                logger.info("✅ OpenAI client initialized successfully")
            except Exception as e:
                logger.warning(f"❌ OpenAI initialization failed: {str(e)}")
                self.client = None
        
        # Fallback to Anthropic
        if not self.client and self.anthropic_key:
            try:
                self.client = self._create_anthropic_client()
                self.provider = 'anthropic'
                logger.info("✅ Anthropic client initialized successfully")
            except Exception as e:
                logger.warning(f"❌ Anthropic initialization failed: {str(e)}")
                self.client = None
        
        if not self.client:
            logger.error("❌ No LLM client could be initialized - check API keys in .env")
    
    def _create_openai_client(self):
        """Create OpenAI client with minimal parameters"""
        try:
            # Try importing the library first
            import importlib.util
            spec = importlib.util.find_spec("openai")
            if spec is None:
                raise ImportError("openai not installed")
            
            from openai import OpenAI
            # Create client with ONLY required parameters
            client = OpenAI(api_key=self.openai_key)
            return client
        except Exception as e:
            logger.error(f"Failed to create OpenAI client: {str(e)}")
            raise
    
    def _create_anthropic_client(self):
        """Create Anthropic client with minimal parameters"""
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=self.anthropic_key)
            return client
        except Exception as e:
            logger.error(f"Failed to create Anthropic client: {str(e)}")
            raise
    
    def plan_solution(self, question):
        """Ask LLM to plan the solution approach"""
        if not self.client:
            logger.error("No LLM client available")
            return {'steps': ['Unable to plan - no LLM']}
        
        prompt = f"""You are a data analysis expert. Given this quiz question, create a step-by-step plan.

Question: {question}

Respond with ONLY valid JSON (no markdown, no extra text):
{{
  "steps": ["step 1", "step 2", ...],
  "data_sources": "where to get data",
  "processing": "how to process",
  "expected_answer_type": "number/string/boolean/json"
}}"""
        
        try:
            if self.provider == 'openai':
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{'role': 'user', 'content': prompt}],
                    temperature=0.5
                )
                response_text = response.choices[0].message.content
                return json.loads(response_text)
            
            elif self.provider == 'anthropic':
                response = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    messages=[{'role': 'user', 'content': prompt}]
                )
                response_text = response.content[0].text
                return json.loads(response_text)
            else:
                return {'steps': ['No provider']}
        
        except json.JSONDecodeError as e:
            logger.warning(f"JSON decode error: {str(e)}")
            return {'steps': ['Generic approach']}
        except Exception as e:
            logger.error(f"Error in plan_solution: {str(e)}")
            return {'steps': ['Error in planning']}
    
    def solve_generic(self, question):
        """Use LLM for generic problem solving"""
        if not self.client:
            logger.error("No LLM client available")
            return "Error: No LLM available"
        
        prompt = f"""Answer this quiz question with ONLY the answer, no explanation or extra text.

Question: {question}

Answer:"""
        
        try:
            if self.provider == 'openai':
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{'role': 'user', 'content': prompt}],
                    temperature=0
                )
                answer = response.choices[0].message.content.strip()
            
            elif self.provider == 'anthropic':
                response = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=500,
                    messages=[{'role': 'user', 'content': prompt}]
                )
                answer = response.content[0].text.strip()
            else:
                answer = "No provider"
            
            # Try to parse as number
            try:
                if '.' in str(answer):
                    return float(answer)
                else:
                    return int(answer)
            except (ValueError, AttributeError):
                return answer
        
        except Exception as e:
            logger.error(f"Error in solve_generic: {str(e)}")
            return f"Error: {str(e)}"
    
    def analyze_data(self, data, instruction):
        """Ask LLM to analyze data"""
        if not self.client:
            logger.error("No LLM client available")
            return "Error: No LLM available"
        
        prompt = f"""Analyze this data and complete the task.

Data: {json.dumps(data)[:1000]}

Task: {instruction}

Provide only the answer."""
        
        try:
            if self.provider == 'openai':
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{'role': 'user', 'content': prompt}]
                )
                return response.choices[0].message.content.strip()
            
            elif self.provider == 'anthropic':
                response = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    messages=[{'role': 'user', 'content': prompt}]
                )
                return response.content[0].text.strip()
            
            else:
                return "No provider"
        
        except Exception as e:
            logger.error(f"Error in analyze_data: {str(e)}")
            return f"Error: {str(e)}"
