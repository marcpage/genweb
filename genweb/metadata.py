#!/usr/bin/env python3


""" Hanldes loading and saving of metadta """


from yaml import safe_load


def validate(metadata: dict[str, dict]) -> dict[str, dict]:
    """Validates that the metadata is correct

    Args:
        metadata (dict[str, dict]): The loaded metadata

    Returns:
        dict[str, dict]: Just returns the metadata so you can chain calls
    """
    return metadata


def load_yaml(path: str) -> dict[str, dict]:
    """Loads a yaml file

    Args:
        path (str): The path to the yaml file

    Returns:
        dict[str, dict]: The data loaded from the yaml file
    """
    with open(path, "r", encoding="utf-8") as file:
        return safe_load(file)


def load(path: str) -> dict[str, dict]:
    """Loads a metadata yaml file

    Args:
        path (str): The path to the metadata yaml file

    Returns:
        dict[str, dict]: The metadata
    """
    return validate(load_yaml(path))
