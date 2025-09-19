from visuscript import *
from visuscript.animation import Animation
from visuscript.config import config

N = 11
FONT_SIZE = 20
config.text_font_size = FONT_SIZE

stack_org = GridOrganizer((N, 1), (FONT_SIZE, 1)).set_transform(
    Transform([0, -FONT_SIZE * N / 2])
)


scene = Scene()

cells = [
    Rect(FONT_SIZE * 2, FONT_SIZE).add_child(
        lambda p: Text(f"x{i + 0xFE00 - N + 1:X}", FONT_SIZE / 2)
        .set_anchor(Anchor.LEFT)
        .translate(p.shape.right + RIGHT * FONT_SIZE / 4)
    )
    for i in range(N)
]
stack_org.organize(cells)


tos_ptr = (
    Drawing(
        Path()
        .L(FONT_SIZE, 0)
        .L(FONT_SIZE, FONT_SIZE / 4)
        .L(FONT_SIZE + FONT_SIZE / 2, 0)
        .L(FONT_SIZE, -FONT_SIZE / 4)
        .L(FONT_SIZE, 0)
    )
    .set_anchor(Anchor.RIGHT)
    .add_child(
        lambda p: Text("TOS", FONT_SIZE / 4)
        .set_anchor(Anchor.BOTTOM_RIGHT)
        .translate(p.shape.top)
    )
    .translate(cells[-1].tshape.left)
)

scene.add_drawables(*cells, tos_ptr)

tos = N - 1

stack = [Text("")] * N

text_to_flash = (
    Text("text")
    .set_anchor(Anchor.TOP_LEFT)
    .translate(scene.x(0.04), scene.y(0.06))
    .set_opacity(0.0)
)
scene.add_drawable(text_to_flash)


def flash_text(text: str, animation: Animation):
    text_to_flash.set_text(text)
    return AnimationSequence(
        OpacityAnimation(text_to_flash, 1.0),
        animation,
        OpacityAnimation(text_to_flash, 0.0),
    )


def push(value: str):
    global tos
    tos -= 1
    text = Text(value).set_transform(stack_org[tos]).set_opacity(0.0)
    old_text = stack[tos]
    stack[tos] = text

    scene.add_drawable(text)

    return flash_text(
        f"Push({value})",
        AnimationSequence(
            TranslationAnimation(tos_ptr.transform, cells[tos].tshape.left),
            AnimationBundle(
                OpacityAnimation(old_text, 0.0), OpacityAnimation(text, 1.0)
            ),
        ),
    )


def pop():
    global tos
    text = stack[tos]
    tos += 1

    return flash_text(
        "Pop()",
        AnimationBundle(
            TranslationAnimation(tos_ptr.transform, cells[tos].tshape.left),
            OpacityAnimation(text, 0.5),
        ),
    )


scene.player << push("4")
scene.player << push("9")
scene.player << push("2")
scene.player << push("3")

scene.player << pop()

scene.player << push("5")
scene.player << pop()
scene.player << pop()
scene.player << push("8")
scene.player << pop()
scene.player << pop()
scene.player << pop()
