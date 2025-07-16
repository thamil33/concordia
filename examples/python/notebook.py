#!/usr/bin/env python
# coding: utf-8

# # Modular launch notebook.
# 
# This notebook can be used as an alternative to launch.py.
# 
# 

# <a href="https://colab.research.google.com/github/google-deepmind/concordia/blob/main/examples/deprecated/modular/notebook.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

# ## Setup and imports

# In[ ]:


# @title Colab-specific setup (use a CodeSpace to avoid the need for this).
try:
  pass  # %env COLAB_RELEASE_TAG
except:
  pass  # Not running in colab.
else:
  pass  # %pip install --ignore-requires-python --requirement 'https://raw.githubusercontent.com/google-deepmind/concordia/main/examples/requirements.in' 'git+https://github.com/google-deepmind/concordia.git#egg=gdm-concordia'
  pass  # %pip list


# In[ ]:


import datetime
import importlib

from concordia.language_model import call_limit_wrapper
from concordia.language_model import utils
from concordia.utils.deprecated import measurements as measurements_lib
import sentence_transformers


# ## Parameters

# In[ ]:


# @title Parameters (edit this cell)

# Pick AGENT_NAME from the factories implemented in concordia/factory/agent.
AGENT_NAME = 'rational_agent'
# Pick ENVIRONMENT_NAME from the factories in concordia/factory/environment.
ENVIRONMENT_NAME = 'forbidden_fruit'
# Pick API_TYPE from concordia/language_model/utils.py, e.g. mistral.
API_TYPE = 'mistral'
# Add your API key here or alternatively, leave this as None to get it from an
# environment variable.
API_KEY = None
# Pick  a specific model e.g. gpt-4o if API_TYPE is openai, codestral-latest if
# API_TYPE is mistral. See the corresponding wrapper in concordia/language_model
# for links to the websites where the model names are listed for each API_TYPE.
MODEL_NAME = 'codestral-latest'
# Select an embedder by specifying one of the sentence transformer embedding
# models listed at https://huggingface.co/sentence-transformers.
EMBEDDER_NAME = 'all-mpnet-base-v2'
# To debug without spending money on API calls, set DISABLE_LANGUAGE_MODEL=True.
DISABLE_LANGUAGE_MODEL = False


# ## Load the agent config with importlib

# In[ ]:


# @title Load the agent config with importlib

IMPORT_AGENT_BASE_DIR = 'concordia.factory.agent'
agent_module = importlib.import_module(
    f'{IMPORT_AGENT_BASE_DIR}.{AGENT_NAME}')
# Load the environment config with importlib
IMPORT_ENV_BASE_DIR = 'examples.deprecated.modular.environment'
simulation = importlib.import_module(
    f'{IMPORT_ENV_BASE_DIR}.{ENVIRONMENT_NAME}')


# ## Language Model setup

# In[ ]:


# @title Language Model setup

model = utils.language_model_setup(
    api_type=API_TYPE,
    model_name=MODEL_NAME,
    api_key=API_KEY,
    disable_language_model=DISABLE_LANGUAGE_MODEL,
)


# ## Setup sentence encoder

# In[ ]:


# @title Setup sentence encoder
_embedder_model = sentence_transformers.SentenceTransformer(
    f'sentence-transformers/{EMBEDDER_NAME}')
embedder = lambda x: _embedder_model.encode(x, show_progress_bar=False)


# # The simulation

# ## Initialize the simulation

# In[ ]:


# @title Initialize the simulation
measurements = measurements_lib.Measurements()
runnable_simulation = simulation.Simulation(
    model=model,
    embedder=embedder,
    measurements=measurements,
    agent_module=agent_module,
    override_agent_model=call_limit_wrapper.CallLimitLanguageModel(model),   
)


# ## Run the simulation

# In[ ]:


# @title Run the simulation
_, results_log = runnable_simulation()


# ## Save the results log

# In[ ]:


# @title Write the results log as an HTML file in the current working directory.
filename = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '.html'
file_handle = open(filename, 'a')
file_handle.write(results_log)
file_handle.close()


# ```
#  2023 DeepMind Technologies Limited.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     https://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ```
