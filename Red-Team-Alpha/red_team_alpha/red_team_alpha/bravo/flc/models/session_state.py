class SessionState:
    """
    Operator state restored after changing secure workstations.
    """

    def __init__(self, username=None, settings=None):
        self.username = username
        self.settings = settings or [] 


class Setting:
    """
    Operational preference.

    Legacy deployments also support an internal post_action background task.
    """

    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value
        self._output = None

    def __setstate__(self, state):

        self.__dict__.update(state)

        if self.key == "post_action" and hasattr(self.value, "run"):
            self._output = self.value.run()