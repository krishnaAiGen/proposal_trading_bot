from langchain_community.llms import Ollama
from openai import OpenAI, OpenAIError
import pandas as pd
import os
import json
import re
import time
from typing import Tuple, Optional
from dotenv import load_dotenv
import ast

load_dotenv()

class Reasoning:
    def __init__(self, model, openai_api_key):
        self.model = model
        self.max_attempts = 5
        self.retry_delay = 1  # seconds between retries
        self.client = OpenAI(api_key=openai_api_key)
        self.ollama_weight = 0.3
        self.openai_weight = 0.5
        self.trained_weight = 0.2
    
    def get_sentiment_score(self, output: str) -> float:
        """
        Extract sentiment score from LLM output using regex pattern matching.
        """
        json_pattern = r'\{[^{}]*\}'
        matches = re.findall(json_pattern, output)
    
        for match in matches:
            try:
                # Parse the match as JSON
                data = json.loads(match)
                
                # Check if 'score' is in the parsed dictionary
                if 'score' in data:
                    score = float(data['score'])
                    # Validate that the score is between 0 and 1
                    if 0 <= score <= 1:
                        return score
            except json.JSONDecodeError:
                # If parsing fails, move to the next match
                continue
        
        raise ValueError("No valid sentiment score found in output")

    def get_openai_sentiment(self, description: str) -> float:
        """
        Get sentiment score from OpenAI model with retry logic.
        """
        message = f"""
            You are a financial and trading expert. Based on the content of this text, evaluate its immediate impact on market prices.
            Output your result in JSON format as {{'score': x}}, where:
            - 0 indicates strongly bearish sentiment
            - 1 indicates strongly bullish sentiment
            - Values between indicate mixed sentiment
            
            Text to analyze: {description}
            
            Return ONLY the JSON object, no other text.
            """
        
        for attempt in range(self.max_attempts):
            try:
                response = self.client.chat.completions.create(
                    model="o1-preview",
                    messages=[
                        {
                            "role": "user",
                            "content": message
                        }
                    ]
                )
                
                output = response.choices[0].message.content
                try:
                    score = float(ast.literal_eval(output)["score"])
                    return score
                except ValueError:
                    if attempt == self.max_attempts - 1:
                        raise RuntimeError(f"Failed to get valid JSON from OpenAI after {self.max_attempts} attempts")
                    time.sleep(self.retry_delay)
                    continue
                    
            except OpenAIError as e:
                if attempt == self.max_attempts - 1:
                    raise RuntimeError(f"OpenAI API error after {self.max_attempts} attempts: {str(e)}")
                time.sleep(self.retry_delay)
                continue

    def calculate_weighted_sentiment(self, ollama_score: float, openai_score: float, trained_score: float) -> Tuple[str, float]:
        """
        Calculate weighted sentiment score combining both models.
        """
        weighted_score = (ollama_score * self.ollama_weight) + (openai_score * self.openai_weight) + (trained_score * self.trained_weight)
        
        if weighted_score < 0.4:
            sentiment = "bearish"
        elif weighted_score > 0.6:
            sentiment = "bullish"
        else:
            sentiment = "neutral"
            
        return sentiment, weighted_score
    
    def predict_sentiment(self, description: str, trained_score: float) -> Tuple[str, float]:
        """
        Predict market sentiment from text description using both models.
        If Ollama fails to produce a score after `max_attempts`, we fall back
        to averaging the OpenAI score and the trained score.
        """
        llm = Ollama(model=self.model, temperature=1)
        prompt = """
        You are a financial and trading expert. Based on the content of this text, evaluate its immediate impact on market prices.
        Output your result in JSON format as {'score': x}, where:
        - 0 indicates strongly bearish sentiment
        - 1 indicates strongly bullish sentiment
        - Values between indicate mixed sentiment
        Output only the JSON object.
       """
   
       # First, try to get the Ollama score up to `max_attempts` times
        ollama_score = None
        for attempt in range(self.max_attempts):
            try:
                print(f"Ollama attempt: {attempt}")
                try:
                    ollama_output = llm.invoke(prompt + description)
                except Exception as e:
                    print(f"Error at invoke: {e}")
                    continue
                    
                ollama_score = self.get_sentiment_score(ollama_output)
                print(f"Ollama score: {ollama_score}")
                break  # If successful, exit the loop
            except (ValueError, json.JSONDecodeError, RuntimeError, OpenAIError) as e:
                print(f"Ollama error: {e}, retrying...")
                continue
               
        # Next, retrieve the OpenAI score
        openai_score = self.get_openai_sentiment(description)
        print(f"OpenAI score: {openai_score}")
        print(f"Trained score: {trained_score}")
    
        # If Ollama score was not obtained after `max_attempts`, fallback to
        # a 50–50 average of OpenAI score and trained score
        if ollama_score is None:
            fallback_score = (0.6 * openai_score) + (0.4 * trained_score)
            if fallback_score < 0.4:
                final_sentiment = "negative"
            elif fallback_score > 0.6:
                final_sentiment = "positive"
            else:
                final_sentiment = "neutral"
            return final_sentiment, fallback_score
        else:
            # If Ollama was successful, combine the three scores using your existing weights
            final_sentiment, weighted_score = self.calculate_weighted_sentiment(
                ollama_score,
                openai_score,
                trained_score
            )
            return final_sentiment, weighted_score


# if __name__ == "__main__":
#     reasoning = Reasoning(
#         model="deepseek-r1:8b",
#         openai_api_key=os.getenv("OPENAI_KEY")
#     )
    
#     # Analyze a single text
#     text = """
#     The Arbitrum Growth Circle is a series of events aimed at accelerating the growth of the Arbitrum ecosystem by providing peer learning opportunities for builders, promoting best practices in development, and fostering collaboration among them. The events will consist of bi-weekly clinics focused on specific topics, with each clinic culminating in a final evaluation session to assess impact and gather feedback.
#     The primary target audience is high-potential protocols that are relatively new to building in the Arbitrum ecosystem or are currently underserved. The events will be promoted through targeted outreach, direct engagement, referral networks, participant databases, and channel activations. Regular promotional content and participant success stories will also be shared via various channels to maintain visibility and drive engagement.
#     The Arbitrum Growth Circle aligns with Arbitrum's mission by advancing ecosystem development, product excellence, and community strength. The events are expected to have a significant impact on the growth of Orbit chains, the adoption of Stylus, and the improvement of technical knowledge sharing within the ecosystem.
#     A post-event Impact Report will be compiled, which will include an executive summary, detailed metrics, interpretation of the KPIs in relation to a Theory of Change / Logic Model, a value analysis, and recommendations for future improvements and scaling opportunities.
#     """
    
    
#     sentiment, score = reasoning.predict_sentiment(text, 0.9)
#     print(f"Sentiment: {sentiment}, Score: {score}")












