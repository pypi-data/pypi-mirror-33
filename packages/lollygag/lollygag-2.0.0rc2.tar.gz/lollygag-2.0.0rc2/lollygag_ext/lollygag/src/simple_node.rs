use html5ever::rcdom::{Handle, NodeData as Html5NodeData};

#[derive(Debug)]
pub struct SimpleHtmlNode {
    pub data: NodeData,
    pub children: Vec<SimpleHtmlNode>,
}

#[derive(Debug)]
pub enum NodeData {
    Element {
        name: String,
        attributes: Vec<(String, String)>,
    },
    Text(String),
    Document,
    Unknown,
}

unsafe impl Send for SimpleHtmlNode {}
unsafe impl Sync for SimpleHtmlNode {}

impl SimpleHtmlNode {
    pub fn new(data: NodeData, children: Vec<SimpleHtmlNode>) -> SimpleHtmlNode {
        SimpleHtmlNode {
            data: data,
            children: children,
        }
    }

    pub fn from_html5ever_node(node: &Handle) -> SimpleHtmlNode {
        match node.data {
            Html5NodeData::Element {
                ref name,
                ref attrs,
                ..
            } => {
                let mut attributes = vec![];
                for attr in attrs.borrow().iter() {
                    let attribute = (attr.name.local.to_string(), attr.value.to_string());
                    attributes.push(attribute);
                }
                SimpleHtmlNode {
                    data: NodeData::Element {
                        name: name.local.to_string(),
                        attributes: attributes,
                    },
                    children: SimpleHtmlNode::convert_children(node),
                }
            }
            Html5NodeData::Text { ref contents, .. } => SimpleHtmlNode {
                data: NodeData::Text(contents.borrow().to_string()),
                children: vec![],
            },
            Html5NodeData::Document { .. } => SimpleHtmlNode {
                data: NodeData::Document,
                children: SimpleHtmlNode::convert_children(node),
            },
            _ => SimpleHtmlNode {
                data: NodeData::Unknown,
                children: SimpleHtmlNode::convert_children(node),
            },
        }
    }

    fn convert_children(node: &Handle) -> Vec<SimpleHtmlNode> {
        let mut children = vec![];
        for child in node.children.borrow().iter() {
            let child = SimpleHtmlNode::from_html5ever_node(child);
            if let NodeData::Text(ref text) = &child.data {
                if text.trim().len() == 0 {
                    continue;
                }
            }
            children.push(child);
        }
        children
    }

    pub fn to_string(&self) -> String {
        self.write(0)
    }

    pub fn write(&self, indent: usize) -> String {
        let padding = " ".repeat(indent);
        let write_children = || {
            let mut result = String::new();
            for child in &self.children {
                result += &child.write(indent + 4);
            }
            result
        };
        let result = match self.data {
            NodeData::Text(ref text) => format!("{}{}\n", padding, text.trim()),
            NodeData::Element {
                ref name,
                ref attributes,
            } => {
                let mut result = format!("{}<{}", padding, name);
                for (key, value) in attributes {
                    result += &format!(" {}=\"{}\"", key, value);
                }
                result += &format!(">\n{}{}</{}>\n", write_children(), padding, name);
                result
            }
            NodeData::Document => format!("<document>\n{}</document>\n", write_children()),
            NodeData::Unknown => format!("<UNKNOWN_NODE>\n{}</UNKNOWN_NODE>\n", write_children()),
        };
        result
    }
}
