class ValidationError(Exception):
    """An error while validating data."""

    def __init__(self, message, field=None, code=None, params=None):
        from django.utils.encoding import force_text
        """
        ValidationError can be passed any object that can be printed (usually
        a string), a list of objects or a dictionary.
        """

        self.field = field
        self.code = code
        self.params = params
        self.msg = force_text(message)
        self.messages = [self.msg]

    def __str__(self):
        return "{0} ({1})".format(self.msg, self.field)


class ObjectNotFoundError(Exception):
    """An error while getting object"""

    def __init__(self, message, modelclass=None, code=None, params=None):
        from django.utils.encoding import force_text
        """
        ObjectNotFoundError can be passed any object that can be printed (usually
        a string), a list of objects or a dictionary.
        """

        self.modelclass = modelclass
        self.code = code
        self.params = params
        self.msg = force_text(message)
        self.messages = [self.msg]

    def __str__(self):
        return "{0} ({1})".format(self.msg, self.modelclass)


class ExtLibError(Exception):
    """An error while calling external lib"""

    def __init__(self, message, lib=None, code=None, params=None):
        from django.utils.encoding import force_text
        """
        ExtLibError can be passed any object that can be printed (usually
        a string), a list of objects or a dictionary.
        """

        self.lib = lib
        self.code = code
        self.params = params
        self.msg = force_text(message)
        self.messages = [self.msg]

    def __str__(self):
        return "{0} ({1})".format(self.msg, self.lib)


class InternalError(Exception):
    """An unexpected general error"""

    def __init__(self, message, fct=None, code=None, params=None):
        from django.utils.encoding import force_text
        """
        InternalError can be passed any object that can be printed (usually
        a string), a list of objects or a dictionary.
        """

        self.fct = fct
        self.code = code
        self.params = params
        self.msg = force_text(message)
        self.messages = [self.msg]

    def __str__(self):
        return "{0} ({1})".format(self.msg, self.fct)