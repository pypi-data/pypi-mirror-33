"""
Author: ZviWex
"""
import sys
import os
from IPython.terminal.prompts import Prompts, Token
from integrate_shell import background_shell

# initialyzing
sys.last_value = None

class MyPrompt(Prompts):
    def in_prompt_tokens(self, cli=None):
        
        # manipulating shell command
        if sys.last_value != None:   
            command = None   
            
            if type(sys.last_value) == SyntaxError:
                command = sys.last_value.text.replace("\n", "")
            elif type(sys.last_value) == NameError:
                command = repr(sys.last_value)
                command = command[command.find("'")+1:]
                command = command[:command.find("'")]

            if command:
                print "Executing shell command: {}".format(command)
                c.command(command)
    
            sys.last_value = None
        
        # printing the pommand prompt cwd 
        return [(Token, os.getcwd()), (Token.Prompt, '>')]
       
ip = get_ipython() # pylint: disable=E0602
ip.prompts = MyPrompt(ip)

c = background_shell()

def command(cmsg):
    c.command(cmsg)