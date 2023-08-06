import json, grammalecte
from termcolor import colored


class GrammarChecker():

    def __init__(self):
        self.grammar_checker = grammalecte.GrammarChecker("fr")
        opt_on = []
        opt_off = ['apos', 'esp', 'typo', 'unit', 'num', 'nbsp']

        self.grammar_checker.gce.setOptions({'html': True, 'latex': True})
        self.grammar_checker.gce.setOptions({ opt: True for opt in opt_on if opt in self.grammar_checker.gce.getOptions() })
        self.grammar_checker.gce.setOptions({ opt: False for opt in opt_off if opt in self.grammar_checker.gce.getOptions() })

    def correct(self, text):
        grammer_check_result = json.loads(self.grammar_checker.generateParagraphAsJSON(0, text))
        grammar_errors = grammer_check_result['lGrammarErrors']
        spelling_errors = grammer_check_result['lSpellingErrors']
        return self.format_correction(text, grammar_errors, spelling_errors)

    def format_correction(self, text, grammar_errors, spelling_errors):
        message = ''
        last = 0

        errors = []
        for spelling_error in spelling_errors:
            errors.append({
                'type': 'spelling',
                'start': spelling_error['nStart'],
                'end': spelling_error['nEnd']})

        for grammar_error in grammar_errors:
            start = grammar_error['nStart']

            item = 0
            while item < len(errors) and errors[item]['start'] < start:
                item += 1

            errors.insert(item, {
                'type': 'grammar',
                'start': start,
                'suggestions': grammar_error['aSuggestions'],
                'end': grammar_error['nEnd']})

        for error in errors:
            start = error['start']
            end = error['end']
            message += colored(text[last:start], 'cyan')
            if error['type'] == 'spelling':
                message += colored(text[start:end], 'red', attrs=[])
            elif error['type'] == 'grammar':
                message += colored(text[start:end], 'white', 'on_red')
                message += ' '
                message += colored('({})'.format(', '.join(error['suggestions'])), 'white', 'on_green')
            last = end

        if message == '':
            return colored(text, 'green')
        else:
            message += colored(text[last:], 'cyan')
            return message