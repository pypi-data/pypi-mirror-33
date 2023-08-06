import mistune
from .grammar_renderer import GrammarRenderer


def check_grammar(content):
    renderer = GrammarRenderer()
    markdown = mistune.Markdown(renderer=renderer)
    return markdown(content)