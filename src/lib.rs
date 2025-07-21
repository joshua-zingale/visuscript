use pyo3::prelude::*;
use data_types::{Vec2, Rgb, Transform};
use drawable::Drawable;

pub mod data_types;
pub mod drawable;

/// A Python module implemented in Rust.
#[pymodule]
fn visuscript_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Vec2>()?;
    m.add_class::<Rgb>()?;
    m.add_class::<Transform>()?;
    m.add_class::<Drawable>()?;
    Ok(())
}
