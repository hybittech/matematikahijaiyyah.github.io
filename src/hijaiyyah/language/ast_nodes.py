"""AST node definitions for HC v1.0."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Tuple


class ASTNode:
    pass


@dataclass
class Program(ASTNode):
    body: List[ASTNode] = field(default_factory=list)


@dataclass
class LetStmt(ASTNode):
    name: str = ""
    value: Any = None
    type_ann: str = ""


@dataclass
class ConstStmt(ASTNode):
    name: str = ""
    value: Any = None
    type_ann: str = ""


@dataclass
class ExpressedStmt(ASTNode):
    expr: Any = None


@dataclass
class ReturnStmt(ASTNode):
    value: Any = None


@dataclass
class Block(ASTNode):
    statements: List[ASTNode] = field(default_factory=list)


@dataclass
class FnDecl(ASTNode):
    name: str = ""
    params: List[Tuple[str, str]] = field(default_factory=list)
    ret_type: str = ""
    body: Any = None


@dataclass
class Literal(ASTNode):
    value: Any = None
    lit_type: str = "unknown"


@dataclass
class VarRef(ASTNode):
    name: str = ""


@dataclass
class BinaryExpr(ASTNode):
    left: Any = None
    op: str = ""
    right: Any = None


@dataclass
class MethodCall(ASTNode):
    obj: Any = None
    method: str = ""
    args: List[Any] = field(default_factory=list)


@dataclass
class CallExpr(ASTNode):
    callee: str = ""
    args: List[Any] = field(default_factory=list)


@dataclass
class ModuleAccess(ASTNode):
    path: List[str] = field(default_factory=list)


@dataclass
class IfExpr(ASTNode):
    condition: Any = None
    then_branch: Any = None
    else_branch: Any = None


@dataclass
class RangeExpr(ASTNode):
    start: Any = None
    end: Any = None
    inclusive: bool = False


@dataclass
class MatchExpr(ASTNode):
    condition: Any = None
    arms: List[MatchArm] = field(default_factory=list)


@dataclass
class MatchArm(ASTNode):
    pattern: Any = None
    body: Any = None


@dataclass
class ForStmt(ASTNode):
    var: str = ""
    iterable: Any = None
    body: Any = None


@dataclass
class WhileStmt(ASTNode):
    condition: Any = None
    body: Any = None


@dataclass
class IndexExpr(ASTNode):
    obj: Any = None
    index: Any = None


@dataclass
class ArrayLiteral(ASTNode):
    elements: List[Any] = field(default_factory=list)


@dataclass
class BreakStmt(ASTNode):
    pass


@dataclass
class ContinueStmt(ASTNode):
    pass
