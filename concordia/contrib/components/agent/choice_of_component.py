"""Select a component from a list and call `get_pre_act_value` on it."""

from typing import Sequence

from concordia.components.agent import action_spec_ignored
from concordia.document import interactive_document
from concordia.language_model import language_model
from concordia.types_concordia import entity as entity_lib
from concordia.types_concordia import entity_component
from concordia.types_concordia import logging


class ChoiceOfComponent(action_spec_ignored.ActionSpecIgnored):
  """Select a component from a list and calls `get_pre_act_value` on it."""

  def __init__(
      self,
      model: language_model.LanguageModel,
      observations_component_key: str,
      menu_of_components: Sequence[str],
      pre_act_label: str = 'ChoiceComponent',
      logging_channel: logging.LoggingChannel = logging.NoOpLoggingChannel,
  ):
    """Initialize a component that selects other components from a list.

    Args:
      model: The language model to use.
      observations_component_key: The name of the component that contains the
        observations.
      menu_of_components: The sequence of components to choose from.
      pre_act_label: Prefix to add to the output of the component when called
        in `pre_act`.
      logging_channel: The channel to log debug information to.
    """
    super().__init__(pre_act_label)
    self._model = model
    self._observations_component_key = observations_component_key
    self._menu = menu_of_components
    self._logging_channel = logging_channel

  def _make_pre_act_value(self) -> str:
    agent_name = self.get_entity().name

    observations = self.get_named_component_pre_act_value(
        self._observations_component_key)

    prompt = interactive_document.InteractiveDocument(self._model)
    prompt.statement(observations)

    # Load the component that is most relevant to the agent's current situation.
    component_index = prompt.multiple_choice_question(
        question=('Which of the following options is the most relevant '
                  f'to {agent_name}\'s '
                  f'current situation? i.e. the most helpful for {agent_name} '
                  'to consider as context while deciding what to do next'),
        answers=[item.replace('\n', '') for item in self._menu],
    )
    component_name = self._menu[component_index]
    loaded_component = self.get_entity().get_component(
        component_name, type_=action_spec_ignored.ActionSpecIgnored)
    result = loaded_component.get_pre_act_value()

    self._logging_channel({
        'Key': self.get_pre_act_label(),
        'Value': result,
        'Chain of thought': prompt.view().text().splitlines(),
    })

    return result


class ChoiceOfComponentWithoutPreAct(
    action_spec_ignored.ActionSpecIgnored
):
  """A ChoiceOfComponent component that does not output its state to pre_act.
  """

  def __init__(self, *args, **kwargs):
    self._component = ChoiceOfComponent(*args, **kwargs)

  def set_entity(self, entity: entity_component.EntityWithComponents) -> None:
    self._component.set_entity(entity)

  def _make_pre_act_value(self) -> str:
    return ''

  def get_pre_act_value(self) -> str:
    return self._component.get_pre_act_value()

  def pre_act(
      self,
      unused_action_spec: entity_lib.ActionSpec,
  ) -> str:
    del unused_action_spec
    return ''

  def update(self) -> None:
    self._component.update()
