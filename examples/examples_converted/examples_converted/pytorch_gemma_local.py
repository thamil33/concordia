#!/usr/bin/env python
# coding: utf-8

# # Illustrate how to use a PyTorch Gemma model running locally.
#
# Note: This will download a 2 billion parameter model from Hugging Face, so make sure you have enough space for that.

# In[ ]:


# @title Colab-specific setup (use a CodeSpace to avoid the need for this).
try:
  get_ipython().run_line_magic('pass', ' #env COLAB_RELEASE_TAG')
except:
  pass  # Not running in colab.
else:
  get_ipython().run_line_magic('pass', " #pip install --ignore-requires-python --requirement 'https://raw.githubusercontent.com/google-deepmind/concordia/main/examples/requirements.in' 'git+https://github.com/google-deepmind/git#egg=gdm-concordia'")
  get_ipython().run_line_magic('pass', ' #pip list')


# In[ ]:


from language_model import pytorch_gemma_model


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
