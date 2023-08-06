#! /usr/bin/env python3
##
# Extra CLI modes
##

import argparse

from j2static.tools import merge, marks

TEMPLATE_MAPPINGS = {
	"pdf": "tex",
	"html": "html",
	"tex": "tex",
        "txt": "txt"
}


def _parent():
    parser = argparse.ArgumentParser(add_help=False)

    # inputs
    parser.add_argument('--template-dir', default="_templates/")
    parser.add_argument('--data-dir', default="_data/")
    parser.add_argument('--static-dir', default="_static/")

    # outputs
    parser.add_argument('--out-dir', default="site/")
    return parser


def main():
    """J2 Mail Merge mode"""
    parser = argparse.ArgumentParser(parents=[_parent()])

    parser.add_argument("source", help='the source for the merge')
    parser.add_argument("--mode", default="csv", choices=["csv", "dir"], help='the way in which source should be intepreted')
    parser.add_argument("--builder", default="html", choices=TEMPLATE_MAPPINGS.keys(), help='the converter to use for outputting')
    parser.add_argument("--template", default=None, help='the template to use')
    parser.add_argument("--context", default=[], help='extra files to pass to the template')

    args = parser.parse_args()

    context = {}
    if args.context:
        context.update( merge.load_data(args.context) )

    # if a template is not provided, but a builder is, try to guess the template name
    if args.builder and not args.template:
        args.template = "base."+TEMPLATE_MAPPINGS[args.builder]

    if args.mode == "csv":
        data = merge.merge_csv(args.source, callback=marks.deflatten)
    elif args.mode == "dir":
        data = merge.merge_dir(args.source)
    else:
        raise ValueError("unknown mode")

    merge.write_dict(data, context=context, template=args.template, out_type=args.builder)
    

if __name__ == "__main__":
    main()
