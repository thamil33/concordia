from agents.llm_entity_agent import LlmEntityAgent
import os

class setup_lmstudio_primarysetup_lmstudio_primary:
    def complete(self, prompt: str):
        # Replace with real LLM client logic
        return "move_forward"

def run_simulation():
    from dotenv import load_dotenv
    load_dotenv()

    agent = LlmEntityAgent(name="FrameworkAgent", llm_client=LlmEntityAgent())

    for step in range(3):
        observation = {"step": step, "state": "running"}
        agent.observe(observation)
        action = agent.act()
        print(f"Step {step}: Observation={observation}, Action={action}")

if __name__ == "__main__":
    run_simulation()
