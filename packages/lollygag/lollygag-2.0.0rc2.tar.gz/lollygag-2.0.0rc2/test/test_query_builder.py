from lollygag.query_builder import QueryBuilder


def test_can_build_name_query():
    qb = QueryBuilder().name('div')
    assert qb.raw_query == {'name': 'div'}


def test_can_build_chained_query():
    qb = QueryBuilder().name('foo')._and().attribute('bar', 'b.*')
    assert qb.raw_query == {
        'and': ({
            'name': 'foo'
        }, {
            'attribute': {
                'name': 'bar',
                'value': 'b.*'
            }
        })
    }


def test_longer_chained_query():
    qb = QueryBuilder().name('foo')._and().attribute(
        'bar', 'b.*')._or().data('kewlaid')
    assert qb.raw_query == {
        'or': ({
            'and': ({
                'name': 'foo'
            }, {
                'attribute': {
                    'name': 'bar',
                    'value': 'b.*'
                }
            })
        }, {
            'data': 'kewlaid'
        })
    }


def test_not_query():
    qb = QueryBuilder()._not().name('div')
    assert qb.raw_query == {'not': {'name': 'div'}}


def test_not_chains():
    qb = QueryBuilder()._not().name('div')._and()._not().data('foo')
    assert qb.raw_query == {
        'and': ({
            'not': {
                'name': 'div'
            }
        }, {
            'not': {
                'data': 'foo'
            }
        })
    }
