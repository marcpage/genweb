#!/usr/bin/env python3


""" Hanldes loading and saving of metadta """


from yaml import safe_load


OPEN = open


def load(path: str) -> dict:
    with OPEN(path, "r", encoding="utf-8") as file:
        return safe_load(file)
