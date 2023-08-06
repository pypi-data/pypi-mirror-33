class WSError(Exception):

    def __init__(self, ws_url, message=False, method=False,
                 attr=False, code=False, ws_method=False):
        self.ws_url = ws_url
        self.message = message
        self.method = method
        self.attr = attr
        self.code = code
        self.ws_method = ws_method

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        m = "\nWebService Error: (connected to `%s`)" % self.ws_url
        if self.message:
            if self.code:
                m += "\nResponse Code %s." % self.code
            m += "\n%s" % self.message
            return m
        if self.method:
            m += "\nThe function you are looking for " + \
                 "was not found in the Web Service."
            m += "\n(Function: `%s`)" % self.method
        if self.attr:
            m += "\nThe Attribute you are trying to get " + \
                 "was never set."
            if self.ws_method:
                m += "\n(Attribute: `%s`, WS Function: `%s`)" % \
                    (self.attr, self.ws_method)
            else:
                m += "\n(Attribute: `%s`)" % self.attr
        if self.code:
            m += "\nThe WebService answered with code %s." % self.code
        return m
