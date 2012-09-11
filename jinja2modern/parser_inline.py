import glob
import os
import shutil
from jinja2 import Template, PackageLoader, TemplateNotFound
from jinja2modern.parser_error import ParserError
from jinja2modern.utils import create_dir_if_not_exist, open_if_exists
from settings import JINJA2MODERN_HOME, JINJA2MODERN_MEDIA_PATH, JINJA2MODERN_MEDIA_URL

class Parser():
    def __init__(self, environment, template, out_dir, libs = None):
        self.environment = environment
        self.environment.extend(
            jinja2modern_loader = PackageLoader('jinja2modern')
        )

        self.template = template
        self.out_dir = out_dir
        self.libs = libs

    def needUpdate(self, in_files, out_file):

        if not out_file or not os.path.exists(out_file):
            return True

        out_file_stat = os.stat(out_file)

        if not out_file_stat.st_size:
            return True

        for file in in_files:
            if os.stat(file).st_mtime > out_file_stat.st_mtime:
                return True

        return False

    def parse(self, input):

        if input in self.libs:
            lib = glob.glob(os.path.join(JINJA2MODERN_HOME, self.libs[input]['src']))

            if not lib:
                raise ParserError('%s lib not found' % input)

            try:
                from settings import JINJA2MODERN_JS_LIBS_PATH
                out_path = os.path.join(JINJA2MODERN_MEDIA_PATH, JINJA2MODERN_JS_LIBS_PATH)
            except ImportError:
                out_path = os.path.join(JINJA2MODERN_MEDIA_PATH, self.out_dir, 'libs')

            out_file = os.path.split(lib[0])[1]
            out_path_file = os.path.join(out_path, out_file)

            if self.needUpdate(lib, out_path_file):
                create_dir_if_not_exist(out_path)
                shutil.copy(lib[0], out_path_file)

            if 'template' in self.libs[input]:
                return self.render(
                    template = self.libs[input]['template'],
                    file_link = (JINJA2MODERN_JS_LIBS_PATH or self.out_dir + '/libs') + '/' + out_file
                )
            else:
                return self.render(
                    file_link = (JINJA2MODERN_JS_LIBS_PATH or self.out_dir + '/libs') + '/' + out_file
                )

        else:
            out_relative_path, out_file = os.path.split(input)
            if out_relative_path:
                out_path = os.path.join(JINJA2MODERN_HOME, JINJA2MODERN_MEDIA_PATH, out_relative_path)
            else:
                out_path = os.path.join(JINJA2MODERN_HOME, JINJA2MODERN_MEDIA_PATH, self.out_dir)

            out_path_file = os.path.join(out_path, out_file)

            input = os.path.join(JINJA2MODERN_HOME, input)

            if self.needUpdate([input], out_path_file):
                create_dir_if_not_exist(out_path)
                shutil.copy(input, out_path_file)

            return self.render(
                file_link = (out_relative_path or self.out_dir) + '/' + out_file
            )

    def render(self, file_link = '', template = None):

        if not template:
            template = self.template

        try:
            out_t = self.environment.get_template(template)
        except TemplateNotFound:
            out_t = self.environment.jinja2modern_loader.load(self.environment, template)

        return out_t.render(file_link = JINJA2MODERN_MEDIA_URL + '/' + file_link)