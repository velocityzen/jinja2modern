from jinja2 import nodes
from jinja2.ext import Extension
from jinja2modern.parser_bin import Parser

class CoffeeTagExtension(Extension):
    tags = {'coffee'}

    def __init__(self, environment):
        super(CoffeeTagExtension, self).__init__(environment)
        environment.extend(
            coffee_parser=Parser(
                environment = environment,
                parser_bin = 'coffee',
                parser_single = '--output {out_path} --join {out_file} {in_file}',
                parser_multiple = '--output {out_path} --join {out_file} {in_files}',
                template = 'tags/js.html',
                out_dir= 'js',
                out_extension= 'js'
            )
        )

    def parse(self, parser):
        lineno = parser.stream.next().lineno

        args = [parser.parse_expression()]

        if parser.stream.look().value.strip('{% '):
            body = parser.parse_statements(
                ['name:endcoffee',],
                drop_needle=True
            )
        else:
            body = []

        return nodes.CallBlock(self.call_method('_run_parser', args), [], [], body).set_lineno(lineno)

    def _run_parser(self, name, caller):
        return self.environment.coffee_parser.parse(caller(), name)
