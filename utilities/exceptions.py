class ElementNotFoundError(Exception):
    pass


class GeneratorNotFoundError(Exception):
    pass


class GenerationValidationException(Exception):
    pass


class ParsingError(Exception):
    pass


class DiffError(Exception):
    pass


class VersionUnavailableError(Exception):
    pass
