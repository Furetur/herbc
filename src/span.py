import dataclasses

from antlr4 import ParserRuleContext


@dataclasses.dataclass()
class Span:
    # start
    start_line: int
    start_column: int
    start_index: int
    # end
    end_line: int
    end_column: int
    end_index: int

    def __str__(self):
        return f"{self.start_line}:{self.start_column}"

    @staticmethod
    def from_antlr(ctx: ParserRuleContext) -> 'Span':
        return Span(
            start_line=ctx.start.line,
            start_column=ctx.start.column,
            start_index=ctx.start.start,
            end_line=ctx.stop.line,
            end_column=ctx.stop.column,
            end_index=ctx.stop.start,
        )


INVALID_SPAN = Span(start_line=-1, start_column=-1, start_index=-1, end_line=-1, end_column=-1, end_index=-1)
