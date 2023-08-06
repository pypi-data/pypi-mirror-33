## @module teambot.bot
# Contains the bot class.

import irc.bot
from .handler import Handler

## The main bot class.
#
#
class TeamBot(irc.bot.SingleServerIRCBot):
	## Initializes the bot.
	#
	# @param self The bot instance.
	# @param channels A list of channels for the bot to join.
	# @param nickname A nickname for the bot.
	# @param server The server to connect to.
	# @param chandler The Handler subclass to use.
	def __init__(self, channels, nickname, server, port=6667, chandler=Handler):
		irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
		self.chanlist = channels
		self.bot_nick = nickname
		self.handler = chandler(self)

	## Joins the supplied channels and stores the connection object.
	#
	# @param self The bot object.
	# @param conn The connection object. Stored in self.conn after this.
	# @param event The welcome event. Unused.
	def on_welcome(self, conn, event):
		for channel in self.chanlist:
			conn.join(channel)
		self.conn = conn

	## Called when a message is sent in a public channel.
	#
	# @param self The bot object.
	# @param conn The connection object.
	# @param event The event object.
	def on_pubmsg(self, conn, event):
		self.handler.event = event
		self.handler.on_pubmsg(event.target,event.source.nick,event.arguments[0])

	## Called when a message is sent to the bot in a private message/query.
	#
	# @param self The bot object.
	# @param conn The connection object.
	# @param event The event object.
	def on_privmsg(self, conn, event):
		self.handler.event = event
		self.handler.on_privmsg(event.source.nick,event.arguments[0])
