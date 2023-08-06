use cpython::{PyDict, PyResult, PyString, Python};

pub fn get_strs_from_dict(dict: &PyDict, py: Python, key: &str) -> PyResult<String> {
    let pykey = PyString::new(py, key);
    match dict.get_item(py, pykey) {
        Some(string) => {
            let string = try!(string.cast_as::<PyString>(py));
            let string = try!(string.to_string(py));
            Ok(string.into_owned())
        }
        _ => panic!(format!("KeyError \"{}\"", key)), // FIXME: return proper error
    }
}
