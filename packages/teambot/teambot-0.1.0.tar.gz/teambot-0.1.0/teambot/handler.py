## @package teambot.handler
# Contains the base handler class.

## Base Handler class.
#
# This class will handle all messages from bots.
# In on_pubmsg or on_privmsg, the event property will be set with the message event. (See jaraco/irc documentation for event object properties.
class Handler:
	def __init__(self,bot):
		self._bot = bot # save bot instance

	## Called when a message is sent in a public channel.
	#
	# @param self The handler object
	# @param channel The channel the message was sent in.
	# @param nick The nickname of the user who sent the message.
	# @param text The text of the message.
	def on_pubmsg(self,channel,nick,text):
		pass

	## Called when a message is sent to the bot in a private message/query.
	#
	# @param self The handler object
	# @param nick The nickname of the user who sent the message.
	# @param text The text of the message.
	def on_privmsg(self,nick,text):
		pass

	## Sends a message to a channel or nick.
	#
	# @param self The handler object
	# @param target The target of the message
	# @param message The message to send
	def say(self,target,message):
		self._bot.conn.privmsg(target,message)

## Command handler mixin for Handler class
#
# In specific, this class causes all messages to be sent to the `handle_command` function. The event property is still set.
class CommandHandlerMixin:
	## Called when a message is sent in a public channel.
	#
	# CommandHandlerMixin causes the message to be sent to `handle_command`.
	#
	# @param self The handler object
	# @param channel The channel the message was sent in.
	# @param nick The nickname of the user who sent the message.
	# @param text The text of the message.
	def on_pubmsg(self,channel,nick,text):
		self.handle_command(channel,nick,text)

	## Called when a message is sent to the bot in a private message/query.
	#
	# CommandHandlerMixin causes the message to be sent to `handle_command`.
	#
	# @param self The handler object
	# @param nick The nickname of the user who sent the message.
	# @param text The text of the message.
	def on_privmsg(self,nick,text):
		self.handle_command(self.event.target,nick,text)

	## Called when a message is recieved.
	#
	# @param self The handler object
	# @param target The target of the original message.
	# @param nick The nickname of the user who sent the message.
	# @param text The text of the message.
	def handle_command(self,target,nick,text):
		pass
