from slugify import Slugify, CYRILLIC


def slugify_function(text: str) -> str:
    slugify = Slugify(pretranslate=CYRILLIC)
    return slugify(text).lower()
