import sys
import os
 
# getting the name of the directory
# where the this file is present.
current = os.path.dirname(os.path.realpath(__file__))
 
# Getting the parent directory name
# where the current directory is present.
parent = os.path.dirname(current)
 
# adding the parent directory to
# the sys.path.
sys.path.append(parent)

from CONSTS import *
from errorHandler import UnknownChar, TooManyDecimalPoints


def lex(text):
    lexer = Lexer(text)
    tokens = lexer.tokenize()
    return tokens

class Token:
    def __init__(self, name, value=None):
        self.name = name
        self.value = value
        
    def __repr__(self):
        return f"Token({self.name}, {self.value})" if self.value else f"Token({self.name})"
    
    def __str__(self):
        return f"Token({self.name}, {self.value})" if self.value else f"Token({self.name})"

class Lexer:
    def __init__(self, text):
        self.text = text
        self.tokens = []
        self.pos = -1
        self.current_char = None
        self.advance()
        
    def advance(self):
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None
        
    def tokenize(self):
        while self.pos < len(self.text):
            if self.current_char in WHITESPACE:
                self.advance()
            elif self.current_char in CHARS:
                word = ""
                while self.pos < len(self.text) and self.current_char in CHARS + DIGITS:
                    word += self.current_char
                    self.advance()
                if word in KEYWORDS:
                    self.tokens.append(Token(word))
                else:
                    self.tokens.append(Token("identifier", word))
            elif self.current_char in DIGITS:
                numb = ""
                dots = 0
                while self.pos < len(self.text) and self.current_char in DIGITS + ".":
                    numb += self.current_char
                    if self.current_char == ".":
                        dots += 1
                    if dots > 1:
                        raise TooManyDecimalPoints()
                    self.advance()
                if dots == 0:
                    self.tokens.append(Token("number", int(numb)))
                else:
                    self.tokens.append(Token("number", float(numb)))
            elif self.current_char in ('"', "'"):
                check = self.current_char
                self.advance()
                string = ""
                while self.pos < len(self.text) and self.current_char != check:
                    string += self.current_char
                    self.advance()
                if self.current_char != check:
                    raise Exception("Invalid string")
                self.advance()
                self.tokens.append(Token("string", string))
            elif self.current_char == "+":
                self.advance()
                if self.current_char == "+":
                    self.advance()
                    self.tokens.append(Token("add-one"))
                elif self.current_char == "=":
                    self.advance()
                    self.tokens.append(Token("add-eq"))
                else:
                    self.tokens.append(Token("add"))
            elif self.current_char == "-":
                self.advance()
                if self.current_char == "-":
                    self.advance()
                    self.tokens.append(Token("sub-one"))
                elif self.current_char == "=":
                    self.advance()
                    self.tokens.append(Token("sub-eq"))
                else:
                    self.tokens.append(Token("sub"))
            elif self.current_char == "*":
                self.advance()
                if self.current_char == "=":
                    self.advance()
                    self.tokens.append(Token("mul-eq"))
                else:
                    self.tokens.append(Token("mul"))
            elif self.current_char == "/":
                self.advance()
                if self.current_char == "=":
                    self.advance()
                    self.tokens.append(Token("div-eq"))
                else:
                    self.tokens.append(Token("div"))
            elif self.current_char == "%":
                self.advance()
                if self.current_char == "=":
                    self.advance()
                    self.tokens.append(Token("mod-eq"))
                else:
                    self.tokens.append(Token("mod"))
            elif self.current_char == "=":
                self.advance()
                if self.current_char == "=":
                    self.advance()
                    self.tokens.append(Token("eq"))
                else:
                    self.tokens.append(Token("assign"))
            elif self.current_char == "!":
                self.advance()
                if self.current_char == "=":
                    self.advance()
                    self.tokens.append(Token("neq"))
                else:
                    self.tokens.append(Token("not"))
            elif self.current_char == ">":
                self.advance()
                if self.current_char == "=":
                    self.advance()
                    self.tokens.append(Token("gte"))
                else:
                    self.tokens.append(Token("gt"))
            elif self.current_char == "<":
                self.advance()
                if self.current_char == "=":
                    self.advance()
                    self.tokens.append(Token("lte"))
                else:
                    self.tokens.append(Token("lt"))
            elif self.current_char == "&":
                self.advance()
                if self.current_char == "&":
                    self.advance()
                    self.tokens.append(Token("and"))
                else:
                    raise Exception("Invalid token")
            elif self.current_char == "|":
                self.advance()
                if self.current_char == "|":
                    self.advance()
                    self.tokens.append(Token("or"))
                else:
                    raise Exception("Invalid token")
            elif self.current_char == "(":
                self.advance()
                self.tokens.append(Token("lparen"))
            elif self.current_char == ")":
                self.advance()
                self.tokens.append(Token("rparen"))
            elif self.current_char == "{":
                self.advance()
                self.tokens.append(Token("lbrace"))
            elif self.current_char == "}":
                self.advance()
                self.tokens.append(Token("rbrace"))
            elif self.current_char == "[":
                self.advance()
                self.tokens.append(Token("lbracket"))
            elif self.current_char == "]":
                self.advance()
                self.tokens.append(Token("rbracket"))
            elif self.current_char == ",":
                self.advance()
                self.tokens.append(Token("comma"))
            elif self.current_char == ":":
                self.advance()
                self.tokens.append(Token("colon"))
            elif self.current_char == ";":
                self.advance()
                self.tokens.append(Token("semicolon"))
            else:
                raise UnknownChar(self.current_char)
        return self.tokens
    
if __name__ == "__main__":
    while True:
        code = input("bamboo lexer >>> ")
        if code == "exit":
            break
        print(lex(code))
