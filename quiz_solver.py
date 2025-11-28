# FILE quiz_solver.py - Core logic for solving quizzes
import asyncio
import requests
import json
import logging
import re
from io import BytesIO
from llm_handler import LLMHandler

logger = logging.getLogger(__name__)

class QuizSolver:
    def __init__(self):
        self.llm = LLMHandler()
    
    async def render_page(self, url):
        """Render JavaScript-heavy pages using Playwright"""
        try:
            from playwright.async_api import async_playwright
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(url, wait_until="networkidle", timeout=30000)
                await page.wait_for_timeout(2000)
                content = await page.content()
                text = await page.evaluate("document.body.innerText")
                await browser.close()
                return content, text
        except Exception as e:
            logger.error(f"Error rendering page: {str(e)}")
            return None, None
    
    def solve(self, quiz_url):
        """Main solve method - orchestrates the quiz solving"""
        html, text = asyncio.run(self.render_page(quiz_url))
        if not html or not text:
            raise Exception("Failed to render quiz page")
        
        question = self.extract_question(text)
        submit_url = self.extract_submit_url(html)
        
        logger.info(f"Question: {question}")
        logger.info(f"Submit URL: {submit_url}")
        
        plan = self.llm.plan_solution(question)
        logger.info(f"Plan: {plan}")
        
        answer = self.execute_plan(plan, question, quiz_url, html)
        return answer
    
    def extract_question(self, text):
        """Extract quiz question from page text"""
        lines = text.split("\n")
        for line in lines:
            if line.strip().startswith("Q") and "." in line:
                return line.strip()
        return text[:500]
    
    def extract_submit_url(self, html):
        """Extract submit URL from HTML"""
        urls = re.findall(r"https?://[^\s\"]", html)
        submit_urls = [u for u in urls if "submit" in u.lower() or "answer" in u.lower()]
        return submit_urls[0] if submit_urls else None
    
    def execute_plan(self, plan, question, quiz_url, html):
        """Execute the solving strategy based on question type"""
        if any(x in question.lower() for x in ["download", "file"]):
            answer = self.handle_file_download(question, quiz_url, html)
        elif any(x in question.lower() for x in ["api", "endpoint"]):
            answer = self.handle_api_call(question)
        elif any(x in question.lower() for x in ["sum", "average", "count", "analyze"]):
            answer = self.handle_data_analysis(question, quiz_url, html)
        elif any(x in question.lower() for x in ["chart", "graph"]):
            answer = self.handle_visualization(question, quiz_url)
        else:
            answer = self.llm.solve_generic(question)
        return answer
    
    def handle_file_download(self, question, quiz_url, html):
        """Handle questions involving file downloads"""
        try:
            urls = re.findall(r"https?://.*?\.(pdf|csv|xlsx|json)", html)
            if urls:
                file_url = urls[0]
                response = requests.get(file_url, timeout=30)
                
                if file_url.endswith(".pdf"):
                    return self.process_pdf(response.content, question)
                elif file_url.endswith(".csv"):
                    return self.process_csv(response.content, question)
                elif file_url.endswith(".xlsx"):
                    return self.process_excel(response.content, question)
        except Exception as e:
            logger.error(f"Error in file download: {str(e)}")
            return "Unable to process file"
    
    def process_pdf(self, content, question):
        """Process PDF files"""
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(BytesIO(content))
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return self.llm.solve_generic(f"{question}\nContent:\n{text[:2000]}")
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            return "PDF processing failed"
    
    def process_csv(self, content, question):
        """Process CSV files"""
        try:
            import pandas as pd
            df = pd.read_csv(BytesIO(content))
            return self.llm.solve_generic(f"{question}\nData:\n{df.to_string()[:2000]}")
        except Exception as e:
            logger.error(f"Error processing CSV: {str(e)}")
            return "CSV processing failed"
    
    def process_excel(self, content, question):
        """Process Excel files"""
        try:
            import pandas as pd
            df = pd.read_excel(BytesIO(content))
            return self.llm.solve_generic(f"{question}\nData:\n{df.to_string()[:2000]}")
        except Exception as e:
            logger.error(f"Error processing Excel: {str(e)}")
            return "Excel processing failed"
    
    def handle_api_call(self, question):
        """Handle API-based questions"""
        try:
            api_match = re.search(r"https?://[^\s]", question)
            if api_match:
                api_url = api_match.group(0)
                response = requests.get(api_url, timeout=10)
                data = response.json()
                return self.llm.solve_generic(f"{question}\nResponse:\n{json.dumps(data)[:2000]}")
        except Exception as e:
            logger.error(f"Error in API call: {str(e)}")
            return "API call failed"
    
    def handle_data_analysis(self, question, quiz_url, html):
        """Handle data analysis questions"""
        return self.llm.solve_generic(question)
    
    def handle_visualization(self, question, quiz_url):
        """Handle visualization questions"""
        return self.llm.solve_generic(question)
    
    def submit_answer(self, email, secret, url, answer):
        """Submit the answer back to the server"""
        payload = {"email": email, "secret": secret, "url": url, "answer": answer}
        submit_endpoint = "https://tds-llm-analysis.s-anand.net/submit"
        try:
            response = requests.post(submit_endpoint, json=payload, timeout=30)
            return response.json()
        except Exception as e:
            logger.error(f"Error submitting answer: {str(e)}")
            return {"error": str(e)}
