from dero.latex.logic.tools import _readable_repr


class ReprMixin:
    repr_cols = []

    def __repr__(self):
        if self.repr_cols:
            repr_col_strs = [f'{col}={getattr(self, col, None).__repr__()}' for col in self.repr_cols]
            repr_col_str = f'({", ".join(repr_col_strs)})'
        else:
            repr_col_str = ''
        return f'<{type(self).__name__}{repr_col_str}>'

    @property
    def readable_repr(self):
        return show_contents(self)


def show_contents(obj):
    """
    Used to view what's inside a latex table object

    >>>import dero.latex.table as lt
    >>>dt = lt.DataTable.from_df(some_df)
    >>>show_contents(dt)
    :param obj:
    :return:
    """
    print(_readable_repr(repr(obj)))