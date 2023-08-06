#[macro_use]
extern crate cpython;
extern crate html5ever;

use cpython::{PyDict, PyList, PyResult, PyString, Python};

extern crate lollygag;
mod html_node;
mod query;
mod utils;

use html_node::{node_type, HtmlNode};
use query::{query as query_consts, query_html, query_http_endpoint, query_multiple_endpoints,
            PyQuery};

trait Getter {
    fn get<TKey, TReturn>(&self, py: Python, key: &TKey) -> PyResult<TReturn>
    where
        TKey: cpython::ToPyObject,
        TReturn: cpython::PythonObjectWithCheckedDowncast;
}

impl Getter for PyDict {
    fn get<TKey, TReturn>(&self, py: Python, key: &TKey) -> PyResult<TReturn>
    where
        TKey: cpython::ToPyObject,
        TReturn: cpython::PythonObjectWithCheckedDowncast,
    {
        let result = match self.get_item(py, key) {
            Some(val) => val,
            _ => panic!(format!("KeyError")), // FIXME: return proper error
        };
        Ok(result.cast_into::<TReturn>(py).unwrap())
    }
}

py_module_initializer!(
    lollygag_ext,
    init_lollygag_ext,
    PyInit_lollygag_ext,
    |py, module| {
        module.add(py, "__doc__", "Rust extension for lollygag")?;
        module.add(
            py,
            "query_html",
            py_fn!(py, query_html(html: &PyString, query: &PyQuery)),
        )?;
        module.add(
            py,
            "query_http_endpoint",
            py_fn!(py, query_http_endpoint(url: &PyString, query: &PyQuery)),
        )?;
        module.add(
            py,
            "query_multiple_endpoints",
            py_fn!(py, query_multiple_endpoints(url: &PyList, query: &PyQuery)),
        )?;
        module.add(py, "QUERY_NONE", query_consts::QUERY_NONE)?;
        module.add(py, "QUERY_NAME", query_consts::QUERY_NAME)?;
        module.add(py, "QUERY_ATTRIBUTE", query_consts::QUERY_ATTRIBUTE)?;
        module.add(py, "QUERY_AND", query_consts::QUERY_AND)?;
        module.add(py, "QUERY_OR", query_consts::QUERY_OR)?;
        module.add(py, "QUERY_DATA", query_consts::QUERY_DATA)?;
        module.add(py, "QUERY_NOT", query_consts::QUERY_NOT)?;
        module.add_class::<PyQuery>(py)?;
        module.add_class::<HtmlNode>(py)?;
        module.add(py, "NODE_UNKNOWN", node_type::UNKNOWN)?;
        module.add(py, "NODE_DOCUMENT", node_type::DOCUMENT)?;
        module.add(py, "NODE_ELEMENT", node_type::ELEMENT)?;
        module.add(py, "NODE_TEXT", node_type::TEXT)?;
        Ok(())
    }
);
