class CrossReferenceError(RuntimeError):
    pass


class CardParseSyntaxError(SyntaxError):
    """
    Class that is used for testing.
    Users should just treat this as a SyntaxError.
    """
    pass

class DuplicateIDsError(RuntimeError):
    pass

class MissingDeckSections(RuntimeError):
    pass

class UnsupportedCard(NotImplementedError):
    pass
