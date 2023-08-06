use cpython::PythonObject;
use cpython::{PyDict, PyList, PyObject, PyResult, PyString, PyTuple, Python};
use html5ever::parse_document;
use html5ever::rcdom::RcDom;
use html5ever::tendril::TendrilSink;

use html_node::HtmlNode;
use lollygag::{self, query_tree, HtmlQuery};
use utils::get_strs_from_dict;

pub mod query {
    pub const QUERY_NONE: u8 = 0;
    pub const QUERY_ATTRIBUTE: u8 = 1;
    pub const QUERY_NAME: u8 = 2;
    pub const QUERY_OR: u8 = 3;
    pub const QUERY_AND: u8 = 4;
    pub const QUERY_DATA: u8 = 5;
    pub const QUERY_NOT: u8 = 6;
}

pub fn query_multiple_endpoints(py: Python, urls: &PyList, query: &PyQuery) -> PyResult<PyDict> {
    let mut query_urls: Vec<String> = vec![];
    for url in urls.iter(py) {
        let url = try!(url.cast_into::<PyString>(py));
        let url = try!(url.to_string(py)).into_owned();
        query_urls.push(url);
    }
    let query = try!(query.to_query(py));
    let mut query_results = PyDict::new(py);
    for (url, result) in lollygag::query_multiple_endpoints(query_urls, &query) {
        match result {
            Ok(result) => {
                let mut query_result_values = vec![];
                for res in result {
                    query_result_values.push(HtmlNode::new(py, res)?.into_object());
                }
                query_results.set_item(py, url, PyList::new(py, query_result_values.as_slice()));
            }
            _ => unimplemented!(),
        }
    }
    Ok(query_results)
}

/// Run a query on a single http endpoint's response
/// Params:
/// url: str
/// query: PyQuery object
/// returns: List of nodes matching the query
pub fn query_http_endpoint(py: Python, url: &PyString, query: &PyQuery) -> PyResult<PyList> {
    let url = try!(url.to_string(py));
    let query = try!(query.to_query(py));
    let result = lollygag::query_http_endpoint(&url, &query);
    lollygag_to_py_result(py, result)
}

/// Run a query on a single html file
/// Params:
/// html: str
/// query: PyQuery object
/// returns: List of nodes matching the query
pub fn query_html(py: Python, html: &PyString, query: &PyQuery) -> PyResult<PyList> {
    let query = try!(query.to_query(py));
    let html = try!(html.to_string(py));
    let mut html = html.as_bytes();
    let handle = parse_document(RcDom::default(), Default::default())
        .from_utf8()
        .read_from(&mut html)
        .unwrap();
    let result = query_tree(&handle.document, &query);
    lollygag_to_py_result(py, result)
}

fn lollygag_to_py_result(
    py: Python,
    result: Result<Vec<lollygag::SimpleHtmlNode>, lollygag::LollygagError>,
) -> PyResult<PyList> {
    let result = match result {
        Ok(result) => result,
        Err(_) => vec![],
    };
    map_results(py, result)
}

fn map_results(py: Python, result: Vec<lollygag::SimpleHtmlNode>) -> PyResult<PyList> {
    let mut result_nodes: Vec<HtmlNode> = vec![];
    for res in result {
        let node = try!(HtmlNode::new(py, res));
        result_nodes.push(node);
    }
    make_result(py, result_nodes)
}

fn make_result(py: Python, result: Vec<HtmlNode>) -> PyResult<PyList> {
    let mut mapped: Vec<PyObject> = vec![];
    for node in result {
        mapped.push(node.into_object());
    }
    let result = PyList::new(py, mapped.as_slice());
    Ok(result)
}

py_class!(pub class PyQuery |py| {
    data kind: u8;
    data value: PyObject;

    def __new__(_cls, kind: u8, value: PyObject) -> PyResult<PyQuery> {
        PyQuery::create_instance(py, kind, value)
    }

    def __repr__(&self) -> PyResult<String> {
        Ok(format!("<LollygagQueryProxyObject, kind: {}, value: {}>", self.kind(py), self.value(py)))
    }
});

impl PyQuery {
    pub fn to_query(&self, py: Python) -> PyResult<HtmlQuery> {
        macro_rules! binary_query {
            ($query:ident) => {{
                let list = try!(self.value(py).cast_as::<PyTuple>(py));
                let (x, y) = (
                    try!(list.get_item(py, 0).cast_as::<PyQuery>(py)?.to_query(py)),
                    try!(list.get_item(py, 1).cast_as::<PyQuery>(py)?.to_query(py)),
                );
                Ok(HtmlQuery::$query {
                    x: Box::new(x),
                    y: Box::new(y),
                })
            }};
        }

        match *self.kind(py) {
            query::QUERY_NAME => {
                let string = try!(self.value(py).cast_as::<PyString>(py));
                let string = try!(string.to_string(py));
                Ok(HtmlQuery::Name(string.into_owned()))
            }
            query::QUERY_ATTRIBUTE => {
                let dict = try!(self.value(py).cast_as::<PyDict>(py));
                let name = try!(get_strs_from_dict(&dict, py, "name"));
                let value = try!(get_strs_from_dict(&dict, py, "value"));
                Ok(HtmlQuery::Attribute {
                    key: name,
                    value: value,
                })
            }
            query::QUERY_AND => binary_query!(And),
            query::QUERY_OR => binary_query!(Or),
            query::QUERY_NONE => Ok(HtmlQuery::None),
            query::QUERY_DATA => {
                let string = try!(self.value(py).cast_as::<PyString>(py));
                let string = try!(string.to_string(py));
                Ok(HtmlQuery::Data(string.into_owned()))
            }
            query::QUERY_NOT => {
                let compiled = try!(self.value(py).cast_as::<PyQuery>(py)).to_query(py);
                Ok(compiled?.not())
            }
            _ => unimplemented!(),
        }
    }
}
