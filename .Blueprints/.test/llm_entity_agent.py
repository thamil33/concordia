from typing import Any, Dict, Optional

class LlmEntityAgent:
    """
    Basic agent that interacts with an LLM to determine actions.
    """

    def __init__(self, name: str, llm_client: Any, config: Optional[Dict[str, Any]] = None):
        """
        Args:
            name: The name of the agent.
            llm_client: An object responsible for communicating with the LLM.
            config: Optional configuration dictionary.
        """
        self.name = name
        self.llm_client = llm_client
        self.config = config or {}

    def observe(self, observation: Dict[str, Any]) -> None:
        """
        Receive an observation from the environment.
        """
        self.last_observation = observation

    def act(self) -> Any:
        """
        Decide on an action using the LLM.
        Returns:
            The action decided by the LLM.
        """
        prompt = self._build_prompt(self.last_observation)
        response = self.llm_client.complete(prompt)
        return self._parse_response(response)

    def _build_prompt(self, observation: Dict[str, Any]) -> str:
        """
        Build a prompt for the LLM based on the observation.
        """
        return f"Observation: {observation}\nWhat should the agent do next?"

    def _parse_response(self, response: Any) -> Any:
        """
        Parse the LLM's response into an action.
        """
        # Placeholder: just return the response for now
        return response
