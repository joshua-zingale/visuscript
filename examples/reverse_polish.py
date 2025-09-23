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
    return sequence(
        animate_transform(operand.transform, stack_organizer[-len(stack)])
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
    return sequence(
        bundle(
            animate_translation(operator.transform, operand1.tshape.center),
            animate_translation(
                operand1.transform,
                operand1.tshape.center + LEFT * operand1.ushape.width,
            ),
            animate_translation(
                operand2.transform,
                operand1.tshape.center + RIGHT * operand2.ushape.width,
            ),
        ),
        run(
            lambda: result.translate(
                operand2.tshape.right + RIGHT * result.tshape.width
            )
        ),
        bundle(
            animate_rgb(operator.fill, "red"),
            animate_rgb(operand1.fill, "orange"),
            animate_rgb(operand2.fill, "orange"),
            animate_opacity(result, 1.0),
        ),
        wait(2),
        bundle(
            animate_translation(result.transform, operator.lazy.tshape.center),
            animate_opacity(operator.fill, 0.0, duration=0.5),
            animate_opacity(operand1.fill, 0.0, duration=0.5),
            animate_opacity(operand2.fill, 0.0, duration=0.5),
        ),
    )


for text, duplicate in zip(inputs, input_duplicated):
    if stack:
        scene.player << animate_rgb(stack[-1].fill, "off_white")
    if re.search(r"^\d*\.?\d+$", text.text):
        scene.player << bundle(
            push_operand(text),
            animate_rgb(duplicate.fill, "yellow"),
        )
    else:
        scene.player << bundle(
            read_operator(text),
            animate_rgb(duplicate.fill, "yellow"),
        )

scene.player << wait()
