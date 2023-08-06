

class EqOnAttrsMixin:
    equal_attrs = None

    def __eq__(self, other):
        if self.equal_attrs is None:
            return self == other

        for equal_attr in self.equal_attrs:
            if not hasattr(other, equal_attr): # other object doesn't have this property, must not be equal
                return False
            if getattr(self, equal_attr) != getattr(other, equal_attr):
                return False

        # passed all checks, must be equal
        return True