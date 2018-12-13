#!/usr/bin/env python

def main():
    import jinja2
    args = parser()
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(args.path))
    template = env.get_template(args.filename)
    rtemplate = template.render()
    print(rtemplate)

def parser():
    import argparse
    parser = argparse.ArgumentParser(description='Jinja Renderer.')
    parser.add_argument("filename", help='File-name', type=str)
    parser.add_argument('-p', "--path",
            help="The absolute path to the directory your template resides in",
            default="./", type=str)
    return parser.parse_args()

if __name__ == '__main__':
    main()
