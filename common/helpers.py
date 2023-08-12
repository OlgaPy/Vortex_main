from slugify import CYRILLIC, Slugify


def slugify_function(text: str) -> str:
    """Slugify text, also works with cyrillic letters."""
    slugify = Slugify(pretranslate=CYRILLIC)
    return slugify(text).lower()
