from bricks.executors.base import BaseExecutor


class NativeExecutor(BaseExecutor):
    """Executed native python methods of the plugin.
    Those methods must be exposed with the
    bricks.plugin_kit.base.native_command decorator.

    The parameters are received as keyword arguments in the method.

    Example::

        class Plugin(BasePlugin):
            ...
            @native_command()
            def test(self, only_unit=False):
                ...

    Then we can run it like this

    ::

        bricks run test -p only_unit=true

    The parameters are always received as strings.
    """

    def execute_command(self, command, params):
        try:
            command(**params)
        except Exception as e:
            return str(e)
        else:
            return 0
