from typology.concepts import (
    Color, Date
)


class HTMLColor(Color):

    def validate(self, value):
        HEX_DIGITS = [str(item) for item in list(range(10)) + list('abcdefgh')]
        if value.startswith('#'):
            if 4 <= len(value) <= 7:
                if all([item in HEX_DIGITS for item in list(value[1:].lower())]):
                    return True
        return False

    def __init__(self, value):
        Color.__init__(self)

        if self.validate(value):
            self.value = value
        else:
            raise ValueError('Invalid HTML color: {}'.format(value))

    def __repr__(self):
        return(self.value)


class ISODate(Date):

    def validate(self, value):
        pass

    def __init__(self, value):
        Date.__init__(self)

    def __repr__(self):
        return(self.value)
