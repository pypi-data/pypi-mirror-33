from lollygag.query import compile_query, query_html
from lollygag_ext import NODE_DOCUMENT, NODE_ELEMENT, NODE_TEXT

some_html = """
<asd-node style="boi" foo="bar">   <some-node foo="baz">
                          asdkjaksdjaskjdjs
</asd-node>
<asd-node>
                            </asd-node>
<li>
    <i>
        some asd data   </i>
</li>
"""


def test_data_query_regex():
    html = """
<ul>
    <li>
        something interesting
    </li>
    <li>
        some item
    </li>
    <li>
        something interesting
    </li>
    <li>
        some item
    </li>
    <li>
        something interesting
    </li>
</ul>
    """
    query = compile_query({"data": "inter.*"})
    result = query_html(html, query)
    assert result
    assert len(result) == 3
    for r in result:
        r = str(r)
        print(r)
        assert r == """<li>
    something interesting
</li>
"""


def test_name_query_regex():
    query = compile_query({"name": "some.*"})
    result = query_html(some_html, query)
    assert result
    assert len(result) == 1

    res = str(result[0])
    print(res)
    assert res == """<some-node foo="baz">
    asdkjaksdjaskjdjs
</some-node>
"""


def test_attribute_query_regex():
    query = compile_query({"attribute": {"name": "foo", "value": "ba."}})
    result = query_html(some_html, query)
    assert result
    assert len(result) == 2

    res = str(result[0])
    print(res)
    assert res == """<asd-node style="boi" foo="bar">
    <some-node foo="baz">
        asdkjaksdjaskjdjs
    </some-node>
</asd-node>
"""

    res = str(result[1])
    print(res)
    assert res == """<some-node foo="baz">
    asdkjaksdjaskjdjs
</some-node>
"""


def test_attribute_query():
    query = compile_query({"attribute": {"name": "foo", "value": "bar"}})
    result = query_html(some_html, query)
    assert result
    assert len(result) == 1

    res = str(result[0])
    print(res)
    assert res == """<asd-node style="boi" foo="bar">
    <some-node foo="baz">
        asdkjaksdjaskjdjs
    </some-node>
</asd-node>
"""


def test_not_attribute_query():
    """
    Query:
        element should not have `foo="bar"` attribute nor should be named any of ['html', 'head', 'body]
    """
    query = compile_query({
        "not": {
            "or": (
                {
                    "attribute": {
                        "name": "foo",
                        "value": "bar"
                    }
                },
                {
                    "name": "html|head|body"
                },
            )
        },
    })
    html = """<foo foo="bar"></foo><foo >boingatros</foo>"""
    result = query_html(html, query)
    print(result)
    assert result
    for r in result:
        print(str(r))
    assert len(result) == 3
    assert result[0].get_type() == NODE_DOCUMENT
    assert result[1].get_type() == NODE_ELEMENT
    assert str(result[1]) == """<foo>
    boingatros
</foo>
"""
    assert result[2].get_type() == NODE_TEXT
    assert str(result[2]) == "boingatros\n"


def test_or_query():
    query = compile_query({
        "or": ({
            "attribute": {
                "name": "foo",
                "value": "bar"
            },
            "name": "asd-node",
        }, {
            "data": "asd"
        })
    })
    result = query_html(some_html, query)
    assert result
    assert len(result) == 3

    res = str(result[0])
    print(res)
    assert res == """<asd-node style="boi" foo="bar">
    <some-node foo="baz">
        asdkjaksdjaskjdjs
    </some-node>
</asd-node>
"""
    res = str(result[1])
    print(res)
    assert res == """<some-node foo="baz">
    asdkjaksdjaskjdjs
</some-node>
"""
    res = str(result[2])
    print(res)
    assert res == """<i>
    some asd data
</i>
"""
