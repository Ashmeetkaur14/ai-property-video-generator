import re

# Fixed words our templates use. Anything else must come from the input.
TEMPLATE_WORDS = {
    "introducing", "a", "an", "in", "priced", "at",
    "book", "your", "visit", "contact", "us", "to", "know", "more",
}


def _words(text):
    return set(re.findall(r"[a-z]+", text.lower()))


def _numbers(text):
    return set(re.findall(r"\d+(?:\.\d+)?", text))


def source_text(prop):
    """All the facts the user gave us, joined into one text."""
    parts = [prop.get(k, "") for k in ("name", "location", "type", "price", "cta")]
    parts += prop.get("features", [])
    return " ".join(str(p) for p in parts)


def fact_check(prop, scenes):
    """Return a list of problems. An empty list means the script is clean."""
    src = source_text(prop)
    allowed_words = _words(src) | TEMPLATE_WORDS
    allowed_numbers = _numbers(src)

    problems = []
    for i, scene in enumerate(scenes, 1):
        for field in ("caption", "subtitle", "voice"):
            text = scene.get(field, "")
            for n in sorted(_numbers(text) - allowed_numbers):
                problems.append(f"Scene {i} ({field}): number '{n}' is not in the input")
            for w in sorted(_words(text) - allowed_words):
                problems.append(f"Scene {i} ({field}): word '{w}' is not in the input")
    return problems