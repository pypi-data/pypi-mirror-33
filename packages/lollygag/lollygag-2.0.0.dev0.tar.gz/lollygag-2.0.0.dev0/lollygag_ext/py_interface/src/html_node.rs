use cpython::PythonObject;
use cpython::{PyList, PyResult, PyString, PyTuple, Python};
use lollygag;

pub mod node_type {
    pub const UNKNOWN: u8 = 0;
    pub const DOCUMENT: u8 = 1;
    pub const ELEMENT: u8 = 2;
    pub const TEXT: u8 = 3;
}

py_class!(pub class HtmlNode |py| {
    data node: lollygag::SimpleHtmlNode;

    def __str__(&self) -> PyResult<String> {
        Ok(self.node(py).to_string())
    }

    def __repr__(&self) -> PyResult<String> {
        let result = match self.node(py).data {
            lollygag::NodeData::Element {ref name, ref attributes } => {
                format!("HtmlNode <{}>", name)
            },
            lollygag::NodeData::Text (ref content) => {
                format!("TextNode[{}]", content.len())
            },
            lollygag::NodeData::Document => {
                format!("Document")
            }
            _ => format!("UNKNOWN")
        };
        Ok(format!("<Lollygag::HtmlNode {}>", result))
    }

    def get_children(&self) -> PyResult<PyList> {
        unimplemented!()
    }

    def get_type(&self) -> PyResult<u8> {
        let result = match self.node(py).data {
            lollygag::NodeData::Element { .. } => {
                node_type::ELEMENT
            },
            lollygag::NodeData::Text (_) => {
                node_type::TEXT
            },
            lollygag::NodeData::Document => {
                node_type::DOCUMENT
            },
            _ => node_type::UNKNOWN
        };
        Ok(result)
    }

    def get_attributes(&self) -> PyResult<Option<PyList>> {
        let result = match self.node(py).data {
            lollygag::NodeData::Element { ref attributes, .. } => {
                let mut result = vec![];
                for (key, value) in attributes {
                    result.push( PyTuple::new(py,
                        &[
                            PyString::new(py, key).into_object(), 
                            PyString::new(py, value).into_object()
                        ]).into_object());
                }
                Some(PyList::new(py, result.as_slice()))
            }
            _ => None
        };
        Ok(result)
    }
});

impl HtmlNode {
    pub fn new(py: Python, node: lollygag::SimpleHtmlNode) -> PyResult<HtmlNode> {
        HtmlNode::create_instance(py, node)
    }
}
