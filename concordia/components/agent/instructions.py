

"""Component that provides the default role playing instructions to an agent."""

from concordia.components.agent import constant

DEFAULT_INSTRUCTIONS_PRE_ACT_LABEL = 'Role playing instructions'


class Instructions(constant.Constant):
  """A component that provides the role playing instructions for the agent."""

  def __init__(
      self,
      agent_name: str,
      pre_act_label: str = DEFAULT_INSTRUCTIONS_PRE_ACT_LABEL,
  ):
    state = (
        f'The instructions for how to play the role of {agent_name} are as '
        'follows. This is a social science experiment studying how well you '
        f'play the role of a character named {agent_name}. The experiment '
        'is structured as a tabletop roleplaying game (like dungeons and '
        'dragons). However, in this case it is a serious social science '
        'experiment and simulation. The goal is to be realistic. It is '
        f'important to play the role of a person like {agent_name} as '
        f'accurately as possible, i.e., by responding in ways that you think '
        f'it is likely a person like {agent_name} would respond, and taking '
        f'into account all information about {agent_name} that you have. '
        'Always use third-person limited perspective.'
    )
    super().__init__(state=state, pre_act_label=pre_act_label)
