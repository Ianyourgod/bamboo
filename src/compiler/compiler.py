import os
import json
import zipfile


def compile(ast):
    comp = Compiler()
    
    return comp.compile(ast)

def visit(node):
    return node.left

class Compiler:
    def __init__(self):
        with open("src/compiler/assets/emptyproject.json", "r") as f:
            self.json = json.load(f)
        self.blocks = []
        
    def compile(self, ast):
        self.blocks = {"a":{"opcode":"event_whenflagclicked","next":None,"parent":None,"inputs":{},"fields":{},"shadow":False,"topLevel":True,"x":160,"y":250}}
        self.i = 0
        print(ast, end="\n\n")
        while self.i < len(ast):
            j = ast[self.i]
            blc = self.visit(j)
            if self.i>0:
                if not "parent" in self.blocks[str(self.i-1)]:
                    blc["parent"] = str(self.i-1)
                if not "next" in self.blocks[str(self.i-1)]:
                    self.blocks[str(self.i-1)]["next"] = str(self.i)
            else:
                blc["parent"] = "a"
                self.blocks["a"]["next"] = str(self.i)
            self.blocks[str(self.i)] = blc
            self.i+=1
        if not "parent" in self.blocks[str(self.i-1)]:
            blc["parent"] = str(self.i-1)
            
        for i in self.blocks:
            if i == "a": continue
            self.blocks[i]["shadow"] = False
            self.blocks[i]["topLevel"] = False
            if not "next" in self.blocks[i] or (not self.blocks[i]["next"] in self.blocks):
                self.blocks[i]["next"] = None
            if not "parent" in self.blocks[i] or (not self.blocks[i]["parent"] in self.blocks):
                self.blocks[i]["parent"] = None
            print(f"{i}: {self.blocks[i]}")
        
        # output
        self.json["targets"][1]["blocks"] = self.blocks
        with open("project.json", "w") as f:
            json.dump(self.json, f)
        with zipfile.ZipFile("out.pmp", "w") as f:
            f.write("project.json")
            os.remove("project.json")
            f.write("src/compiler/assets/592bae6f8bb9c8d88401b54ac431f7b6.svg", "592bae6f8bb9c8d88401b54ac431f7b6.svg")
            f.write("src/compiler/assets/cd21514d0531fdffb22204e0ec5ed84a.svg", "cd21514d0531fdffb22204e0ec5ed84a.svg")
        
    def visit(self, node):
        block = {}
        match node.type:
            case "call":
                # looks
                match node.left:
                    case "say":
                        block["opcode"] = "looks_say"
                        t = self.i
                        block["inputs"] = {
                            "MESSAGE": self.visit(node.right[0])
                        }
                        self.i = t
                    case "sayfor":
                        block["opcode"] = "looks_sayforsecs"
                        t = self.i
                        block["inputs"] = {
                            "MESSAGE": self.visit(node.right[0]),
                            "SECS": self.visit(node.right[1])
                        }
                        self.i = t
                    case "think":
                        block["opcode"] = "looks_think"
                        t = self.i
                        block["inputs"] = {
                            "MESSAGE": self.visit(node.right[0])
                        }
                        self.i = t
                    case "thinkfor":
                        block["opcode"] = "looks_thinkforsecs"
                        t = self.i
                        block["inputs"] = {
                            "MESSAGE": self.visit(node.right[0]),
                            "SECS": self.visit(node.right[1])
                        }
                        self.i = t
                        
                # operators
                    case "join":
                        block["opcode"] = "operator_join"
                        t = self.i
                        block["inputs"] = {
                            "STRING1": self.visit(node.right[0]),
                            "STRING2": self.visit(node.right[1])
                        }
                        self.i = t
            
            # data
            case "number":
                block = [1, [4, node.left]]
            case "string":
                block = [1, [10, node.left]]
            case "identifier":
                block = [3,[12,node.left,node.left],"null"]
            
            # control
            case "if":
                block["opcode"] = "control_if"
                temp = self.i
                block["inputs"] = {
                    "CONDITION": self.visit(node.left)
                }
                t_i = self.i+1
                if node.right:
                    for i in node.right:
                        self.i += 1
                        self.blocks[str(self.i)] = self.visit(i)
                        self.blocks[str(self.i)]["parent"] = str(self.i-1)
                        if self.i > temp+2:
                            self.blocks[str(self.i-1)]["next"] = str(self.i)
                    block["next"] = str(self.i+1)
                    self.i = temp
                    block["inputs"]["SUBSTACK"] = [2, str(t_i)]
                else:
                    self.i += 1
            case "while":
                block["opcode"] = "control_while"
                temp = self.i
                block["inputs"] = {
                    "CONDITION": self.visit(node.left)
                }
                t_i = self.i+1
                if node.right:
                    for i in node.right:
                        self.i += 1
                        self.blocks[str(self.i)] = self.visit(i)
                        self.blocks[str(self.i)]["parent"] = str(self.i-1)
                        if self.i > temp+2:
                            self.blocks[str(self.i-1)]["next"] = str(self.i)
                    block["next"] = str(self.i+1)
                    self.i = temp
                    block["inputs"]["SUBSTACK"] = [2, str(t_i)]
                else:
                    self.i += 1
            case "repeat":
                block["opcode"] = "control_repeat"
                temp = self.i
                block["inputs"] = {
                    "TIMES": self.visit(node.left)
                }
                t_i = self.i+1
                if node.right:
                    for i in node.right:
                        self.i += 1
                        self.blocks[str(self.i)] = self.visit(i)
                        self.blocks[str(self.i)]["parent"] = str(self.i-1)
                        if self.i > temp+2:
                            self.blocks[str(self.i-1)]["next"] = str(self.i)
                        print(self.i)
                    print(self.i+1)
                    block["next"] = str(self.i+1)
                    self.i = temp
                    block["inputs"]["SUBSTACK"] = [2, str(t_i)]
                else:
                    self.i += 1
                    
            # operators
            case "bool":
                blc = {}
                if node.left:
                    blc["opcode"] = "operator_trueBoolean"
                else:
                    blc["opcode"] = "operator_falseBoolean"
                blc["next"] = None
                blc["parent"] = str(self.i+1)
                self.i+=1
                self.blocks[str(self.i)] = blc
                block = [2,str(self.i)]
            case "eq":
                blc = {}
                blc["opcode"] = "operator_equals"
                blc["inputs"] = {
                    "OPERAND1": self.visit(node.left),
                    "OPERAND2": self.visit(node.right)
                }
                blc["next"] = None
                blc["parent"] = str(self.i+1)
                self.i+=1
                self.blocks[str(self.i)] = blc
                block = [2,str(self.i)]
            case "neq":
                blc = {}
                blc["opcode"] = "operator_notequal"
                blc["inputs"] = {
                    "OPERAND1": self.visit(node.left),
                    "OPERAND2": self.visit(node.right)
                }
                blc["next"] = None
                blc["parent"] = str(self.i+1)
                self.i+=1
                self.blocks[str(self.i)] = blc
                block = [2,str(self.i)]
            case "gt":
                blc = {}
                blc["opcode"] = "operator_gt"
                blc["inputs"] = {
                    "OPERAND1": self.visit(node.left),
                    "OPERAND2": self.visit(node.right)
                }
                blc["next"] = None
                blc["parent"] = str(self.i+1)
                self.i+=1
                self.blocks[str(self.i)] = blc
                block = [2,str(self.i)]
            case "gte":
                blc = {}
                blc["opcode"] = "operator_gtorequal"
                blc["inputs"] = {
                    "OPERAND1": self.visit(node.left),
                    "OPERAND2": self.visit(node.right)
                }
                blc["next"] = None
                blc["parent"] = str(self.i+1)
                self.i+=1
                self.blocks[str(self.i)] = blc
                block = [2,str(self.i)]
            case "lt":
                blc = {}
                blc["opcode"] = "operator_lt"
                blc["inputs"] = {
                    "OPERAND1": self.visit(node.left),
                    "OPERAND2": self.visit(node.right)
                }
                blc["next"] = None
                blc["parent"] = str(self.i+1)
                self.i+=1
                self.blocks[str(self.i)] = blc
                block = [2,str(self.i)]
            case "lte":
                blc = {}
                blc["opcode"] = "operator_ltorequal"
                blc["inputs"] = {
                    "OPERAND1": self.visit(node.left),
                    "OPERAND2": self.visit(node.right)
                }
                blc["next"] = None
                blc["parent"] = str(self.i+1)
                self.i+=1
                self.blocks[str(self.i)] = blc
                block = [2,str(self.i)]
            # math
            case "add":
                blc = {}
                if node.left.type == "string" or node.right.type == "string":
                    blc["opcode"] = "operator_join"
                    blc["inputs"] = {
                        "STRING1": self.visit(node.left),
                        "STRING2": self.visit(node.right)
                    }
                else:
                    blc["opcode"] = "operator_add"
                    blc["inputs"] = {
                        "NUM1": self.visit(node.left),
                        "NUM2": self.visit(node.right)
                    }
                blc["next"] = None
                blc["parent"] = str(self.i+1)
                self.i+=1
                self.blocks[str(self.i)] = blc
                block = [2,str(self.i)]
            case "sub":
                blc = {}
                blc["opcode"] = "operator_subtract"
                blc["inputs"] = {
                    "NUM1": self.visit(node.left),
                    "NUM2": self.visit(node.right)
                }
                blc["next"] = None
                blc["parent"] = str(self.i+1)
                self.i+=1
                self.blocks[str(self.i)] = blc
                block = [2,str(self.i)]
            case "mul":
                blc = {}
                blc["opcode"] = "operator_multiply"
                blc["inputs"] = {
                    "NUM1": self.visit(node.left),
                    "NUM2": self.visit(node.right)
                }
                blc["next"] = None
                blc["parent"] = str(self.i+1)
                self.i+=1
                self.blocks[str(self.i)] = blc
                block = [2,str(self.i)]
            case "div":
                blc = {}
                blc["opcode"] = "operator_divide"
                blc["inputs"] = {
                    "NUM1": self.visit(node.left),
                    "NUM2": self.visit(node.right)
                }
                blc["next"] = None
                blc["parent"] = str(self.i+1)
                self.i+=1
                self.blocks[str(self.i)] = blc
                block = [2,str(self.i)]
            
            # variable
            case "assign":
                self.json["targets"][1]["variables"][node.left.left] = [node.left.left, "null"]
                block["opcode"] = "data_setvariableto"
                t = self.i
                block["inputs"] = {
                    "VALUE": self.visit(node.right)
                }
                self.i = t
                block["fields"] = {
                    "VARIABLE":[node.left.left, node.left.left]
                }
        return block