from visuscript import *
from visuscript.config import config
from copy import deepcopy
import re


FONT_SIZE = 30
config.text_font_size = FONT_SIZE

inputs: list[Text] = list(
    map(Text, ["3", "2", "3", "8", "3", "*", "+", "3", "/", "-", "+"])
)
stack: list[Text] = []

scene = Scene()
input_organizer = GridOrganizer((1, 11), (1, FONT_SIZE)).set_transform(
    Transform([-FONT_SIZE * (len(inputs) // 2), scene.y(0) + FONT_SIZE * 2])
)
stack_organizer = GridOrganizer((10, 1), (FONT_SIZE, 1)).set_transform(
    Transform([0, scene.y(1) - FONT_SIZE - FONT_SIZE * 10])
)
input_organizer.organize(inputs)
input_duplicated: list[Text] = deepcopy(inputs)


scene.add_drawable(Text("Inputs").translate(y=scene.y(0) + FONT_SIZE))

scene.add_drawable(
    Text("Stack")
    .set_anchor(Anchor.TOP)
    .translate(stack_organizer[-1].translation + DOWN * FONT_SIZE / 2)
)

[*map(scene.add_drawable, inputs + input_duplicated)]


def push_operand(operand: Text):
    stack.append(operand)
    return AnimationSequence(
        TransformAnimation(operand.transform, stack_organizer[-len(stack)])
    )


def read_operator(operator: Text):
    stack
    operand2, operand1 = stack.pop(), stack.pop()
    val2, val1 = int(operand2.text), int(operand1.text)
    match operator.text:
        case "*":
            stack.append(Text(str(val1 * val2)))
        case "/":
            stack.append(Text(str(val1 // val2)))
        case "+":
            stack.append(Text(str(val1 + val2)))
        case "-":
            stack.append(Text(str(val1 - val2)))
        case c:
            raise ValueError(f"invalid input: '{c}'")

    result = stack[-1].set_opacity(0.0).set_fill("blue")
    scene << result
    return AnimationSequence(
        AnimationBundle(
            TranslationAnimation(operator.transform, operand1.transformed_shape.center),
            TranslationAnimation(
                operand1.transform,
                operand1.transformed_shape.center + LEFT * operand1.shape.width,
            ),
            TranslationAnimation(
                operand2.transform,
                operand1.transformed_shape.center + RIGHT * operand2.shape.width,
            ),
        ),
        RunFunction(
            lambda: result.translate(
                operand2.transformed_shape.right
                + RIGHT * result.transformed_shape.width
            )
        ),
        AnimationBundle(
            RgbAnimation(operator.fill, "red"),
            RgbAnimation(operand1.fill, "orange"),
            RgbAnimation(operand2.fill, "orange"),
            OpacityAnimation(result, 1.0),
        ),
        NoAnimation(duration=2),
        AnimationBundle(
            TranslationAnimation(
                result.transform, operator.lazy.transformed_shape.center
            ),
            OpacityAnimation(operator.fill, 0.0, duration=0.5),
            OpacityAnimation(operand1.fill, 0.0, duration=0.5),
            OpacityAnimation(operand2.fill, 0.0, duration=0.5),
        ),
    )


for text, duplicate in zip(inputs, input_duplicated):
    if stack:
        scene.player << RgbAnimation(stack[-1].fill, "off_white")
    if re.search(r"^\d*\.?\d+$", text.text):
        scene.player << AnimationBundle(
            push_operand(text),
            RgbAnimation(duplicate.fill, "yellow"),
        )
    else:
        scene.player << AnimationBundle(
            read_operator(text),
            RgbAnimation(duplicate.fill, "yellow"),
        )

scene.player << NoAnimation()
