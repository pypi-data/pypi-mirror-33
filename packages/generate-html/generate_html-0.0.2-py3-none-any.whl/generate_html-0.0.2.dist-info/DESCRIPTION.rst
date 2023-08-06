# generate-html

Generate HTML5 with pure Python.

## Usage

	@document
	def hello_world(h):
		with h.p(class_='main'):
			yield h.span(h.strong("Hello World!"), data_msg='greeting')

	>>> print(to_html(hello_world()))
	<!doctype html><p class="main"><span data-msg="greeting"><strong>Hello World!</strong></span></p>

## Installation

generate-html is distributed on [PyPI](https://pypi.org) as a universal
wheel and is available on Linux/macOS and Windows and supports
Python 3.5+ and PyPy.

    $ pip install generate-html

## License

generate-html is distributed under the terms of the
[MIT License](https://choosealicense.com/licenses/mit).


