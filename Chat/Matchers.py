import re


class BaseMatcher:
    _command: str
    __next_is_optional: bool
    __next: None
    compiler: None
    alias: classmethod
    including: classmethod

    def __init__(self, compiler, command: str):
        self.compiler = compiler
        self._command = command
        self.__next = None
        self.__next_is_optional = None

    def matches(self, message: str) -> bool:
        """
        Returns true if the message given matches the command
        :param message: The message to check
        :return: The result
        """
        result = self._matches(message)
        if self.__next is not None:
            if self.__next_is_optional:
                result = result or self.__next.matches(message)
            else:
                result = result and self.__next.matches(message)
        return result

    def _matches(self, message: str) -> bool:
        """
        This method evaluates whether the message matches the command
        :param message: The message
        :return: The bool result
        """
        return self._command in message.lower()

    def set_next_command(self, optional, matcher):
        self.__next = matcher
        self.__next_is_optional = optional
        return self.__next

    def __str__(self):
        return "<{} command={}>".format(self.__class__.__name__, self._command)


"""
Methods are separated due to typing issues. (I enjoy having static typing for autocomplete)
"""


def including(self, command: str, matcher=BaseMatcher):
    """
    Adds and inclusive component to the command chain, this component must be matched in addition to the current
    component for the result to be true.
    :param self: The current Matcher object
    :param command: The command to add as the next in the chain
    :param matcher: The matcher this command will use.
    :return: The resulting Matcher object for chaining.
    """
    return self.set_next_command(False, matcher(self.compiler, command))


def alias(self, command: str, matcher=BaseMatcher):
    """
    Adds an alias, if the messaged is not matched by this matcher, the alias will be tried.
    :param self: The current Matcher object
    :param command: The command to add as the next in the chain
    :param matcher: The matcher this command will use.
    :return: The resulting Matcher object for chaining.
    """
    return self.set_next_command(True, matcher(self.compiler, command))


BaseMatcher.alias = alias
BaseMatcher.including = including


class CaseSensitiveMatcher(BaseMatcher):
    def __init__(self, compiler, command: str):
        super().__init__(compiler, command)

    def _matches(self, message: str):
        return self._command in message


class RegexMatcher(BaseMatcher):
    def __init__(self, compiler, command: str):
        super().__init__(compiler, command)

    def _matches(self, message: str):
        return bool(re.search(self._command, message))
