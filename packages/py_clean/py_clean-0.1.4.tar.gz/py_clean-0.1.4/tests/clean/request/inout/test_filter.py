from clean.request.inout.filter import Sort, Page


def test_sort_entity():
    sort = Sort(by='created')

    assert sort.by == 'created'


def test_sort_entity_from_dict():
    params = dict(by='created')
    sort = Sort.from_dict(params)

    assert sort.by == 'created'


def test_page_defaults_entity():
    page = Page()

    assert page.offset == 0
    assert page.limit == 100


def test_page_entity():
    page = Page(offset=100, limit=1000)

    assert page.limit == 1000
    assert page.offset == 100


def test_page_entity_from_dict():
    params = dict(offset=100, limit=1000)
    page = Page.from_dict(params)

    assert page.limit == 1000
    assert page.offset == 100
