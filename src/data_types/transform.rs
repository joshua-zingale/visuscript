
use pyo3::{prelude::*, IntoPyObjectExt};
use pyo3::exceptions::{PyTypeError, PyValueError};
use pyo3::types::PyString;
use super::vec2::Vec2;
use std::f64::consts::PI;


#[pyclass]
#[derive(Debug, Clone)]
pub struct Transform([f64; 9]);


impl Transform {

    pub fn identity() -> Transform {
        Transform([
            1.0,0.0,0.0,
            0.0,1.0,0.0,
            0.0,0.0,1.0
            ])
    }

    fn rotation_radians(&self) -> f64 {
        self.0[3].atan2(self.0[0])
    }

    fn transform(&self, vec2: Vec2) -> Vec2 {

        let mut result = Vec2([0.0,0.0]);
        for i in 0..2 {
            for j in 0..2 {
                result.0[i] += self.0[Transform::index(i,j)] * vec2.0[j];
            }
            result.0[i] += self.0[Transform::index(i,2)];

        }

        result
    }

    fn compose(&self, other: Transform) -> Transform {
        let mut result_matrix = [0.0; 9];

        for i in 0..3 {
            for j in 0..3 {
                for k in 0..3 {
                    result_matrix[Transform::index(i,j)] += self.0[Transform::index(i,k)] * other.0[Transform::index(k,j)];
                }
            }
        }

        Transform(result_matrix)
    }

    fn index(i: usize, j: usize) -> usize {
        i*3 +j
    }
}

#[pymethods]
impl Transform {
    #[new]
    fn new(translation: Vec2, scale: Vec2, rotation: f64) -> Self {

        // Initialization taken from
        // https://en.wikipedia.org/wiki/Transformation_matrix#Affine_transformations
        let (tx, ty) = (translation.0[0], translation.0[1]);
        let (sx, sy) = (scale.0[0], scale.0[1]);
        let rot_rad = rotation * PI / 180.0;
        let (cos_rot, sin_rot) = (rot_rad.cos(), rot_rad.sin());

        Transform([
            sx * cos_rot,  -sy * sin_rot, tx,
            sx * sin_rot,   sy * cos_rot, ty,
            0.0,            0.0,          1.0,
        ])
    }

    #[getter]
    fn translation(&self) -> Vec2 {
        Vec2([self.0[2], self.0[5]])
    }

    #[getter]
    fn scale(&self) -> Vec2 {
        let sx = (self.0[0].powi(2) + self.0[3].powi(2)).sqrt();
        let sy = (self.0[1].powi(2) + self.0[4].powi(2)).sqrt();
        Vec2([sx, sy])
    }

    #[getter]
    fn rotation(&self) -> f64 {
        self.rotation_radians() * 180.0/PI
    }

    pub fn inverse(&self) -> PyResult<Self> {
        let a = self.0[0];
        let b = self.0[1];
        let tx = self.0[2];
        let c = self.0[3];
        let d = self.0[4];
        let ty = self.0[5];

        let det = a * d - b * c;

        if det.abs() < f64::EPSILON { 
            return Err(PyValueError::new_err("Transform is non-invertible."));
        }

        let inv_det = 1.0 / det;

        let m00 = d * inv_det;
        let m01 = -b * inv_det;
        let m02 = (b * ty - d * tx) * inv_det;

        let m10 = -c * inv_det;
        let m11 = a * inv_det;
        let m12 = (c * tx - a * ty) * inv_det;

        Ok(Transform([
            m00, m01, m02,
            m10, m11, m12,
            0.0, 0.0, 1.0,
        ]))
    }

    fn __matmul__<'py>(&self, py: Python<'py>, other: PyObject) -> PyResult<PyObject> {
        if let Ok(transform) = other.extract::<Transform>(py) {
            let result = self.compose(transform);
            return result.into_py_any(py)
        }
        if let Ok(vec2) = other.extract::<Vec2>(py) {
            let result = self.transform(vec2);
            return result.into_py_any(py)
        }
        Err(PyTypeError::new_err(format!("A Transform can only be composed with a Vec2 or another Transform, not with {}", other.bind(py).get_type().name().unwrap_or(PyString::new(py, "<unknown>")))))
    }

    


}

