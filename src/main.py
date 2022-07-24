import sys
from antlr4 import *
from parser.generated.HerbLexer import HerbLexer
from parser.generated.HerbParser import HerbParser


def main(argv):
    input_stream = FileStream("programs/import.herb")
    print(input_stream)
    lexer = HerbLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = HerbParser(stream)
    tree = parser.prog()
    print(tree)


if __name__ == '__main__':
    main(sys.argv)