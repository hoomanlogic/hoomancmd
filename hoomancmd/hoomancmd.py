# Backward compatibility fix.
from . import *

# todo: learn more about the characters used in stdout.write, then probably write a print function that
#       utilizes self.stdout.write("%s\n"%str(self.nohelp % (arg,)))

# todo: cleanup all docstrings to have subsequent param lines matching extended indentation

# todo: Explore tab completion further and try to utilize command words in the command completion
# todo: add way special character that will cause the interpreter to verify with the user that it understood the
#       desired action before executing it
# todo: print_table bugfix: when there are no other items in the list, the calculated values are not processed
#                                    {=|fill}
# ={Active Actions For 'Learn songs'|center}=
#                                    {=|fill}