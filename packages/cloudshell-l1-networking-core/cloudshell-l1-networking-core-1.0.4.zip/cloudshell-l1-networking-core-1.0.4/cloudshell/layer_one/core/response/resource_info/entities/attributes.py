from cloudshell.layer_one.core.response.resource_info.entities.base import Attribute


class StringAttribute(Attribute):
    """
    String attribute
    """

    def __init__(self, name, value):
        super(StringAttribute, self).__init__(name, Attribute.STRING, value or self.DEFAULT_VALUE)


class NumericAttribute(Attribute):
    """
    Numeric attribute
    """
    DEFAULT_VALUE = 0

    def __init__(self, name, value):
        if value is None:
            value = self.DEFAULT_VALUE
        super(NumericAttribute, self).__init__(name, Attribute.NUMERIC, str(value))


class BooleanAttribute(Attribute):
    """
    Boolean attribute
    """
    TRUE = 'True'
    FALSE = 'False'
    DEFAULT_VALUE = TRUE

    def __init__(self, name, value):
        super(BooleanAttribute, self).__init__(name, Attribute.BOOLEAN, value or self.DEFAULT_VALUE)
