## @package teambot.console
#
# The source of the `teambot` tool. Automatically creates a teambot class.

import sys, argparse

## A basic teambot bot.py file.
#
# Used for "teambot new".
BASE_BOT_PY = """import teambot

class {classname}(teambot.Handler{mixin}):
{code}

if __name__=="__main__":
{indent}channels = "{channels}".split()
{indent}bot = teambot.TeamBot(channels,"{nick}","{server}",chandler={classname})
{indent}bot.start()
"""

## The code for the base handler class.
#
# Defines on_pubmsg and on_privmsg functions.
BASE_HANDLER_CODE = """{indent}def on_pubmsg(self,channel,nick,text):
{indent}{indent}pass # change this
{indent}def on_privmsg(self,nick,text):
{indent}{indent}pass # change this"""

## The code for the command mixin handler class.
#
# Defines the handle_command function.
BASE_MIXIN_CODE = """{indent}def handle_command(self,target,nick,text):
{indent}{indent}pass # change this"""

## Prompts user for value. Returns default if user supplies no response.
#
# @param ps The prompt string.
# @param default Default value to return on no input. Defaults to None
def prompt(ps,default=None):
	if default is not None:
		ps = "{} [{}]: ".format(ps,default)
	else:
		ps = "{}: ".format(ps)
	ret = input(ps)
	if not ret:
		return default
	return ret

## Verifies #prompt output to be in a collection.
#
# @param ps The prompt string
# @param answers The acceptable answers
# @param default The default value to return.
# @param loop Whether this command should loop until correct output is recieved. Defaults to True.
def prompt_verify(ps,answers,default=None,loop=True):
	ret = prompt(ps,default)
	if ret not in answers:
		if loop:
			print("Invalid response \"{}\"!".format(ret))
			return prompt_verify(ps,answers,default,loop)
		else:
			return default
	return ret

## The different kinds of indentation supported for automatic creation.
#
INDENTATION = {"tabs":"\t","quadspace":"    ","doublespace":"  "}

## Creates a new bot.
#
# This function is invoked for `teambot new`.
# @param args The args namespace, as returned by argparse.ArgumentParser.parse_args.
def cli_new(args):
	classname = prompt("Class name?","BotHandler")
	indent = INDENTATION[prompt_verify("Indentation? ({})".format(", ".join(x for x in INDENTATION.keys())),list(INDENTATION.keys()),default="tabs")]
	mixin = prompt("Use command handler mixin (all commands, privmsg or pubmsg, go to the same function, yes/no)?","yes")
	mixin = ",teambot.CommandHandlerMixin" if mixin[0].lower()=="y" else ""
	code = BASE_HANDLER_CODE.format(indent=indent) if len(mixin)==0 else BASE_MIXIN_CODE.format(indent=indent)
	nick = prompt("Bot nick?")
	while nick is None:
		print("Bot nick is required!")
		nick = prompt("Bot nick?")
	server = prompt("Server to connect to?","localhost")
	channels = prompt("Channels to join? (space seperated)","#bots")
	with open("bot.py","w") as f:
		f.write(BASE_BOT_PY.format(**locals()))

## The possible operations and what functions to call.
OPERATIONS = {"new": cli_new}

## The source code for the `teambot` tool.
#
# To be specific, this function parses the arguments and delegates to seperate functions for the operations.
def main(gargs=None):
	if gargs is None:
		gargs = sys.argv[1:]
	parser = argparse.ArgumentParser(prog="teambot",description="A tool for making IRC bots with teambot.")
	parser.add_argument("operation",help="The operation to do. Valid operations: {}".format(", ".join(x for x in OPERATIONS.keys())))
	parser.add_argument("args",nargs="*")
	args = parser.parse_args(gargs)
	if args.operation not in OPERATIONS:
		parser.error("invalid operation \"{}\"".format(args.operation))
	OPERATIONS[args.operation](args)
