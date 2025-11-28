"""
FILE: llm_handler.py
Integration with LLM APIs (OpenAI, Anthropic)
"""

import os
import json
import logging

logger = logging.getLogger(__name__)


class LLMHandler:
    def __init__(self):
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        self.model = os.getenv('LLM_MODEL', 'gpt-4-turbo')
        self.client = None
        self.provider = None
        
        if self.openai_key:
            try:
                from openai import OpenAI
                # Initialize without proxies to avoid compatibility issues
                self.client = OpenAI(
                    api_key=self.openai_key,
                    timeout=30.0,
                    max_retries=2
                )
                self.provider = 'openai'
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.warning(f"OpenAI initialization failed: {str(e)}")
                self.client = None
        
        if not self.client and self.anthropic_key:
            try:
                from anthropic import Anthropic
                # Initialize without proxies to avoid compatibility issues
                self.client = Anthropic(api_key=self.anthropic_key)
                self.provider = 'anthropic'
                logger.info("Anthropic client initialized successfully")
            except Exception as e:
                logger.warning(f"Anthropic initialization failed: {str(e)}")
                self.client = None
        
        if not self.client:
            logger.error("No LLM client could be initialized - check API keys")
    
    def plan_solution(self, question):
        """Ask LLM to plan the solution approach"""
        if not self.client:
            logger.error("No LLM client available")
            return {'steps': ['Error: No LLM client']}
        
        prompt = f"""You are a data analysis expert. Given this quiz question, create a step-by-step plan.

Question: {question}

Provide a JSON plan with:
- steps: list of actions
- data_sources: where to get data from
- processing: how to process data
- expected_answer_type: number, string, boolean, json, or base64"""
        
        try:
            if self.provider == 'openai':
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{'role': 'user', 'content': prompt}],
                    temperature=0.5
                )
                return json.loads(response.choices[0].message.content)
            elif self.provider == 'anthropic':
                response = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    messages=[{'role': 'user', 'content': prompt}]
                )
                return json.loads(response.content[0].text)
            else:
                return {'steps': ['Generic approach']}
        except json.JSONDecodeError:
            logger.warning("LLM response was not valid JSON, returning generic plan")
            return {'steps': ['Generic approach']}
        except Exception as e:
            logger.error(f"Error in plan_solution: {str(e)}")
            return {'steps': ['Error in planning']}
    
    def solve_generic(self, question):
        """Use LLM for generic problem solving"""
        if not self.client:
            logger.error("No LLM client available")
            return "Error: No LLM client"
        
        prompt = f"""Solve this data analysis quiz question. Provide only the answer, no explanation.

Question: {question}"""
        
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
                    max_tokens=1000,
                    messages=[{'role': 'user', 'content': prompt}]
                )
                answer = response.content[0].text.strip()
            else:
                answer = "Unable to generate answer"
            
            # Try to convert to number if possible
            try:
                return int(answer)
            except ValueError:
                try:
                    return float(answer)
                except ValueError:
                    return answer
        
        except Exception as e:
            logger.error(f"Error in solve_generic: {str(e)}")
            return "Error"
    
    def analyze_data(self, data, instruction):
        """Ask LLM to analyze data"""
        if not self.client:
            logger.error("No LLM client available")
            return "Error: No LLM client"
        
        prompt = f"""Analyze this data: {json.dumps(data)}

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
                return "Unable to analyze"
        except Exception as e:
            logger.error(f"Error in analyze_data: {str(e)}")
            return "Error"
