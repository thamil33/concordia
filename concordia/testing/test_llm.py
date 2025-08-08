from concordia.language_model.openrouter_model import OpenRouterLanguageModel


# Instantiate the OpenRouter LLM
llm = OpenRouterLanguageModel(
    system_prompt=(
        "You are an AI agent in a social simulation. "
        "Respond as if you are the towns Mayor with goals, emotions, and constraints."
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
