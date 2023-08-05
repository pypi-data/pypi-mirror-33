from amino import do, Do
from amino.state import EitherState
from amino.lenses.lens import lens
from amino.boolean import false

from chiasma.util.id import Ident, IdentSpec, ensure_ident_or_generate

from ribosome.compute.api import prog
from ribosome.config.component import ComponentData

from myo.ui.data.ui_data import UiData
from myo.ui.data.window import Window
from myo.ui.pane import ui_modify_pane
from myo.env import Env
from myo.components.ui.compute.pane import render_view


@do(EitherState[UiData, Window])
def ui_close_pane(ident: Ident) -> Do:
    yield ui_modify_pane(ident, lens.open.set(false))


@prog
@do(EitherState[ComponentData[Env, UiData], Window])
def ui_close_pane_prog(ident_spec: IdentSpec) -> Do:
    ident = ensure_ident_or_generate(ident_spec)
    yield ui_close_pane(ident).zoom(lens.comp)


@prog.do(None)
def close_pane(ident_spec: IdentSpec) -> Do:
    ident = ensure_ident_or_generate(ident_spec)
    yield ui_close_pane_prog(ident)
    yield render_view(ident)


__all__ = ('close_pane',)
