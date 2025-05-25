from visuscript import *
from visuscript.animation import *
from visuscript.output import print_png
from copy import deepcopy

class Var:
    def __init__(self, *, value, _type = int, font_size=50, scene: Scene, **kwargs):

        self.text_element = Text(text=str(_type(value)) if value is not None else "", font_size = font_size, **kwargs)
        self._type = _type
        self._scene = scene

    @property
    def value(self):
        if self.text_element.text == "" and self._type is not str:
            return None
        return self._type(self.text_element.text)
    
    @value.setter
    def value(self, value):
        if value is None:
            self.text_element.text = ""
        else:
            if isinstance(value, Var):
                self.text_element.text = str(self._type(value.value))

                source = value.text_element.transform.translation.xy
                destination = self.text_element.transform.translation.xy

                self._scene.animations << PathAnimation(self.text_element, Path().M(*source).L(*destination), fps=30, duration = 0.5)
            else:
                self.text_element.text = str(self._type(value))

    def __str__(self) -> str:
        return self._type(self.value)
    
    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other):
        return self == other

    def __add__(self, other):
        return self.value + other
    
    def __sub__(self, other):
        return self.value - other

    def __lt__(self, other: Self):
        og_transform = deepcopy(self.text_element.transform)
        width = self.text_element.width
        comparison = Text(text=f" < {other.value}", transform=Transform([width/2,0], scale=0), font_size=self.text_element.font_size, anchor=Anchor.LEFT).set_parent(self.text_element)
        total_width = width + comparison.width

        scale = width/total_width

        xy = self.text_element.transform.translation.xy

        self._scene.animations << AnimationSequence(
            AnimationBundle(TransformAnimation(drawable=self.text_element, target=Transform(xy + [-comparison.width/2*scale, 0], scale=scale)),ScaleAnimation(comparison, 1)),
            NoAnimation(),
            AnimationBundle(TransformAnimation(drawable=self.text_element, target=og_transform), ScaleAnimation(comparison, 0.0)),
            RF(lambda : comparison.set_parent(None))
            )

        self._scene.pf()
        return self.value < other.value
    
    def __gt__(self, other: Self):
        og_transform = deepcopy(self.text_element.transform)
        width = self.text_element.width
        comparison = Text(text=f" > {other.value}", transform=Transform([width/2,0], scale=0), font_size=self.text_element.font_size, anchor=Anchor.LEFT).set_parent(self.text_element)
        total_width = width + comparison.width

        scale = width/total_width

        xy = self.text_element.transform.translation.xy

        self._scene.animations << AnimationSequence(
            AnimationBundle(TransformAnimation(drawable=self.text_element, target=Transform(xy + [-comparison.width/2*scale, 0], scale=scale)),ScaleAnimation(comparison, 1)),
            NoAnimation(),
            AnimationBundle(TransformAnimation(drawable=self.text_element, target=og_transform), ScaleAnimation(comparison, 0.0)),
            RF(lambda : comparison.set_parent(None))
            )

        self._scene.pf()
        return self.value > other.value



class TwoPointerArray:
    def animating(foo):
        def decorated_animating_function(self: Self, *args, **kwargs):
            r = foo(self, *args, **kwargs)
            if self.auto_print:
                self._scene.print_frames()
            return r
        return decorated_animating_function


    def __init__(self, array: list, scene: Scene, auto_print = True, mark_i_visited = False):
        self._mark_i_visited = mark_i_visited
        self._box_size = 50
        
        self.auto_print: bool = auto_print
        

        self._scene: Scene = scene

        drawing, boxes, elements = get_array(array, self._box_size, scene)
        self._it: Text = Text(text="i", font_size=20)
        self._jt: Text = Text(text="j", font_size=20)
        

        self._boxes: list[Drawing] = boxes
        self._elements: list[Var] = elements

        x_start = -(len(self) - 1) * self._box_size/2 #+ ((len(self)+1) % 2) * self._box_size/2
        self._storage = Var(value=None, scene=scene)

        self._drawing = drawing.add_children(
            Pivot().set_transform([x_start, -self._box_size * 3/4]).add_child(self._it),
            Pivot().set_transform([x_start, self._box_size * 3/4]).add_child(self._jt),
            self._storage.text_element.set_transform([0, 100])
        )
        self._scene << self._drawing

        self.i = 0
        self.j = 0

        self._selected: int | None = None

        if auto_print:
            print_png(self._scene)        

    def __str__(self):
        return str(list(map(lambda x: x.value, self._elements)))
    
    def __repr__(self):
        return str(self)
    
    @property
    def i(self) -> int:
        return self._i
    
    @i.setter
    @animating
    def i(self, value: int):
        self._i = value
        self._scene.animations << PathAnimation(self._it, Path().M(*self._it.transform.translation.xy).L(value*self._box_size, 0))

    @property
    def j(self) -> int:
        return self._j
    
    # def select(self, index: int):
    #     if self._selected != None:
    #         self._boxes[self._selected].set_stroke(stroke=Color())
    #     self._boxes[index].set_stroke(stroke=Color("pale_green"))


    
    @j.setter
    @animating
    def j(self, value: int):
        self._j = value
        self._scene.animations << PathAnimation(self._jt, Path().M(*self._jt.transform.translation.xy).L(value*self._box_size, 0))

    @property
    def storage(self) -> Var:
        return self._storage
    
    @storage.setter
    @animating
    def storage(self, value: Var):
        self._storage.value = value

    @i.setter
    @animating
    def i(self, value: int):
        self._i = value

        if self._mark_i_visited:
            for box in self._boxes[:self._i]:
                box.set_fill(Color("blue"))
        self._scene.animations << PathAnimation(self._it, Path().M(*self._it.transform.translation.xy).L(value*self._box_size, 0))


    def get_drawing(self):
        return self._drawing

    @animating
    def swap(self, a: int, b: int):

        ea = self._elements[a]
        eb = self._elements[b]

        x_mid = (ea.text_element.transform.translation.x + eb.text_element.transform.translation.x)/2
        x_delta = abs(ea.text_element.transform.translation.x - eb.text_element.transform.translation.x)
        lift = x_delta
        
        self._scene.animations << [
            PathAnimation(ea.text_element, Path().M(*ea.text_element.transform.translation.xy).Q(x_mid, ea.text_element.transform.translation.y - lift, *eb.text_element.transform.translation.xy)),
            PathAnimation(eb.text_element, Path().M(*eb.text_element.transform.translation.xy).Q(x_mid, eb.text_element.transform.translation.y + lift, *ea.text_element.transform.translation.xy))
        ]

        self._elements[a] = eb
        self._elements[b] = ea
    
    def __getitem__(self, index: int) -> Var:
        return self._elements[index]
    
    @animating
    def __setitem__(self, index: int, value: Var):
        self[index].value = value
    
    def __len__(self):
        return len(self._elements)
    


def get_array(arr, box_size: float, scene: Scene):

    leftmost = -(box_size*(len(arr)-1))/2

    boxes: list[Drawing] = []
    elements: list[Var] = []

    for i,e in enumerate(arr):
        tfm=Transform([leftmost + i*box_size, 0])
        boxes.append(Rect(box_size, box_size, transform=tfm))
        elements.append(Var(value=e, font_size=box_size, transform=tfm, scene=scene))


    return Pivot().add_children(*(boxes + list(map(lambda x: x.text_element, elements)))), boxes, elements