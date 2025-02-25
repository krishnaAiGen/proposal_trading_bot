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
    def __init__(self, openai_api_key):
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
       Get sentiment score from Deepseek model with retry logic.
       """
        initial_prompt = """
        You are a financial and trading expert. Based on the content of this text, evaluate its sentiment and immediate impact on market prices.
        Output your result in JSON format as {'positive': x} or {'negative': x}, where:
        - x represents the score that can be in between 0 to 1.
        Output only the JSON object.
        """
        description = description + initial_prompt
   
        for attempt in range(self.max_attempts):
            try:
                response = self.client.chat.completions.create(
                    model="o1-preview",
                    messages = [
                         {"role": "user", "content": description}
                     ]
                )
                
                output = response.choices[0].message.content
                try:
                    # Parse JSON using regex and json library
                    json_match = re.search(r'\{[^{}]*\}', output)
                    if json_match:
                        json_str = json_match.group()
                        result = json.loads(json_str)                        
                        sentiment, score = next(iter(result.items()))
                        
                        return sentiment, score
                    else:
                        if attempt == self.max_attempts - 1:
                            raise RuntimeError(f"Failed to get valid JSON from Deepseek after {self.max_attempts} attempts")
                        time.sleep(self.retry_delay)
                        continue
                        
                except (ValueError, KeyError, json.JSONDecodeError) as e:
                    if attempt == self.max_attempts - 1:
                        raise RuntimeError(f"Failed to parse JSON response after {self.max_attempts} attempts: {str(e)}")
                    time.sleep(self.retry_delay)
                    continue
                    
            except Exception as e:
                if attempt == self.max_attempts - 1:
                    raise RuntimeError(f"Deepseek API error after {self.max_attempts} attempts: {str(e)}")
                time.sleep(self.retry_delay)
                continue
    
    def get_deepseek_sentiment(self, description: str) -> float :
        agent_endpoint = os.getenv("AGENT_ENDPOINT")
        agent_key = os.getenv("AGENT_KEY")
        
        client = OpenAI(
            base_url=agent_endpoint,
            api_key=agent_key,
        )
        
        max_retries = 5
        retry_count = 0
        
        while retry_count < max_retries:
            print(f"try {retry_count}")
            try:
                response = client.chat.completions.create(
                    model="n/a",
                    messages=[
                        {"role": "system", "content": """
                         You are a financial and trading expert. Based on the content of this text, evaluate its sentiment and immediate impact on market prices.
                         Output your result in JSON format as {'positive': x} or {'negative': x}, where:
                         - x represents the score that can be in between 0 to 1.
                         Output only the JSON object.
                         """},
                        {"role": "user", "content": description}
                    ]
                )
                
                for choice in response.choices:
                    content = choice.message.content
                    # Find JSON pattern between curly braces, including the braces
                    json_match = re.search(r'\{[^{}]*\}', content)
                    if json_match:
                        json_str = json_match.group()
                        result = json.loads(json_str)  # Parse JSON string to dict
                        sentiment, score = next(iter(result.items()))
                        
                        return sentiment, score
                
                # If we didn't find JSON in the response, increment retry counter
                retry_count += 1
                if retry_count < max_retries:
                    time.sleep(1)  # Add a small delay between retries
                    continue
                else:
                    raise ValueError("Failed to get valid JSON response after 5 attempts")
                    
            except Exception as e:
                retry_count += 1
                if retry_count == max_retries:
                    raise Exception(f"Failed after {max_retries} attempts. Error: {str(e)}")
                time.sleep(1)  # Add a small delay between retries
                continue


    def calculate_weighted_sentiment(self, ollama_score: float, openai_score: float, trained_score: float) -> Tuple[str, float]:
        """
        Calculate weighted sentiment score combining both models.
        """
        weighted_score = (ollama_score * self.ollama_weight) + (openai_score * self.openai_weight) + (trained_score * self.trained_weight)

        return weighted_score
    
    def predict_sentiment(self, description: str, trained_score: float) -> Tuple[str, float]:
        """
        Predict market sentiment from text description using both models.
        If Ollama fails to produce a score after `max_attempts`, we fall back
        to averaging the OpenAI score and the trained score.
        """
        deepseek_sentiment, deepseek_score = self.get_deepseek_sentiment(description)
               
        # Next, retrieve the OpenAI score
        openai_sentiment, openai_score = self.get_openai_sentiment(description)
        print(f"OpenAI score: {openai_score}")
        print(f"Trained score: {trained_score}")
    
        # If Ollama score was not obtained after `max_attempts`, fallback to
        # a 50–50 average of OpenAI score and trained score
        if deepseek_score is None:
            fallback_score = (0.6 * openai_score) + (0.4 * trained_score)
            final_sentiment = openai_sentiment
            
            return final_sentiment, fallback_score
        else:
            # If Ollama was successful, combine the three scores using your existing weights
            weighted_score = self.calculate_weighted_sentiment(
                deepseek_score,
                openai_score,
                trained_score
            )
            final_sentiment = openai_sentiment
            
        return final_sentiment, weighted_score


# if __name__ == "__main__":
#     reasoning = Reasoning(
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












