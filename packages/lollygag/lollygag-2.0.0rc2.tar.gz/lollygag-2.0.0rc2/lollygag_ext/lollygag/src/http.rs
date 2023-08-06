use html5ever::parse_document;
use html5ever::rcdom::{Handle, RcDom};
use html5ever::tendril::stream::TendrilSink;
use reqwest;
use reqwest::Response;
use std;
use std::sync::{Arc, Mutex};
use std::thread;

use std::collections::HashMap;

use super::LollygagError;
use query::{query_tree, HtmlQuery};
use simple_node::SimpleHtmlNode;

type LollygagResult = Result<Vec<SimpleHtmlNode>, LollygagError>;

/// Send a GET request to each url
/// Then run the query against the returned responses
pub fn query_multiple_endpoints(
    urls: Vec<String>,
    query: &HtmlQuery,
) -> HashMap<String, LollygagResult> {
    let result = Arc::new(Mutex::new(HashMap::new()));
    let mut threads = vec![];
    for url in urls {
        let query = query.clone();
        let retval = result.clone();
        threads.push(thread::spawn(move || {
            let result = query_endpoint_worker(url.clone(), query);
            let mut retval = retval.lock().unwrap();
            retval.insert(url, result);
        }));
    }
    for thread in threads {
        thread
            .join()
            .expect("Failed to join threads in [query_multiple_endpoints]!");
    }
    let lock = match Arc::try_unwrap(result) {
        Ok(lock) => lock,
        _ => panic!("Arc still has owners!"),
    };
    lock.into_inner().expect("Mutex cannot be locked!")
}

fn query_endpoint_worker(url: String, query: HtmlQuery) -> LollygagResult {
    match query_http_endpoint(&url, &query) {
        Ok(results) => {
            let mut mapped = vec![];
            for result in results {
                mapped.push(result);
            }
            Ok(mapped)
        }
        Err(e) => Err(e),
    }
}

/// Send a GET request to the specified url
/// Then run the query against the returned (assumed) html
pub fn query_http_endpoint(url: &str, query: &HtmlQuery) -> LollygagResult {
    match fetch_url(url) {
        Ok(mut response) => match response.text() {
            Ok(body) => process_body(body, query, url),
            Err(e) => Err(LollygagError::ParseError(format!(
                "url [{}] response has no text field\n{}",
                url, e
            ))),
        },
        Err(e) => panic!(e),
    }
}

fn process_body(body: String, query: &HtmlQuery, url: &str) -> LollygagResult {
    let handle = match get_handle(body) {
        Ok(handle) => handle,
        Err(e) => {
            return Err(LollygagError::ParseError(format!(
                "url [{}] response could not be parsed\n{}",
                url, e
            )))
        }
    };
    query_tree(&handle, query)
}

fn get_handle(html: String) -> std::io::Result<Handle> {
    let handle = parse_document(RcDom::default(), Default::default())
        .from_utf8()
        .read_from(&mut html.as_bytes())
        .unwrap();
    Ok(handle.document)
}

fn fetch_url(url: &str) -> Result<Response, reqwest::Error> {
    let client = reqwest::Client::new();
    client.get(url).send()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_can_fetch_google_via_https() {
        let url = "https://google.com";
        let result = fetch_url(url);
        match result {
            Ok(result) => match result.status() {
                reqwest::StatusCode::Ok => {}
                _ => panic!(),
            },
            Err(e) => panic!("whops {:?}", e),
        }
    }

    #[test]
    fn test_can_query_google() {
        match query_http_endpoint(
            "https://google.com",
            &HtmlQuery::Data("goo.{3}".to_string()),
        ) {
            Ok(result) => assert_eq!(result.len(), 3),
            Err(e) => panic!("{:?}", e),
        }
    }

    #[test]
    fn test_can_query_multiple_urls() {
        let query: HtmlQuery = HtmlQuery::Data("goo.{3}".to_string());
        let results = query_multiple_endpoints(
            vec![
                String::from("https://google.com"),
                String::from("https://youtube.com"),
                String::from("https://github.com"),
            ],
            &query,
        );
        assert_eq!(results.len(), 3);
        for (_url, result) in results {
            if let Err(e) = result {
                panic!("{:?}", e);
            }
        }
    }
}
