import pytest

from common.helpers import slugify_function


@pytest.mark.parametrize(
    "text,expected_slug",
    (
        ("privet, kak dela?", "privet-kak-dela"),
        ("Привет, как дела?", "privet-kak-dela"),
    ),
)
def test_slugify_function(text, expected_slug):
    assert slugify_function(text) == expected_slug
