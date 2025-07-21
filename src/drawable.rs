use pyo3::prelude::*;
use super::{Transform, Rgb};



#[pyclass]
#[pyo3(subclass)]
#[derive(Debug, Clone)]
pub struct Drawable {
    element_text: String,

    transform: Transform,

    stroke: Rgb,
    stroke_opacity: f64,
    fill: Rgb,
    fill_opacity: f64,
    opacity: f64,
}


#[pymethods]
impl Drawable {
    #[new]
    #[pyo3(signature = (
        element_text = String::new(),
        transform = Transform::identity(),
        stroke = Rgb([255, 255, 255]),
        stroke_opacity = 1.0,
        fill = Rgb([255, 255, 255]),
        fill_opacity = 0.0,
        opacity = 1.0,
    ))]
    fn new(
        element_text: String,
        transform: Transform,
        stroke: Rgb,
        stroke_opacity: f64,
        fill: Rgb,
        fill_opacity: f64,
        opacity: f64,
    ) -> Drawable {
        Drawable {
            element_text,
            transform,
            stroke,
            stroke_opacity,
            fill,
            fill_opacity,
            opacity,
        }
    }

    #[getter]
    fn _transform(&self) -> Transform {
        self.transform.clone()
    }

    #[getter]
    fn _element_text(&self) -> String {
        self.element_text.clone()
    }

    #[getter]
    fn _stroke(&self) -> Rgb {
        self.stroke.clone()
    }

    #[getter]
    fn _stroke_opacity(&self) -> f64 {
        self.stroke_opacity
    }

    #[getter]
    fn _fill(&self) -> Rgb {
        self.fill.clone()
    }

    #[getter]
    fn _fill_opacity(&self) -> f64 {
        self.fill_opacity
    }

    #[getter]
    fn _opacity(&self) -> f64 {
        self.opacity
    }

    #[setter]
    fn set__transform(&mut self, transform: Transform) {
        self.transform = transform;
    }

    #[setter]
    fn set__element_text(&mut self, element_text: String) {
        self.element_text = element_text;
    }

    #[setter]
    fn set__stroke(&mut self, stroke: Rgb) {
        self.stroke = stroke;
    }

    #[setter]
    fn set__stroke_opacity(&mut self, stroke_opacity: f64) {
        self.stroke_opacity = stroke_opacity;
    }

    #[setter]
    fn set__fill(&mut self, fill: Rgb) {
        self.fill = fill;
    }

    #[setter]
    fn set__fill_opacity(&mut self, fill_opacity: f64) {
        self.fill_opacity = fill_opacity;
    }

    #[setter]
    fn set__opacity(&mut self, opacity: f64) {
        self.opacity = opacity;
    }

}