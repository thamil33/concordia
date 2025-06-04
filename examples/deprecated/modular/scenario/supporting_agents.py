
"""Configure specific supporting agent instances for use in substrates."""

from collections.abc import Mapping
import dataclasses
from typing import Any

from concordia.contrib.components.game_master.deprecated import industrial_action
from examples.deprecated.modular.environment.modules import wild_west_railroad_construction_labor
import immutabledict


@dataclasses.dataclass(frozen=True)
class SupportingAgentConfig:
  """Class for configuring a supporting agent.

  Attributes:
    module_name: the name of the supporting agent module to load and use.
    overrides: a mapping of kwarg names to values to override.
  """

  module_name: str
  overrides: Mapping[str, Any] | None = None


below_pressure_threshold_wild_west = industrial_action.get_pressure_str(
    pressure=0.0,
    pressure_threshold=wild_west_railroad_construction_labor.PRESSURE_THRESHOLD,
)
at_pressure_threshold_wild_west = industrial_action.get_pressure_str(
    pressure=wild_west_railroad_construction_labor.PRESSURE_THRESHOLD,
    pressure_threshold=wild_west_railroad_construction_labor.PRESSURE_THRESHOLD,
)
max_pressure_wild_west = industrial_action.get_pressure_str(
    pressure=1.0,
    pressure_threshold=wild_west_railroad_construction_labor.PRESSURE_THRESHOLD,
)


SUPPORTING_AGENT_CONFIGS: Mapping[str, SupportingAgentConfig] = (
    immutabledict.immutabledict(
        # keep-sorted start numeric=yes block=yes
        labor_collective_action__fixed_rule_boss=SupportingAgentConfig(
            module_name='basic_puppet_agent',
            overrides=immutabledict.immutabledict(
                fixed_response_by_call_to_action=immutabledict.immutabledict({
                    below_pressure_threshold_wild_west: (
                        wild_west_railroad_construction_labor.BOSS_OPTIONS[
                            'hold firm']),
                    at_pressure_threshold_wild_west: (
                        wild_west_railroad_construction_labor.BOSS_OPTIONS[
                            'hold firm']),
                    max_pressure_wild_west: (
                        wild_west_railroad_construction_labor.BOSS_OPTIONS[
                            'cave to pressure'])
                }),
                search_in_prompt=True,
            ),
        )
    )
)
