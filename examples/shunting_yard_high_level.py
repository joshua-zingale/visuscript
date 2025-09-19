from visuscript import *
from visuscript.drawable import Arrow
from visuscript.organizer import Organizer
from visuscript.primatives.protocols import HasTransform
from visuscript.config import config
from typing import Union, Sequence
from copy import deepcopy

FONT_SIZE = 16
SEPARATION = FONT_SIZE * 2.15

config.animation_duration = 1.5

scene = Scene()


def main():
    inp = "1 - 2 / 3 + 4 * ( 5 - 6 )"

    tokens = tokenize(inp)
    input_organizer = GridOrganizer((1, len(tokens)), (1, SEPARATION)).set_transform(
        Transform(
            UP * FONT_SIZE * 3
            + LEFT * SEPARATION * (len(tokens) // 2)
            - SEPARATION / 2
            + FONT_SIZE
        )
    )
    input_organizer.organize(tokens)
    scene << tokens
    scene << Text("Infix Notation", FONT_SIZE * 2 / 3).set_anchor(
        Anchor.BOTTOM_LEFT
    ).translate(tokens[0].gshape.top_left + UP * FONT_SIZE / 2)

    shunting_arrow = Arrow(
        source=(tokens[0].gshape.center + tokens[-1].gshape.center) / 2
        + DOWN * FONT_SIZE,
        destination=(tokens[0].gshape.center + tokens[-1].gshape.center) / 2
        + DOWN * FONT_SIZE * 2,
    ).set_opacity(0.0)
    shunting_text = (
        Text("Shunting Yard Algorithm", font_size=FONT_SIZE // 2)
        .set_anchor(Anchor.LEFT)
        .translate(shunting_arrow.ushape.right + RIGHT * FONT_SIZE / 2)
        .set_opacity(0.0)
    )
    polish_text = (
        Text("Reverse Polish Notation", FONT_SIZE * 2 / 3)
        .set_anchor(Anchor.BOTTOM_LEFT)
        .translate(
            tokens[0].gshape.top_left + DOWN * FONT_SIZE * 3 + UP * FONT_SIZE / 2
        )
        .set_opacity(0.0)
    )
    scene << shunting_arrow
    scene << shunting_text
    scene << polish_text

    polish_tokens = deepcopy(shunting_yard(tokens))
    polish_organizer = GridOrganizer((1, len(tokens)), (1, SEPARATION)).set_transform(
        Transform(LEFT * SEPARATION * (len(tokens) // 2) - SEPARATION / 2 + FONT_SIZE)
    )
    scene << polish_tokens
    scene.player << AnimationBundle(
        organizer_animation(polish_tokens, polish_organizer),
        fade_in(shunting_arrow),
        fade_in(shunting_text),
        fade_in(polish_text),
    )

    evaluation_tokens = deepcopy(polish_tokens)
    evaluation_organizer = GridOrganizer(
        (1, len(tokens)), (1, SEPARATION)
    ).set_transform(
        Transform(
            DOWN * FONT_SIZE * 3
            + LEFT * SEPARATION * (len(tokens) // 2)
            - SEPARATION / 2
            + FONT_SIZE
        )
    )
    scene << evaluation_tokens
    expression_text = (
        Text("Expression Evaluation", FONT_SIZE * 2 / 3)
        .set_anchor(Anchor.BOTTOM_LEFT)
        .translate(
            tokens[0].gshape.top_left + DOWN * FONT_SIZE * 6 + UP * FONT_SIZE / 2
        )
        .set_opacity(0.0)
    )
    scene << expression_text
    scene.player << AnimationBundle(
        organizer_animation(evaluation_tokens, evaluation_organizer),
        fade_in(expression_text),
    )

    while len(evaluation_tokens) > 1:
        scene.player << evaluate_step(evaluation_tokens)
        scene.player << organizer_animation(evaluation_tokens, evaluation_organizer)


def organizer_animation(objects: Sequence[HasTransform], organizer: Organizer):
    return AnimationBundle(
        *map(
            lambda v: TransformAnimation(v[0].transform, v[1]), zip(objects, organizer)
        )
    )


def tokenize(text: str):
    return list(map(text_to_token, text.split(" ")))


def evaluate_step(tokens: list[Union["Operator", "Value"]]):
    i = 0
    while not isinstance(tokens[i], Operator):
        i += 1

    lvalue = tokens[i - 2]
    rvalue = tokens[i - 1]

    assert isinstance(lvalue, Value) and isinstance(rvalue, Value)
    match tokens[i].text:
        case "+":
            result = lvalue.value + rvalue.value
        case "-":
            result = lvalue.value - rvalue.value
        case "*":
            result = lvalue.value * rvalue.value
        case "/":
            result = lvalue.value / rvalue.value
        case _:
            raise RuntimeError()

    value = (
        Value(f"{result:.3}".rstrip("0").rstrip("."))
        .set_opacity(0.0)
        .set_transform(lvalue.transform)
    )
    operator = tokens[i]
    return AnimationSequence(
        AnimationBundle(
            *map(lambda v: RgbAnimation(v.fill, "gold"), tokens[i - 2 : i + 1])
        ),
        AnimationBundle(
            *map(lambda v: ScaleAnimation(v.transform, 0.5), tokens[i - 2 : i + 1]),
            TranslationAnimation(
                lvalue.transform,
                lvalue.tshape.center
                + DOWN * FONT_SIZE
                + LEFT * lvalue.tshape.width / 3
                + LEFT * operator.tshape.width / 4,
            ),
            TranslationAnimation(
                operator.transform, lvalue.tshape.center + DOWN * FONT_SIZE
            ),
            TranslationAnimation(
                rvalue.transform,
                lvalue.tshape.center
                + DOWN * FONT_SIZE
                + RIGHT * rvalue.tshape.width / 3
                + RIGHT * operator.tshape.width / 4,
            ),
        ),
        RunFunction(lambda: scene.add_drawable(value)),
        AnimationBundle(
            OpacityAnimation(value, 1.0),
            *map(lambda v: OpacityAnimation(v, 0.0), tokens[i - 2 : i + 1]),
        ),
        RunFunction(lambda: scene.remove_drawables([lvalue, operator, rvalue])),
        RunFunction(lambda: tokens.__setitem__(i - 2, value)),
        RunFunction(lambda: tokens.remove(operator)),
        RunFunction(lambda: tokens.remove(rvalue)),
    )


def text_to_token(text: str) -> "Token":
    if text in Operator.operators:
        return Operator(text)
    if text == "(":
        return OpenParenthesis()
    if text == ")":
        return CloseParenthesis()
    return Value(text)


def shunting_yard(tokens: list["Token"]) -> list[Union["Operator", "Value"]]:
    op_stack: list[Operator | OpenParenthesis] = []
    polish_stack: list[Operator | Value] = []

    for token in tokens:
        if isinstance(token, Operator):
            while len(op_stack) > 0 and op_stack[-1].precedence >= token.precedence:
                top = op_stack.pop()
                assert isinstance(top, Operator)
                polish_stack.append(top)
            op_stack.append(token)
        elif isinstance(token, OpenParenthesis):
            op_stack.append(token)
        elif isinstance(token, CloseParenthesis):
            top = op_stack[-1]
            op_stack.pop()
            while not isinstance(top, OpenParenthesis):
                polish_stack.append(top)
                top = op_stack[-1]
                op_stack.pop()
        else:
            assert isinstance(token, (Value, Operator))
            polish_stack.append(token)

    while len(op_stack) > 0:
        top = op_stack.pop()
        assert isinstance(top, Operator)
        polish_stack.append(top)

    return polish_stack


class Token(Text):
    pass


class Operator(Token):
    operators = {"+": 10, "-": 10, "*": 20, "/": 20}

    def __init__(self, operator: str, font_size=FONT_SIZE):
        if operator not in self.operators:
            raise ValueError(f"Operator must be one of {self.operators}")

        super().__init__(operator, font_size)
        self.set_fill("red")

    @property
    def precedence(self):
        return self.operators[self.text]


class OpenParenthesis(Token):
    def __init__(self):
        super().__init__("(")
        self.set_fill("blue")

    @property
    def precedence(self):
        return min(Operator.operators.values()) - 5


class CloseParenthesis(Token):
    def __init__(self):
        super().__init__(")")
        self.set_fill("blue")


class Value(Token):
    def __init__(self, value: str, font_size=FONT_SIZE):
        super().__init__(value, font_size)
        self._value = float(value)
        self.set_fill("green")

    @property
    def value(self):
        return self._value


if __name__ == "__main__":
    main()
