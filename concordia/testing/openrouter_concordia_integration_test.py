import os
import pytest
from ...concordia.language_model.openrouter_model import OpenRouterLanguageModel
import dotenv 

dotenv.load_dotenv()

def test_openrouter_sample_text():
    model = OpenRouterLanguageModel(
        model_name='mistralai/mistral-small-3.1-24b-instruct:free',
    )
    prompt = 'What is the capital of France?'
    response = model.sample_text(prompt)
    print('Sample text response:', response)
    assert isinstance(response, str)
    assert 'Paris' in response or response.strip() != ''

def test_openrouter_sample_choice():
    model = OpenRouterLanguageModel(
        model_name='mistralai/mistral-small-3.1-24b-instruct:free',
    )
    prompt = 'Which of the following is a fruit?'
    choices = ['Car', 'Apple', 'Chair']
    idx, choice, info = model.sample_choice(prompt, choices)
    print('Sample choice response:', idx, choice, info)
    assert choice in choices
    assert isinstance(idx, int) 