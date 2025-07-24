from visuscript.visuscript_core import SvgString
def test_initialization_no_parameters():
    s = SvgString("<circle/>")
    assert str(s) == "<circle/>"

def test_initialization_with_parameters():
    s = SvgString("<circle transform=\"{transform}\">")

def test_set_parameters():
    s = SvgString("<circle transform=\"{transform}\">")
    svg_arguments = {
        "transform": "rotate(180)"
    }
    s.set_parameters(svg_arguments) 
    assert str(s) == "<circle transform=\"rotate(180)\">"