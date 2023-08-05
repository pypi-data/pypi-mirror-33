import re

from depytg.types import Message, User


def is_for_me(msg: Message, me: User, group_requires_at=True):
    """
    Checks whether this message is for the bot.

    :param msg: (Message) The message to check
    :param me: (User) Bot's data from getMe()
    :param group_requires_at: (bool) Whether messages sent to groups/channels should include the bot's username
    to be considered
    :return: (bool) True if the message is for the bot
    """

    # Private chat with bot
    if msg.chat.type == 'private':
        return True

    # Message is a reply to a bot's message
    if msg.reply_to_message.from_.id == me.id:
        return True

    if "text" in msg:
        # Message is a command and tagging the bot is not required to trigger it
        if not group_requires_at and msg.text.startswith("/"):
            return True

        # Bot is tagged in the massage
        if "@" + me.username in msg.text:
            return True

    return False

def escape_markdown(text: str):
    """
    Helper function to escape telegram markup symbols.
    Borrowed from Telegram Bot Api (telegram.utils.helpers)
    """
    escape_chars = '\*_`\['
    return re.sub(r'([%s])' % escape_chars, r'\\\1', text)
