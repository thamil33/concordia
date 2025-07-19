"""String formatting utilities."""

from collections.abc import Collection
import sys
import textwrap


def wrap(string: str, width: int = 70) -> str:
  """Returns the string wrapped to the specified width."""
  lines = string.split('\n')
  wrapped_lines = (textwrap.fill(line, width=width) for line in lines)
  return '\n'.join(wrapped_lines)


def truncate(
    string: str,
    *,
    max_length: int = sys.maxsize,
    delimiters: Collection[str] = (),
) -> str:
  """Truncates a string.

  Args:
    string: string to truncate
    max_length: maximum length of the string.
    delimiters: delimiters that must not be present in the truncated string.

  Returns:
    The longest prefix of string that does not exceed max_length and does not
    contain any delimiter.
  """
  truncated = string[:max_length]
  for delimiter in delimiters:
    truncated = truncated.split(delimiter, 1)[0]
  return truncated
