from asyncio import coroutine

from Chat.Matchers import BaseMatcher


class Command:
    # The chain of matchers for this command
    __head: BaseMatcher

    # The callback method
    __callback: coroutine

    def __init__(self, callback: coroutine):
        self.__head = None
        self.__callback = callback

    def listens_for(self, command: str, matcher=BaseMatcher) -> BaseMatcher:
        """
        Add the first command component to the chain.
        :param command: The command to set as the head
        :param matcher: The matcher to use for this command (defaults to BaseMatcher (case insensitive))
        :return: The resulting BaseMatcher for chaining
        """
        self.__head = matcher(self, command)
        return self.__head

    def matches(self, message):
        """
        Calls the 'head' of the command chain which recursively checks if each component matches.
        :param message: The message to validate
        :return: True if this command matches the message.
        """
        return self.__head.matches(message)

    @property
    def callback(self) -> staticmethod:
        """
        We wrap the callback property to filter arguments that aren't required by the command callback.
        :return: A wrapped callback
        """

        def wrapper(*args, **kwargs):
            valid_args = self.__callback.__code__.co_varnames
            output_args = {}
            for key in kwargs:
                if key in valid_args:
                    output_args[key] = kwargs[key]
            return self.__callback(*args, **output_args)

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


class BlockingCommand(Command):
    pass
