# 1 Agent Interaction:
Should Yin and Yang be able to communicate directly, or only through environmental events?

Do you want their interactions to be fully autonomous, or will you script some initial exchanges?

# 2 Environment:
What kind of environment will they interact with?
 Is it a simple text-based world, or do you want to model objects/events they can perceive and act upon?

# 3 Questioning Phase:
Should the questioning happen automatically at the end of the simulation, or do you want a separate agent (game_master) to prompt them?
Should the answers be generated using their memory/history, or do you want to provide them with a specific context for answering?

# 4 Game Master Role:

Will the game_master only ask questions, or also control/modify the environment or agents during the simulation?


# 5 Agent Memory:

Should Yin and Yang have persistent memory of their experiences, or only short-term context?



1) Yes, they will have free range of action to communicate or collaborate with each other, and inspect the environment (We will start with a very simple environment initially and iterate as we continue to flesh out the simulation) i.e, a small square room, all white, with one table and one chair - just as an example.

2) Touched upon in question 1, this will be simple initially, but we will evolve it into a fully fledged interactive environment of some sorts.

3) after looking at the source code, concordia\prefabs\game_master\interviewer.py I think would be a perfect match for the the questioning phase, so this is how I'm visualizing it: primary_game_master (most like the concordia\prefabs\game_master\situated.py prefab or concordia\prefabs\game_master\game_theoretic_and_dramaturgic.py). This primary_gm will serve as the 'Simulation control and environmental management' agent, as per there usual role within Concordia. At some point, depending on how this is actually implemented in the source code, the simulation proper will terminate, and the interview game_agent will begin to question each of the two agents to assess there understanding of the 6 fundamental questions. Again this is a high level, rough draft description, much may change as we implement.


4) covered in question 3, the answer being both (most likely two seperate game_masters, but perhaps not).


5) yes, we want to fully implement the assosciative memory as well as the component memory available to entities, I believe per concordia source that the game_master's and actors will have seperate memory banks... I am not certain about how it works for the actors.

Relevant Insights:
- As far as the scripted vs autonomous direction... we will keep things open at first, and if certain aspects require more structure we will adjust as needed. For instance, I imagine at soe point once the environment builds in complexity, we will set up some initial memories for each actor (yin and yang), or perhaps even them both seperate fragmented memories (small things they remember about the time before they just became self-aware), which could be complimentary if they collaborated on to piece together.. just as an example.
