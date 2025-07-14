use pyo3::prelude::*;
use data_types::{Vec2, Rgb};

pub mod data_types;

/// A Python module implemented in Rust.
#[pymodule]
fn visuscript_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Vec2>()?;
    m.add_class::<Rgb>()?;
    Ok(())
}
