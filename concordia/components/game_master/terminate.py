
"""Component that helps a game master terminate the simulation."""

from concordia.typing import entity as entity_lib
from concordia.typing import entity_component


DEFAULT_TERMINATE_COMPONENT_KEY = '__terminate__'
DEFAULT_TERMINATE_PRE_ACT_LABEL = '\nTerminate'


class Terminate(
    entity_component.ContextComponent, entity_component.ComponentWithLogging
):
  """A component that decides whether to terminate the simulation.
  """

  def __init__(
      self,
      pre_act_label: str = DEFAULT_TERMINATE_PRE_ACT_LABEL,
  ):
    """Initializes the component.

    Args:
      pre_act_label: Prefix to add to the output of the component when called
        in `pre_act`.
    """
    super().__init__()
    self._pre_act_label = pre_act_label
    self._terminate_now = False

  def pre_act(
      self,
      action_spec: entity_lib.ActionSpec,
  ) -> str:
    result = ''
    if action_spec.output_type == entity_lib.OutputType.TERMINATE:
      return 'Yes' if self._terminate_now else 'No'

    return result

  def terminate(self):
    self._terminate_now = True
