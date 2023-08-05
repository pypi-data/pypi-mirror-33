from myo.output.syntax.base import OutputSyntax
from myo.output.parser.scala import CodeEntry

from amino import IO, Map, _


class Syntax(OutputSyntax):

    @property
    def _handlers(self):
        return Map({
            CodeEntry: self._code,
        })

    def __call__(self, lines):
        return ((lines.with_index.flat_map2(self._line)).sequence(IO) +
                self._file)

    def _line(self, index, line):
        def run(entry):
            return (
                self._handlers.get(type(entry)) /
                (lambda a: a(index, line, entry))
            )
        return line.entry // run

    def _code(self, index, line, entry):
        col = (line.target.col / (_.col + 1) | 1)
        rex = '\%{}c.'.format(col)
        return self._cont('ErrorMsg', self._line_re(index, rex), 'MyoCode')

    @property
    def _file(self):
        path = '.\+\ze '
        line = ' \zs\d\+'
        return (self._cont('MyoPath', path, 'MyoLocation') +
                self._cont('MyoPath', line, 'MyoLocation'))

__all__ = ('Syntax',)
