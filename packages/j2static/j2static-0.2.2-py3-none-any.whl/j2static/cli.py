#! /usr/bin/env python3

import argparse
from j2static.main import generate
from j2static.webserver import serve

_options = {
    'generate': generate,
    'serve': serve
}


def main():
    """Main Entrypoint for CLI"""
    parser = argparse.ArgumentParser("static site generator.")
    parser.add_argument('action', choices=_options.keys())

    # inputs
    parser.add_argument('--template-dir', default="_templates/")
    parser.add_argument('--data-dir', default="_data/")
    parser.add_argument('--static-dir', default="_static/")

    # outputs
    parser.add_argument('--out-dir', default="site/")

    args = parser.parse_args()

    chosen_action = _options[args.action]
    chosen_action(args)


if __name__ == "__main__":
    main()
