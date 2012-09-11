from jinja2 import nodes
from jinja2.ext import Extension
from jinja2modern.parser_bin import Parser

class LessTagExtension(Extension):
    tags = {'less'}

    def __init__(self, environment):
        super(LessTagExtension, self).__init__(environment)
        environment.extend(
            less_parser=Parser(
                environment = environment,
                parser_bin = 'less/bin/lessc',
                parser_single= '-x {in_file} {out_path_file}',
                template = 'tags/css.html',
                out_dir= 'css',
                out_extension= 'css'
            )
        )

    def parse(self, parser):
        lineno = parser.stream.next().lineno

        args = [parser.parse_expression()]

        if parser.stream.look().value.strip('{% '):
            body = parser.parse_statements(
                ['name:endless',],
                drop_needle=True
            )
        else:
            body = []

        return nodes.CallBlock(self.call_method('_run_parser', args), [], [], body).set_lineno(lineno)

    def _run_parser(self, name, caller):
        return self.environment.less_parser.parse(caller(), name)
