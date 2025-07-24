use pyo3::prelude::*;
use super::Arena;
use crate::data_types::SvgString;


#[pyclass]
#[derive(Default)]
pub struct World {
    svg_strings: Arena<SvgString>,
}

#[pymethods]
impl World {
    #[new]
    fn new() -> World {
        World::default()
    }

    fn run_frame(& self) {
        print!("<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"1920\" height=\"1080\"  fill=\"none\">")
    }
}