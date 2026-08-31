"""
HC v1.0 PARSER
==============
Recursive-descent parser: Token stream → AST
Aligned with HC Language Spec v1.0 / HL-18E formal grammar.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

from hijaiyyah.core.exceptions import HijaiyyahError
from hijaiyyah.language.ast_nodes import (
    ArrayLiteral,
    ASTNode,
    BinaryExpr,
    Block,
    BreakStmt,
    CallExpr,
    ConstStmt,
    ContinueStmt,
    ExpressedStmt,
    FnDecl,
    ForStmt,
    IfExpr,
    IndexExpr,
    LetStmt,
    Literal,
    MatchArm,
    MatchExpr,
    MethodCall,
    ModuleAccess,
    Program,
    RangeExpr,
    ReturnStmt,
    VarRef,
    WhileStmt,
)
from hijaiyyah.language.lexer import Token, TokenType


class ParseError(HijaiyyahError):
    """Raised on syntax errors during parsing."""

    def __init__(self, message: str, token: Optional[Token] = None):
        self.token = token
        if token:
            super().__init__(
                f"L{token.line}:{token.col}: {message} (got {token.type.name} '{token.value}')"
            )
        else:
            super().__init__(message)


class Parser:
    """
    Recursive-descent parser for HC v1.0.

    Grammar precedence (lowest to highest):
      assignment → logical_or → logical_and → equality →
      comparison → addition → multiplication → unary → postfix → primary
    """

    def __init__(self, tokens: List[Token]):
        self._tokens = tokens
        self._pos = 0

    # ── Token navigation ─────────────────────────────────────────

    def _current(self) -> Token:
        if self._pos < len(self._tokens):
            return self._tokens[self._pos]
        return Token(TokenType.EOF, "", 0, 0)

    def _peek(self, offset: int = 0) -> Token:
        idx = self._pos + offset
        if idx < len(self._tokens):
            return self._tokens[idx]
        return Token(TokenType.EOF, "", 0, 0)

    def _advance(self) -> Token:
        tok = self._current()
        self._pos += 1
        return tok

    def _at(self, *types: TokenType) -> bool:
        return self._current().type in types

    def _at_value(self, value: str) -> bool:
        return self._current().value == value

    def _match(self, *types: TokenType) -> Optional[Token]:
        if self._current().type in types:
            return self._advance()
        return None

    def _expect(self, ttype: TokenType, msg: str = "") -> Token:
        tok = self._current()
        if tok.type == ttype:
            return self._advance()
        err_msg = msg or f"Expected {ttype.name}"
        raise ParseError(err_msg, tok)

    def _expect_member_name(self, msg: str) -> Token:
        """
        Accept an identifier, or a keyword standing in for one.

        After '::' or '.', a keyword can never begin a new construct, so
        reading it as a plain name is unambiguous. Without this, any stdlib
        function whose name collides with a keyword is simply unreachable:
        hm::exomatrix::audit could not be called at all, because 'audit'
        lexes as KW_AUDIT rather than IDENTIFIER.
        """
        tok = self._current()
        if tok.type == TokenType.IDENTIFIER or tok.type.name.startswith("KW_"):
            return self._advance()
        raise ParseError(msg, tok)

    def _skip_newlines(self) -> None:
        while self._at(TokenType.NEWLINE):
            self._advance()

    def _skip_semis_and_newlines(self) -> None:
        while self._at(TokenType.NEWLINE, TokenType.SEMICOLON):
            self._advance()

    # ── Entry point ──────────────────────────────────────────────

    def parse(self) -> Program:
        """Parse the entire token stream into a Program AST."""
        program = Program()
        self._skip_newlines()

        while not self._at(TokenType.EOF):
            stmt = self._parse_statement()
            if stmt is not None:
                program.body.append(stmt)
            self._skip_semis_and_newlines()

        return program

    # ── Statements ───────────────────────────────────────────────

    def _parse_statement(self) -> Optional[ASTNode]:
        self._skip_newlines()
        tok = self._current()

        if tok.type == TokenType.KW_LET:
            return self._parse_let()
        if tok.type == TokenType.KW_CONST:
            return self._parse_const()
        if tok.type == TokenType.KW_FN:
            return self._parse_fn()
        if tok.type == TokenType.KW_IF:
            return self._parse_if()
        if tok.type == TokenType.KW_MATCH:
            return self._parse_match()
        if tok.type == TokenType.KW_FOR:
            return self._parse_for()
        if tok.type == TokenType.KW_WHILE:
            return self._parse_while()
        if tok.type == TokenType.KW_RETURN:
            return self._parse_return()
        if tok.type == TokenType.KW_BREAK:
            self._advance()
            self._match(TokenType.SEMICOLON)
            return BreakStmt()
        if tok.type == TokenType.KW_CONTINUE:
            self._advance()
            self._match(TokenType.SEMICOLON)
            return ContinueStmt()
        if tok.type == TokenType.EOF:
            return None

        # Expression statement
        expr = self._parse_expression()
        self._match(TokenType.SEMICOLON)
        return ExpressedStmt(expr=expr)

    # ── let / const ──────────────────────────────────────────────

    def _parse_let(self) -> LetStmt:
        self._expect(TokenType.KW_LET)
        _ = self._match(TokenType.KW_MUT) is not None
        name_tok = self._expect(TokenType.IDENTIFIER, "Expected variable name")
        type_ann = ""
        if self._match(TokenType.COLON):
            type_ann = self._parse_type_annotation()
        self._expect(TokenType.ASSIGN, "Expected '=' in let statement")
        value = self._parse_expression()
        self._match(TokenType.SEMICOLON)
        return LetStmt(name=name_tok.value, value=value, type_ann=type_ann)

    def _parse_const(self) -> ConstStmt:
        self._expect(TokenType.KW_CONST)
        name_tok = self._expect(TokenType.IDENTIFIER, "Expected constant name")
        type_ann = ""
        if self._match(TokenType.COLON):
            type_ann = self._parse_type_annotation()
        self._expect(TokenType.ASSIGN, "Expected '=' in const statement")
        value = self._parse_expression()
        self._match(TokenType.SEMICOLON)
        return ConstStmt(name=name_tok.value, value=value, type_ann=type_ann)

    def _parse_type_annotation(self) -> str:
        parts = []
        while self._at(
            TokenType.IDENTIFIER,
            TokenType.LT,
            TokenType.GT,
            TokenType.LBRACKET,
            TokenType.RBRACKET,
            TokenType.SEMICOLON,
            TokenType.INTEGER,
            TokenType.COMMA,
        ):
            if self._at(TokenType.ASSIGN, TokenType.LBRACE):
                break
            parts.append(self._advance().value)
        return " ".join(parts)

    # ── fn ───────────────────────────────────────────────────────

    def _parse_fn(self) -> FnDecl:
        self._expect(TokenType.KW_FN)
        name_tok = self._expect(TokenType.IDENTIFIER, "Expected function name")
        self._expect(TokenType.LPAREN, "Expected '(' after function name")

        params: List[Tuple[str, str]] = []
        if not self._at(TokenType.RPAREN):
            params = self._parse_param_list()
        self._expect(TokenType.RPAREN, "Expected ')' after parameters")

        ret_type = ""
        if self._match(TokenType.ARROW):
            ret_type = self._parse_type_annotation()

        body = self._parse_block()
        return FnDecl(name=name_tok.value, params=params, ret_type=ret_type, body=body)

    def _parse_param_list(self) -> List[Tuple[str, str]]:
        params = []
        params.append(self._parse_param())
        while self._match(TokenType.COMMA):
            params.append(self._parse_param())
        return params

    def _parse_param(self) -> Tuple[str, str]:
        name = self._expect(TokenType.IDENTIFIER, "Expected parameter name").value
        ptype = ""
        if self._match(TokenType.COLON):
            ptype = self._parse_type_annotation()
        return (name, ptype)

    # ── Block ────────────────────────────────────────────────────

    def _parse_block(self) -> Block:
        self._skip_newlines()
        self._expect(TokenType.LBRACE, "Expected '{'")
        self._skip_newlines()

        stmts: List[ASTNode] = []
        while not self._at(TokenType.RBRACE, TokenType.EOF):
            stmt = self._parse_statement()
            if stmt is not None:
                stmts.append(stmt)
            self._skip_semis_and_newlines()

        self._expect(TokenType.RBRACE, "Expected '}'")
        return Block(statements=stmts)

    # ── Control flow ─────────────────────────────────────────────

    def _parse_if(self) -> IfExpr:
        self._expect(TokenType.KW_IF)
        condition = self._parse_expression()
        then_branch = self._parse_block()

        else_branch = None
        self._skip_newlines()
        if self._match(TokenType.KW_ELSE):
            self._skip_newlines()
            if self._at(TokenType.KW_IF):
                else_branch = self._parse_if()
            else:
                else_branch = self._parse_block()

        return IfExpr(condition=condition, then_branch=then_branch, else_branch=else_branch)

    def _parse_match(self) -> MatchExpr:
        self._expect(TokenType.KW_MATCH)
        condition = self._parse_expression()
        self._skip_newlines()
        self._expect(TokenType.LBRACE, "Expected '{' after match expression")
        self._skip_newlines()

        arms: List[MatchArm] = []
        while not self._at(TokenType.RBRACE, TokenType.EOF):
            arm = self._parse_match_arm()
            arms.append(arm)
            self._match(TokenType.COMMA)
            self._skip_newlines()

        self._expect(TokenType.RBRACE, "Expected '}'")
        return MatchExpr(condition=condition, arms=arms)

    def _parse_match_arm(self) -> MatchArm:
        pattern = self._parse_pattern()
        self._expect(TokenType.FAT_ARROW, "Expected '=>' in match arm")
        self._skip_newlines()

        if self._at(TokenType.LBRACE):
            body = self._parse_block()
        else:
            body = self._parse_expression()

        return MatchArm(pattern=pattern, body=body)

    def _parse_pattern(self) -> ASTNode:
        if self._match(TokenType.UNDERSCORE):
            return VarRef(name="_")

        tok = self._current()

        # Integer pattern, possibly range
        if tok.type == TokenType.INTEGER:
            start = self._advance()
            start_val = int(start.value)
            # Check for range: 1..=9 or 1..9
            if self._at(TokenType.DOT_DOT_EQ):
                self._advance()
                end_tok = self._expect(TokenType.INTEGER, "Expected end of range")
                return RangeExpr(
                    start=Literal(value=start_val, lit_type="int"),
                    end=Literal(value=int(end_tok.value), lit_type="int"),
                    inclusive=True,
                )
            if self._at(TokenType.DOT_DOT):
                self._advance()
                end_tok = self._expect(TokenType.INTEGER, "Expected end of range")
                return RangeExpr(
                    start=Literal(value=start_val, lit_type="int"),
                    end=Literal(value=int(end_tok.value), lit_type="int"),
                    inclusive=False,
                )
            return Literal(value=start_val, lit_type="int")

        if tok.type == TokenType.STRING_LIT:
            return Literal(value=self._advance().value, lit_type="string")

        if tok.type == TokenType.HIJAIYYAH:
            return Literal(value=self._advance().value, lit_type="hybit_ref")

        if tok.type == TokenType.KW_TRUE:
            self._advance()
            return Literal(value=True, lit_type="bool")

        if tok.type == TokenType.KW_FALSE:
            self._advance()
            return Literal(value=False, lit_type="bool")

        if tok.type == TokenType.IDENTIFIER:
            return VarRef(name=self._advance().value)

        raise ParseError("Invalid match pattern", tok)

    def _parse_for(self) -> ForStmt:
        self._expect(TokenType.KW_FOR)
        var_tok = self._expect(TokenType.IDENTIFIER, "Expected loop variable")
        self._expect(TokenType.KW_IN, "Expected 'in' in for loop")
        iterable = self._parse_expression()
        body = self._parse_block()
        return ForStmt(var=var_tok.value, iterable=iterable, body=body)

    def _parse_while(self) -> WhileStmt:
        self._expect(TokenType.KW_WHILE)
        condition = self._parse_expression()
        body = self._parse_block()
        return WhileStmt(condition=condition, body=body)

    def _parse_return(self) -> ReturnStmt:
        self._expect(TokenType.KW_RETURN)
        value = None
        if not self._at(TokenType.SEMICOLON, TokenType.NEWLINE, TokenType.RBRACE, TokenType.EOF):
            value = self._parse_expression()
        self._match(TokenType.SEMICOLON)
        return ReturnStmt(value=value)

    # ── Expressions (precedence climbing) ────────────────────────

    def _parse_expression(self) -> ASTNode:
        return self._parse_logical_or()

    def _parse_logical_or(self) -> ASTNode:
        left = self._parse_logical_and()
        while self._match(TokenType.PIPE_PIPE):
            right = self._parse_logical_and()
            left = BinaryExpr(left=left, op="||", right=right)
        return left

    def _parse_logical_and(self) -> ASTNode:
        left = self._parse_equality()
        while self._match(TokenType.AMP_AMP):
            right = self._parse_equality()
            left = BinaryExpr(left=left, op="&&", right=right)
        return left

    def _parse_equality(self) -> ASTNode:
        left = self._parse_comparison()
        while True:
            if self._match(TokenType.EQ):
                right = self._parse_comparison()
                left = BinaryExpr(left=left, op="==", right=right)
            elif self._match(TokenType.NEQ):
                right = self._parse_comparison()
                left = BinaryExpr(left=left, op="!=", right=right)
            else:
                break
        return left

    def _parse_comparison(self) -> ASTNode:
        left = self._parse_range()
        while True:
            if self._match(TokenType.LT):
                right = self._parse_range()
                left = BinaryExpr(left=left, op="<", right=right)
            elif self._match(TokenType.GT):
                right = self._parse_range()
                left = BinaryExpr(left=left, op=">", right=right)
            elif self._match(TokenType.LTE):
                right = self._parse_range()
                left = BinaryExpr(left=left, op="<=", right=right)
            elif self._match(TokenType.GTE):
                right = self._parse_range()
                left = BinaryExpr(left=left, op=">=", right=right)
            else:
                break
        return left

    def _parse_range(self) -> ASTNode:
        left = self._parse_addition()
        if self._match(TokenType.DOT_DOT_EQ):
            right = self._parse_addition()
            return RangeExpr(start=left, end=right, inclusive=True)
        if self._match(TokenType.DOT_DOT):
            right = self._parse_addition()
            return RangeExpr(start=left, end=right, inclusive=False)
        return left

    def _parse_addition(self) -> ASTNode:
        left = self._parse_multiplication()
        while True:
            if self._match(TokenType.PLUS):
                right = self._parse_multiplication()
                left = BinaryExpr(left=left, op="+", right=right)
            elif self._match(TokenType.MINUS):
                right = self._parse_multiplication()
                left = BinaryExpr(left=left, op="-", right=right)
            else:
                break
        return left

    def _parse_multiplication(self) -> ASTNode:
        left = self._parse_unary()
        while True:
            if self._match(TokenType.STAR):
                right = self._parse_unary()
                left = BinaryExpr(left=left, op="*", right=right)
            elif self._match(TokenType.SLASH):
                right = self._parse_unary()
                left = BinaryExpr(left=left, op="/", right=right)
            elif self._match(TokenType.PERCENT):
                right = self._parse_unary()
                left = BinaryExpr(left=left, op="%", right=right)
            else:
                break
        return left

    def _parse_unary(self) -> ASTNode:
        if self._match(TokenType.BANG):
            operand = self._parse_unary()
            return BinaryExpr(left=Literal(value=True, lit_type="bool"), op="!=", right=operand)
        if self._match(TokenType.MINUS):
            operand = self._parse_unary()
            return BinaryExpr(left=Literal(value=0, lit_type="int"), op="-", right=operand)
        return self._parse_postfix()

    # ── Postfix: method calls, indexing, field access ────────────

    def _parse_postfix(self) -> ASTNode:
        node = self._parse_primary()

        while True:
            if self._at(TokenType.DOT):
                self._advance()
                name_tok = self._expect_member_name(
                    "Expected method or field name after '.'"
                )

                # Method call: obj.method(args)
                if self._at(TokenType.LPAREN):
                    self._advance()
                    args = self._parse_arg_list()
                    self._expect(TokenType.RPAREN, "Expected ')' after method arguments")
                    node = MethodCall(obj=node, method=name_tok.value, args=args)
                else:
                    # Field access: obj.field — treat as method call with no args
                    node = MethodCall(obj=node, method=name_tok.value, args=[])

            elif self._at(TokenType.LBRACKET):
                self._advance()
                index = self._parse_expression()
                self._expect(TokenType.RBRACKET, "Expected ']' after index")
                node = IndexExpr(obj=node, index=index)

            else:
                break

        return node

    # ── Primary expressions ──────────────────────────────────────

    def _parse_primary(self) -> ASTNode:
        tok = self._current()

        # Integer literal
        if tok.type == TokenType.INTEGER:
            self._advance()
            return Literal(value=int(tok.value), lit_type="int")

        # Float literal
        if tok.type == TokenType.FLOAT:
            self._advance()
            return Literal(value=float(tok.value), lit_type="float")

        # String literal
        if tok.type == TokenType.STRING_LIT:
            self._advance()
            return Literal(value=tok.value, lit_type="string")

        # Hijaiyyah character literal
        if tok.type == TokenType.HIJAIYYAH:
            self._advance()
            return Literal(value=tok.value, lit_type="hybit_ref")

        # Boolean literals
        if tok.type == TokenType.KW_TRUE:
            self._advance()
            return Literal(value=True, lit_type="bool")

        if tok.type == TokenType.KW_FALSE:
            self._advance()
            return Literal(value=False, lit_type="bool")

        if tok.type == TokenType.KW_NONE:
            self._advance()
            return Literal(value=None, lit_type="none")

        # Array literal: [expr, expr, ...]
        if tok.type == TokenType.LBRACKET:
            return self._parse_array_literal()

        # Parenthesized expression
        if tok.type == TokenType.LPAREN:
            self._advance()
            expr = self._parse_expression()
            self._expect(TokenType.RPAREN, "Expected ')' after expression")
            return expr

        # If expression (in expression position)
        if tok.type == TokenType.KW_IF:
            return self._parse_if()

        # Match expression (in expression position)
        if tok.type == TokenType.KW_MATCH:
            return self._parse_match()

        # Identifier (variable reference or function/module call)
        if tok.type == TokenType.IDENTIFIER:
            return self._parse_identifier_expr()

        raise ParseError("Unexpected token in expression", tok)

    def _parse_array_literal(self) -> ArrayLiteral:
        self._expect(TokenType.LBRACKET)
        elements: List[ASTNode] = []

        if not self._at(TokenType.RBRACKET):
            elements.append(self._parse_expression())
            while self._match(TokenType.COMMA):
                if self._at(TokenType.RBRACKET):
                    break
                elements.append(self._parse_expression())

        self._expect(TokenType.RBRACKET, "Expected ']' after array elements")
        return ArrayLiteral(elements=elements)

    def _parse_identifier_expr(self) -> ASTNode:
        """
        Parse identifier-starting expressions:
          - Simple variable: x
          - Function call: foo(args)
          - Module call: hm::vectronometry::norm2(h)
          - Module access: hm::vectronometry
        """
        name_tok = self._advance()  # consume identifier
        name = name_tok.value

        # Module path: identifier :: identifier :: ...
        if self._at(TokenType.DCOLON):
            path_parts = [name]
            while self._match(TokenType.DCOLON):
                next_tok = self._expect_member_name("Expected a name after '::'")
                path_parts.append(next_tok.value)

            full_path = "::".join(path_parts)

            # Module function call: hm::module::func(args)
            if self._at(TokenType.LPAREN):
                self._advance()
                args = self._parse_arg_list()
                self._expect(TokenType.RPAREN, "Expected ')' after function arguments")
                return CallExpr(callee=full_path, args=args)

            # Module access (no call): hm::module
            return ModuleAccess(path=path_parts)

        # Simple function call: func(args)
        if self._at(TokenType.LPAREN):
            self._advance()
            args = self._parse_arg_list()
            self._expect(TokenType.RPAREN, "Expected ')' after function arguments")
            return CallExpr(callee=name, args=args)

        # Simple variable reference
        return VarRef(name=name)

    def _parse_arg_list(self) -> List[ASTNode]:
        """Parse comma-separated argument list (may be empty)."""
        args: List[ASTNode] = []

        if self._at(TokenType.RPAREN):
            return args

        args.append(self._parse_expression())
        while self._match(TokenType.COMMA):
            if self._at(TokenType.RPAREN):
                break
            args.append(self._parse_expression())

        return args
