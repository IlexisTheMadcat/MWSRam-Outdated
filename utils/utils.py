
# Lib

# Site

# Local


def _get_from_guilds(bot, getter, argument):
    """Copied from discord.ext.commands.converter to prevent
    access to protected attributes inspection error"""
    result = None
    for guild in bot.guilds:
        result = getattr(guild, getter)(argument)
        if result:
            return result
    return result
