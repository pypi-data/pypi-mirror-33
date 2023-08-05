from typing import Union
from depytg.internals import TelegramMethodBase
from depytg.types import *


class getMe(TelegramMethodBase):
    """
    A simple method for testing your bot's auth token. Requires no parameters. Returns basic information about the bot
    in form of a User object.
    """

    ReturnType = User


class getUpdates(TelegramMethodBase):
    """
    Use this method to receive incoming updates using long polling (wiki). An Array of Update objects is returned.
    :param offset: (int) Optional. Identifier of the first update to be returned. Must be greater by one than the
    highest among the identifiers of previously received updates. By default, updates starting with the earliest
    unconfirmed update are returned. An update is considered confirmed as soon as getUpdates is called with an offset
    higher than its update_id. The negative offset can be specified to retrieve updates starting from -offset update
    from the end of the updates queue. All previous updates will forgotten.
    :param limit: (int) Optional. Limits the number of updates to be retrieved. Values between 1—100 are accepted.
    Defaults to 100.
    :param timeout: (int) Optional. Timeout in seconds for long polling. Defaults to 0, i.e. usual short polling. Should
    be positive, short polling should be used for testing purposes only.
    :param allowed_updates: ('Array of String') Optional. List the types of updates you want your bot to receive. For
    example, specify [“message”, “edited_channel_post”, “callback_query”] to only receive updates of these types. See
    Update for a complete list of available update types. Specify an empty list to receive all updates regardless of
    type (default). If not specified, the previous setting will be used.
    """

    ReturnType = Sequence[Update]

    def __init__(self, offset: int = None,
                 limit: int = None,
                 timeout: int = None,
                 allowed_updates: Sequence[str] = None):
        super().__init__()

        self.offset = offset
        self.limit = limit
        self.timeout = timeout
        self.allowed_updates = allowed_updates


class setWebhook(TelegramMethodBase):
    """
    Use this method to specify a url and receive incoming updates via an outgoing webhook. Whenever there is an update
    for the bot, we will send an HTTPS POST request to the specified url, containing a JSON-serialized Update. In case
    of an unsuccessful request, we will give up after a reasonable amount of attempts. Returns true.
    :param url: (str) HTTPS url to send updates to. Use an empty string to remove webhook integration
    :param certificate: (InputFile) Optional. Upload your public key certificate so that the root certificate in use can
    be checked. See our self-signed guide for details.
    :param max_connections: (int) Optional. Maximum allowed number of simultaneous HTTPS connections to the webhook for
    update delivery, 1-100. Defaults to 40. Use lower values to limit the load on your bot‘s server, and higher values
    to increase your bot’s throughput.
    :param allowed_updates: ('Array of String') Optional. List the types of updates you want your bot to receive. For
    example, specify [“message”, “edited_channel_post”, “callback_query”] to only receive updates of these types. See
    Update for a complete list of available update types. Specify an empty list to receive all updates regardless of
    type (default). If not specified, the previous setting will be used.
    """

    ReturnType = bool

    def __init__(self, url: str,
                 certificate: InputFile = None,
                 max_connections: int = None,
                 allowed_updates: Sequence[str] = None):
        super().__init__()

        self.url = url
        self.certificate = certificate
        self.max_connections = max_connections
        self.allowed_updates = allowed_updates


class deleteWebhook(TelegramMethodBase):
    """
    Use this method to remove webhook integration if you decide to switch back to getUpdates. Returns True on success.
    Requires no parameters.
    """

    ReturnType = bool


class getWebhookInfo(TelegramMethodBase):
    """
    Use this method to get current webhook status. Requires no parameters. On success, returns a WebhookInfo object. If
    the bot is using getUpdates, will return an object with the url field empty.
    """

    ReturnType = WebhookInfo


class sendMessage(TelegramMethodBase):
    """
    Use this method to send text messages. On success, the sent Message is returned.
    :param chat_id: ('Integer or String') Unique identifier for the target chat or username of the target channel (in
    the format @channelusername)
    :param text: (str) Text of the message to be sent
    :param parse_mode: (str) Optional. Send Markdown or HTML, if you want Telegram apps to show bold, italic,
    fixed-width text or inline URLs in your bot's message.
    :param disable_web_page_preview: (bool) Optional. Disables link previews for links in this message
    :param disable_notification: (bool) Optional. Sends the message silently. Users will receive a notification with no
    sound.
    :param reply_to_message_id: (int) Optional. If the message is a reply, ID of the original message
    :param reply_markup: ('InlineKeyboardMarkup or ReplyKeyboardMarkup or ReplyKeyboardRemove or ForceReply') Optional.
    Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions
    to remove reply keyboard or to force a reply from the user.
    """

    ReturnType = Message

    def __init__(self, chat_id: Union[int, str],
                 text: str,
                 parse_mode: str = None,
                 disable_web_page_preview: bool = None,
                 disable_notification: bool = None,
                 reply_to_message_id: int = None,
                 reply_markup: Union[InlineKeyboardMarkup,
                                     ReplyKeyboardMarkup,
                                     ReplyKeyboardRemove,
                                     ForceReply] = None):
        super().__init__()

        self.chat_id = chat_id
        self.text = text
        self.parse_mode = parse_mode
        self.disable_web_page_preview = disable_web_page_preview
        self.disable_notification = disable_notification
        self.reply_to_message_id = reply_to_message_id
        self.reply_markup = reply_markup


class forwardMessage(TelegramMethodBase):
    """
    Use this method to forward messages of any kind. On success, the sent Message is returned.
    :param chat_id: (Union[int, str]) Unique identifier for the target chat or username of the target channel (in the
    format @channelusername)
    :param from_chat_id: (Union[int, str]) Unique identifier for the chat where the original message was sent (or
    channel username in the format @channelusername)
    :param disable_notification: (bool) Optional. Sends the message silently. Users will receive a notification with no
    sound.
    :param message_id: (int) Message identifier in the chat specified in from_chat_id
    """

    ReturnType = Message

    def __init__(self, chat_id: Union[int, str],
                 from_chat_id: Union[int, str],
                 message_id: int,
                 disable_notification: bool = None):
        super().__init__()

        self.chat_id = chat_id
        self.from_chat_id = from_chat_id
        self.disable_notification = disable_notification
        self.message_id = message_id


class sendPhoto(TelegramMethodBase):
    """
    Use this method to send photos. On success, the sent Message is returned.
    :param chat_id: (Union[int, str]) Unique identifier for the target chat or username of the target channel (in the
    format @channelusername)
    :param photo: (Union[InputFile, str]) Photo to send. Pass a file_id as String to send a photo that exists on the
    Telegram servers (recommended), pass an HTTP URL as a String for Telegram to get a photo from the Internet, or
    upload a new photo using multipart/form-data. More info on Sending Files »
    :param caption: (str) Optional. Photo caption (may also be used when resending photos by file_id), 0-200 characters
    :param parse_mode: (str) Optional. Send Markdown or HTML, if you want Telegram apps to show bold, italic,
    fixed-width text or inline URLs in your bot's message.
    :param disable_notification: (bool) Optional. Sends the message silently. Users will receive a notification with no
    sound.
    :param reply_to_message_id: (int) Optional. If the message is a reply, ID of the original message
    :param reply_markup: (Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply]) Optional.
    Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions
    to remove reply keyboard or to force a reply from the user.
    """

    ReturnType = Message

    def __init__(self, chat_id: Union[int, str],
                 photo: Union[InputFile, str] = None,
                 caption: str = None,
                 parse_mode: str = None,
                 disable_notification: bool = None,
                 reply_to_message_id: int = None,
                 reply_markup: Union[
                     InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply] = None):
        super().__init__()

        self.chat_id = chat_id
        self.photo = photo
        self.caption = caption
        self.parse_mode = parse_mode
        self.disable_notification = disable_notification
        self.reply_to_message_id = reply_to_message_id
        self.reply_markup = reply_markup


class sendAudio(TelegramMethodBase):
    """
    Use this method to send audio files, if you want Telegram clients to display them in the music player. Your audio
    must be in the .mp3 format. On success, the sent Message is returned. Bots can currently send audio files of up to
    50 MB in size, this limit may be changed in the future.
    :param chat_id: (Union[int, str]) Unique identifier for the target chat or username of the target channel (in the
    format @channelusername)
    :param audio: (Union[InputFile, str]) Audio file to send. Pass a file_id as String to send an audio file that exists
    on the Telegram servers (recommended), pass an HTTP URL as a String for Telegram to get an audio file from the
    Internet, or upload a new one using multipart/form-data. More info on Sending Files »
    :param caption: (str) Optional. Audio caption, 0-200 characters
    :param parse_mode: (str) Optional. Send Markdown or HTML, if you want Telegram apps to show bold, italic,
    fixed-width text or inline URLs in your bot's message.
    :param duration: (int) Optional. Duration of the audio in seconds
    :param performer: (str) Optional. Performer
    :param title: (str) Optional. Track name
    :param disable_notification: (bool) Optional. Sends the message silently. Users will receive a notification with no
    sound.
    :param reply_to_message_id: (int) Optional. If the message is a reply, ID of the original message
    :param reply_markup: (Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply]) Optional.
    Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions
    toremove reply keyboard or to force a reply from the user.
    """

    ReturnType = Message

    def __init__(self, chat_id: Union[int, str],
                 audio: Union[InputFile, str] = None,
                 caption: str = None,
                 parse_mode: str = None,
                 duration: int = None,
                 performer: str = None,
                 title: str = None,
                 disable_notification: bool = None,
                 reply_to_message_id: int = None,
                 reply_markup: Union[
                     InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply] = None):
        super().__init__()

        self.chat_id = chat_id
        self.audio = audio
        self.caption = caption
        self.parse_mode = parse_mode
        self.duration = duration
        self.performer = performer
        self.title = title
        self.disable_notification = disable_notification
        self.reply_to_message_id = reply_to_message_id
        self.reply_markup = reply_markup


class sendDocument(TelegramMethodBase):
    """
    Use this method to send general files. On success, the sent Message is returned. Bots can currently send files of
    any type of up to 50 MB in size, this limit may be changed in the future.
    :param chat_id: (Union[int, str]) Unique identifier for the target chat or username of the target channel (in the
    format @channelusername)
    :param document: (Union[InputFile, str]) File to send. Pass a file_id as String to send a file that exists on the
    Telegram servers (recommended), pass an HTTP URL as a String for Telegram to get a file from the Internet, or upload
    a new one using multipart/form-data. More info on Sending Files »
    :param caption: (str) Optional. Document caption (may also be used when resending documents by file_id), 0-200
    characters
    :param parse_mode: (str) Optional. Send Markdown or HTML, if you want Telegram apps to show bold, italic,
    fixed-width text or inline URLs in your bot's message.
    :param disable_notification: (bool) Optional. Sends the message silently. Users will receive a notification with no
    sound.
    :param reply_to_message_id: (int) Optional. If the message is a reply, ID of the original message
    :param reply_markup: (Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply]) Optional.
    Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions
    toremove reply keyboard or to force a reply from the user.
    """

    ReturnType = Message

    def __init__(self, chat_id: Union[int, str],
                 document: Union[InputFile, str] = None,
                 caption: str = None,
                 parse_mode: str = None,
                 disable_notification: bool = None,
                 reply_to_message_id: int = None,
                 reply_markup: Union[
                     InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply] = None):
        super().__init__()

        self.chat_id = chat_id
        self.document = document
        self.caption = caption
        self.parse_mode = parse_mode
        self.disable_notification = disable_notification
        self.reply_to_message_id = reply_to_message_id
        self.reply_markup = reply_markup


class sendVideo(TelegramMethodBase):
    """
    Use this method to send video files, Telegram clients support mp4 videos (other formats may be sent as Document). On
    success, the sent Message is returned. Bots can currently send video files of up to 50 MB in size, this limit may be
    changed in the future.
    :param chat_id: (Union[int, str]) Unique identifier for the target chat or username of the target channel (in the
    format @channelusername)
    :param video: (Union[InputFile, str]) Video to send. Pass a file_id as String to send a video that exists on the
    Telegram servers (recommended), pass an HTTP URL as a String for Telegram to get a video from the Internet, or
    upload a new video using multipart/form-data. More info on Sending Files »
    :param duration: (int) Optional. Duration of sent video in seconds
    :param width: (int) Optional. Video width
    :param height: (int) Optional. Video height
    :param caption: (str) Optional. Video caption (may also be used when resending videos by file_id), 0-200 characters
    :param parse_mode: (str) Optional. Send Markdown or HTML, if you want Telegram apps to show bold, italic, fixed-width text or inline URLs in the media caption.
    :param supports_streaming: (bool) Optional. Pass True, if the uploaded video is suitable for streaming.
    :param disable_notification: (bool) Optional. Sends the message silently. Users will receive a notification with no
    sound.
    :param reply_to_message_id: (int) Optional. If the message is a reply, ID of the original message
    :param reply_markup: (Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply]) Optional.
    Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions
    to remove reply keyboard or to force a reply from the user.
    """

    ReturnType = Message

    def __init__(self, chat_id: Union[int, str],
                 video: Union[InputFile, str] = None,
                 duration: int = None,
                 width: int = None,
                 height: int = None,
                 caption: str = None,
                 parse_mode: str = None,
                 supports_streaming: bool = None,
                 disable_notification: bool = None,
                 reply_to_message_id: int = None,
                 reply_markup: Union[
                     InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply] = None):
        super().__init__()

        self.chat_id = chat_id
        self.video = video
        self.duration = duration
        self.width = width
        self.height = height
        self.caption = caption
        self.parse_mode = parse_mode
        self.supports_streaming = supports_streaming
        self.disable_notification = disable_notification
        self.reply_to_message_id = reply_to_message_id
        self.reply_markup = reply_markup


class sendVoice(TelegramMethodBase):
    """
    Use this method to send audio files, if you want Telegram clients to display the file as a playable voice message.
    For this to work, your audio must be in an .ogg file encoded with OPUS (other formats may be sent as Audio or
    Document). On success, the sent Message is returned. Bots can currently send voice messages of up to 50 MB in size,
    this limit may be changed in the future.
    :param chat_id: (Union[int, str]) Unique identifier for the target chat or username of the target channel (in the
    format @channelusername)
    :param voice: (Union[InputFile, str]) Audio file to send. Pass a file_id as String to send a file that exists on the
    Telegram servers (recommended), pass an HTTP URL as a String for Telegram to get a file from the Internet, or upload
    a new one using multipart/form-data. More info on Sending Files »
    :param caption: (str) Optional. Voice message caption, 0-200 characters
    :param parse_mode: (str) Optional. Send Markdown or HTML, if you want Telegram apps to show bold, italic,
    fixed-width text or inline URLs in your bot's message.
    :param duration: (int) Optional. Duration of the voice message in seconds
    :param disable_notification: (bool) Optional. Sends the message silently. Users will receive a notification with no
    sound.
    :param reply_to_message_id: (int) Optional. If the message is a reply, ID of the original message
    :param reply_markup: (Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply]) Optional.
    Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions
    to remove reply keyboard or to force a reply from the user.
    """

    ReturnType = Message

    def __init__(self, chat_id: Union[int, str],
                 voice: Union[InputFile, str] = None,
                 caption: str = None,
                 parse_mode: str = None,
                 duration: int = None,
                 disable_notification: bool = None,
                 reply_to_message_id: int = None,
                 reply_markup: Union[
                     InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply] = None):
        super().__init__()

        self.chat_id = chat_id
        self.voice = voice
        self.caption = caption
        self.parse_mode = parse_mode
        self.duration = duration
        self.disable_notification = disable_notification
        self.reply_to_message_id = reply_to_message_id
        self.reply_markup = reply_markup


class sendVideoNote(TelegramMethodBase):
    """
    As of v.4.0, Telegram clients support rounded square mp4 videos of up to 1 minute long. Use this method to send
    video messages. On success, the sent Message is returned.
    :param chat_id: (Union[int, str]) Unique identifier for the target chat or username of the target channel (in the
    format @channelusername)
    :param video_note: (Union[InputFile, str]) Video note to send. Pass a file_id as String to send a video note that
    exists on the Telegram servers (recommended) or upload a new video using multipart/form-data. More info on Sending
    Files ». Sending video notes by a URL is currently unsupported
    :param duration: (int) Optional. Duration of sent video in seconds
    :param length: (int) Optional. Video width and height
    :param disable_notification: (bool) Optional. Sends the message silently. Users will receive a notification with no
    sound.
    :param reply_to_message_id: (int) Optional. If the message is a reply, ID of the original message
    :param reply_markup: (Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply]) Optional.
    Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions
    to remove reply keyboard or to force a reply from the user.
    """

    ReturnType = Message

    def __init__(self, chat_id: Union[int, str],
                 video_note: Union[InputFile, str] = None,
                 duration: int = None,
                 length: int = None,
                 disable_notification: bool = None,
                 reply_to_message_id: int = None,
                 reply_markup: Union[
                     InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply] = None):
        super().__init__()

        self.chat_id = chat_id
        self.video_note = video_note
        self.duration = duration
        self.length = length
        self.disable_notification = disable_notification
        self.reply_to_message_id = reply_to_message_id
        self.reply_markup = reply_markup


class sendMediaGroup(TelegramMethodBase):
    """
    As of v.4.0, Telegram clients support rounded square mp4 videos of up to 1 minute long. Use this method to send
    video messages. On success, the sent Message is returned.
    :param chat_id: (Union[int, str]) Unique identifier for the target chat or username of the target channel (in the
    format @channelusername)
    :param media: 	(Sequence[InputMedia]) A JSON-serialized array describing photos and videos to be sent, must include 2–10 items.
    :param disable_notification: (bool) Optional. Sends the message silently. Users will receive a notification with no
    sound.
    :param reply_to_message_id: (int) Optional. If the message is a reply, ID of the original message.
    """

    ReturnType = Message

    def __init__(self, chat_id: Union[int, str],
                 media: Sequence[InputMedia],
                 disable_notification: bool = None,
                 reply_to_message_id: int = None):
        super().__init__()

        self.chat_id = chat_id
        self.media = media
        self.disable_notification = disable_notification
        self.reply_to_message_id = reply_to_message_id


class sendLocation(TelegramMethodBase):
    """
    Use this method to send point on the map. On success, the sent Message is returned.
    :param chat_id: (Union[int, str]) Unique identifier for the target chat or username of the target channel (in the
    format @channelusername)
    :param latitude: (float) Latitude of the location
    :param longitude: (float) Longitude of the location
    :param live_period: (int) Optional. Period in seconds for which the location will be updated (see Live Locations,
    should be between 60 and 86400.
    :param disable_notification: (bool) Optional. Sends the message silently. Users will receive a notification with no
    sound.
    :param reply_to_message_id: (int) Optional. If the message is a reply, ID of the original message
    :param reply_markup: (Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply]) Optional.
    Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions
    to remove reply keyboard or to force a reply from the user.
    """

    ReturnType = Message

    def __init__(self, chat_id: Union[int, str],
                 latitude: float,
                 longitude: float,
                 live_period: int = None,
                 disable_notification: bool = None,
                 reply_to_message_id: int = None,
                 reply_markup: Union[
                     InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply] = None):
        super().__init__()

        self.chat_id = chat_id
        self.latitude = latitude
        self.longitude = longitude
        self.live_period = live_period
        self.disable_notification = disable_notification
        self.reply_to_message_id = reply_to_message_id
        self.reply_markup = reply_markup


class editMessageLiveLocation(TelegramMethodBase):
    """
    Use this method to edit live location messages sent by the bot or via the bot (for inline bots). A location can be
    edited until its live_period expires or editing is explicitly disabled by a call to stopMessageLiveLocation. On
    success, if the edited message was sent by the bot, the edited Message is returned, otherwise True is returned.
    :param chat_id: (Union[int, str]) Optional. Required if inline_message_id is not specified. Unique identifier for
    the target chat or username of the target channel (in the format @channelusername)
    :param message_id: (int) Optional. Required if inline_message_id is not specified. Identifier of the sent message
    :param inline_message_id: (str) Optional. Required if chat_id and message_id are not specified. Identifier of the
    inline message
    :param latitude: (float) Latitude of new location
    :param longitude: (float) Longitude of new location
    :param reply_markup: (InlineKeyboardMarkup) Optional. A JSON-serialized object for a new inline keyboard.
    """

    ReturnType = Union[Message, bool]

    def __init__(self, latitude: float,
                 longitude: float,
                 chat_id: Union[int, str] = None,
                 message_id: int = None,
                 inline_message_id: str = None,
                 reply_markup: InlineKeyboardMarkup = None):
        super().__init__()

        self.chat_id = chat_id
        self.message_id = message_id
        self.inline_message_id = inline_message_id
        self.latitude = latitude
        self.longitude = longitude
        self.reply_markup = reply_markup


class stopMessageLiveLocation(TelegramMethodBase):
    """
    Use this method to stop updating a live location message sent by the bot or via the bot (for inline bots) before
    live_period expires. On success, if the message was sent by the bot, the sent Message is returned, otherwise True
    is returned.
    :param chat_id: (Union[int, str]) Optional. Required if inline_message_id is not specified. Unique identifier for
    the target chat or username of the target channel (in the format @channelusername)
    :param message_id: (int) Optional. Required if inline_message_id is not specified. Identifier of the sent message
    :param inline_message_id: (str) Optional. Required if chat_id and message_id are not specified. Identifier of the
    inline message
    :param reply_markup: (InlineKeyboardMarkup) Optional. A JSON-serialized object for a new inline keyboard.
    """

    ReturnType = Union[Message, bool]

    def __init__(self, chat_id: Union[int, str] = None,
                 message_id: int = None,
                 inline_message_id: str = None,
                 reply_markup: InlineKeyboardMarkup = None):
        super().__init__()

        self.chat_id = chat_id
        self.message_id = message_id
        self.inline_message_id = inline_message_id
        self.reply_markup = reply_markup


class sendVenue(TelegramMethodBase):
    """
    Use this method to send information about a venue. On success, the sent Message is returned.
    :param chat_id: (Union[int, str]) Unique identifier for the target chat or username of the target channel (in the
    format @channelusername)
    :param latitude: (float) Latitude of the venue
    :param longitude: (float) Longitude of the venue
    :param title: (str) Name of the venue
    :param address: (str) Address of the venue
    :param foursquare_id: (str) Optional. Foursquare identifier of the venue
    :param disable_notification: (bool) Optional. Sends the message silently. Users will receive a notification with no
    sound.
    :param reply_to_message_id: (int) Optional. If the message is a reply, ID of the original message
    :param reply_markup: (Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply]) Optional.
    Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions
    to remove reply keyboard or to force a reply from the user.
    """

    ReturnType = Message

    def __init__(self, chat_id: Union[int, str],
                 latitude: float,
                 longitude: float,
                 title: str,
                 address: str,
                 foursquare_id: str = None,
                 disable_notification: bool = None,
                 reply_to_message_id: int = None,
                 reply_markup: Union[
                     InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply] = None):
        super().__init__()

        self.chat_id = chat_id
        self.latitude = latitude
        self.longitude = longitude
        self.title = title
        self.address = address
        self.foursquare_id = foursquare_id
        self.disable_notification = disable_notification
        self.reply_to_message_id = reply_to_message_id
        self.reply_markup = reply_markup


class sendContact(TelegramMethodBase):
    """
    Use this method to send phone contacts. On success, the sent Message is returned.
    :param chat_id: (Union[int, str]) Unique identifier for the target chat or username of the target channel (in the
    format @channelusername)
    :param phone_number: (str) Contact's phone number
    :param first_name: (str) Contact's first name
    :param last_name: (str) Optional. Contact's last name
    :param disable_notification: (bool) Optional. Sends the message silently. Users will receive a notification with no
    sound.
    :param reply_to_message_id: (int) Optional. If the message is a reply, ID of the original message
    :param reply_markup: (Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply]) Optional.
    Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions
    toremove keyboard or to force a reply from the user.
    """

    ReturnType = Message

    def __init__(self, chat_id: Union[int, str],
                 phone_number: str,
                 first_name: str,
                 last_name: str = None,
                 disable_notification: bool = None,
                 reply_to_message_id: int = None,
                 reply_markup: Union[InlineKeyboardMarkup,
                                     ReplyKeyboardMarkup,
                                     ReplyKeyboardRemove,
                                     ForceReply] = None):
        super().__init__()

        self.chat_id = chat_id
        self.phone_number = phone_number
        self.first_name = first_name
        self.last_name = last_name
        self.disable_notification = disable_notification
        self.reply_to_message_id = reply_to_message_id
        self.reply_markup = reply_markup


class sendChatAction(TelegramMethodBase):
    """
    Use this method when you need to tell the user that something is happening on the bot's side. The status is set for
    5 seconds or less (when a message arrives from your bot, Telegram clients clear its typing status). Returns True on
    success.
    :param chat_id: (Union[int, str]) Unique identifier for the target chat or username of the target channel (in the
    format @channelusername)
    :param action: (str) Type of action to broadcast. Choose one, depending on what the user is about to receive: typing
    for text messages, upload_photo for photos, record_video or upload_video for videos, record_audio or upload_audio
    for audio files, upload_document for general files, find_location for location data, record_video_note or
    upload_video_note for video notes.
    """

    ReturnType = bool

    def __init__(self, chat_id: Union[int, str],
                 action: str):
        super().__init__()

        self.chat_id = chat_id
        self.action = action


class getUserProfilePhotos(TelegramMethodBase):
    """
    Use this method to get a list of profile pictures for a user. Returns a UserProfilePhotos object.
    :param user_id: (int) Unique identifier of the target user
    :param offset: (int) Optional. Sequential number of the first photo to be returned. By default, all photos are
    returned.
    :param limit: (int) Optional. Limits the number of photos to be retrieved. Values between 1—100 are accepted.
    Defaults to 100.
    """

    ReturnType = UserProfilePhotos

    def __init__(self, user_id: int,
                 offset: int = None,
                 limit: int = None):
        super().__init__()

        self.user_id = user_id
        self.offset = offset
        self.limit = limit


class getFile(TelegramMethodBase):
    """
    Use this method to get basic info about a file and prepare it for downloading. For the moment, bots can download
    files of up to 20MB in size. On success, a File object is returned. The file can then be downloaded via the link
    https://api.telegram.org/file/bot\<token\>/\<file_path\>, where <file_path> is taken from the response. It is
    guaranteed that the link will be valid for at least 1 hour. When the link expires, a new one can be requested by
    calling getFile again.
    :param file_id: (str) File identifier to get info about
    """

    ReturnType = File

    def __init__(self, file_id: str):
        super().__init__()

        self.file_id = file_id


class kickChatMember(TelegramMethodBase):
    """
    Use this method to kick a user from a group, a supergroup or a channel. In the case of supergroups and channels, the
    user will not be able to return to the group on their own using invite links, etc., unless unbanned first. The bot
    must be an administrator in the chat for this to work and must have the appropriate admin rights. Returns True on
    success.
    :param chat_id: (Union[int, str]) Unique identifier for the target group or username of the target supergroup or
    channel (in the format @channelusername)
    :param user_id: (int) Unique identifier of the target user
    :param until_date: (int) Optional. Date when the user will be unbanned, unix time. If user is banned for more than
    366 days or less than 30 seconds from the current time they are considered to be banned forever
    """

    ReturnType = bool

    def __init__(self, chat_id: Union[int, str],
                 user_id: int,
                 until_date: int = None):
        super().__init__()

        self.chat_id = chat_id
        self.user_id = user_id
        self.until_date = until_date


class unbanChatMember(TelegramMethodBase):
    """
    Use this method to unban a previously kicked user in a supergroup or channel. The user will not return to the group
    or channel automatically, but will be able to join via link, etc. The bot must be an administrator for this to work.
    Returns True on success.
    :param chat_id: (Union[int, str]) Unique identifier for the target group or username of the target supergroup or
    channel (in the format @username)
    :param user_id: (int) Unique identifier of the target user
    """

    ReturnType = bool

    def __init__(self, chat_id: Union[int, str],
                 user_id: int):
        super().__init__()

        self.chat_id = chat_id
        self.user_id = user_id


class restrictChatMember(TelegramMethodBase):
    """
    Use this method to restrict a user in a supergroup. The bot must be an administrator in the supergroup for this to
    work and must have the appropriate admin rights. Pass True for all boolean parameters to lift restrictions from a
    user. Returns True on success.
    :param chat_id: (Union[int, str]) Unique identifier for the target chat or username of the target supergroup (in the
    format @supergroupusername)
    :param user_id: (int) Unique identifier of the target user
    :param until_date: (int) Optional. Date when restrictions will be lifted for the user, unix time. If user is
    restricted for more than 366 days or less than 30 seconds from the current time, they are considered to be
    restricted forever
    :param can_send_messages: (bool) Optional. Pass True, if the user can send text messages, contacts, locations and
    venues
    :param can_send_media_messages: (bool) Optional. Pass True, if the user can send audios, documents, photos, video,
    video notes and voice notes, implies can_send_messages
    :param can_send_other_messages: (bool) Optional. Pass True, if the user can send animations, games, stickers and use
    inline bots, implies can_send_media_messages
    :param can_add_web_page_previews: (bool) Optional. Pass True, if the user may add web page previews to their
    messages, implies can_send_media_messages
    """

    ReturnType = bool

    def __init__(self, chat_id: Union[int, str],
                 user_id: int,
                 until_date: int = None,
                 can_send_messages: bool = None,
                 can_send_media_messages: bool = None,
                 can_send_other_messages: bool = None,
                 can_add_web_page_previews: bool = None):
        super().__init__()

        self.chat_id = chat_id
        self.user_id = user_id
        self.until_date = until_date
        self.can_send_messages = can_send_messages
        self.can_send_media_messages = can_send_media_messages
        self.can_send_other_messages = can_send_other_messages
        self.can_add_web_page_previews = can_add_web_page_previews


class promoteChatMember(TelegramMethodBase):
    """
    Use this method to promote or demote a user in a supergroup or a channel. The bot must be an administrator in the
    chat for this to work and must have the appropriate admin rights. Pass False for all boolean parameters to demote a
    user. Returns True on success.
    :param chat_id: (Union[int, str]) Unique identifier for the target chat or username of the target channel (in the
    format @channelusername)
    :param user_id: (int) Unique identifier of the target user
    :param can_change_info: (bool) Optional. Pass True, if the administrator can change chat title, photo and other
    settings
    :param can_post_messages: (bool) Optional. Pass True, if the administrator can create channel posts, channels only
    :param can_edit_messages: (bool) Optional. Pass True, if the administrator can edit messages of other users,
    channels only
    :param can_delete_messages: (bool) Optional. Pass True, if the administrator can delete messages of other users
    :param can_invite_users: (bool) Optional. Pass True, if the administrator can invite new users to the chat
    :param can_restrict_members: (bool) Optional. Pass True, if the administrator can restrict, ban or unban chat
    members
    :param can_pin_messages: (bool) Optional. Pass True, if the administrator can pin messages, supergroups only
    :param can_promote_members: (bool) Optional. Pass True, if the administrator can add new administrators with a
    subset of his own privileges or demote administrators that he has promoted, directly or indirectly (promoted by
    administrators that were appointed by him)
    """

    ReturnType = bool

    def __init__(self, chat_id: Union[int, str],
                 user_id: int,
                 can_change_info: bool = None,
                 can_post_messages: bool = None,
                 can_edit_messages: bool = None,
                 can_delete_messages: bool = None,
                 can_invite_users: bool = None,
                 can_restrict_members: bool = None,
                 can_pin_messages: bool = None,
                 can_promote_members: bool = None):
        super().__init__()

        self.chat_id = chat_id
        self.user_id = user_id
        self.can_change_info = can_change_info
        self.can_post_messages = can_post_messages
        self.can_edit_messages = can_edit_messages
        self.can_delete_messages = can_delete_messages
        self.can_invite_users = can_invite_users
        self.can_restrict_members = can_restrict_members
        self.can_pin_messages = can_pin_messages
        self.can_promote_members = can_promote_members


class exportChatInviteLink(TelegramMethodBase):
    """
    Use this method to export an invite link to a supergroup or a channel. The bot must be an administrator in the chat
    for this to work and must have the appropriate admin rights. Returns exported invite link as String on success.
    :param chat_id: (Union[int, str]) Unique identifier for the target chat or username of the target channel (in the
    format @channelusername)
    """

    ReturnType = str

    def __init__(self, chat_id: Union[int, str]):
        super().__init__()

        self.chat_id = chat_id


class setChatPhoto(TelegramMethodBase):
    """
    Use this method to set a new profile photo for the chat. Photos can't be changed for private chats. The bot must be
    an administrator in the chat for this to work and must have the appropriate admin rights. Returns True on success.
    :param chat_id: (Union[int, str]) Unique identifier for the target chat or username of the target channel (in the
    format @channelusername)
    :param photo: (InputFile) New chat photo, uploaded using multipart/form-data
    """

    ReturnType = bool

    def __init__(self, chat_id: Union[int, str],
                 photo: InputFile = None):
        super().__init__()

        self.chat_id = chat_id
        self.photo = photo


class deleteChatPhoto(TelegramMethodBase):
    """
    Use this method to delete a chat photo. Photos can't be changed for private chats. The bot must be an administrator
    in the chat for this to work and must have the appropriate admin rights. Returns True on success.
    :param chat_id: (Union[int, str]) Unique identifier for the target chat or username of the target channel (in the
    format @channelusername)
    """

    ReturnType = bool

    def __init__(self, chat_id: Union[int, str]):
        super().__init__()

        self.chat_id = chat_id


class setChatTitle(TelegramMethodBase):
    """
    Use this method to change the title of a chat. Titles can't be changed for private chats. The bot must be an
    administrator in the chat for this to work and must have the appropriate admin rights. Returns True on success.
    :param chat_id: (Union[int, str]) Unique identifier for the target chat or username of the target channel (in the
    format @channelusername)
    :param title: (str) New chat title, 1-255 characters
    """

    ReturnType = bool

    def __init__(self, chat_id: Union[int, str],
                 title: str):
        super().__init__()

        self.chat_id = chat_id
        self.title = title


class setChatDescription(TelegramMethodBase):
    """
    Use this method to change the description of a supergroup or a channel. The bot must be an administrator in the chat
    for this to work and must have the appropriate admin rights. Returns True on success.
    :param chat_id: (Union[int, str]) Unique identifier for the target chat or username of the target channel (in the
    format @channelusername)
    :param description: (str) Optional. New chat description, 0-255 characters
    """

    ReturnType = bool

    def __init__(self, chat_id: Union[int, str],
                 description: str = None):
        super().__init__()

        self.chat_id = chat_id
        self.description = description


class pinChatMessage(TelegramMethodBase):
    """
    Use this method to pin a message in a supergroup. The bot must be an administrator in the chat for this to work and
    must have the appropriate admin rights. Returns True on success.
    :param chat_id: (Union[int, str]) Unique identifier for the target chat or username of the target channel (in the format @channelusername)
    :param message_id: (int) Identifier of a message to pin
    :param disable_notification: (bool) Optional. Pass True, if it is not necessary to send a notification to all group
    members about the new pinned message
    """

    ReturnType = bool

    def __init__(self, chat_id: Union[int, str],
                 message_id: int,
                 disable_notification: bool = None):
        super().__init__()

        self.chat_id = chat_id
        self.message_id = message_id
        self.disable_notification = disable_notification


class unpinChatMessage(TelegramMethodBase):
    """
    Use this method to unpin a message in a supergroup chat. The bot must be an administrator in the chat for this to
    work and must have the appropriate admin rights. Returns True on success.
    :param chat_id: (Union[int, str]) Unique identifier for the target chat or username of the target channel (in the format @channelusername)
    """

    ReturnType = bool

    def __init__(self, chat_id: Union[int, str]):
        super().__init__()

        self.chat_id = chat_id


class leaveChat(TelegramMethodBase):
    """
    Use this method for your bot to leave a group, supergroup or channel. Returns True on success.
    :param chat_id: (Union[int, str]) Unique identifier for the target chat or username of the target supergroup or
    channel (in the format @channelusername)
    """

    ReturnType = bool

    def __init__(self, chat_id: Union[int, str]):
        super().__init__()

        self.chat_id = chat_id


class getChat(TelegramMethodBase):
    """
    Use this method to get up to date information about the chat (current name of the user for one-on-one conversations,
    current username of a user, group or channel, etc.). Returns a Chat object on success.
    :param chat_id: (Union[int, str]) Unique identifier for the target chat or username of the target supergroup or
    channel (in the format @channelusername)
    """

    ReturnType = Chat

    def __init__(self, chat_id: Union[int, str]):
        super().__init__()

        self.chat_id = chat_id


class getChatAdministrators(TelegramMethodBase):
    """
    Use this method to get a list of administrators in a chat. On success, returns an Array of ChatMember objects that
    contains information about all chat administrators except other bots. If the chat is a group or a supergroup and no
    administrators were appointed, only the creator will be returned.
    :param chat_id: (Union[int, str]) Unique identifier for the target chat or username of the target supergroup or
    channel (in the format @channelusername)
    """

    ReturnType = Sequence[ChatMember]

    def __init__(self, chat_id: Union[int, str]):
        super().__init__()

        self.chat_id = chat_id


class getChatMembersCount(TelegramMethodBase):
    """
    Use this method to get the number of members in a chat. Returns Int on success.
    :param chat_id: (Union[int, str]) Unique identifier for the target chat or username of the target supergroup or
    channel (in the format @channelusername)
    """

    ReturnType = int

    def __init__(self, chat_id: Union[int, str]):
        super().__init__()

        self.chat_id = chat_id


class getChatMember(TelegramMethodBase):
    """
    Use this method to get information about a member of a chat. Returns a ChatMember object on success.
    :param chat_id: (Union[int, str]) Unique identifier for the target chat or username of the target supergroup or
    channel (in the format @channelusername)
    :param user_id: (int) Unique identifier of the target user
    """

    ReturnType = ChatMember

    def __init__(self, chat_id: Union[int, str],
                 user_id: int):
        super().__init__()

        self.chat_id = chat_id
        self.user_id = user_id


class setChatStickerSet(TelegramMethodBase):
    """
    Use this method to set a new group sticker set for a supergroup. The bot must be an administrator in the chat for
    this to work and must have the appropriate admin rights. Use the field can_set_sticker_set optionally returned in
    getChat requests to check if the bot can use this method. Returns True on success.
    :param chat_id: (Union[int, str]) Unique identifier for the target chat or username of the target supergroup (in the
    format @supergroupusername)
    :param sticker_set_name: (str) Name of the sticker set to be set as the group sticker set
    """

    ReturnType = bool

    def __init__(self, chat_id: Union[int, str],
                 sticker_set_name: str):
        super().__init__()

        self.chat_id = chat_id
        self.sticker_set_name = sticker_set_name


class deleteChatStickerSet(TelegramMethodBase):
    """
    Use this method to delete a group sticker set from a supergroup. The bot must be an administrator in the chat for
    this to work and must have the appropriate admin rights. Use the field can_set_sticker_set optionally returned in
    getChat requests to check if the bot can use this method. Returns True on success.
    :param chat_id: (Union[int, str]) Unique identifier for the target chat or username of the target supergroup (in the
    format @supergroupusername)
    """

    ReturnType = bool

    def __init__(self, chat_id: Union[int, str]):
        super().__init__()

        self.chat_id = chat_id


class editMessageText(TelegramMethodBase):
    """
    Use this method to edit text and game messages sent by the bot or via the bot (for inline bots). On success, if
    edited message is sent by the bot, the edited Message is returned, otherwise True is returned.
    :param chat_id: (Union[int, str]) Optional. Required if inline_message_id is not specified. Unique identifier for
    the target chat or username of the target channel (in the format @channelusername)
    :param message_id: (int) Optional. Required if inline_message_id is not specified. Identifier of the sent message
    :param inline_message_id: (str) Optional. Required if chat_id and message_id are not specified. Identifier of the
    inline message
    :param text: (str) New text of the message
    :param parse_mode: (str) Optional. Send Markdown or HTML, if you want Telegram apps to show bold, italic,
    fixed-width text or inline URLs in your bot's message.
    :param disable_web_page_preview: (bool) Optional. Disables link previews for links in this message
    :param reply_markup: (InlineKeyboardMarkup) Optional. A JSON-serialized object for an inline keyboard.
    """

    ReturnType = Union[Message, bool]

    def __init__(self, text: str,
                 chat_id: Union[int, str] = None,
                 message_id: int = None,
                 inline_message_id: str = None,
                 parse_mode: str = None,
                 disable_web_page_preview: bool = None,
                 reply_markup: InlineKeyboardMarkup = None):
        super().__init__()

        self.chat_id = chat_id
        self.message_id = message_id
        self.inline_message_id = inline_message_id
        self.text = text
        self.parse_mode = parse_mode
        self.disable_web_page_preview = disable_web_page_preview
        self.reply_markup = reply_markup


class editMessageCaption(TelegramMethodBase):
    """
    Use this method to edit captions of messages sent by the bot or via the bot (for inline bots). On success, if edited
    message is sent by the bot, the edited Message is returned, otherwise True is returned.
    :param chat_id: (Union[int, str]) Optional. Required if inline_message_id is not specified. Unique identifier for
    the target chat or username of the target channel (in the format @channelusername)
    :param message_id: (int) Optional. Required if inline_message_id is not specified. Identifier of the sent message
    :param inline_message_id: (str) Optional. Required if chat_id and message_id are not specified. Identifier of the
    inline message
    :param caption: (str) Optional. New caption of the message
    :param parse_mode: (str) Optional. Send Markdown or HTML, if you want Telegram apps to show bold, italic,
    fixed-width text or inline URLs in your bot's message.
    :param reply_markup: (InlineKeyboardMarkup) Optional. A JSON-serialized object for an inline keyboard.
    """

    ReturnType = Union[Message, bool]

    def __init__(self, chat_id: Union[int, str] = None,
                 message_id: int = None,
                 inline_message_id: str = None,
                 caption: str = None,
                 parse_mode: str = None,
                 reply_markup: InlineKeyboardMarkup = None):
        super().__init__()

        self.chat_id = chat_id
        self.message_id = message_id
        self.inline_message_id = inline_message_id
        self.caption = caption
        self.parse_mode = parse_mode
        self.reply_markup = reply_markup


class editMessageReplyMarkup(TelegramMethodBase):
    """
    Use this method to edit only the reply markup of messages sent by the bot or via the bot (for inline bots). On
    success, if edited message is sent by the bot, the edited Message is returned, otherwise True is returned.
    :param chat_id: (Union[int, str]) Optional. Required if inline_message_id is not specified. Unique identifier for
    the target chat or username of the target channel (in the format @channelusername)
    :param message_id: (int) Optional. Required if inline_message_id is not specified. Identifier of the sent message
    :param inline_message_id: (str) Optional. Required if chat_id and message_id are not specified. Identifier of the
    inline message
    :param reply_markup: (InlineKeyboardMarkup) Optional. A JSON-serialized object for an inline keyboard.
    """

    ReturnType = Union[Message, bool]

    def __init__(self, chat_id: Union[int, str] = None,
                 message_id: int = None,
                 inline_message_id: str = None,
                 reply_markup: InlineKeyboardMarkup = None):
        super().__init__()

        self.chat_id = chat_id
        self.message_id = message_id
        self.inline_message_id = inline_message_id
        self.reply_markup = reply_markup


class deleteMessage(TelegramMethodBase):
    """
    Use this method to delete a message, including service messages, with the following limitations:
    - A message can only be deleted if it was sent less than 48 hours ago.
    - Bots can delete outgoing messages in groups and supergroups.
    - Bots granted can_post_messages permissions can delete outgoing messages in channels.
    - If the bot is an administrator of a group, it can delete any message there.
    - If the bot has can_delete_messages permission in a supergroup or a channel, it can delete any message there.
    Returns True on success.
    :param chat_id: (Union[int, str]) Unique identifier for the target chat or username of the target channel (in the
    format @channelusername)
    :param message_id: (int) Identifier of the message to delete
    """

    ReturnType = bool

    def __init__(self, chat_id: Union[int, str],
                 message_id: int):
        super().__init__()

        self.chat_id = chat_id
        self.message_id = message_id


class sendSticker(TelegramMethodBase):
    """
    Use this method to send .webp stickers. On success, the sent Message is returned.
    :param chat_id: (Union[int, str]) Unique identifier for the target chat or username of the target channel (in the
    format @channelusername)
    :param sticker: (Union[InputFile, str]) Sticker to send. Pass a file_id as String to send a file that exists on the
    Telegram servers (recommended), pass an HTTP URL as a String for Telegram to get a .webp file from the Internet, or
    upload a new one using multipart/form-data. More info on Sending Files »
    :param disable_notification: (bool) Optional. Sends the message silently. Users will receive a notification with no
    sound.
    :param reply_to_message_id: (int) Optional. If the message is a reply, ID of the original message
    :param reply_markup: (Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply]) Optional.
    Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions
    to remove reply keyboard or to force a reply from the user.
    """

    ReturnType = Message

    def __init__(self, chat_id: Union[int, str],
                 sticker: Union[InputFile, str] = None,
                 disable_notification: bool = None,
                 reply_to_message_id: int = None,
                 reply_markup: Union[
                     InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply] = None):
        super().__init__()

        self.chat_id = chat_id
        self.sticker = sticker
        self.disable_notification = disable_notification
        self.reply_to_message_id = reply_to_message_id
        self.reply_markup = reply_markup


class getStickerSet(TelegramMethodBase):
    """
    Use this method to get a sticker set. On success, a StickerSet object is returned.
    :param name: (str) Name of the sticker set
    """

    ReturnType = StickerSet

    def __init__(self, name: str):
        super().__init__()

        self.name = name


class uploadStickerFile(TelegramMethodBase):
    """
    Use this method to upload a .png file with a sticker for later use in createNewStickerSet and addStickerToSet
    methods (can be used multiple times). Returns the uploaded File on success.
    :param user_id: (int) User identifier of sticker file owner
    :param png_sticker: (InputFile) Png image with the sticker, must be up to 512 kilobytes in size, dimensions must not
    exceed 512px, and either width or height must be exactly 512px.
    """

    ReturnType = File

    def __init__(self, user_id: int,
                 png_sticker: InputFile = None):
        super().__init__()

        self.user_id = user_id
        self.png_sticker = png_sticker


class createNewStickerSet(TelegramMethodBase):
    """
    Use this method to create new sticker set owned by a user. The bot will be able to edit the created sticker set.
    Returns True on success.
    :param user_id: (int) User identifier of created sticker set owner
    :param name: (str) Short name of sticker set, to be used in t.me/addstickers/ URLs (e.g., animals). Can contain only
    english letters, digits and underscores. Must begin with a letter, can't contain consecutive underscores and must
    end in “_by_<bot username>”. <bot_username> is case insensitive. 1-64 characters.
    :param title: (str) Sticker set title, 1-64 characters
    :param png_sticker: (Union[InputFile, str]) Png image with the sticker, must be up to 512 kilobytes in size,
    dimensions must not exceed 512px, and either width or height must be exactly 512px. Pass a file_id as a String to
    send a file that already exists on the Telegram servers, pass an HTTP URL as a String for Telegram to get a file
    from the Internet, or upload a new one using multipart/form-data.
    :param emojis: (str) One or more emoji corresponding to the sticker
    :param contains_masks: (bool) Optional. Pass True, if a set of mask stickers should be created
    :param mask_position: (MaskPosition) Optional. A JSON-serialized object for position where the mask should be placed
    on faces
    """

    ReturnType = bool

    def __init__(self, user_id: int,
                 name: str,
                 title: str,
                 emojis: str,
                 png_sticker: Union[InputFile, str] = None,
                 contains_masks: bool = None,
                 mask_position: MaskPosition = None):
        super().__init__()

        self.user_id = user_id
        self.name = name
        self.title = title
        self.png_sticker = png_sticker
        self.emojis = emojis
        self.contains_masks = contains_masks
        self.mask_position = mask_position


class addStickerToSet(TelegramMethodBase):
    """
    Use this method to add a new sticker to a set created by the bot. Returns True on success.
    :param user_id: (int) User identifier of sticker set owner
    :param name: (str) Sticker set name
    :param png_sticker: (Union[InputFile, str]) Png image with the sticker, must be up to 512 kilobytes in size,
    dimensions must not exceed 512px, and either width or height must be exactly 512px. Pass a file_id as a String to
    send a file that already exists on the Telegram servers, pass an HTTP URL as a String for Telegram to get a file
    from the Internet, or upload a new one using multipart/form-data. More info on Sending Files »
    :param emojis: (str) One or more emoji corresponding to the sticker
    :param mask_position: (MaskPosition) Optional. A JSON-serialized object for position where the mask should be placed
    on faces
    """

    ReturnType = bool

    def __init__(self, user_id: int,
                 name: str,
                 emojis: str,
                 png_sticker: Union[InputFile, str] = None,
                 mask_position: MaskPosition = None):
        super().__init__()

        self.user_id = user_id
        self.name = name
        self.png_sticker = png_sticker
        self.emojis = emojis
        self.mask_position = mask_position


class setStickerPositionInSet(TelegramMethodBase):
    """
    Use this method to move a sticker in a set created by the bot to a specific position . Returns True on success.
    :param sticker: (str) File identifier of the sticker
    :param position: (int) New sticker position in the set, zero-based
    """

    ReturnType = bool

    def __init__(self, sticker: str,
                 position: int):
        super().__init__()

        self.sticker = sticker
        self.position = position


class deleteStickerFromSet(TelegramMethodBase):
    """
    Use this method to delete a sticker from a set created by the bot. Returns True on success.
    :param sticker: (str) File identifier of the sticker
    """

    ReturnType = bool

    def __init__(self, sticker: str):
        super().__init__()

        self.sticker = sticker


class answerInlineQuery(TelegramMethodBase):
    """
    Use this method to send answers to an inline query. On success, True is returned.
    No more than 50 results per query are allowed.
    :param inline_query_id: (str) Unique identifier for the answered query
    :param results: ('Array of InlineQueryResult') A JSON-serialized array of results for the inline query
    :param cache_time: (int) Optional. The maximum amount of time in seconds that the result of the inline query may be
    cached on the server. Defaults to 300.
    :param is_personal: (bool) Optional. Pass True, if results may be cached on the server side only for the user that
    sent the query. By default, results may be returned to any user who sends the same query
    :param next_offset: (str) Optional. Pass the offset that a client should send in the next query with the same text
    to receive more results. Pass an empty string if there are no more results or if you don‘t support pagination.
    Offset length can’t exceed 64 bytes.
    :param switch_pm_text: (str) Optional. If passed, clients will display a button with specified text that switches
    the user to a private chat with the bot and sends the bot a start message with the parameter switch_pm_parameter
    :param switch_pm_parameter: (str) Optional. Deep-linking parameter for the /start message sent to the bot when user
    presses the switch button. 1-64 characters, only A-Z, a-z, 0-9, _ and - are allowed.
    """

    ReturnType = bool

    def __init__(self, inline_query_id: str,
                 results: Sequence[InlineQueryResult],
                 cache_time: int = None,
                 is_personal: bool = None,
                 next_offset: str = None,
                 switch_pm_text: str = None,
                 switch_pm_parameter: str = None):
        super().__init__()

        self.inline_query_id = inline_query_id
        self.results = results
        self.cache_time = cache_time
        self.is_personal = is_personal
        self.next_offset = next_offset
        self.switch_pm_text = switch_pm_text
        self.switch_pm_parameter = switch_pm_parameter


class sendInvoice(TelegramMethodBase):
    """
    Use this method to send invoices. On success, the sent Message is returned.
    :param chat_id: (int) Unique identifier for the target private chat
    :param title: (str) Product name, 1-32 characters
    :param description: (str) Product description, 1-255 characters
    :param payload: (str) Bot-defined invoice payload, 1-128 bytes. This will not be displayed to the user, use for your
    internal processes.
    :param provider_token: (str) Payments provider token, obtained via Botfather
    :param start_parameter: (str) Unique deep-linking parameter that can be used to generate this invoice when used as a
    start parameter
    :param currency: (str) Three-letter ISO 4217 currency code, see more on currencies
    :param prices: ('Array of LabeledPrice') Price breakdown, a list of components (e.g. product price, tax, discount,
    delivery cost, delivery tax, bonus, etc.)
    :param provider_data: (str) Optional. JSON-encoded data about the invoice, which will be shared with the
    payment provider. A detailed description of required fields should be provided by the payment provider.
    :param photo_url: (str) Optional. URL of the product photo for the invoice. Can be a photo of the goods or a
    marketing image for a service. People like it better when they see what they are paying for.
    :param photo_size: (int) Optional. Photo size
    :param photo_width: (int) Optional. Photo width
    :param photo_height: (int) Optional. Photo height
    :param need_name: (bool) Optional. Pass True, if you require the user's full name to complete the order
    :param need_phone_number: (bool) Optional. Pass True, if you require the user's phone number to complete the order
    :param need_email: (bool) Optional. Pass True, if you require the user's email to complete the order
    :param need_shipping_address: (bool) Optional. Pass True, if you require the user's shipping address to
    complete the order.
    :param send_phone_number_to_provider: (bool) Optional. Pass True, if user's phone number should be sent to provider.
    :param send_email_to_provider: (bool) Optional. Pass True, if user's email address should be sent to provider.
    :param is_flexible: (bool) Optional. Pass True, if the final price depends on the shipping method
    :param disable_notification: (bool) Optional. Sends the message silently. Users will receive a notification with no
    sound.
    :param reply_to_message_id: (int) Optional. If the message is a reply, ID of the original message
    :param reply_markup: (InlineKeyboardMarkup) Optional. A JSON-serialized object for an inline keyboard. If empty, one
    'Pay total price' button will be shown. If not empty, the first button must be a Pay button.
    """

    ReturnType = Message

    def __init__(self, chat_id: int,
                 title: str,
                 description: str,
                 payload: str,
                 provider_token: str,
                 start_parameter: str,
                 currency: str,
                 prices: Sequence[LabeledPrice],
                 provider_data: str = None,
                 photo_url: str = None,
                 photo_size: int = None,
                 photo_width: int = None,
                 photo_height: int = None,
                 need_name: bool = None,
                 need_phone_number: bool = None,
                 need_email: bool = None,
                 need_shipping_address: bool = None,
                 send_phone_number_to_provider: bool = None,
                 send_email_to_provider: bool = None,
                 is_flexible: bool = None,
                 disable_notification: bool = None,
                 reply_to_message_id: int = None,
                 reply_markup: InlineKeyboardMarkup = None):
        super().__init__()

        self.chat_id = chat_id
        self.title = title
        self.description = description
        self.payload = payload
        self.provider_token = provider_token
        self.start_parameter = start_parameter
        self.currency = currency
        self.prices = prices
        self.provider_data = provider_data
        self.photo_url = photo_url
        self.photo_size = photo_size
        self.photo_width = photo_width
        self.photo_height = photo_height
        self.need_name = need_name
        self.need_phone_number = need_phone_number
        self.need_email = need_email
        self.need_shipping_address = need_shipping_address
        self.send_phone_number_to_provider = send_phone_number_to_provider
        self.send_email_to_provider = send_email_to_provider
        self.is_flexible = is_flexible
        self.disable_notification = disable_notification
        self.reply_to_message_id = reply_to_message_id
        self.reply_markup = reply_markup


class answerShippingQuery(TelegramMethodBase):
    """
    If you sent an invoice requesting a shipping address and the parameter is_flexible was specified, the Bot API will
    send an Update with a shipping_query field to the bot. Use this method to reply to shipping queries. On success,
    True is returned.
    :param shipping_query_id: (str) Unique identifier for the query to be answered
    :param ok: (bool) Specify True if delivery to the specified address is possible and False if there are any problems
    (for example, if delivery to the specified address is not possible)
    :param shipping_options: ('Array of ShippingOption') Optional. Required if ok is True. A JSON-serialized array of
    available shipping options.
    :param error_message: (str) Optional. Required if ok is False. Error message in human readable form that explains
    why it is impossible to complete the order (e.g. "Sorry, delivery to your desired address is unavailable'). Telegram
    will display this message to the user.
    """

    ReturnType = bool

    def __init__(self, shipping_query_id: str,
                 ok: bool,
                 shipping_options: Sequence[ShippingOption] = None,
                 error_message: str = None):
        super().__init__()

        self.shipping_query_id = shipping_query_id
        self.ok = ok
        self.shipping_options = shipping_options
        self.error_message = error_message


class answerPreCheckoutQuery(TelegramMethodBase):
    """
    Once the user has confirmed their payment and shipping details, the Bot API sends the final confirmation in the form
    of an Update with the field pre_checkout_query. Use this method to respond to such pre-checkout queries. On success,
    True is returned. Note: The Bot API must receive an answer within 10 seconds after the pre-checkout query was sent.
    :param pre_checkout_query_id: (str) Unique identifier for the query to be answered
    :param ok: (bool) Specify True if everything is alright (goods are available, etc.) and the bot is ready to proceed
    with the order. Use False if there are any problems.
    :param error_message: (str) Optional. Required if ok is False. Error message in human readable form that explains
    the reason for failure to proceed with the checkout (e.g. "Sorry, somebody just bought the last of our amazing black
    T-shirts while you were busy filling out your payment details. Please choose a different color or garment!").
    Telegram will display this message to the user.
    """

    ReturnType = bool

    def __init__(self, pre_checkout_query_id: str,
                 ok: bool,
                 error_message: str = None):
        super().__init__()

        self.pre_checkout_query_id = pre_checkout_query_id
        self.ok = ok
        self.error_message = error_message


class sendGame(TelegramMethodBase):
    """
    Use this method to send a game. On success, the sent Message is returned.
    :param chat_id: (int) Unique identifier for the target chat
    :param game_short_name: (str) Short name of the game, serves as the unique identifier for the game. Set up your
    games via Botfather.
    :param disable_notification: (bool) Optional. Sends the message silently. Users will receive a notification with no
    sound.
    :param reply_to_message_id: (int) Optional. If the message is a reply, ID of the original message
    :param reply_markup: (InlineKeyboardMarkup) Optional. A JSON-serialized object for an inline keyboard. If empty, one
    ‘Play game_title’ button will be shown. If not empty, the first button must launch the game.
    """

    ReturnType = Message

    def __init__(self, chat_id: int,
                 game_short_name: str,
                 disable_notification: bool = None,
                 reply_to_message_id: int = None,
                 reply_markup: InlineKeyboardMarkup = None):
        super().__init__()

        self.chat_id = chat_id
        self.game_short_name = game_short_name
        self.disable_notification = disable_notification
        self.reply_to_message_id = reply_to_message_id
        self.reply_markup = reply_markup


class setGameScore(TelegramMethodBase):
    """
    Use this method to set the score of the specified user in a game. On success, if the message was sent by the bot,
    returns the edited Message, otherwise returns True. Returns an error, if the new score is not greater than the
    user's current score in the chat and force is False.
    :param user_id: (int) User identifier
    :param score: (int) New score, must be non-negative
    :param force: (bool) Optional. Pass True, if the high score is allowed to decrease. This can be useful when fixing
    mistakes or banning cheaters
    :param disable_edit_message: (bool) Optional. Pass True, if the game message should not be automatically edited to
    include the current scoreboard
    :param chat_id: (int) Optional. Required if inline_message_id is not specified. Unique identifier for the target
    chat
    :param message_id: (int) Optional. Required if inline_message_id is not specified. Identifier of the sent message
    :param inline_message_id: (str) Optional. Required if chat_id and message_id are not specified. Identifier of the
    inline message
    """

    ReturnType = bool

    def __init__(self, user_id: int,
                 score: int,
                 force: bool = None,
                 disable_edit_message: bool = None,
                 chat_id: int = None,
                 message_id: int = None,
                 inline_message_id: str = None):
        super().__init__()

        self.user_id = user_id
        self.score = score
        self.force = force
        self.disable_edit_message = disable_edit_message
        self.chat_id = chat_id
        self.message_id = message_id
        self.inline_message_id = inline_message_id


class getGameHighScores(TelegramMethodBase):
    """
    Use this method to get data for high score tables. Will return the score of the specified user and several of his
    neighbors in a game. On success, returns an Array of GameHighScore objects.
    :param user_id: (int) Target user id
    :param chat_id: (int) Optional. Required if inline_message_id is not specified. Unique identifier for the target
    chat
    :param message_id: (int) Optional. Required if inline_message_id is not specified. Identifier of the sent message
    :param inline_message_id: (str) Optional. Required if chat_id and message_id are not specified. Identifier of the
    inline message
    """

    ReturnType = Sequence[GameHighScore]

    def __init__(self, user_id: int,
                 chat_id: int = None,
                 message_id: int = None,
                 inline_message_id: str = None):
        super().__init__()

        self.user_id = user_id
        self.chat_id = chat_id
        self.message_id = message_id
        self.inline_message_id = inline_message_id
