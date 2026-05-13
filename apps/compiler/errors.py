class PolicyCompilerError(Exception):
    """Base class for policy compiler errors."""


class LexError(PolicyCompilerError):
    """Raised when the lexer finds an invalid character."""


class ParseError(PolicyCompilerError):
    """Raised when tokens do not match the grammar."""


class SemanticError(PolicyCompilerError):
    """Raised when the policy is syntactically valid but unsafe or invalid."""
