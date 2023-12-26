# a block will look like:
# {
#   "type": "block",
#   "opcode": "operator_add",
#   "args": [
#       {
#           "type": "input",
#           "value": "1"
#       },
#       {
#           "type": "input",
#           "value": "2"
#       }
#   ]
# }

builtins = {
    "say": "looks_say",
    "wait": "control_wait"
}

class ICompiler:
    def __init__(self) -> None:
        self.out = []

    def block(self, opcode: str, args: list):
        return {
            "type": "block",
            "opcode": opcode,
            "args": args
        }
    
    def cblock(self, opcode: str, args: list, code, code2=None):
        return {
            "type": "cblock",
            "opcode": opcode,
            "args": args,
            "code": code,
            "code2": code2
        }
    
    def hat(self, opcode: str, args: list, code):
        return {
            "type": "hat",
            "opcode": opcode,
            "args": args,
            "code": code
        }
    
    def value(self, value: str):
        return {
            "type": "input",
            "value": value
        }

    def compile(self, ast: list):
        self.out = []
        self.ast = ast

        for self.node in ast:
            self.out.append(self.compileNode(self.node))

        return self.out
    
    def compileNode(self, node):
        if node.type == "add":
            return self.block(
                "operator_add",
                [
                    self.compileNode(node.left),
                    self.compileNode(node.right)
                ]
            )
        elif node.type == "sub":
            return self.block(
                "operator_subtract",
                [
                    self.compileNode(node.left),
                    self.compileNode(node.right)
                ]
            )
        elif node.type == "mul":
            return self.block(
                "operator_multiply",
                [
                    self.compileNode(node.left),
                    self.compileNode(node.right)
                ]
            )
        elif node.type == "div":
            return self.block(
                "operator_divide",
                [
                    self.compileNode(node.left),
                    self.compileNode(node.right)
                ]
            )
        elif node.type == "assign":
            return self.block(
                "data_setvariableto",
                [
                    self.value(node.left),
                    self.compileNode(node.right)
                ]
            )
        elif node.type == "if":
            tempCompiler = ICompiler()
            return self.cblock(
                "control_if",
                [
                    self.compileNode(node.left)
                ],
                tempCompiler.compile(node.right[0]),
                self.compileNode(node.right[1]) if node.right[1] else None
            )
        elif node.type == "else if":
            tempCompiler = ICompiler()
            return self.cblock(
                "control_if",
                [
                    self.compileNode(node.left)
                ],
                tempCompiler.compile(node.right[0]),
                self.compileNode(node.right[1]) if node.right[1] else None
            )
        elif node.type == "else":
            tempCompiler = ICompiler()
            return tempCompiler.compile(node.left)
        elif node.type == "eq":
            return self.block(
                "operator_equals",
                [
                    self.compileNode(node.left),
                    self.compileNode(node.right)
                ]
            )
        elif node.type == "neq":
            self.block(
                "operator_notequals",
                [
                    self.compileNode(node.left),
                    self.compileNode(node.right)
                ]
            )
        elif node.type == "gt":
            return self.block(
                "operator_gt",
                [
                    self.compileNode(node.left),
                    self.compileNode(node.right)
                ]
            )
        elif node.type == "gte":
            return self.block(
                "operator_gte",
                [
                    self.compileNode(node.left),
                    self.compileNode(node.right)
                ]
            )
        elif node.type == "lt":
            return self.block(
                "operator_lt",
                [
                    self.compileNode(node.left),
                    self.compileNode(node.right)
                ]
            )
        elif node.type == "lte":
            return self.block(
                "operator_lte",
                [
                    self.compileNode(node.left),
                    self.compileNode(node.right)
                ]
            )
        elif node.type == "and":
            return self.block(
                "operator_and",
                [
                    self.compileNode(node.left),
                    self.compileNode(node.right)
                ]
            )
        elif node.type == "or":
            return self.block(
                "operator_or",
                [
                    self.compileNode(node.left),
                    self.compileNode(node.right)
                ]
            )
        elif node.type == "not":
            return self.block(
                "operator_not",
                [
                    self.compileNode(node.left)
                ]
            )
        elif node.type == "call":
            if node.left in builtins:
                return self.block(
                    builtins[node.left],
                    [self.compileNode(arg) for arg in node.right]
                )
            else:
                tempCompiler = ICompiler()
                return self.block(
                    "procedures_call",
                    [
                        self.value(node.left),
                        tempCompiler.compile(node.right)
                    ] 
                )
        elif node.type == "define":
            tempCompiler = ICompiler()
            return self.hat(
                "procedures_definition",
                [node.right[0]],
                tempCompiler.compile(node.right[1])
            )
        elif node.type == "return":
            return self.block(
                "procedures_return",
                [
                    self.compileNode(node.left)
                ]
            )
        elif node.type == "for":
            tempCompiler = ICompiler()
            return self.cblock(
                "control_for_each",
                [
                    node.left[0],
                    self.compileNode(node.left[1])
                ],
                tempCompiler.compile(node.right)
            )
        elif node.type == "while":
            tempCompiler = ICompiler()
            return self.cblock(
                "control_repeat_until",
                [
                    self.value(node.left)
                ],
                tempCompiler.compile(node.right)
            )
        elif node.type == "number":
            return self.value(node.left)
        elif node.type == "string":
            return self.value(node.left)
        elif node.type == "identifier":
            return self.block(
                "identifier",
                [
                    self.value(node.left)
                ]
            )
        else:
            raise Exception(f"Unknown node type {node.type}")

def compile(ast: list) -> str:
    compiler = ICompiler()
    return compiler.compile(ast)