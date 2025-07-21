from visuscript.visuscript_core import Drawable, Transform, Vec2, Rgb

def test_init():
    drawable = Drawable(
        '<rect width="{}" height={}'
    )

    assert drawable._element_text == '<rect width="{}" height={}'
    assert drawable._transform.translation == Vec2(0,0)
    assert drawable._transform.scale == Vec2(1,1)
    assert drawable._transform.rotation == 0
    assert drawable._fill == Rgb(255,255,255)
    assert drawable._fill_opacity == 0.0
    assert drawable._opacity == 1.0
    assert drawable._stroke == Rgb(255,255,255)
    assert drawable._stroke_opacity == 1.0

def test_default_init():
    drawable = Drawable()

    assert drawable._element_text == ""
    assert drawable._transform.translation == Vec2(0,0)
    assert drawable._transform.scale == Vec2(1,1)
    assert drawable._transform.rotation == 0
    assert drawable._fill == Rgb(255,255,255)
    assert drawable._fill_opacity == 0.0
    assert drawable._opacity == 1.0
    assert drawable._stroke == Rgb(255,255,255)
    assert drawable._stroke_opacity == 1.0


