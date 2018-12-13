#!/usr/bin/env python
'''This prgoam renders your jinja
Usage:  python jinjaRender.py filename 
Optional arguments:
    -p --path /path/to/dir/
    
jinjaRender.jinjaRender(filename, path)
'''

def main():
    '''For command line use calls parser and prints return
    '''
    args = parser()
    print(jinjaRender(args.filename, args.path))
    return

def parser():
    '''This function just loads the argmunts by default the assumption 
    is made that the target template exists in the programs working 
    directory
    '''
    import argparse
    parser = argparse.ArgumentParser(description='Jinja Renderer.')
    parser.add_argument("filename", help='File-name', type=str)
    parser.add_argument('-p', "--path",
            help="The absolute path to the directory your template resides in",
            default="./", type=str)
    return parser.parse_args()

def jinjaRender(filename, path):
    '''This function pulls a template from an absolute path and atempts to 
    render it providing the results.
    '''
    import jinja2
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(path))
    template = env.get_template(filename)
    return template.render() 

if __name__ == '__main__':
    main()
