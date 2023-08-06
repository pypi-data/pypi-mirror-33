from lollygag.query import compile_query
from lollygag.query import query_http_endpoint
from lollygag.query import query_multiple_endpoints


def test_can_query_rust_lang():
    url = "https://rust-lang.org/en-US"
    query = compile_query({"and": ({"name": "a"}, {"data": "(r|R)ust"})})
    result = query_http_endpoint(url, query)
    print("\n".join([str(r) for r in result]))
    assert result
    assert len(result) == 2
    assert result[0].get_attributes()[0] == ('href', 'friends.html')
    assert result[1].get_attributes()[0] == ('href', 'whitepapers.html')


def test_can_query_multiple_endpoints():
    urls = set([
        "https://rust-lang.org/en-US",
        "https://google.com",
    ])
    query = compile_query({"and": ({"name": "a"}, {"data": "(r|R)ust"})})
    result = query_multiple_endpoints(urls, query)
    print(result)
    assert len(result) == len(urls)
    for url in urls:
        assert url in result
