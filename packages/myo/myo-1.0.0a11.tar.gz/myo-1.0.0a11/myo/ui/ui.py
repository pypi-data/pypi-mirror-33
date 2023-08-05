from amino import Dat, Maybe, Boolean
from amino.boolean import false

from chiasma.util.id import Ident

from ribosome.compute.program import Program
from ribosome.compute.api import prog


@prog.strict
def owns_no_view(ident: Ident) -> Boolean:
    return false


class Ui(Dat['Ui']):

    @staticmethod
    def cons(
            owns_view: Program[bool]=owns_no_view,
            render: Program=None,
            open_pane: Program=None,
            open_window: Program=None,
            open_space: Program=None,
            kill_pane: Program[bool]=None,
    ) -> 'Ui':
        return Ui(
            owns_view,
            Maybe.optional(render),
            Maybe.optional(open_pane),
            Maybe.optional(open_window),
            Maybe.optional(open_space),
            Maybe.optional(kill_pane),
        )

    def __init__(
            self,
            owns_view: Program[bool],
            render: Maybe[Program],
            open_pane: Maybe[Program],
            open_window: Maybe[Program],
            open_space: Maybe[Program],
            kill_pane: Maybe[Program[bool]],
    ) -> None:
        self.owns_view = owns_view
        self.render = render
        self.open_pane = open_pane
        self.open_window = open_window
        self.open_space = open_space
        self.kill_pane = kill_pane


__all__ = ('Ui',)
