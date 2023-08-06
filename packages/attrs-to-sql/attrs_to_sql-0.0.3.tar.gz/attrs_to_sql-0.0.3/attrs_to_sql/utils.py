import re


def camelcase_to_underscore(camelcase: str) -> str:
    """https://stackoverflow.com/a/1176023"""
    underscored = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", camelcase)
    underscored = re.sub("([a-z0-9])([A-Z])", r"\1_\2", underscored)
    lowered = underscored.lower()
    return lowered
