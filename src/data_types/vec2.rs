use pyo3::prelude::*;
use pyo3::types::{PyDict, PyIterator};
use pyo3::exceptions::{PyTypeError, PyZeroDivisionError};
use pyo3::ffi::c_str;

#[pyclass]
pub struct Vec2([f64; 2]);

impl<'a> FromPyObject<'a> for Vec2 {
    fn extract_bound(obj: &Bound<'a, PyAny>) -> PyResult<Self> {
        // We first try to treat the object as an iterator
        let iter = PyIterator::from_object(obj)
            .map_err(|e| {
                // If it's not an iterator, provide a better error message.
                // We're expecting a sequence/iterable, not the given type.
                PyTypeError::new_err(format!(
                    "Expected a sequence or iterable with two floats, got {}",
                    obj.get_type().name().unwrap()
                ))
            })?;

        let mut values = Vec::with_capacity(2);
        
        for item in iter {
            let item = item?;
            let value = item.extract::<f64>()
                .map_err(|e| {
                    PyTypeError::new_err(format!(
                        "Invalid value in sequence. Expected float, got {}", 
                        item.get_type().name().unwrap()
                    ))
                })?;
            values.push(value);
        }

        if values.len() != 2 {
            Err(PyTypeError::new_err(format!(
                "Vec2 requires an iterable with exactly two float values, but got {} values.",
                values.len()
            )))
        } else {
            Ok(Vec2([values[0], values[1]]))
        }
    }
}

#[pymethods]
impl Vec2 {
    #[new]
    fn new(x: f64, y: f64) -> Vec2 {
        Vec2([x,y])
    }

    #[getter]
    fn get_x(&self) -> f64{
        self.0[0]
    }

    #[getter]
    fn get_y(&self) -> f64{
        self.0[1]
    }

    fn __eq__(&self, other: Vec2) -> bool {
        self.0[0] == other.0[0] && self.0[1] == other.0[1]
    }

    fn __add__(&self, other: Vec2) -> Vec2 {
        Vec2([self.0[0] + other.0[0], self.0[1] + other.0[1]])
    }

    fn __sub__(&self, other: Vec2) -> Vec2 {
        Vec2([self.0[0] - other.0[0], self.0[1] - other.0[1]])
    }

    fn __mul__(&self, other: Vec2) -> Vec2 {
        Vec2([self.0[0] * other.0[0], self.0[1] * other.0[1]])
    }

    fn __truediv__<'py>(&self, other: Vec2) -> PyResult<Vec2> {
        if other.0[0] == 0.0 {
            return Err(PyZeroDivisionError::new_err("Zero encountered in x value."))
        }
        if other.0[1] == 0.0 {
            return Err(PyZeroDivisionError::new_err("Zero encountered in y value."))
        }
        Ok(Vec2([self.0[0] / other.0[0], self.0[1] / other.0[1]]))
    }

    fn __pow__(&self, other: Vec2, _modulus: usize) -> Vec2 {
        Vec2([f64::powf(self.0[0], other.0[0]), f64::powf(self.0[1], other.0[1])])
    }

    fn __neg__(&self) -> Self {
        Vec2([-self.0[0], -self.0[1]])
    }

    fn __iter__<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let dict: Bound<'py, PyDict> = PyDict::new(py);
        dict.set_item("x", self.0[0])?;
        dict.set_item("y", self.0[1])?;
        py.eval(c_str!("iter((x, y))"), None, Some(&dict))
    }

    fn __repr__(&self) -> String {
        format!("Vec2({}, {})", self.0[0], self.0[1])
    }

    fn __str__(&self) -> String {
        format!("[ {}, {} ]", self.0[0], self.0[1])
    }
}