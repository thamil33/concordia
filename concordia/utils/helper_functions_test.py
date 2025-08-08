

import unittest

from absl.testing import absltest
from concordia.prefabs.entity import basic
from concordia.utils import helper_functions

EXPECTED_OUTPUT_STANDARD_CASE = """
---
**`basic__Entity`**:
```python
Entity(
    description='An entity.',
    params={'name': 'Logan', 'goal': ''}
)
```
---
""".strip()


class TestPrettyPrintFunction(unittest.TestCase):

  def test_empty_dictionary(self):
    """Tests that an empty dictionary returns the correct placeholder string."""
    self.assertEqual(
        first=helper_functions.print_pretty_prefabs({}),
        second='(The dictionary is empty)',
    )

  def test_standard_case_with_filtering(self):
    """Tests a standard case with two objects, ensuring 'entities=None' and 'entities=()' are correctly filtered out."""
    test_dict = {
        'basic__Entity': basic.Entity(
            description='An entity.',
            params={'name': 'Logan', 'goal': ''},
            entities=None,
        )
    }
    self.assertEqual(
        helper_functions.print_pretty_prefabs(test_dict),
        EXPECTED_OUTPUT_STANDARD_CASE,
    )


if __name__ == '__main__':
  absltest.main()
