"""Helper functions for language model sampling.
"""

import re


def _extract_parenthesized_choice(sample: str):
  """Given text formatted as 'lorum(a)ipsum', return 'a'."""
  match = re.search(r'\((\w)\)', sample)
  if match:
    return match.group(1)
  else:
    return None


def extract_choice_response(sample: str) -> str | None:
  """
  Given a sample that may include reasoning before the choice,
  extracts the final choice. e.g. "I think the answer is b. b" -> "b"
  """
  # Strip whitespace and make lowercase for robust matching.
  sample = sample.strip().lower()

  # Find all alphabetic characters in the sample.
  letters = re.findall(r'[a-z]', sample)

  # The intended choice is almost always the very last letter the model outputs.
  if letters:
    return letters[-1]

  # Fallback for parenthesized choices if the above fails for some reason.
  parenthesized = _extract_parenthesized_choice(sample)
  if parenthesized:
      return parenthesized

  return None


def dynamically_adjust_temperature(
    attempts: int,
    max_attempts: int,
) -> float:
  """Adjusts choice sampling temperature based on number of attempts so far."""
  # Increase temperature after the first failed attempt.
  temperature = 0.0
  if attempts > 1 and attempts < (max_attempts / 2.0):
    temperature = 0.5
  elif attempts > (max_attempts / 2.0):
    temperature = 0.75
  return temperature
