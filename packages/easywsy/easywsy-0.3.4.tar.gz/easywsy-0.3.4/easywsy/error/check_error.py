class CheckError(Exception):

    def __init__(self, message=False, method=False, attr=False,
                 not_found=False, value=False):
        self.method = method
        self.attr = attr
        self.message = message
        self.not_found = not_found
        self.value = value

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        m = False
        if self.message:
            m = "\n%s" % self.message
            return m
        if self.method and self.attr:
            m = "\nThe Attribute `%s` Failed the check on method `%s`." % \
                (self.attr, self.method)
            if self.value:
                m += "\nIt's value was `%s`" % self.value
        if self.attr and not self.method:
            if self.not_found:
                m = "\nCould not find a Check method for Attribute `%s`." % \
                    self.attr
            else:
                m = "\nThe Attribute `%s` Failed a Check." % self.attr
        if self.method and not self.attr:
            m = "\nThe Method `%s` could not validate an Attribute." % \
                self.method
        if not m:
            m = "\nThere was an Attribute that could not pass a Check."
        return m
