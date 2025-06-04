---
applyTo: '**'
---
# Copilot Instructions

We will primarily be using Windows PowerShell to run commands, ensure that any command is formatted to work in PowerShell.

.Blueprints - These are development-centered documents.

.concordia_env - This is the location of the venv being used for this project.
.concordia_env\Scripts\Activate.ps1 - This is the script to activate the virtual environment on Windows PowerShell.

concordia - Location of the concordia project. This is where the main code lives. It has been
installed in editable mode, so any changes made here will be reflected in the main project.

examples - This is where example code lives. It is not used in the main project, but can be used to test.

.Blueprints\openrouter_full_docs.txt - This is a document that contains the full documentation for the OpenRouter API.

.env - This is the environment file, and one point of truth, that contains the API keys and other environment variables needed for our custom LLM implementation. Both Openrouter and LMStudio, we will likely need to add sentence transformers path to this file as well.
