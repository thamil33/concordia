

"""Tests that "import examples" will work."""

from absl.testing import absltest


class PlaceholderTest(absltest.TestCase):

  def test_import(self):
    import examples  # pylint: disable=g-import-not-at-top,import-outside-toplevel
    del examples


if __name__ == "__main__":
  absltest.main()
