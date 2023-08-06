from functools import reduce
from warnings import warn
from lollygag_ext import PyQuery, QUERY_NAME, QUERY_ATTRIBUTE, QUERY_AND, QUERY_OR, QUERY_DATA, QUERY_NONE, QUERY_NOT
from lollygag_ext import query_html as _query_html
from lollygag_ext import query_http_endpoint as _query_http_endpoint
from lollygag_ext import query_multiple_endpoints as _query_multiple_endpoints


def query_multiple_endpoints(urls, query: PyQuery):
    """
    Get nodes matching the query in the response of the GET request sent to each `url` of `urls`
    Params:
        urls: iterable of strs
    """
    urls = list(urls)
    return _query_multiple_endpoints(urls, query)


def query_http_endpoint(url: str, query: PyQuery):
    """
    Get nodes matching the query in the response of the GET request sent to `url`
    """
    return _query_http_endpoint(url, query)


def query_html(html: str, query: PyQuery):
    """
    Get nodes matching the query from an html string
    """
    return _query_html(html, query)


def compile_query(query: dict) -> PyQuery:
    """
    Compiles a query
    Syntax:
        TBA
    """

    def _pair_to_dict(pair):
        if isinstance(pair, dict):
            return pair
        return {pair[0]: pair[1]}

    def _reduce(pair):
        try:
            return {'and': (_pair_to_dict(pair[0]), _pair_to_dict(pair[1]))}
        except (KeyError, IndexError):
            return _pair_to_dict(pair)

    def _get_first_pair(d: dict):
        return list(query.items())[0]

    if len(query) < 2:
        return compile_single_item(*_get_first_pair(query))
    try:
        reduced = reduce(lambda x, y: _reduce((x, y)), query.items())
    except KeyError:
        print(query)
        reduced = query
        raise
    return compile_single_item(*_get_first_pair(reduced))


def compile_single_item(key: str, value, parent: PyQuery = None) -> PyQuery:
    try:
        compiler = {
            'name': lambda: compile_name(value),
            'attribute': lambda: compile_attribute(value),
            'data': lambda: compile_data(value),
            'or': lambda: compile_binary(QUERY_OR, value, parent),
            'and': lambda: compile_binary(QUERY_AND, value, parent),
            'not': lambda: compile_not(value),
        }[key]
    except KeyError:
        warn(f"{key} is not a recognised query type!")
        return PyQuery(QUERY_NONE)
    return compiler()


def compile_not(query) -> PyQuery:
    return PyQuery(QUERY_NOT, compile_query(query))


def compile_name(value: str) -> PyQuery:
    assert isinstance(value, str), "Name queries must be strs!"
    return PyQuery(QUERY_NAME, value)


def compile_attribute(value: dict) -> PyQuery:
    assert isinstance(value, dict), "Attribute queries must be dicts!"
    assert "name" in value, "Attribute queries must contain 'name' field!"
    assert "value" in value, "Attribute queries must contain 'value' field!"
    return PyQuery(QUERY_ATTRIBUTE, value)


def compile_data(value: str) -> PyQuery:
    assert isinstance(value, str), "Data queries must be strs!"
    return PyQuery(QUERY_DATA, value)


def compile_binary(t, queries, parent=None):
    result = PyQuery(t, tuple(compile_query(q) for q in queries))
    if parent:
        result = PyQuery(t, (parent, result))
    return result
