

"""Logger."""

import termcolor


class Logger:
  """Utility for logs messages depending on verbosity."""

  def __init__(self, color: str = 'magenta', verbose=False, semi_verbose=True):
    self._color = color
    self._verbose = verbose
    self._semi_verbose = semi_verbose

  def verbose(self, entry: str):
    if self._verbose:
      self._log(entry)

  def semi_verbose(self, entry: str):
    if self._semi_verbose:
      self._log(entry)

  def _log(self, entry: str):
    print(termcolor.colored(entry, self._color))
