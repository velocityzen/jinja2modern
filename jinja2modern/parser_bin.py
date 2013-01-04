import os
import shlex
import subprocess
from jinja2 import PackageLoader, TemplateNotFound
from jinja2modern.parser_error import ParserError
from jinja2modern.utils import strip_list, create_dir_if_not_exist
from settings import JINJA2MODERN_ENGINES, JINJA2MODERN_HOME, JINJA2MODERN_MEDIA_PATH, JINJA2MODERN_MEDIA_URL


class Parser():

    def __init__(self, environment, parser_bin, template, out_dir, out_extension = None, parser_single = None, parser_multiple = None):
        self.parser_bin = JINJA2MODERN_ENGINES[parser_bin]
        if not os.path.exists(self.parser_bin):
            raise ParserError("Parser not found: {parser}".format(parser = self.parser_bin))

        self.environment = environment
        self.environment.extend(
            jinja2modern_loader = PackageLoader('jinja2modern')
        )

        self.template = template
        self.out_dir = out_dir
        self.out_extension = out_extension
        self.parser_single = parser_single
        self.parser_multiple = parser_multiple

    def needUpdate(self, in_files, out_file):

        if not out_file or not os.path.exists(out_file):
            return True

        out_file_stat = os.stat(out_file)

        if not out_file_stat.st_size:
            return True

        for file in in_files:
            if os.stat(file).st_mtime >= out_file_stat.st_mtime:
                return True

        return False

    def parse(self, input_str, out_file):

        #single file {% tag "some_file" %}
        if not input_str and out_file:
            files = [out_file]

            if self.out_extension:
                out_file = os.path.splitext(os.path.basename(out_file))[0] + '.' + self.out_extension
            else:
                out_file = os.path.basename(out_file)

        else:
            files = strip_list(input_str.split('\n'))

        files = [os.path.join(JINJA2MODERN_HOME, f) for f in files]

        if out_file:
            out_relative_path, out_file = os.path.split(out_file)
            if out_relative_path:
                out_path = os.path.join(JINJA2MODERN_HOME, JINJA2MODERN_MEDIA_PATH, out_relative_path)
            else:
                out_path = os.path.join(JINJA2MODERN_HOME, JINJA2MODERN_MEDIA_PATH, self.out_dir)
            out_path_file = os.path.join(out_path, out_file)
            create_dir_if_not_exist(out_path)

        #single file
        if len(files) == 1 and self.parser_single:

            # no out_file for single file conversion in self (example uglify tag in single file mode)
            if not out_file:
                render = False

                if self.out_extension:
                    out_path_file = os.path.splitext(files[0])[0] + '.' + self.out_extension
                else:
                    out_path_file = files[0]

                out_path, out_file = os.path.split(files[0])

            else:
                render = True

            if self.needUpdate(files, out_path_file):

                args = shlex.split('{bin} {options}'.format(
                    bin = self.parser_bin,
                    options = self.parser_single.format(
                        in_file = files[0],
                        out_path = out_path,
                        out_file = out_file,
                        out_path_file = out_path_file
                    )
                ))

                self.compile(args)

            if render:
                return self.render((out_relative_path or self.out_dir) + '/' + out_file)
            else:
                return ''

        #multiple
        elif len(files) > 1 and self.parser_multiple and out_file:
            if self.needUpdate(files, out_path_file):
                args = shlex.split('{bin} {options}'.format(
                    bin = self.parser_bin,
                    options = self.parser_multiple.format(
                        in_files = ' '.join(files),
                        out_path = out_path,
                        out_path_file = out_path_file,
                        out_file = out_file,
                    )
                ))

                self.compile(args)
            return self.render( (out_relative_path or self.out_dir) + '/' + out_file)

        else:
            raise ParserError("Not enough parameters")

    def compile(self, args):
        p = subprocess.Popen(args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={
                'PATH': '/usr/local/bin:' + os.getenv('PATH')
            }
        )
        output, errors = p.communicate()

        if errors:
            raise ParserError(errors.decode("utf-8"))

    def render(self, file_link):
        try:
            out_t = self.environment.get_template(self.template)
        except TemplateNotFound:
            out_t = self.environment.jinja2modern_loader.load(self.environment, self.template)

        return out_t.render(file_link = JINJA2MODERN_MEDIA_URL + '/' + file_link)

