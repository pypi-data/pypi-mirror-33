import shutil

import os
from jinja2 import Environment, FileSystemLoader, TemplateSyntaxError


class PreProcess:
    def __init__(self, directory, data):
        self.directory = directory
        self.data = data

    def process(self, temp_dir):
        self.move_to_temp(temp_dir)
        self.render_templates(temp_dir)

    def move_to_temp(self, temp_dir):
        shutil.copytree(self.directory, temp_dir)

    def render_templates(self, temp_dir):
        env = Environment(loader=FileSystemLoader(temp_dir), trim_blocks=True)

        files = os.listdir(temp_dir)
        files = [file for file in files if file.endswith('.xml')]

        for file in files:
            try:
                content = env.get_template(file).render(**self.data)

                # generate file from template and write to the same file.
                with open(os.path.join(temp_dir, file), 'w') as f:
                    f.write(content)
            except TemplateSyntaxError as e:
                print(f'{file}:{e.lineno}: {e}')
