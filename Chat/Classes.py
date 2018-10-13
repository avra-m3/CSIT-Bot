from asyncio import coroutine
from typing import List


class ChatCommand:
    # Are arguments for this command case sensitive.
    case_sensitive: bool
    # The name of the command, also the base hook.
    name: str
    # All hooks, matching any of these will trigger the callback
    hooks: List[str]
    # Secondaries are hooks that are required in addition to whichever hook is matched.
    secondaries: List[str]
    # does this command cancel out subsequent commands.
    blocking: bool
    # The raw, unwrapped co-routine.
    _callback: coroutine

    def __init__(self, name: str, callback):
        self.name = name

        self.hooks = [name]
        self._callback = callback

        self.case_sensitive = False
        self.blocking = False
        self.secondaries = []

    def is_case_sensitive(self):
        """
        Set this command to be case_sensitive
        :return: self; for chaining
        """
        self.case_sensitive = True
        return self

    def alias(self, *hooks: str, required=False):
        """
        Add a/multiple alias hooks for this command these hooks will trigger the command as well.
        :param required: If true, the aliases will be required in addition to any of the hooks.
        :param hooks: All arguments passed get added as hooks
        :return: self for chaining
        """
        if not required:
            self.hooks.extend(hooks)
        else:
            self.secondaries.extend(hooks)
        return self

    def blocks(self):
        """
        Make this command blocking, this will prevents commands listed after from being called.
        :return: self for chaining
        """
        self.blocking = True
        return self

    def found_in(self, message) -> bool:
        """
        Is this chatCommand found in message?

        :param message: The message to check
        :return: whether this message was found
        """
        if isinstance(message, str):
            if not self.case_sensitive:
                message = message.lower()
            for hook in self.hooks:
                if not self.case_sensitive:
                    hook = hook.lower()
                message = message.strip()
                if hook in message:
                    flag = True
                    for sec_hook in self.secondaries:
                        if not self.case_sensitive:
                            sec_hook = sec_hook.lower()
                        if sec_hook not in message:
                            flag = False
                            break
                    if flag:
                        return True
        return False

    @property
    def callback(self) -> staticmethod:
        """
        We wrap the callback property to filter arguments that aren't required by the command callback.
        :return: A wrapped callback
        """

        def wrapper(*args, **kwargs):
            valid_args = self._callback.__code__.co_varnames
            output_args = {}
            for key in kwargs:
                if key in valid_args:
                    output_args[key] = kwargs[key]
            return self._callback(*args, **output_args)

        return wrapper

    def __call__(self, *args, **kwargs) -> coroutine:
        """
        For readability, we treat calling this object as calling the callback.
        Additionally, we insert the command argument at this point.
        :param args: The positional arguments
        :param kwargs: The key word arguments.
        :return: A coroutine object.
        """
        kwargs["command"] = self
        return self.callback(*args, **kwargs)
