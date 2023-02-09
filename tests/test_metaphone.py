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
        assert double_metaphone(name) == metaphone, f"{name} => {double_metaphone(name)}"


def test_homophones():
    names = [
        ('Marc', 'Mark'),
        ('Jon', 'John'),
        ('Mathew', 'Matthew'),
        # Wasserman should match Vasserman
        # ('Wasserman', 'Vasserman'), Wasserman (('ASRMN', 'FSRMN')) <> Vasserman (('FSRMN', None))
        # german & anglicisations, e.g. 'smith' match 'schmidt', 'snider' match 'schneider'
        # ('smith', 'schmidt'), smith (('SM0', 'XMT')) <> schmidt (('XMT', 'SMT'))
        # ('snider', 'schneider'), snider (('SNTR', 'XNTR')) <> schneider (('XNTR', 'SNTR'))
        # Arnow should match Arnoff
        # ('Arnow', 'Arnoff'), Arnow (('ARN', 'ARNF')) <> Arnoff (('ARNF', None))
    ]
    for phone1, phone2 in names:
        assert double_metaphone(phone1) == double_metaphone(phone2), (
            f'{phone1} ({double_metaphone(phone1)}) <> {phone2} ({double_metaphone(phone2)})'
        )


def test_add_coverage():
    """ For word ideas: /usr/share/dict/words """
    names = {
        "Arnoff": ('ARNF', None),
        "Arnow": ('ARN', 'ARNF'),
        "Jankelowicz": ('JNKLTS', 'ANKLFX'),
        "McLaughlin": ('MKLFLN', None),
        "Mcintosh": ('MSNTX', None),
        "Mclochland": ('MKLKLNT', None),
        "Vasserman": ('FSRMN', None),
        "Wasserman": ('ASRMN', 'FSRMN'),
        "Xander": ('SNTR', None),
        "Yankelovich": ('ANKLFX', 'ANKLFK'),
        "bajador": ('PJTR', 'PHTR'),
        "blubber": ('PLPR', None),
        "breaux": ('PR', None),
        "cabrillo": ('KPRL', 'KPR'),
        "caesar": ('SSR', None),
        "cagney": ('KKN', None),
        "campbell": ('KMPL', None),
        "carlisle": ('KRLL', None),
        "carlysle": ('KRLL', None),
        "caucasian": ('KKSN', 'KKXN'),
        "chaetopods": ('XTPTS', None),
        "chalk": ('XLK', None),
        "charac": ('KRK', None),
        "chianti": ('KNT', None),
        "chord": ('KRT', None),
        "cough": ('KF', None),
        "edge": ('AJ', None),
        "filipowicz": ('FLPTS', 'FLPFX'),
        "gallegos": ('KLKS', 'KKS'),
        "ghiradelli": ('JRTL', None),
        "ghislane": ('JLN', None),
        "gigi": ('JJ', 'KK'),
        "gough": ('KF', None),
        "hochmeier": ('HKMR', None),
        "hugh": ('H', None),
        "island": ('ALNT', None),
        "isle": ('AL', None),
        "jose": ('HS', None),
        "knox": ('NKS', None),
        "laugh": ('LF', None),
        "medrinaque": ('MTRNK', None),
        "menognath": ('MNN0', 'MNKNT'),
        "michael": ('MKL', 'MXL'),
        "middleweight": ('MTLT', None),
        "misaccent": ('MSXNT', None),
        "nation": ('NXN', None),
        "pizza": ('PS', 'PTS'),
        "raspberry": ('RSPR', None),
        "resnais": ('RSN', 'RSNS'),
        "resucceed": ('RSKST', None),
        "rizzle": ('RSL', None),
        "rogier": ('RJ', 'RJR'),
        "rough": ('RF', None),
        "san jacinto": ('SNHSNT', None),
        "saxcornet": ('SKSRNT', None),
        "scene": ('SN', None),
        "schenker": ('XNKR', 'SKNKR'),
        "schermerhorn": ('XRMRRN', 'SKRMRRN'),
        "schmidt": ('XMT', 'SMT'),
        "schneider": ('XNTR', 'SNTR'),
        "school": ('SKL', None),
        "schooner": ('SKNR', None),
        "science": ('SNS', None),
        "sivvens": ('SFNS', None),
        "smith": ('SM0', 'XMT'),
        "snider": ('SNTR', 'XNTR'),
        "solatia": ('SLX', None),
        "sugar": ('XKR', 'SKR'),
        "thames": ('TMS', None),
        "thomas": ('TMS', None),
        "tough": ('TF', None),
        "veszelyite": ('FSLT', 'FXLT'),
        "write": ('RT', None),
        "zhao": ('J', None),
        "Mckay": None,
        "Piotrowicz": None,
        "Staszczyk": None,
        "mechanician": None,
        "bellocchio": None,
        "bacchus": None,
        "accident": None,
        "accede": None,
        "succeed": None,
        "mac caffrey": None,
        "mac gregor": None,
        "nonacquiescence": None,
        "cause": None,
        "Çelik": None,
        "odor": None,
        "noncostraight": None,
        "ghost": None,
        "obsignate": None,
        "oligodendroglia": None,
        "geyser": None,
        "DANGER": None,
        "RANGER": None,
        "MANGER": None,
        "haggis": None,
        "Joseph": None,
        "hajilij": None,
        "mujtahid": None,
        "Zulhijjah": None,
        "Akkad": None,
        "mumbler": None,
        "mummy": None,
        "Muñoz": None,
        "Joseph": None,
        "zaqqum": None,
        "Deidesheimer": None,
        "Deimos": None,
        "dentiscalp": None,
        "Wright": None,
        "Wabunga": None,
    }

    for name, metaphone in sorted(names.items()):
        print(f'        "{name}": {double_metaphone(name)},')
        #assert double_metaphone(name) == metaphone, f"{name} => {double_metaphone(name)}"


if __name__ == "__main__":
    test_double_metaphone()
    test_homophones()
    test_add_coverage()

