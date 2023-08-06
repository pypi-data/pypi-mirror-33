from hypothesis import given, note
from hypothesis.strategies import text, integers
import pytest
import generate_html

@given(text())
def test_simple_content(t):
    @generate_html.document
    def d(h):
        yield t
    assert d().__html__() == '<!doctype html>' + generate_html.escape(t)

@given(text(), integers(0, 100))
def test_simple_component(t, i):
    @generate_html.component
    def c(h):
        with h.p():
            yield h.insert_contents()
    @generate_html.document
    def d(h):
        for _ in range(i):
            with c(h):
                yield h.span(t)
    note(d().__html__())
    assert d().__html__() == '<!doctype html>' + f'<p><span>{generate_html.escape(t)}</span></p>' * i

@given(integers(0, 10))
def test_iterative_component(i):
    @generate_html.component
    def c(h):
        with h.p():
            for x in range(i):
                yield h.insert_contents(x)
    @generate_html.document
    def d(h):
        for x in c(h):
            yield h.span(x)
    note(d().__html__())
    assert d().__html__() == '<!doctype html><p>' + ''.join(f'<span>{x}</span>' for x in range(i)) + '</p>'

def test_recursive_component():
    @generate_html.component
    def c1(h):
        with h.b():
            yield h.insert_contents()
    @generate_html.component
    def c2(h):
        with c1(h):
            with h.i():
                yield h.insert_contents()
    @generate_html.document
    def d(h):
        for () in c2(h):
            yield 'hi'
    assert d().__html__() == '<!doctype html><b><i>hi</i></b>'

def test_insert_components_fail():
    @generate_html.component
    def c(h):
        yield h.p(h.insert_contents())
    @generate_html.document
    def d(h):
        with c(h):
            yield h.span('nothing')

    with pytest.raises(TypeError):
        d().__html__()

@given(text())
def test_comment(t):
    @generate_html.document
    def d(h):
        yield h.insert_comment(t)
    note(d().__html__())
    assert d().__html__() == '<!doctype html><!-- ' + generate_html.escape(t) + ' -->'
