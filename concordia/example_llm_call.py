# example_llm_call.py
from concordia.language_model.openrouter_model import OpenRouterLanguageModel
from concordia.utils import measurements as measurements_lib
# Instantiate the OpenRouter LLM
llm = OpenRouterLanguageModel(
    system_prompt=(
        "You are an AI agent in a social simulation. "
        "Respond as if you are a character with goals, emotions, and constraints."
    ),
    max_tokens=1000  # limit output length if needed
)

# Example usage: generate dialogue
prompt = "A villager approaches the mayor, worried about the lack of food."
response = llm.sample_text(
    prompt,
    temperature=0.7,
    max_tokens=200
)

print("Agent Response:", response)
