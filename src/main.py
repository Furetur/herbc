import sys
from antlr4 import *
from src.parser.generated.HerbLexer import HerbLexer
from src.parser.generated.HerbParser import HerbParser
from src.parser.parser import parse


def main(argv):
    file = parse("programs/import.herb")
    print(file)


if __name__ == '__main__':
    main(sys.argv)