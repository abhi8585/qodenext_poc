import openai
import os
import json
import pandas as pd
from app.utils.config.config_client import ConfigClient


config = ConfigClient(env='dev')
chatgpt_api_key = config.get_value("ChatGpt", "api-key")
openai.api_key  = chatgpt_api_key


class ChatGptClient:
    def __init__(self):
        pass


    def get_completion(prompt, model="gpt-3.5-turbo"):
        messages = [{"role": "user", "content": prompt}]
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=0, # this is the degree of randomness of the model's output
        )
        return response.choices[0].message["content"]
