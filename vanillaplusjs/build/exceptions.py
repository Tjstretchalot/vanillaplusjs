class BuildException(Exception):
    """Raised if, for some reason, we cannot build the project"""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return self.message


class CyclicDependencyException(BuildException):
    """Raised if the dependencies form a cycle which cannot be
    resolved"""

    def __init__(self, message: str):
        super().__init__(message)


class MissingConfigurationException(BuildException):
    """Raised if a required configuration variable is not set"""

    def __init__(self, message: str):
        super().__init__(message)


class IntegrityMismatchException(BuildException):
    """Raised if an external files integrity is not as expected"""

    def __init__(self, message: str):
        super().__init__(message)
