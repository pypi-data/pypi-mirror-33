import argparse
from pageshot.converter import to_png
from pygments import highlight
from pygments.formatters import HtmlFormatter, ImageFormatter
from pygments.lexers import PythonLexer

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", help="page url", dest="url")
    parser.add_argument("--outfile", help="output image location", dest="outfile")
    args = parser.parse_args()

    if args.url is None:
        parser.error("--url requires an argument")

    url = args.url
    outfile = args.outfile if args.outfile is not None else "page.png"
    to_png(url, outfile)
