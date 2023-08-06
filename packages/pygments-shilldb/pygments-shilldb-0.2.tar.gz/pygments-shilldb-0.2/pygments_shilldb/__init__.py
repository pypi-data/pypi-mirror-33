from pygments.lexers.lisp import RacketLexer
from pygments.token import Name, Keyword

class ShilldbLexer(RacketLexer):
    name = 'ShillDB'
    aliases = ['shilldb']
    filenames = ['*.rkt', '*.cap', '*.amb']

    EXTRA_KEYWORDS = ['->/join', '->i/join', 'view/c']

    def get_tokens_unprocessed(self, text):
        for index, token, value in RacketLexer.get_tokens_unprocessed(self, text):
            if token is Name and value in self.EXTRA_KEYWORDS:
                yield index, Keyword, value
            else:
                yield index, token, value