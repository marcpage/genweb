#!/usr/bin/env python3


from genweb.metaphone import double_metaphone


def test_double_metaphone():
    names = {
        "maurice": ("MRS", None),
        "aubrey": ("APR", None),
        "cambrillo": ("KMPRL", "KMPR"),
        "heidi": ("HT", None),
        "katherine": ("K0RN", "KTRN"),
        "Thumbail": ("0MPL", "TMPL"),
        "catherine": ("K0RN", "KTRN"),
        "richard": ("RXRT", "RKRT"),
        "bob": ("PP", None),
        "eric": ("ARK", None),
        "geoff": ("JF", "KF"),
        "Through": ("0R", "TR"),
        "Schwein": ("XN", "XFN"),
        "dave": ("TF", None),
        "ray": ("R", None),
        "steven": ("STFN", None),
        "bryce": ("PRS", None),
        "randy": ("RNT", None),
        "bryan": ("PRN", None),
        "Rapelje": ("RPL", None),
        "brian": ("PRN", None),
        "otto": ("AT", None),
        "auto": ("AT", None),
        "Dallas": ("TLS", None),
        "maisey": ("MS", None),
        "zhang": ("JNK", None),
        "Chile": ("XL", None),
        "Jose": ("HS", None),
        "Arnow": ("ARN", "ARNF"),
        "solilijs": ("SLLS", None),
        "Parachute": ("PRKT", None),
        "Nowhere": ("NR", None),
        "Tux": ("TKS", None),
        "80210": ("", None),
        "1600": ("", None),
        "Pennsylvania": ("PNSLFN", None),
        "Ave": ("AF", None),
        "Avenue": ("AFN", None),
    }

    for name, metaphone in names.items():
        print(f"name = {name}, Metaphone = {double_metaphone(name)}")
        assert double_metaphone(name) == metaphone


def test_homophones():
    assert double_metaphone("Marc") == double_metaphone("Mark")
    assert double_metaphone("Jon") == double_metaphone("John")
    assert double_metaphone("Mathew") == double_metaphone("Matthew")


if __name__ == "__main__":
    test_double_metaphone()
    test_homophones()
