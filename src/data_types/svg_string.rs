use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use std::collections::HashMap;

pub type SvgArguments = HashMap<String, String>;

#[pyclass]
pub struct SvgString(String, SvgArguments);


#[pymethods]
impl SvgString {
    #[new]
    fn new(string: String) -> SvgString{
        SvgString(string, HashMap::new())
    }

    fn __str__(&self) -> PyResult<String> {
        let mut formated_string = String::new();
        let mut chars = self.0.chars().peekable();

        loop {
            match chars.next() {
                None => break,
                Some(c) => match c {
                    '\\' => match chars.next() {
                        None => Err(PyValueError::new_err("String termnated before finishing escape sequence, i.e. there is a single backslash at the end of the string."))?,
                        Some(c) => formated_string.push(c)
                    }
                    '{' => {
                        let mut name = String::new();

                        loop {
                            match chars.next() {
                                None => Err(PyValueError::new_err("Unclosed '{' in string."))?,
                                Some('}') => {
                                    match self.1.get(&name) {
                                        None => Err(PyValueError::new_err(format!("No provided value for parameter '{}'", name)))?,
                                        Some(argument) => formated_string.push_str(&argument),
                                    }
                                    break
                                }
                                Some(c) => name.push(c)
                            }
                        }
                    }
                    c => formated_string.push(c)
                }
            }
        }

        Ok(formated_string)
    }

    fn __repr__(&self) -> String {
        format!("SvgString({})", self.0.clone())
    }

    pub fn set_parameters(&mut self, svg_arguments: SvgArguments) {
        self.1 = svg_arguments;
    }
}

impl Default for SvgString {
    fn default() -> SvgString{
        SvgString(String::new(), HashMap::new())
    }
}