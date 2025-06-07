from concordia.language_model import lmstudio_model
from concordia.agents.entity_agent import EntityAgent
from concordia.environment.engine import Engine
from concordia.prefabs import basic
from concordia.components.agent import BasicAgentComponents
from concordia.associative_memory.basic_associative_memory import BasicAssociativeMemory

def main():
    # Initialize the language model
    llm = lmstudio_model.LMStudioModel()

    # Create the simulation engine
    engine = Engine()

    # Create a basic agent with memory and components
    agent = EntityAgent(
        name="TestAgent",
        llm=llm,
        memory=BasicAssociativeMemory(),
        components=BasicAgentComponents(),
        prefab=basic.BasicAgentPrefab()
    )

    # Add the agent to the engine
    engine.add_entity(agent)

    # Run a simple simulation step
    engine.step()

if __name__ == "__main__":
    main()
