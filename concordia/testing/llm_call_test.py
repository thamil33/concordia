"""Tests for the LLM."""

import os
import unittest

# Import the class directly to avoid potential namespace issues.
from concordia.language_model.openrouter_model import OpenRouterLanguageModel

# A model available on OpenRouter for testing.
_OPENROUTER_TEST_MODEL = 'mistralai/mistral-7b-instruct-v0.2'


class LlmsTest(unittest.TestCase):

  def test_openrouter_llm_call(self):
    """Test the OpenRouter LLM call.

    This test is conditional on the presence of the OPENROUTER_API_KEY
    environment variable. If the variable is not set, the test is skipped.
    """
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
      self.skipTest('OPENROUTER_API_KEY environment variable not set.')

    # The model is now initialized directly with the imported class.
    llm = OpenRouterLanguageModel(
        model_name=_OPENROUTER_TEST_MODEL, api_key=api_key)
    result = llm('Why is the sky blue?')
    self.assertIsInstance(result, str)
    # Replaced assertNotEmpty with its standard unittest equivalent.
    self.assertTrue(result)


if __name__ == '__main__':
  unittest.main()
