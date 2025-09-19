from visuscript import *
from visuscript.animated_collection import AnimatedList, Var
import random

N = 20
WIDTH = 2
STROKE_WIDTH = 0.25
SPACING = 60


def main():
    with Scene() as s:
        random.seed(3163)
        data = [Var(random.randrange(1, 200)) for _ in range(N)]

        methods = [bubble_sort, insertion_sort, quick_sort]
        for i, method in enumerate(methods):
            mid = (
                RIGHT * (N * WIDTH + SPACING) * (i - len(methods) / 2)
                + DOWN * 75
                + SPACING * RIGHT / 2
            )
            position = mid + LEFT * N * WIDTH / 2
            abl = AnimatedBarList(data, transform=Transform(position))
            s << abl.collection_drawable
            s << Text(method.__name__, font_size=10).translate(*mid + DOWN * 7)
            s << (counts := Text("", font_size=5).translate(*mid + DOWN * 18))
            s.updaters << FunctionUpdater(
                lambda t, dt, counts=counts, a=abl: counts.set_text(
                    f"{a.num_comparisons:} comparisons || {a.num_swaps} swaps"
                )
            ).update(0, 0)

            s.animations << method(abl).set_speed(12)


class AnimatedBarList(AnimatedList[Var, Rect]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.num_comparisons = 0
        self.num_swaps = 0

    def new_drawable_for(self, var: Var):
        return (
            Rect(WIDTH, var.value)
            .set_fill("blue")
            .set_anchor(Anchor.BOTTOM)
            .set_stroke_width(STROKE_WIDTH)
        )

    def get_organizer(self):
        return GridOrganizer((1, len(self)), (1, WIDTH))

    def swap(self, a, b, *args, **kwargs):
        assert isinstance(a, int)
        assert isinstance(b, int)
        return AnimationBundle(
            super().swap(a, b).compress(),
            RunFunction(self.add_swap),
            flash(self.drawables[a].fill, "green"),
            flash(self.drawables[b].fill, "green") if a != b else None,
        )

    def compare(self, a: int, b: int):
        return AnimationBundle(
            RunFunction(self.add_compare),
            flash(self.drawables[a].fill, "light_gray"),
            flash(self.drawables[b].fill, "light_gray") if a != b else None,
        )

    def add_compare(self):
        self.num_comparisons += 1

    def add_swap(self):
        self.num_swaps += 1


def bubble_sort(abl: AnimatedBarList) -> AnimationSequence:
    sequence = AnimationSequence()
    changed = True
    while changed:
        changed = False
        for i in range(1, len(abl)):
            sequence << abl.compare(i - 1, i)
            if abl[i - 1] > abl[i]:
                sequence << abl.swap(i - 1, i)
                changed = True
    return sequence


def insertion_sort(abl: AnimatedBarList) -> AnimationSequence:
    sequence = AnimationSequence()
    for i in range(1, len(abl)):
        for j in range(i, 0, -1):
            sequence << abl.compare(j - 1, j)
            if abl[j] < abl[j - 1]:
                sequence << abl.swap(j - 1, j)
            else:
                break
    return sequence


def quick_sort(abl: AnimatedBarList, low: int | None = None, high: int | None = None):
    sequence = AnimationSequence()
    if low is None:
        low = 0
    if high is None:
        high = len(abl) - 1
    if low < high:
        pi, seq = partition(abl, low, high)
        sequence << seq
        sequence << quick_sort(abl, low, pi - 1)
        sequence << quick_sort(abl, pi + 1, high)
        return sequence


def partition(abl: AnimatedBarList, low, high):
    sequence = AnimationSequence()

    i = low - 1

    for j in range(low, high):
        sequence << abl.compare(j, high)
        if abl[j] < abl[high]:
            i += 1
            sequence << abl.swap(i, j)

    sequence << abl.swap(i + 1, high)
    return i + 1, sequence


if __name__ == "__main__":
    main()
