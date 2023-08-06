extern crate html5ever;
extern crate regex;
extern crate reqwest;
extern crate tokio;

mod http;
mod query;
mod simple_node;
pub use http::*;
pub use query::*;
pub use simple_node::*;

#[derive(Debug)]
pub enum LollygagError {
    UnknownError,
    ParseError(String),
    HttpError(usize),
    LogicError(String),
}
