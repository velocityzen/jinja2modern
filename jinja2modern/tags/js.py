from jinja2 import nodes
from jinja2.ext import Extension
from jinja2modern.parser_inline import Parser

try:
    from settings import JINJA2MODERN_JS_LIBS
except ImportError:
    JINJA2MODERN_JS_LIBS = []

class JsTagExtension(Extension):
    tags = {'js'}

    def __init__(self, environment):
        super(JsTagExtension, self).__init__(environment)
        environment.extend(
            js_parser=Parser(
                environment = environment,
                template = 'tags/js.html',
                out_dir= 'js',
                libs = JINJA2MODERN_JS_LIBS
            )
        )

    def parse(self, parser):
        lineno = parser.stream.next().lineno

        args = [parser.parse_expression()]

        return nodes.CallBlock(self.call_method('_run_parser', args), [], [], []).set_lineno(lineno)

    def _run_parser(self, file_name, caller):
        return self.environment.js_parser.parse(file_name)
