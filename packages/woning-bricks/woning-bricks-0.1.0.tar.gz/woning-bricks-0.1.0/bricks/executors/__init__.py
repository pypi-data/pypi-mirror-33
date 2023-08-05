from bricks.exceptions import DriverNotRecognizedError
from bricks.executors.docker import DockerComposeExecutor
from bricks.executors.local import LocalExecutor
from bricks.executors.native import NativeExecutor

_executor_classes = {
    'local': LocalExecutor,
    'docker': DockerComposeExecutor,
    'native': NativeExecutor
}


def get_executor(driver, project):
    try:
        return _executor_classes[driver](project)
    except KeyError:
        raise DriverNotRecognizedError(driver)
