from CONSTS import KEYWORDS
from errorHandler import ExpectedChar

def parse(tokens):
    parser = Parser(tokens)
    return parser.parse()

class Node:
    def __init__(self, type, left, right=None):
        self.type = type
        self.left = left
        self.right = right
    
    def __repr__(self):
        return f"(type: {self.type}, {self.left}, {self.right})" if self.right else f"(type: {self.type}, {self.left})"
    

class Parser:
    def __init__(self, tokens: list):
        self.tokens = tokens
        self.pos = -1
        self.current_token = None
        self.ast = []
        self.advance()

    def advance(self):
        self.pos += 1
        self.current_token = self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def parse(self):
        
        while self.pos < len(self.tokens):
            self.ast.append(self.expr())
            if (not self.current_token or self.current_token.name != "semicolon"):
                raise ExpectedChar("semicolon", self.current_token.name if self.current_token else "EOF")
            self.advance()
        return self.ast
    
    def expr(self):
        node = self.conditionals()
        if self.current_token and self.current_token.name == "assign":
            self.advance()
            node = Node("assign", node, self.conditionals())
        elif self.current_token  and self.current_token.name == "if":
            node = self.if_statement()
            elifs = []
            while self.current_token and self.current_token.name == "else":
                self.advance()
                if self.current_token and self.current_token.name == "if":
                    tnode = self.if_statement()
                    tnode.type = "else if"
                    elifs.append(tnode)
                elif self.current_token and self.current_token.name == "lbrace":
                    tnode = Node("else", self.code_block())
                    elifs.append(tnode)
                    break
                else:
                    raise ExpectedChar("if or lbrace", self.current_token.name)
            if elifs:
                for i, elif_ in enumerate(elifs):
                    if i == 0:
                        node.right[1] = elif_
                    else:
                        elifs[i - 1].right[1] = elif_
            
        elif self.current_token and self.current_token.name == "while":
            self.advance()
            cond = self.conditionals()
            if self.current_token and self.current_token.name == "lbrace":
                code = self.code_block()
                node = Node("while", cond, code)
            else:
                raise ExpectedChar("rbrace", self.current_token.name)
            
        elif self.current_token and self.current_token.name == "for":
            self.advance()
            
            if not (self.current_token and self.current_token.name == "identifier"):
                raise ExpectedChar("identifier", self.current_token.name)
            
            var = self.current_token.value

            self.advance()
            if not (self.current_token and self.current_token.name == "in"):
                raise ExpectedChar("in", self.current_token.name)
            
            self.advance()
            iter = self.conditionals()
            
            if not (self.current_token and self.current_token.name == "lbrace"):
                raise ExpectedChar("lbrace", self.current_token.name)
            
            self.advance()
            code = self.code_block()
            node = Node("for", [var, iter], code)

            
        elif self.current_token and self.current_token.name == "define":
            node = self.define_statement()
            
        elif self.current_token and self.current_token.name == "return":
            self.advance()
            node = Node("return", self.expr())

        return node
    def conditionals(self):
        node = self.term()
        while self.current_token and self.current_token.name in ["eq", "neq", "gte", "gt", "lte", "lt", "and", "or"]:
            node_name = self.current_token.name
            self.advance()
            node = Node(node_name, node, self.term())
        return node
    def term(self):
        node = self.factor()
        while self.current_token and self.current_token.name in ["add", "sub", "not"]:
            if self.current_token.name == "add":
                self.advance()
                node = Node("add", node, self.factor())
            elif self.current_token.name == "sub":
                self.advance()
                node = Node("sub", node, self.factor())
        return node
    def factor(self):
        node = self.atom()
        while self.current_token and self.current_token.name in ["mul", "div"]:
            if self.current_token.name == "mul":
                self.advance()
                node = Node("mul", node, self.atom())
            elif self.current_token.name == "div":
                self.advance()
                node = Node("div", node, self.atom())
        return node
    def atom(self):
        if self.current_token:
            match self.current_token.name:
                case "number":
                    node = Node("number", self.current_token.value)
                    self.advance()
                    return node
                case "sub":
                    self.advance()
                    node = Node("sub", Node("number", 0), Node("number",self.current_token.value))
                    self.advance()
                    return node
                case "string":
                    node = Node("string", self.current_token.value)
                    self.advance()
                    return node
                case "identifier":
                    name = self.current_token.value
                    self.advance()
                    if self.current_token and self.current_token.name == "lparen":
                        node = self.call_statement(name)
                    else:
                        node = Node("identifier", name)
                    return node
                case "true":
                    node = Node("bool", True)
                    self.advance()
                    return node
                case "false":
                    node = Node("bool", False)
                    self.advance()
                    return node
                case "none":
                    node = Node("none", None)
                    self.advance()
                    return node
                case "not":
                    self.advance()
                    node = Node("not", self.atom())
                    return node
                case "lparen":
                    self.advance()
                    node = self.expr()
                    if self.current_token.name != "rparen":
                        raise ExpectedChar(")", self.current_token.name)
                    self.advance()
                    return node
            if self.current_token.name in KEYWORDS:
                return
        raise ExpectedChar("number, string, identifier, bool, none, or lparen", self.current_token.name)
    
    def if_statement(self):
        self.advance()
        cond = self.conditionals()
        if self.current_token and self.current_token.name == "lbrace":
            code = self.code_block()
            node = Node("if", cond, [code, None])
        else:
            raise ExpectedChar("rbrace", self.current_token.name)
        return node
        
    def call_statement(self, name):
        self.advance()
        args = []
        args_temp = []
        paren_count = 1
        while self.current_token:
            if self.current_token.name == "lparen":
                paren_count += 1
            elif self.current_token.name == "rparen":
                paren_count -= 1
                if paren_count == 0:
                    break
            args_temp.append(self.current_token)
            self.advance()
            if self.current_token and self.current_token.name == "comma" and paren_count == 1:
                args.append(args_temp)
                self.advance()
                args_temp = []
        if args_temp:
            args.append(args_temp)
        self.advance()
        args_temp = []
        for i in args:
            new_parse = Parser(i)
            args_temp.append(new_parse.expr())
        node = Node("call", name, args_temp)
        return node
        
        
    def define_statement(self):
        self.advance()
        name = self.current_token.value
        self.advance()
        if self.current_token.name == "lparen":
            self.advance()
            args = []
            args_temp = []
            while self.current_token and self.current_token.name != "rparen":
                args_temp.append(self.current_token)
                self.advance()
                if self.current_token.name == "comma":
                    args.append(args_temp)
                    self.advance()
                    args_temp = []
            if args_temp:
                args.append(args_temp)
            self.advance()
            args_temp = []
            for i in args:
                new_parse = Parser(i)
                args_temp.append(new_parse.expr().left)
            if self.current_token.name == "lbrace":
                code = self.code_block()
                node = Node("define", name, [args_temp, code])
            else:
                raise ExpectedChar("lbrace", self.current_token.name)
        else:
            raise ExpectedChar("lparen", self.current_token.name)
        return node
    
    def code_block(self):
        brace_count = 1
        self.advance()
        code = []
        while brace_count > 0:
            code.append(self.current_token)
            self.advance()
            if self.current_token.name == "lbrace":
                brace_count += 1
            elif self.current_token.name == "rbrace":
                brace_count -= 1
        self.advance()
        new_parse = Parser(code)
        return new_parse.parse()
        