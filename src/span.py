import dataclasses

from antlr4 import ParserRuleContext


@dataclasses.dataclass()
class Span:
    line: int
    column: int

    def __str__(self):
        return f"{self.line}:{self.column}"

    @staticmethod
    def from_antlr(ctx: ParserRuleContext) -> 'Span':
        return Span(
            line=ctx.start.line,
            column=ctx.start.column,
        )


INVALID_SPAN = Span(line=-1, column=-1)
