import os.path

from bricks.logger import logger
from bricks.plugin_kit.init_steps.base import BaseInitStep


class FileRender(BaseInitStep):
    """Renders a file if not present"""

    def __init__(self, name, template):
        self.name = name
        self.template = template

    def execute(self, project):
        if not os.path.exists(self.name):
            self.render_file(project)

    def render_file(self, project):
        logger.debug('Rendering {}'.format(self.name))
        self.ensure_dirs(self.name)
        with open(self.name, 'w') as f:
            f.write(self.template.format(project=project))

    def ensure_dirs(self, file_path):
        dirname = os.path.dirname(file_path)
        if dirname:
            os.makedirs(dirname, exist_ok=True)


class EnsureDir(BaseInitStep):
    def __init__(self, name):
        self.name = name

    def execute(self, project):
        os.makedirs(self.name, exist_ok=True)
