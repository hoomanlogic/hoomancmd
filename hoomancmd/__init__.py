"""
hoomancmd

Command-line interface extends python's cmd.Cmd utiling the hoomanlogic text-based human language input framework.
"""

import hoomanlogic
import cmd


#=======================================================================================================================
# HoomanCmd
#=======================================================================================================================
@hoomanlogic.interface
class HoomanCmd(cmd.Cmd):
    """
    Extends the Python standard cmd.Cmd class to add a much more intuitive and forgiving command line interface for
    the user and give the developer the structure and functions to much more easily provide it without having to
    rewrite the wheel.

    ..  note:: This repository is open source and is available on `GitHub`_.
    We would love contributions.

    .. _GitHub: https://github.com/hoomanlogic/hoomancmd

    Getting Started
    ---------------

    The do_command structure that is built-in to ``cmd.Cmd`` class should be avoided for commands that
    are intended for end-users, as they will lack the use of command word synonyms and command word suggestions,
    but it is recommended for quick testing of commands on the developer end.
    """

    #===================================================================================================================
    # Class Attributes
    #===================================================================================================================
    synonyms_yes = ['y', 'yes']
    """List of acceptable synonyms for interpreting answer to a question as yes or True"""
    synonyms_no = ['n', 'no']
    """List of acceptable synonyms for interpreting answer to a question as no or False"""

    #===================================================================================================================
    # Initialization
    #===================================================================================================================
    def __init__(self, completekey='tab', stdin=None, stdout=None, prompt='>> ', enable_match_suggestion=True):
        # always call base initializer
        cmd.Cmd.__init__(self, completekey, stdin, stdout)

        # todo: figure out why cmdLoop is suddenly failing
        # for now we disable it
        # self.use_rawinput = False

        ### cmd.Cmd instance attributes
        # set command line prompt
        self.prompt = prompt

        ### HoomanCmd instance attributes
        # initialize and docstring instance attributes
        self.last_suggestion = None
        """The last suggestion for a user-input command that wasn't found in the list of command words"""
        self.last_suggestion_argline = None
        """The raw argument lines for the last suggestion for a user-input command that wasn't found in the list of
        command words"""
        self.last_suggestion_was_accepted = False
        """The user's decision for the last suggestion for a user-input command that wasn't found in the list of command words"""
        self.command_dictionary = {}
        """The command dictionary for defining the command words for command functions as well as the argument structure.
        See ``define_interface`` for more info on how to utilize the command_dictionary"""
        self.command_func_prefix = ''
        """Optional prefix for command function, used by docstring to find commands and output the documentation to the user"""

        self.enable_match_suggestion = enable_match_suggestion
        """Turn on match suggestion functionality for catching typos"""

        self.exit_requested = False

    #=================================================================h==================================================
    # Overrides
    #===================================================================================================================
    def default(self, line):
        # call handle_input to process user input
        return self._handle_unrecognized_user_input(line)

    def onecmd(self, line):
        """Interpret the argument as though it had been typed in response to the prompt.

        This was overridden to support managed arguments that will handle user input and take the load off of the
        command method to decide if all the necessary arguments were supplied, and even modify the values if need be.
        Basically, by the point it gets to the command, it should be clean enough that almost no, if any, validation
        needs to be done. Managed arguments are optional to support the quick and dirty.

        The return value is a flag indicating whether interpretation of
        commands by the interpreter should stop.
        """
        cmd, arg, line = self.parseline(line)
        if not line:
            return self.emptyline()
        if cmd is None:
            return self.default(line)
        self.lastcmd = line
        if line == 'EOF':
            self.lastcmd = ''
        if cmd == '':
            return self.default(line)
        else:
            if not self.operator.listen_and_respond(line):
                try:
                    func = getattr(self, 'do_' + cmd)
                except AttributeError:
                    return self.default(line)
                return func(arg)

        return self.exit_requested

    def do_help(self, arg):

        cmd.Cmd.do_help(self, arg)

    @hoomanlogic.translator(synonyms=['q', 'quit', 'goodbye', 'aufwiedersehen', 'ciao', 'fuckoff', 'hastalavista'])
    def exit(self):
        self.exit_requested = True
        return True

    #===================================================================================================================
    # Private Methods
    #===================================================================================================================
    def _handle_unrecognized_user_input(self, line):
        """Called by overridden ``default`` function to handle user-input.
        This function contains all the logic
        that is the workhorse of the intuitive interface. This method generally should not be overridden"""

        if not self.enable_match_suggestion:
            return False

        # respond to suggestion question
        if line.lower() in HoomanCmd.synonyms_yes and self.suggestion is not None:
            self.last_suggestion_was_accepted = True
            self.default(self.suggestion + ' ' + self.suggestion_argline)
            return False
        elif line.lower() in HoomanCmd.synonyms_no:
            self.last_suggestion_was_accepted = False
            return False

        # we don't need to worry about using split_args here because the command itself
        # is never quoted and the rest is being pieced right back together
        args = line.split()
        cmd = args[0].lower()
        argline = ' '.join(args[1:])

        import matchsuggestion as suggest
        list_of_all_commands = []
        for item in self.command_dictionary.itervalues():
            list_of_all_commands.extend(item)
        bestmatchstats = suggest.getbestmatch_v3(cmd, list_of_all_commands)
        if bestmatchstats is None:
            self.print_line("Unrecognized syntax.")
        else:
            self.suggestion = bestmatchstats.matchterm
            self.suggestion_argline = argline
            if bestmatchstats.get_score() > 95 and bestmatchstats.runner_up_score < 90:
                self.print_line("Switching input command from '{}' to '{}'", cmd, bestmatchstats.matchterm)
                line = self.precmd(' '.join([self.suggestion, self.suggestion_argline]))
                self.suggestion = None
                self.suggestion_argline = None
                self.last_suggestion_was_handled = True
                return self.onecmd(line)
            else:
                self.last_suggestion_was_handled = False
                self.print_line("Did you mean '" + bestmatchstats.matchterm + "'?" + ' : ' + str(bestmatchstats.get_score()) + \
                      ' : ' + bestmatchstats.runner_up_matchterm + ':' + str(bestmatchstats.runner_up_score))
                return False

    #===================================================================================================================
    # Public Methods
    #===================================================================================================================
    @staticmethod
    def split_args(line):
        import shlex
        args = shlex.split(line)
        return args

    def print_table(self, table, col_justify=None, separator=' | '):
        """Prints a nicely formatted table. Special calculations available

        To use a calculated value, it must be

        :param col_justify: -1 left, 0 center, 1 right
        :type col_justify: list<int>, int for each column required
        """

        max_col_lengths = {}
        max_col_index = 0
        if col_justify is None:
            col_justify = [-1]

        for irow, row in enumerate(table):
            for icol, col in enumerate(row):

                # set the highest col count so far
                if icol > max_col_index:
                    max_col_index = icol

                # change to str if not already
                if not isinstance(col, str) and not isinstance(col, unicode):
                    table[irow][icol] = str(col)

        # set to left justify for any undefined column justifications
        for i in range(len(col_justify), max_col_index + 1):
            col_justify.append(-1)

        for irow, row in enumerate(table):
            highest_index_in_row = len(row) - 1
            for icol, col in enumerate(row):

                # last row, we don't care about the length, and if there
                # are less cols in this than others, it could screw it up anyway
                if icol == highest_index_in_row and icol != max_col_index:
                    break

                # compare against the current max and set new max if this is higher
                cur_best = max_col_lengths.get(str(icol), 0)
                if cur_best < len(col):
                    max_col_lengths[str(icol)] = len(col)

        for row in table:
            highest_index_in_row = len(row) - 1
            row_to_print = ''
            for icol, col in enumerate(row):
                # if it's the last col, don't bother calculating
                # just print it
                if icol == highest_index_in_row and icol != max_col_index:
                    calc = HoomanCmd.CalculatedTableValue.extract(col)
                    if calc is not None and calc.calc_mode == 'fill':
                        padding = ((sum(max_col_lengths.values()) + (len(separator) * max_col_index)) - (len(calc.pre_calc_chars) + len(calc.post_calc_chars)))
                        row_to_print += calc.pre_calc_chars + (calc.calc_chars * padding) + calc.post_calc_chars
                    elif calc is not None and calc.calc_mode == 'center':
                        padding = ((sum(max_col_lengths.values()) + (len(separator) * max_col_index)) - (len(calc.pre_calc_chars) + len(calc.post_calc_chars) + len(calc.calc_chars)))
                        leftover = padding % 2
                        padding = padding - leftover
                        left = padding / 2
                        right = left + leftover
                        row_to_print += calc.pre_calc_chars + (left * calc.calc_arg) + (calc.calc_chars) + (right * calc.calc_arg) + calc.post_calc_chars
                    else:
                        row_to_print += col
                else:
                    len_of_field = len(col)
                    padding = max_col_lengths.get(str(icol), len_of_field) - len_of_field
                    separation = ''
                    if icol != highest_index_in_row:
                        separation = separator
                    if padding == 0:
                        row_to_print += col + separation
                    else:
                        if col_justify[icol] < 0:
                            row_to_print += col + (padding * ' ') + separation
                        elif col_justify[icol] > 0:
                            row_to_print += (padding * ' ') + col + separation
                        else:
                            leftover = padding % 2
                            padding = padding - leftover
                            left = padding / 2
                            right = left + leftover
                            row_to_print += (' ' * left) + col + (' ' * right) + separation

            self.print_line(row_to_print, no_formatting=True)

    def print_line(self, line, *args, **kwargs):
        if 'no_formatting' in kwargs and kwargs.get('no_formatting') == True:
            self.stdout.write(line + '\n')
        else:
            self.stdout.write('{}\n'.format((str(line))).format(*args, **kwargs))

    class CalculatedTableValue(object):
        def __init__(self):
            self.pre_calc_chars = ''
            self.calc_chars = ''
            self.post_calc_chars = ''
            self.calc_mode = ''
            self.calc_arg = ' '

        @classmethod
        def extract(self, col):
            import re
            m = re.match('^(.*?)({.*?})(.*?)$', col)

            if m is None:
                return None

            groups = m.groups('')

            if groups[1] == '':
                return None

            instance = HoomanCmd.CalculatedTableValue()
            instance.pre_calc_chars = groups[0]
            instance.post_calc_chars = groups[2]
            calc = groups[1].replace('{', '').replace('}', '').split('|')
            instance.calc_chars = calc[0]
            instance.calc_mode = calc[1]
            if len(calc) == 3:
                instance.calc_arg = calc[2]
            return instance