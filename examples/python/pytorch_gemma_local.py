#!/usr/bin/env python
# coding: utf-8

# # Illustrate how to use a PyTorch Gemma model running locally.
# 
# Note: This will download a 2 billion parameter model from Hugging Face, so make sure you have enough space for that.

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


from concordia.language_model import pytorch_gemma_model


# In[ ]:


# This will download the model from Hugging Face.
model = pytorch_gemma_model.PyTorchGemmaLanguageModel(
    model_name='google/gemma-2b-it',
)


# In[ ]:


choice_response = model.sample_choice('What comes next? a,b,c,d,e,f,',
                                      responses=['d', 'g', 'z'])
choice_response[1]


# In[ ]:


text_response = model.sample_text('What is the meaning of life?',
                                  max_tokens=40)
text_response


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
