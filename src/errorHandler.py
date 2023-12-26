class IdentifierNotFound(Exception):
    def __init__(self, identifier):
        self.identifier = identifier
    def __str__(self):
        return f"Identifier not found: {self.identifier}"
    
class ExpectedChar(Exception):
    def __init__(self, expected, got):
        self.expected = expected
        self.got = got
    def __str__(self):
        return f"Expected {self.expected}, got {self.got}"
    
class UnknownChar(Exception):
    def __init__(self, char):
        self.char = char
    def __str__(self):
        return f"Unknown character: {self.char}"

# what would you name an error for too many decimal points in a number?
class TooManyDecimalPoints(Exception):
    def __init__(self):
        pass
    def __str__(self):
        return "Too many decimal points in number"