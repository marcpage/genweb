#!/usr/bin/env python3

""" noops to remove cleanup from test coverage output """


import genweb.cleanup


def run_cleanup() -> None:
    genweb.cleanup.DRY_RUN = True
    genweb.cleanup.MAKEDIRS = lambda d: d
    genweb.cleanup.MOVE = lambda s, d: (s, d)
    genweb.cleanup.main()
    genweb.cleanup.DRY_RUN = False
    genweb.cleanup.main()


if __name__ == "__main__":
    run_cleanup()
