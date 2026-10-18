import datetime
import logging
import discord
import pywikibot
import re
import wikitextparser

from discord_botter import botter
from page_mod import PageMod
from page_op import PageOp

class DiscordLogger():
    botter = None
    channel = None

    def __init__(self, channel):
        self.botter = botter
        self.channel = channel

    def send_message(self, message=None, embed=None):
        self.botter.bot.send_message(self.channel, message=message, embed=embed)

levels = {
    logging.DEBUG: discord.Color.blue(),
    logging.INFO: discord.Color.green(),
    logging.WARNING: discord.Color.yellow(),
    logging.ERROR: discord.Color.red(),
    logging.CRITICAL: discord.Color.dark_red()
}

def get_level_color(levelno):
    return levels.get(levelno, discord.Color.default())

class DiscordTextChannelHandler(logging.Handler):
    """
    A handler class which writes logging records, appropriately formatted,
    to a Discord text channel.
    """
    messenger = None

    def __init__(self, channel):
        """
        Initialize the handler. Setup the bot and get the target channel.
        """
        logging.Handler.__init__(self)
        self.messenger = DiscordLogger(channel)

    def emit(self, record):
        """
        Emit a record.

        If a formatter is specified, it is used to format the record.
        The record is then written to the stream with a trailing newline.  If
        exception information is present, it is formatted using
        traceback.print_exception and appended to the stream.
        """
        try:
            # if record.msg is not None:
            #     print(f"   {type(record.msg)}: {record.msg}")
            # for arg in record.args:
            #     print(f"   {type(arg)}: {arg}")
            ts = discord.utils.utcnow()
            embed = discord.Embed(
                title=(f"{logging.getLevelName(record.levelno)}" if record.levelno >= logging.WARNING else None),
                description=None,
                # color=discord.Color.blue() # Hex integers like 0x336EFF also work
            )
            # embed.set_author(name=record.name, icon_url=None) # TODO: Add an icon
# %(asctime)s %(timeZone)s %(processName)s:%(threadName)s %(levelname)s:%(levelnameSuffix)s` [%(filename)s:%(lineno)d(%(funcName)s)](https://github.com/wotwiki/wotwiki/blob/master/scripts/%(filename)s#L%(lineno)d)\n
# %(levelname)s\n`%(asctime)s %(timeZone)s %(processName)s:%(threadName)s` [%(filename)s:%(lineno)d(%(funcName)s)](https://github.com/wotwiki/wotwiki/blob/master/scripts/%(filename)s#L%(lineno)d)\n
            asctime = hasattr(record, 'asctime') and record.asctime or ts.strftime("%Y-%m-%d %H:%M:%S")
            timeZone = hasattr(record, 'timeZone') and record.timeZone or ts.astimezone().tzname()
            embed.add_field(name="", value=f"```\n{asctime} {timeZone}\n{record.processName}:{record.threadName}```\n[{record.filename}:{record.lineno}({record.funcName})](https://github.com/wotwiki/wotwiki/blob/master/scripts/{record.filename}#L{record.lineno})", inline=False)
            if record.exc_info:
                exc_type, exc_value, exc_traceback = record.exc_info
                embed.add_field(name="Error", value=f"```\n{exc_traceback}\n```", inline=False)
            # TODO thumbnail etc
            embed.color = get_level_color(record.levelno)
            # embed.set_thumbnail(url="https://example.com")
            # embed.set_image(url="https://example.com")
            # embed.set_footer(text=f"[Source]({record.})")
            if isinstance(record.msg, PageOp):
                embed.title = type(record.msg).__name__
                if record.msg.page:
                    embed.add_field(name="Page", value=DWP(record.msg.page).__to_discord_str__(), inline=False)
                # elif record.msg.title:
                #     embed.add_field(name="Page", value=DWP(record.msg.title).__to_discord_str__(), inline=False)
                if record.msg.description and len(record.msg.description) > 0:
                    embed.add_field(name="Description", value=discord.utils.escape_markdown("\n".join(isinstance(record.msg.description, str) and [record.msg.description] or record.msg.description)), inline=False)
                if isinstance(record.msg, PageMod):
                    if record.msg.summary and len(record.msg.summary) > 0:
                        embed.add_field(name="Summary", value=discord.utils.escape_markdown(' '.join(isinstance(record.msg.summary, str) and [record.msg.summary] or record.msg.summary)), inline=False)
            else:
                msg = self.format(record)
                embed.add_field(name="", value=f"{msg}", inline=False)
            embed.timestamp = ts # Sets current time badge
            self.messenger.send_message(embed=embed)
        # except RecursionError:  # See issue 36272
        #     raise
        except Exception:
            self.handleError(record)

    def __repr__(self):
        return '<%s %s(%s)>' % (self.__class__.__name__, self.channelId, logging.getLevelName(self.level))

#     __class_getitem__ = classmethod(logging.GenericAlias)

class DiscordText():
    str = ""
    dis = ""

    def __init__(self, text, dis):
        self.str = text
        self.dis = dis

    def __str__(self):
        return self.str

    def __to_discord_str__(self):
        return self.dis

class DH1(DiscordText):
    def __init__(self, text):
        super().__init__(text, f"# {text}")

class DWP(DiscordText):
    def __init__(self, page):
        if isinstance(page, pywikibot.Page):
            page = page.title()
        super().__init__(f"'{page}'", f"[{page}](https://wot.fandom.com/wiki/{re.sub(r'\s', '_', page.strip())})")

class DWT(DWP):
    def __init__(self, template):
        if isinstance(template, wikitextparser.Template):
            template = template.name
        template = f"Template:{template}"
        super().__init__(template)
