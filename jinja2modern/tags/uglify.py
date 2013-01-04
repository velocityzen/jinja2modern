from jinja2 import nodes
from jinja2.ext import Extension
from jinja2modern.parser_bin import Parser

class UglifyTagExtension(Extension):
    tags = {'uglify'}

    def __init__(self, environment):
        super(UglifyTagExtension, self).__init__(environment)
        environment.extend(
            uglify_parser=Parser(
                environment = environment,
                parser_bin = 'uglify',
                parser_single = '--output {out_path_file} {in_file}',
                parser_multiple = '--output {out_path_file} {in_files}',
                template = 'tags/js.html',
                out_dir= 'js',
            )
        )

    def parse(self, parser):
        lineno = parser.stream.next().lineno

        if parser.stream.current.type != 'block_end':
            args = [parser.parse_expression()]
        else:
            args = [nodes.Const(None)]

        if parser.stream.look().value.strip('{% '):
            body = parser.parse_statements(
                ['name:enduglify'],
                drop_needle=True
            )
        else:
            body = []

        return nodes.CallBlock(self.call_method('_run_parser', args), [], [], body).set_lineno(lineno)

    def _run_parser(self, name, caller):
        return self.environment.uglify_parser.parse(caller(), name)
