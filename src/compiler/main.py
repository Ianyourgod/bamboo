import pprint
import sys
import os
 
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from parsing.lex import lex
from parsing.parse import parse
from intermediateCompile import compile as icompile

def run(text):
    tokens = lex(text)
    tree = parse(tokens)
    return icompile(tree)

if __name__ == "__main__":
    args = sys.argv[1:]
    mode = "run"
    code = ""

    for arg in args:
        if arg == "-h" or arg == "--help":
            print("Usage: python3 -m compiler [options] [file]")
            print("Options:")
            print("  -h, --help: Display this help message")
            print("  -t  --test: test the compiler")
        elif arg == "-t" or arg == "--test":
            mode = "test"
        else:
            with open(arg, "r") as f:
                code = f.read()
            mode = "frun"

    if mode == "run":
        code = input(">>> ")

    if mode == "frun" or mode == "run":
        print(run(code))

    if mode == "test":
        try:
            print("tokens:")
            pprint.pprint(lex(code))
            print("ast:")
            pprint.pprint(parse(lex(code)))
            print("intermediate code:")
            pprint.pprint(icompile(parse(lex(code))))
        except Exception as e:
            print(f"Error: {e}")