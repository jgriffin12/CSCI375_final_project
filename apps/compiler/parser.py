from apps.compiler.ast_nodes import DenyRule, MaskRule, Program, RoleRule, Statement
from apps.compiler.errors import ParseError
from apps.compiler.tokens import Token, TokenType


class PolicyParser:
    """Parse a token stream into an abstract syntax tree.

    Grammar:
        program      -> statement* EOF
        statement    -> role_rule | deny_rule | mask_rule
        role_rule    -> "role" IDENTIFIER "can" permission_list ";"
        deny_rule    -> "deny" IDENTIFIER IDENTIFIER ";"
        mask_rule    -> "mask" IDENTIFIER "for" IDENTIFIER ";"
        permission_list -> IDENTIFIER ("," IDENTIFIER)*
    """

    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.current = 0

    def parse(self) -> Program:
        """Parse all statements and return the root Program node."""
        statements: list[Statement] = []

        while not self._check(TokenType.EOF):
            statements.append(self._statement())

        self._consume(TokenType.EOF, "Expected end of file.")
        return Program(statements)

    def _statement(self) -> Statement:
        if self._match(TokenType.ROLE):
            return self._role_rule()
        if self._match(TokenType.DENY):
            return self._deny_rule()
        if self._match(TokenType.MASK):
            return self._mask_rule()

        token = self._peek()
        raise ParseError(
            f"Expected a policy statement at line {token.line}, "
            f"column {token.column}."
        )

    def _role_rule(self) -> RoleRule:
        role_name = self._consume_identifier("Expected role name after 'role'.")
        self._consume(TokenType.CAN, "Expected 'can' after role name.")
        permissions = self._permission_list()
        self._consume(TokenType.SEMICOLON, "Expected ';' after role rule.")
        return RoleRule(role_name, permissions)

    def _deny_rule(self) -> DenyRule:
        role_name = self._consume_identifier("Expected role name after 'deny'.")
        permission = self._consume_identifier("Expected permission after denied role.")
        self._consume(TokenType.SEMICOLON, "Expected ';' after deny rule.")
        return DenyRule(role_name, permission)

    def _mask_rule(self) -> MaskRule:
        field_name = self._consume_identifier("Expected field name after 'mask'.")
        self._consume(TokenType.FOR, "Expected 'for' after masked field name.")
        role_name = self._consume_identifier("Expected role name after 'for'.")
        self._consume(TokenType.SEMICOLON, "Expected ';' after mask rule.")
        return MaskRule(field_name, role_name)

    def _permission_list(self) -> list[str]:
        permissions = [self._consume_identifier("Expected permission name.")]
        while self._match(TokenType.COMMA):
            permissions.append(self._consume_identifier("Expected permission after ','."))
        return permissions

    def _consume_identifier(self, message: str) -> str:
        return self._consume(TokenType.IDENTIFIER, message).lexeme

    def _match(self, token_type: TokenType) -> bool:
        if self._check(token_type):
            self._advance()
            return True
        return False

    def _consume(self, token_type: TokenType, message: str) -> Token:
        if self._check(token_type):
            return self._advance()

        token = self._peek()
        raise ParseError(
            f"{message} Found {token.lexeme!r} at line {token.line}, "
            f"column {token.column}."
        )

    def _check(self, token_type: TokenType) -> bool:
        if self.current >= len(self.tokens):
            return False
        return self._peek().token_type == token_type

    def _advance(self) -> Token:
        token = self._peek()
        self.current += 1
        return token

    def _peek(self) -> Token:
        return self.tokens[self.current]
