use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::exceptions::PyZeroDivisionError;
use pyo3::ffi::c_str;

#[pyclass]
#[derive(Clone)]
pub struct Rgb([u8; 3]);

#[pymethods]
impl Rgb {
    #[new]
    fn new(r: u8, g: u8, b: u8) -> Rgb {
        Rgb([r,g,b])
    }

    #[getter]
    fn get_r(&self) -> u8{
        self.0[0]
    }

    #[getter]
    fn get_g(&self) -> u8{
        self.0[1]
    }

    #[getter]
    fn get_b(&self) -> u8{
        self.0[2]
    }


    fn __eq__(&self, other: Rgb) -> bool {
        self.0[0] == other.0[0] && self.0[1] == other.0[1] && self.0[2] == other.0[2]
    }

    fn __add__(&self, other: Rgb) -> Rgb {
        Rgb([
            self.0[0].saturating_add(other.0[0]),
            self.0[1].saturating_add(other.0[1]),
            self.0[2].saturating_add(other.0[2])
            ])
    }

    fn __sub__(&self, other: Rgb) -> Rgb {
        Rgb([
            self.0[0].saturating_sub(other.0[0]),
            self.0[1].saturating_sub(other.0[1]),
            self.0[2].saturating_sub(other.0[2])
            ])
    }

    fn __mul__(&self, other: Rgb) -> Rgb {
        Rgb([
            self.0[0].saturating_mul(other.0[0]),
            self.0[1].saturating_mul(other.0[1]),
            self.0[2].saturating_mul(other.0[2])
            ])
    }

    fn __truediv__<'py>(&self, other: Rgb) -> PyResult<Rgb> {
        if other.0[0] == 0 {
            return Err(PyZeroDivisionError::new_err("Zero encountered in r value."))
        }
        if other.0[1] == 0 {
            return Err(PyZeroDivisionError::new_err("Zero encountered in g value."))
        }
        if other.0[2] == 0 {
            return Err(PyZeroDivisionError::new_err("Zero encountered in b value."))
        }
        Ok(
            Rgb([
                self.0[0] / other.0[0],
                self.0[1] / other.0[1],
                self.0[2] / other.0[2]
                ])
        )
    }

    fn __iter__<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let dict: Bound<'py, PyDict> = PyDict::new(py);
        dict.set_item("r", self.0[0])?;
        dict.set_item("g", self.0[1])?;
        dict.set_item("b", self.0[2])?;
        py.eval(c_str!("iter((r, g, b))"), None, Some(&dict))
    }

    fn __repr__(&self) -> String {
        format!("Vec2({}, {})", self.0[0], self.0[1])
    }

    fn __str__(&self) -> String {
        format!("[ {}, {} ]", self.0[0], self.0[1])
    }
}