import mistune, textwrap
from .grammar_checker import GrammarChecker


class GrammarRenderer(mistune.Renderer):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.grammar_checker = GrammarChecker()

    def header(self, text, level, raw):
        if level == 1:
            return '\n# {}\n\n'.format(self.grammar_checker.correct(text))
        elif level == 2:
            return '\n## {}\n\n'.format(self.grammar_checker.correct(text))
        elif level == 3:
            return '\n### {}\n\n'.format(self.grammar_checker.correct(text))
        elif level == 4:
            return '\n#### {}\n\n'.format(self.grammar_checker.correct(text))
        elif level == 5:
            return '\n##### {}\n\n'.format(self.grammar_checker.correct(text))
        elif level == 6:
            return '\n###### {}\n\n'.format(self.grammar_checker.correct(text))

    def list_item(self, text):
        self.grammar_checker.correct(text)
        return text

    def paragraph(self, text):
        return '{}\n\n'.format(self.grammar_checker.correct(text))

    def hrule(self):
        return '---\n'

    def list(self, body, ordered):
        return '{}\n'.format(body)

    def list_item(self, text):
        return '- {}\n'.format(self.grammar_checker.correct(text))

    def text(self, text):
        return text

    def inline_html(self, text):
        return text

    def double_emphasis(self, text):
        return text

    def emphasis(self, text):
        return text

    def block_code(self, code, language):
        return textwrap.dedent('''
            {}
            '''.format(code))

    def codespan(self, text):
        return '`{}`'.format(text)

    def table(self, header, body):
        s = '{}{}\n'.format(header, body)
        return textwrap.dedent(s)

    def table_row(self, content):
        return '|{}\n'.format(content)

    def table_cell(self, content, **flags):
        return ' {} |'.format(self.grammar_checker.correct(content))

    def link(self, link, title, content):
        return '[{}]({})'.format(content, link)

    def autolink(self, link, is_email=False):
        return '[{}]({})'.format(link, link)
