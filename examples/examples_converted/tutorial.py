#!/usr/bin/env python
# coding: utf-8

# This notebook is a basic tutorial that demonstrates how to configure a simulation using

# It sets up a simple scenario with two entities and a orchestrator, and runs the simulation.

# @title Imports

import numpy as np
from IPython import display
import sentence_transformers

from language_model.no_language_model import NoLanguageModel

from prefabs.simulation import generic as simulation

import prefabs.entity as entity_prefabs
import prefabs.orchestrator as orchestrator_prefabs

from typing_custom import prefab as prefab_lib
from utils import helper_functions

# Import your custom LLM implementation
from language_model import openrouter_model # Adjust import if needed

import os
from dotenv import load_dotenv

# Always load .env from project root
load_dotenv(dotenv_path=os.path.join("C:\\Users\\tyler\\dev\\concordia\\pyscrai\\pysim", ".env"))
# Get API key and model name from environment
API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL_NAME = os.getenv("OPENROUTER_MODEL_NAME", "openrouter-default-model")  # Set your default
print({API_KEY})
print("OPENROUTER_API_KEY in env:", os.getenv("OPENROUTER_API_KEY"))
if not API_KEY:
    raise ValueError("OPENROUTER_API_KEY is required in your .env file.")

# To debug without spending money on API calls, set DISABLE_LANGUAGE_MODEL=True
DISABLE_LANGUAGE_MODEL = False

if not DISABLE_LANGUAGE_MODEL:
    model = openrouter_model.OpenRouterLanguageModel(api_key=API_KEY, model_name=MODEL_NAME)
else:
    model = NoLanguageModel()


# @title Setup sentence encoder

if DISABLE_LANGUAGE_MODEL:
  embedder = lambda _: np.ones(3)
else:
  st_model = sentence_transformers.SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
  embedder = lambda x: st_model.encode(x, show_progress_bar=True)

# test = model.sample_text(
#     'Is societal and technological progress like getting a clearer picture of '
#     'something true and deep?')
# print(test)


# @title Load prefabs from packages to make the specific palette to use here.

prefabs = {
    **helper_functions.get_package_classes(entity_prefabs),
    **helper_functions.get_package_classes(orchestrator_prefabs),
}


#@title Print menu of prefabs

display.display(
    display.Markdown(helper_functions.print_pretty_prefabs(prefabs)))


# @title Configure instances.

instances = [
    prefab_lib.InstanceConfig(
        prefab='basic__Entity',
        role=prefab_lib.Role.ENTITY,
        params={
            'name': 'Oliver Cromwell',
            'goal': 'become lord protector',
        },
    ),
    prefab_lib.InstanceConfig(
        prefab='basic__Entity',
        role=prefab_lib.Role.ENTITY,
        params={
            'name': 'King Charles I',
            'goal': 'avoid execution for treason',
        },
    ),
    prefab_lib.InstanceConfig(
        prefab='generic__orchestrator',
        role=prefab_lib.Role.ORCHESTRATOR,
        params={
            'name': 'default rules',
            # Comma-separated list of thought chain steps.
            'extra_event_resolution_steps': '',
        },
    ),
    prefab_lib.InstanceConfig(
        prefab='formative_memories_initializer__Orchestrator',
        role=prefab_lib.Role.INITIALIZER,
        params={
            'name': 'initial setup rules',
            'next_orchestrator_name': 'default rules',
            'shared_memories': [
                'The king was captured by Parliamentary forces in 1646.',
                'Charles I was tried for treason and found guilty.',
            ],
        },
    ),
]



config = prefab_lib.Config(
    default_premise='Today is January 29, 1649.',
    default_max_steps=5,
    prefabs=prefabs,
    instances=instances,
)


# # The simulation


# @title Initialize the simulation
runnable_simulation = simulation.Simulation(
    config=config,
    model=model,
    embedder=embedder,
)


# @title Run the simulation
results_log = runnable_simulation.play()


# @title Display the log
display.HTML(results_log)
