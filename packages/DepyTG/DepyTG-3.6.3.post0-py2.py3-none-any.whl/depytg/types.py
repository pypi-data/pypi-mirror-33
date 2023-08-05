from typing import Sequence, BinaryIO
from depytg.internals import TelegramObjectBase


class Update(TelegramObjectBase):
    """
    This object represents an incoming update. At most one of the optional parameters can be present in any given
    update.
    :param update_id: (int) The update‘s unique identifier. Update identifiers start from a certain positive number
    and increase sequentially. This ID becomes especially handy if you’re using Webhooks, since it allows you to ignore
    repeated updates or to restore the correct update sequence, should they get out of order.
    :param message: (Message) Optional. New incoming message of any kind — text, photo, sticker, etc.
    :param edited_message: (Message) Optional. New version of a message that is known to the bot and was edited
    :param channel_post: (Message) Optional. New incoming channel post of any kind — text, photo, sticker, etc.
    :param edited_channel_post: (Message) Optional. New version of a channel post that is known to the bot and was
    edited
    :param inline_query: (InlineQuery) Optional. New incoming inline query
    :param chosen_inline_result: (ChosenInlineResult) Optional. The result of an inline query that was chosen by a user
    and sent to their chat partner. Please see our documentation on the feedback collecting for details on how to
    enable these updates for your bot.
    :param callback_query: (CallbackQuery) Optional. New incoming callback query
    :param shipping_query: (ShippingQuery) Optional. New incoming shipping query. Only for invoices with flexible price
    :param pre_checkout_query: (PreCheckoutQuery) Optional. New incoming pre-checkout query. Contains full information
    about checkout
    """

    def __init__(self, update_id: int,
                 message: 'Message' = None,
                 edited_message: 'Message' = None,
                 channel_post: 'Message' = None,
                 edited_channel_post: 'Message' = None,
                 inline_query: 'InlineQuery' = None,
                 chosen_inline_result: 'ChosenInlineResult' = None,
                 callback_query: 'CallbackQuery' = None,
                 shipping_query: 'ShippingQuery' = None,
                 pre_checkout_query: 'PreCheckoutQuery' = None):
        super().__init__()

        self.update_id = update_id
        self.message = message
        self.edited_message = edited_message
        self.channel_post = channel_post
        self.edited_channel_post = edited_channel_post
        self.inline_query = inline_query
        self.chosen_inline_result = chosen_inline_result
        self.callback_query = callback_query
        self.shipping_query = shipping_query
        self.pre_checkout_query = pre_checkout_query


class WebhookInfo(TelegramObjectBase):
    """
    Contains information about the current status of a webhook.
    :param url: (str) Webhook URL, may be empty if webhook is not set up
    :param has_custom_certificate: (bool) True, if a custom certificate was provided for webhook certificate checks
    :param pending_update_count: (int) Number of updates awaiting delivery
    :param last_error_date: (int) Optional. Unix time for the most recent error that happened when trying to deliver an
    update via webhook
    :param last_error_message: (str) Optional. Error message in human-readable format for the most recent error that
    happened when trying to deliver an update via webhook
    :param max_connections: (int) Optional. Maximum allowed number of simultaneous HTTPS connections to the webhook
    for update delivery
    :param allowed_updates: ('Array of String') Optional. A list of update types the bot is subscribed to. Defaults to
    all update types
    """

    def __init__(self, url: str,
                 has_custom_certificate: bool,
                 pending_update_count: int,
                 last_error_date: int = None,
                 last_error_message: str = None,
                 max_connections: int = None,
                 allowed_updates: Sequence[str] = None):
        super().__init__()

        self.url = url
        self.has_custom_certificate = has_custom_certificate
        self.pending_update_count = pending_update_count
        self.last_error_date = last_error_date
        self.last_error_message = last_error_message
        self.max_connections = max_connections
        self.allowed_updates = allowed_updates


class User(TelegramObjectBase):
    """
    This object represents a Telegram user or bot.
    :param id: (int) Unique identifier for this user or bot
    :param is_bot: (bool) True, if this user is a bot
    :param first_name: (str) User‘s or bot’s first name
    :param last_name: (str) Optional. User‘s or bot’s last name
    :param username: (str) Optional. User‘s or bot’s username
    :param language_code: (str) Optional. IETF language tag of the user's language
    """

    def __init__(self, id: int,
                 is_bot: bool,
                 first_name: str,
                 last_name: str = None,
                 username: str = None,
                 language_code: str = None):
        super().__init__()

        self.id = id
        self.is_bot = is_bot
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.language_code = language_code


class Chat(TelegramObjectBase):
    """
    This object represents a chat.
    :param id: (int) Unique identifier for this chat. This number may be greater than 32 bits and some programming
    languages may have difficulty/silent defects in interpreting it. But it is smaller than 52 bits, so a signed 64 bit
    integer or double-precision float type are safe for storing this identifier.
    :param type: (str) Type of chat, can be either “private”, “group”, “supergroup” or “channel”
    :param title: (str) Optional. Title, for supergroups, channels and group chats
    :param username: (str) Optional. Username, for private chats, supergroups and channels if available
    :param first_name: (str) Optional. First name of the other party in a private chat
    :param last_name: (str) Optional. Last name of the other party in a private chat
    :param all_members_are_administrators: (bool) Optional. True if a group has ‘All Members Are Admins’ enabled.
    :param photo: (ChatPhoto) Optional. Chat photo. Returned only in getChat.
    :param description: (str) Optional. Description, for supergroups and channel chats. Returned only in getChat.
    :param invite_link: (str) Optional. Chat invite link, for supergroups and channel chats. Returned only in getChat.
    :param pinned_message: (Message) Optional. Pinned message, for supergroups. Returned only in getChat.
    :param sticker_set_name: (str) Optional. For supergroups, name of group sticker set. Returned only in getChat.
    :param can_set_sticker_set: (bool) Optional. True, if the bot can change the group sticker set. Returned only in
    getChat.
    """

    def __init__(self, id: int,
                 type: str,
                 title: str = None,
                 username: str = None,
                 first_name: str = None,
                 last_name: str = None,
                 all_members_are_administrators: bool = None,
                 photo: 'ChatPhoto' = None,
                 description: str = None,
                 invite_link: str = None,
                 pinned_message: 'Message' = None,
                 sticker_set_name: str = None,
                 can_set_sticker_set: bool = None):
        super().__init__()

        self.id = id
        self.type = type
        self.title = title
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.all_members_are_administrators = all_members_are_administrators
        self.photo = photo
        self.description = description
        self.invite_link = invite_link
        self.pinned_message = pinned_message
        self.sticker_set_name = sticker_set_name
        self.can_set_sticker_set = can_set_sticker_set


class Message(TelegramObjectBase):
    """
    This object represents a message.
    :param message_id: (int) Unique message identifier inside this chat
    :param date: (int) Date the message was sent in Unix time
    :param chat: (Chat) Conversation the message belongs to
    :param from_: (User) Optional. Sender, empty for messages sent to channels
    :param forward_from: (User) Optional. For forwarded messages, sender of the original message
    :param forward_from_chat: (Chat) Optional. For messages forwarded from channels, information about the original
    channel
    :param forward_from_message_id: (int) Optional. For messages forwarded from channels, identifier of the original
    message in the channel
    :param forward_signature: (str) Optional. For messages forwarded from channels, signature of the post author if
    present
    :param forward_date: (int) Optional. For forwarded messages, date the original message was sent in Unix time
    :param reply_to_message: (Message) Optional. For replies, the original message. Note that the Message object in
    this field will not contain further reply_to_message fields even if it itself is a reply.
    :param edit_date: (int) Optional. Date the message was last edited in Unix time
    :param author_signature: (str) Optional. Signature of the post author for messages in channels
    :param text: (str) Optional. For text messages, the actual UTF-8 text of the message, 0-4096 characters.
    :param entities: ('Array of MessageEntity') Optional. For text messages, special entities like usernames, URLs,
    bot commands, etc. that appear in the text
    :param caption_entities: ('Array of MessageEntity') Optional. For messages with a caption, special entities like
    usernames, URLs, bot commands, etc. that appear in the caption
    :param audio: (Audio) Optional. Message is an audio file, information about the file
    :param document: (Document) Optional. Message is a general file, information about the file
    :param game: (Game) Optional. Message is a game, information about the game. More about games »
    :param photo: ('Array of PhotoSize') Optional. Message is a photo, available sizes of the photo
    :param sticker: (Sticker) Optional. Message is a sticker, information about the sticker
    :param video: (Video) Optional. Message is a video, information about the video
    :param voice: (Voice) Optional. Message is a voice message, information about the file
    :param video_note: (VideoNote) Optional. Message is a video note, information about the video message
    :param caption: (str) Optional. Caption for the audio, document, photo, video or voice, 0-200 characters
    :param contact: (Contact) Optional. Message is a shared contact, information about the contact
    :param location: (Location) Optional. Message is a shared location, information about the location
    :param venue: (Venue) Optional. Message is a venue, information about the venue
    :param new_chat_members: ('Array of User') Optional. New members that were added to the group or supergroup and
    information about them (the bot itself may be one of these members)
    :param left_chat_member: (User) Optional. A member was removed from the group, information about them (this member
    may be the bot itself)
    :param new_chat_title: (str) Optional. A chat title was changed to this value
    :param new_chat_photo: ('Array of PhotoSize') Optional. A chat photo was change to this value
    :param delete_chat_photo: (bool) Optional. Service message: the chat photo was deleted
    :param group_chat_created: (bool) Optional. Service message: the group has been created
    :param supergroup_chat_created: (bool) Optional. Service message: the supergroup has been created. This field can‘t
    be received in a message coming through updates, because bot can’t be a member of a supergroup when it is created.
    It can only be found in reply_to_message if someone replies to a very first message in a directly created
    supergroup.
    :param channel_chat_created: (bool) Optional. Service message: the channel has been created. This field can‘t be
    received in a message coming through updates, because bot can’t be a member of a channel when it is created.
    It can only be found in reply_to_message if someone replies to a very first message in a channel.
    :param migrate_to_chat_id: (int) Optional. The group has been migrated to a supergroup with the specified
    identifier. This number may be greater than 32 bits and some programming languages may have difficulty/silent
    defects in interpreting it. But it is smaller than 52 bits, so a signed 64 bit integer or double-precision float
    type are safe for storing this identifier.
    :param migrate_from_chat_id: (int) Optional. The supergroup has been migrated from a group with the specified
    identifier. This number may be greater than 32 bits and some programming languages may have difficulty/silent
    defects in interpreting it. But it is smaller than 52 bits, so a signed 64 bit integer or double-precision float
    type are safe for storing this identifier.
    :param pinned_message: (Message) Optional. Specified message was pinned. Note that the Message object in this field
    will not contain further reply_to_message fields even if it is itself a reply.
    :param invoice: (Invoice) Optional. Message is an invoice for a payment, information about the invoice.
    :param successful_payment: (SuccessfulPayment) Optional. Message is a service message about a successful payment,
    information about the payment.
    :param connected_website: (str) Optional. The domain name of the website on which the user has logged in.
    """

    def __init__(self, message_id: int,
                 date: int,
                 chat: 'Chat',
                 from_: 'User' = None,
                 forward_from: 'User' = None,
                 forward_from_chat: 'Chat' = None,
                 forward_from_message_id: int = None,
                 forward_signature: str = None,
                 forward_date: int = None,
                 reply_to_message: 'Message' = None,
                 edit_date: int = None,
                 author_signature: str = None,
                 text: str = None,
                 entities: Sequence['MessageEntity'] = None,
                 caption_entities: Sequence['MessageEntity'] = None,
                 audio: 'Audio' = None,
                 document: 'Document' = None,
                 game: 'Game' = None,
                 photo: Sequence['PhotoSize'] = None,
                 sticker: 'Sticker' = None,
                 video: 'Video' = None,
                 voice: 'Voice' = None,
                 video_note: 'VideoNote' = None,
                 caption: str = None,
                 contact: 'Contact' = None,
                 location: 'Location' = None,
                 venue: 'Venue' = None,
                 new_chat_members: Sequence['User'] = None,
                 left_chat_member: 'User' = None,
                 new_chat_title: str = None,
                 new_chat_photo: Sequence['PhotoSize'] = None,
                 delete_chat_photo: bool = None,
                 group_chat_created: bool = None,
                 supergroup_chat_created: bool = None,
                 channel_chat_created: bool = None,
                 migrate_to_chat_id: int = None,
                 migrate_from_chat_id: int = None,
                 pinned_message: 'Message' = None,
                 invoice: 'Invoice' = None,
                 successful_payment: 'SuccessfulPayment' = None,
                 connected_website: str = None):
        super().__init__()

        self.message_id = message_id
        self.date = date
        self.chat = chat
        self.from_ = from_
        self.forward_from = forward_from
        self.forward_from_chat = forward_from_chat
        self.forward_from_message_id = forward_from_message_id
        self.forward_signature = forward_signature
        self.forward_date = forward_date
        self.reply_to_message = reply_to_message
        self.edit_date = edit_date
        self.author_signature = author_signature
        self.text = text
        self.entities = entities
        self.caption_entities = caption_entities
        self.audio = audio
        self.document = document
        self.game = game
        self.photo = photo
        self.sticker = sticker
        self.video = video
        self.voice = voice
        self.video_note = video_note
        self.caption = caption
        self.contact = contact
        self.location = location
        self.venue = venue
        self.new_chat_members = new_chat_members
        self.left_chat_member = left_chat_member
        self.new_chat_title = new_chat_title
        self.new_chat_photo = new_chat_photo
        self.delete_chat_photo = delete_chat_photo
        self.group_chat_created = group_chat_created
        self.supergroup_chat_created = supergroup_chat_created
        self.channel_chat_created = channel_chat_created
        self.migrate_to_chat_id = migrate_to_chat_id
        self.migrate_from_chat_id = migrate_from_chat_id
        self.pinned_message = pinned_message
        self.invoice = invoice
        self.successful_payment = successful_payment
        self.connected_website = connected_website


class MessageEntity(TelegramObjectBase):
    """
    This object represents one special entity in a text message. For example, hashtags, usernames, URLs, etc.
    :param type: (str) Type of the entity. Can be mention (@username), hashtag, bot_command, url, email, bold
    (bold text), italic (italic text), code (monowidth string), pre (monowidth block), text_link (for clickable
    text URLs), text_mention (for users without usernames)
    :param offset: (int) Offset in UTF-16 code units to the start of the entity
    :param length: (int) Length of the entity in UTF-16 code units
    :param url: (str) Optional. For “text_link” only, url that will be opened after user taps on the text
    :param user: (User) Optional. For “text_mention” only, the mentioned user
    """

    def __init__(self, type: str,
                 offset: int,
                 length: int,
                 url: str = None,
                 user: 'User' = None):
        super().__init__()

        self.type = type
        self.offset = offset
        self.length = length
        self.url = url
        self.user = user


class PhotoSize(TelegramObjectBase):
    """
    This object represents one size of a photo or a file / sticker thumbnail.
    :param file_id: (str) Unique identifier for this file
    :param width: (int) Photo width
    :param height: (int) Photo height
    :param file_size: (int) Optional. File size
    """

    def __init__(self, file_id: str,
                 width: int,
                 height: int,
                 file_size: int = None):
        super().__init__()

        self.file_id = file_id
        self.width = width
        self.height = height
        self.file_size = file_size


class Audio(TelegramObjectBase):
    """
    This object represents an audio file to be treated as music by the Telegram clients.
    :param file_id: (str) Unique identifier for this file
    :param duration: (int) Duration of the audio in seconds as defined by sender
    :param performer: (str) Optional. Performer of the audio as defined by sender or by audio tags
    :param title: (str) Optional. Title of the audio as defined by sender or by audio tags
    :param mime_type: (str) Optional. MIME type of the file as defined by sender
    :param file_size: (int) Optional. File size
    """

    def __init__(self, file_id: str,
                 duration: int,
                 performer: str = None,
                 title: str = None,
                 mime_type: str = None,
                 file_size: int = None):
        super().__init__()

        self.file_id = file_id
        self.duration = duration
        self.performer = performer
        self.title = title
        self.mime_type = mime_type
        self.file_size = file_size


class Document(TelegramObjectBase):
    """
    This object represents a general file (as opposed to photos, voice messages and audio files).
    :param file_id: (str) Unique file identifier
    :param thumb: (PhotoSize) Optional. Document thumbnail as defined by sender
    :param file_name: (str) Optional. Original filename as defined by sender
    :param mime_type: (str) Optional. MIME type of the file as defined by sender
    :param file_size: (int) Optional. File size
    """

    def __init__(self, file_id: str,
                 thumb: 'PhotoSize' = None,
                 file_name: str = None,
                 mime_type: str = None,
                 file_size: int = None):
        super().__init__()

        self.file_id = file_id
        self.thumb = thumb
        self.file_name = file_name
        self.mime_type = mime_type
        self.file_size = file_size


class Video(TelegramObjectBase):
    """
    This object represents a video file.
    :param file_id: (str) Unique identifier for this file
    :param width: (int) Video width as defined by sender
    :param height: (int) Video height as defined by sender
    :param duration: (int) Duration of the video in seconds as defined by sender
    :param thumb: (PhotoSize) Optional. Video thumbnail
    :param mime_type: (str) Optional. Mime type of a file as defined by sender
    :param file_size: (int) Optional. File size
    """

    def __init__(self, file_id: str,
                 width: int,
                 height: int,
                 duration: int,
                 thumb: 'PhotoSize' = None,
                 mime_type: str = None,
                 file_size: int = None):
        super().__init__()

        self.file_id = file_id
        self.width = width
        self.height = height
        self.duration = duration
        self.thumb = thumb
        self.mime_type = mime_type
        self.file_size = file_size


class Voice(TelegramObjectBase):
    """
    This object represents a voice note.
    :param file_id: (str) Unique identifier for this file
    :param duration: (int) Duration of the audio in seconds as defined by sender
    :param mime_type: (str) Optional. MIME type of the file as defined by sender
    :param file_size: (int) Optional. File size
    """

    def __init__(self, file_id: str,
                 duration: int,
                 mime_type: str = None,
                 file_size: int = None):
        super().__init__()

        self.file_id = file_id
        self.duration = duration
        self.mime_type = mime_type
        self.file_size = file_size


class VideoNote(TelegramObjectBase):
    """
    This object represents a video message (available in Telegram apps as of v.4.0).
    :param file_id: (str) Unique identifier for this file
    :param length: (int) Video width and height as defined by sender
    :param duration: (int) Duration of the video in seconds as defined by sender
    :param thumb: (PhotoSize) Optional. Video thumbnail
    :param file_size: (int) Optional. File size
    """

    def __init__(self, file_id: str,
                 length: int,
                 duration: int,
                 thumb: 'PhotoSize' = None,
                 file_size: int = None):
        super().__init__()

        self.file_id = file_id
        self.length = length
        self.duration = duration
        self.thumb = thumb
        self.file_size = file_size


class Contact(TelegramObjectBase):
    """
    This object represents a phone contact.
    :param phone_number: (str) Contact's phone number
    :param first_name: (str) Contact's first name
    :param last_name: (str) Optional. Contact's last name
    :param user_id: (int) Optional. Contact's user identifier in Telegram
    """

    def __init__(self, phone_number: str,
                 first_name: str,
                 last_name: str = None,
                 user_id: int = None):
        super().__init__()

        self.phone_number = phone_number
        self.first_name = first_name
        self.last_name = last_name
        self.user_id = user_id


class Location(TelegramObjectBase):
    """
    This object represents a point on the map.
    :param longitude: (float) Longitude as defined by sender
    :param latitude: (float) Latitude as defined by sender
    """

    def __init__(self, longitude: float,
                 latitude: float):
        super().__init__()

        self.longitude = longitude
        self.latitude = latitude


class Venue(TelegramObjectBase):
    """
    This object represents a venue.
    :param location: (Location) Venue location
    :param title: (str) Name of the venue
    :param address: (str) Address of the venue
    :param foursquare_id: (str) Optional. Foursquare identifier of the venue
    """

    def __init__(self, location: 'Location',
                 title: str,
                 address: str,
                 foursquare_id: str = None):
        super().__init__()

        self.location = location
        self.title = title
        self.address = address
        self.foursquare_id = foursquare_id


class UserProfilePhotos(TelegramObjectBase):
    """
    This object represent a user's profile pictures.
    :param total_count: (int) Total number of profile pictures the target user has
    :param photos: ('Array of Array of PhotoSize') Requested profile pictures (in up to 4 sizes each)
    """

    def __init__(self, total_count: int,
                 photos: Sequence[Sequence['PhotoSize']]):
        super().__init__()

        self.total_count = total_count
        self.photos = photos


class File(TelegramObjectBase):
    """
    This object represents a file ready to be downloaded. The file can be downloaded via the link
    https://api.telegram.org/file/bot<token>/<file_path>. It is guaranteed that the link will be valid for at least
    1 hour. When the link expires, a new one can be requested by calling getFile.
    :param file_id: (str) Unique identifier for this file
    :param file_size: (int) Optional. File size, if known
    :param file_path: (str) Optional. File path. Use https://api.telegram.org/file/bot<token>/<file_path> to get the
    file.
    """

    def __init__(self, file_id: str,
                 file_size: int = None,
                 file_path: str = None):
        super().__init__()

        self.file_id = file_id
        self.file_size = file_size
        self.file_path = file_path


class ReplyKeyboardMarkup(TelegramObjectBase):
    """
    This object represents a custom keyboard with reply options (see Introduction to bots for details and examples).
    :param keyboard: ('Array of Array of KeyboardButton') Array of button rows, each represented by an Array of
    KeyboardButton objects
    :param resize_keyboard: (bool) Optional. Requests clients to resize the keyboard vertically for optimal fit
    (e.g., make the keyboard smaller if there are just two rows of buttons). Defaults to false, in which case the custom
    keyboard is always of the same height as the app's standard keyboard.
    :param one_time_keyboard: (bool) Optional. Requests clients to hide the keyboard as soon as it's been used. The
    keyboard will still be available, but clients will automatically display the usual letter-keyboard in the chat – the
    user can press a special button in the input field to see the custom keyboard again. Defaults to false.
    :param selective: (bool) Optional. Use this parameter if you want to show the keyboard to specific users only.
    Targets: 1) users that are @mentioned in the text of the Message object; 2) if the bot's message is a reply
    (has reply_to_message_id), sender of the original message.
    """

    def __init__(self, keyboard: Sequence[Sequence['KeyboardButton']],
                 resize_keyboard: bool = None,
                 one_time_keyboard: bool = None,
                 selective: bool = None):
        super().__init__()

        self.keyboard = keyboard
        self.resize_keyboard = resize_keyboard
        self.one_time_keyboard = one_time_keyboard
        self.selective = selective


class KeyboardButton(TelegramObjectBase):
    """
    This object represents one button of the reply keyboard. For simple text buttons String can be used instead of this
    object to specify text of the button. Optional fields are mutually exclusive.
    :param text: (str) Text of the button. If none of the optional fields are used, it will be sent to the bot as a
    message when the button is pressed
    :param request_contact: (bool) Optional. If True, the user's phone number will be sent as a contact when the button
    is pressed. Available in private chats only
    :param request_location: (bool) Optional. If True, the user's current location will be sent when the button is
    pressed. Available in private chats only
    """

    def __init__(self, text: str,
                 request_contact: bool = None,
                 request_location: bool = None):
        super().__init__()

        self.text = text
        self.request_contact = request_contact
        self.request_location = request_location


class ReplyKeyboardRemove(TelegramObjectBase):
    """
    Upon receiving a message with this object, Telegram clients will remove the current custom keyboard and display the
    default letter-keyboard. By default, custom keyboards are displayed until a new keyboard is sent by a bot. An
    exception is made for one-time keyboards that are hidden immediately after the user presses a button (see
    ReplyKeyboardMarkup).
    :param remove_keyboard: (bool) Requests clients to remove the custom keyboard (user will not be able to summon this
    keyboard; if you want to hide the keyboard from sight but keep it accessible, use one_time_keyboard in
    ReplyKeyboardMarkup)
    :param selective: (bool) Optional. Use this parameter if you want to remove the keyboard for specific users only.
    Targets: 1) users that are @mentioned in the text of the Message object; 2) if the bot's message is a reply (has
    reply_to_message_id), sender of the original message.
    """

    def __init__(self, remove_keyboard: bool,
                 selective: bool = None):
        super().__init__()

        self.remove_keyboard = remove_keyboard
        self.selective = selective


class InlineKeyboardMarkup(TelegramObjectBase):
    """
    This object represents an inline keyboard that appears right next to the message it belongs to.
    :param inline_keyboard: ('Array of Array of InlineKeyboardButton') Array of button rows, each represented by an
    Array of InlineKeyboardButton objects
    """

    def __init__(self, inline_keyboard: Sequence[Sequence['InlineKeyboardButton']]):
        super().__init__()

        self.inline_keyboard = inline_keyboard


class InlineKeyboardButton(TelegramObjectBase):
    """
    This object represents one button of an inline keyboard. You must use exactly one of the optional fields.
    :param text: (str) Label text on the button
    :param url: (str) Optional. HTTP url to be opened when button is pressed
    :param callback_data: (str) Optional. Data to be sent in a callback query to the bot when button is pressed, 1-64
    bytes
    :param switch_inline_query: (str) Optional. If set, pressing the button will prompt the user to select one of their
    chats, open that chat and insert the bot‘s username and the specified inline query in the input field. Can be empty,
    in which case just the bot’s username will be inserted.
    :param switch_inline_query_current_chat: (str) Optional. If set, pressing the button will insert the bot‘s username
    and the specified inline query in the current chat's input field. Can be empty, in which case only the bot’s
    username will be inserted.
    :param callback_game: (CallbackGame) Optional. Description of the game that will be launched when the user presses
    the button.
    :param pay: (bool) Optional. Specify True, to send a Pay button.
    """

    def __init__(self, text: str,
                 url: str = None,
                 callback_data: str = None,
                 switch_inline_query: str = None,
                 switch_inline_query_current_chat: str = None,
                 callback_game: 'CallbackGame' = None,
                 pay: bool = None):
        super().__init__()

        self.text = text
        self.url = url
        self.callback_data = callback_data
        self.switch_inline_query = switch_inline_query
        self.switch_inline_query_current_chat = switch_inline_query_current_chat
        self.callback_game = callback_game
        self.pay = pay


class CallbackQuery(TelegramObjectBase):
    """
    This object represents an incoming callback query from a callback button in an inline keyboard. If the button that
    originated the query was attached to a message sent by the bot, the field message will be present. If the button was
    attached to a message sent via the bot (in inline mode), the field inline_message_id will be present. Exactly one of
    the fields data or game_short_name will be present.
    :param id: (str) Unique identifier for this query
    :param from_: (User) Sender
    :param message: (Message) Optional. Message with the callback button that originated the query. Note that message
    content and message date will not be available if the message is too old
    :param inline_message_id: (str) Optional. Identifier of the message sent via the bot in inline mode, that originated
    the query.
    :param chat_instance: (str) Global identifier, uniquely corresponding to the chat to which the message with the
    callback button was sent. Useful for high scores in games.
    :param data: (str) Optional. Data associated with the callback button. Be aware that a bad client can send arbitrary
    data in this field.
    :param game_short_name: (str) Optional. Short name of a Game to be returned, serves as the unique identifier for the
    game
    """

    def __init__(self, id: str,
                 from_: 'User',
                 chat_instance: str,
                 message: 'Message' = None,
                 inline_message_id: str = None,
                 data: str = None,
                 game_short_name: str = None):
        super().__init__()

        self.id = id
        self.from_ = from_
        self.message = message
        self.inline_message_id = inline_message_id
        self.chat_instance = chat_instance
        self.data = data
        self.game_short_name = game_short_name


class ForceReply(TelegramObjectBase):
    """
    Upon receiving a message with this object, Telegram clients will display a reply interface to the user (act as if
    the user has selected the bot‘s message and tapped ’Reply'). This can be extremely useful if you want to create
    user-friendly step-by-step interfaces without having to sacrifice privacy mode.
    :param force_reply: (bool) Shows reply interface to the user, as if they manually selected the bot‘s message and
    tapped ’Reply'
    :param selective: (bool) Optional. Use this parameter if you want to force reply from specific users only. Targets:
    1) users that are @mentioned in the text of the Message object; 2) if the bot's message is a reply (has
    reply_to_message_id), sender of the original message.
    """

    def __init__(self, force_reply: bool,
                 selective: bool = None):
        super().__init__()

        self.force_reply = force_reply
        self.selective = selective


class ChatPhoto(TelegramObjectBase):
    """
    This object represents a chat photo.
    :param small_file_id: (str) Unique file identifier of small (160x160) chat photo. This file_id can be used only for
    photo download.
    :param big_file_id: (str) Unique file identifier of big (640x640) chat photo. This file_id can be used only for
    photo download.
    """

    def __init__(self, small_file_id: str,
                 big_file_id: str):
        super().__init__()

        self.small_file_id = small_file_id
        self.big_file_id = big_file_id


class ChatMember(TelegramObjectBase):
    """
    This object contains information about one member of a chat.
    :param user: (User) Information about the user
    :param status: (str) The member's status in the chat. Can be “creator”, “administrator”, “member”, “restricted”,
    “left” or “kicked”
    :param until_date: (int) Optional. Restictred and kicked only. Date when restrictions will be lifted for this user,
    unix time
    :param can_be_edited: (bool) Optional. Administrators only. True, if the bot is allowed to edit administrator
    privileges of that user
    :param can_change_info: (bool) Optional. Administrators only. True, if the administrator can change the chat title,
    photo and other settings
    :param can_post_messages: (bool) Optional. Administrators only. True, if the administrator can post in the channel,
    channels only
    :param can_edit_messages: (bool) Optional. Administrators only. True, if the administrator can edit messages of
    other users, channels only
    :param can_delete_messages: (bool) Optional. Administrators only. True, if the administrator can delete messages of
    other users
    :param can_invite_users: (bool) Optional. Administrators only. True, if the administrator can invite new users to
    the chat
    :param can_restrict_members: (bool) Optional. Administrators only. True, if the administrator can restrict, ban or
    unban chat members
    :param can_pin_messages: (bool) Optional. Administrators only. True, if the administrator can pin messages,
    supergroups only
    :param can_promote_members: (bool) Optional. Administrators only. True, if the administrator can add new
    administrators with a subset of his own privileges or demote administrators that he has promoted, directly or
    indirectly (promoted by administrators that were appointed by the user)
    :param can_send_messages: (bool) Optional. Restricted only. True, if the user can send text messages, contacts,
    locations and venues
    :param can_send_media_messages: (bool) Optional. Restricted only. True, if the user can send audios, documents,
    photos, videos, video notes and voice notes, implies can_send_messages
    :param can_send_other_messages: (bool) Optional. Restricted only. True, if the user can send animations, games,
    stickers and use inline bots, implies can_send_media_messages
    :param can_add_web_page_previews: (bool) Optional. Restricted only. True, if user may add web page previews to his
    messages, implies can_send_media_messages
    """

    def __init__(self, user: User,
                 status: str,
                 until_date: int = None,
                 can_be_edited: bool = None,
                 can_change_info: bool = None,
                 can_post_messages: bool = None,
                 can_edit_messages: bool = None,
                 can_delete_messages: bool = None,
                 can_invite_users: bool = None,
                 can_restrict_members: bool = None,
                 can_pin_messages: bool = None,
                 can_promote_members: bool = None,
                 can_send_messages: bool = None,
                 can_send_media_messages: bool = None,
                 can_send_other_messages: bool = None,
                 can_add_web_page_previews: bool = None):
        super().__init__()

        self.user = user
        self.status = status
        self.until_date = until_date
        self.can_be_edited = can_be_edited
        self.can_change_info = can_change_info
        self.can_post_messages = can_post_messages
        self.can_edit_messages = can_edit_messages
        self.can_delete_messages = can_delete_messages
        self.can_invite_users = can_invite_users
        self.can_restrict_members = can_restrict_members
        self.can_pin_messages = can_pin_messages
        self.can_promote_members = can_promote_members
        self.can_send_messages = can_send_messages
        self.can_send_media_messages = can_send_media_messages
        self.can_send_other_messages = can_send_other_messages
        self.can_add_web_page_previews = can_add_web_page_previews


class ResponseParameters(TelegramObjectBase):
    """
    Contains information about why a request was unsuccessful.
    :param migrate_to_chat_id: (int) Optional. The group has been migrated to a supergroup with the specified
    identifier. This number may be greater than 32 bits and some programming languages may have difficulty/silent
    defects in interpreting it. But it is smaller than 52 bits, so a signed 64 bit integer or double-precision float
    type are safe for storing this identifier.
    :param retry_after: (int) Optional. In case of exceeding flood control, the number of seconds left to wait before
    the request can be repeated
    """

    def __init__(self, migrate_to_chat_id: int,
                 retry_after: int = None):
        super().__init__()

        self.migrate_to_chat_id = migrate_to_chat_id
        self.retry_after = retry_after


class InputMedia(TelegramObjectBase):
    """
    This object represents the content of a media message to be sent. It must be one of

    - InputMediaPhoto
    - InputMediaVideo
    """

    def __init__(self):
        if self.__class__ == InputMedia:
            raise NotImplemented("Use subclasses: InputMediaPhoto, InputMediaVideo")

        super().__init__()


class InputMediaPhoto(InputMedia):
    """
    Represents a photo to be sent.
    :param type: (str) Type of the result, must be photo
    :param media: (str) File to send. Pass a file_id to send a file that exists on the Telegram servers (recommended),
    pass an HTTP URL for Telegram to get a file from the Internet, or pass "attach://<file_attach_name>" to upload a new
    one using multipart/form-data under <file_attach_name> name.
    :param caption: (str) Optional. Caption of the photo to be sent, 0-200 characters
    :param parse_mode: (bool) Optional. Send Markdown or HTML, if you want Telegram apps to show bold, italic,
    fixed-width text or inline URLs in the media caption.
    """

    def __init__(self, type: str,
                 media: str,
                 caption: str = None,
                 parse_mode: bool = None):
        super().__init__()
        self.type = type
        self.media = media
        self.caption = caption
        self.parse_mode = parse_mode


class InputMediaVideo(InputMedia):
    """
    Represents a photo to be sent.
    :param type: (str) Type of the result, must be video
    :param media: (str) File to send. Pass a file_id to send a file that exists on the Telegram servers (recommended),
    pass an HTTP URL for Telegram to get a file from the Internet, or pass "attach://<file_attach_name>" to upload a new
    one using multipart/form-data under <file_attach_name> name.
    :param caption: (str) Optional. Caption of the photo to be sent, 0-200 characters
    :param parse_mode: (bool) Optional. Send Markdown or HTML, if you want Telegram apps to show bold, italic,
    fixed-width text or inline URLs in the media caption.
    :param width: (int) Optional. Video width.
    :param height: (int) Optional. Video height.
    :param duration: (int) Optional. Video duration.
    :param supports_streaming: (bool) Optional. True, if the uploaded video is suitable for streaming
    """

    def __init__(self, type: str,
                 media: str,
                 caption: str = None,
                 parse_mode: bool = None,
                 width: int = None,
                 height: int = None,
                 duration: int = None,
                 supports_streaming: bool = None):
        super().__init__()
        self.type = type
        self.media = media
        self.caption = caption
        self.parse_mode = parse_mode
        self.width = width
        self.height = height
        self.duration = duration
        self.supports_streaming = supports_streaming


class Sticker(TelegramObjectBase):
    """
    This object represents a sticker.
    :param file_id: (str) Unique identifier for this file
    :param width: (int) Sticker width
    :param height: (int) Sticker height
    :param thumb: (PhotoSize) Optional. Sticker thumbnail in the .webp or .jpg format
    :param emoji: (str) Optional. Emoji associated with the sticker
    :param set_name: (str) Optional. Name of the sticker set to which the sticker belongs
    :param mask_position: (MaskPosition) Optional. For mask stickers, the position where the mask should be placed
    :param file_size: (int) Optional. File size
    """

    def __init__(self, file_id: str,
                 width: int,
                 height: int,
                 thumb: 'PhotoSize' = None,
                 emoji: str = None,
                 set_name: str = None,
                 mask_position: 'MaskPosition' = None,
                 file_size: int = None):
        super().__init__()

        self.file_id = file_id
        self.width = width
        self.height = height
        self.thumb = thumb
        self.emoji = emoji
        self.set_name = set_name
        self.mask_position = mask_position
        self.file_size = file_size


class StickerSet(TelegramObjectBase):
    """
    This object represents a sticker set.
    :param name: (str) Sticker set name
    :param title: (str) Sticker set title
    :param contains_masks: (bool) True, if the sticker set contains masks
    :param stickers: ('Array of Sticker') List of all set stickers
    """

    def __init__(self, name: str,
                 title: str,
                 contains_masks: bool,
                 stickers: Sequence['Sticker']):
        super().__init__()

        self.name = name
        self.title = title
        self.contains_masks = contains_masks
        self.stickers = stickers


class MaskPosition(TelegramObjectBase):
    """
    This object describes the position on faces where a mask should be placed by default.
    :param point: (str) The part of the face relative to which the mask should be placed. One of “forehead”, “eyes”,
    “mouth”, or “chin”.
    :param x_shift: (float) Shift by X-axis measured in widths of the mask scaled to the face size, from left to right.
    For example, choosing -1.0 will place mask just to the left of the default mask position.
    :param y_shift: (float) Shift by Y-axis measured in heights of the mask scaled to the face size, from top to bottom.
    For example, 1.0 will place the mask just below the default mask position.
    """

    def __init__(self, point: str,
                 x_shift: float,
                 y_shift: float):
        super().__init__()

        self.point = point
        self.x_shift = x_shift
        self.y_shift = y_shift


class InlineQuery(TelegramObjectBase):
    """
    This object represents an incoming inline query. When the user sends an empty query, your bot could return some
    default or trending results.
    :param id: (str) Unique identifier for this query
    :param from_: (User) Sender
    :param location: (Location) Optional. Sender location, only for bots that request user location
    :param query: (str) Text of the query (up to 512 characters)
    :param offset: (str) Offset of the results to be returned, can be controlled by the bot
    """

    def __init__(self, id: str,
                 from_: 'User',
                 query: str,
                 offset: str,
                 location: 'Location' = None):
        super().__init__()

        self.id = id
        self.from_ = from_
        self.location = location
        self.query = query
        self.offset = offset


class InlineQueryResult(TelegramObjectBase):
    pass


class InlineQueryResultArticle(InlineQueryResult):
    """
    Represents a link to an article or web page.
    :param type: (str) Type of the result, must be article
    :param id: (str) Unique identifier for this result, 1-64 Bytes
    :param title: (str) Title of the result
    :param input_message_content: (InputMessageContent) Content of the message to be sent
    :param reply_markup: (InlineKeyboardMarkup) Optional. Inline keyboard attached to the message
    :param url: (str) Optional. URL of the result
    :param hide_url: (bool) Optional. Pass True, if you don't want the URL to be shown in the message
    :param description: (str) Optional. Short description of the result
    :param thumb_url: (str) Optional. Url of the thumbnail for the result
    :param thumb_width: (int) Optional. Thumbnail width
    :param thumb_height: (int) Optional. Thumbnail height
    """

    def __init__(self, type: str,
                 id: str,
                 title: str,
                 input_message_content: 'InputMessageContent',
                 reply_markup: 'InlineKeyboardMarkup' = None,
                 url: str = None,
                 hide_url: bool = None,
                 description: str = None,
                 thumb_url: str = None,
                 thumb_width: int = None,
                 thumb_height: int = None):
        super().__init__()

        self.type = type
        self.id = id
        self.title = title
        self.input_message_content = input_message_content
        self.reply_markup = reply_markup
        self.url = url
        self.hide_url = hide_url
        self.description = description
        self.thumb_url = thumb_url
        self.thumb_width = thumb_width
        self.thumb_height = thumb_height


class InlineQueryResultPhoto(InlineQueryResult):
    """
    Represents a link to a photo. By default, this photo will be sent by the user with optional caption. Alternatively,
    you can use input_message_content to send a message with the specified content instead of the photo.
    :param type: (str) Type of the result, must be photo
    :param id: (str) Unique identifier for this result, 1-64 bytes
    :param photo_url: (str) A valid URL of the photo. Photo must be in jpeg format. Photo size must not exceed 5MB
    :param thumb_url: (str) URL of the thumbnail for the photo
    :param photo_width: (int) Optional. Width of the photo
    :param photo_height: (int) Optional. Height of the photo
    :param title: (str) Optional. Title for the result
    :param description: (str) Optional. Short description of the result
    :param caption: (str) Optional. Caption of the photo to be sent, 0-200 characters
    :param reply_markup: (InlineKeyboardMarkup) Optional. Inline keyboard attached to the message
    :param input_message_content: (InputMessageContent) Optional. Content of the message to be sent instead of the photo
    """

    def __init__(self, type: str,
                 id: str,
                 photo_url: str,
                 thumb_url: str,
                 photo_width: int = None,
                 photo_height: int = None,
                 title: str = None,
                 description: str = None,
                 caption: str = None,
                 reply_markup: 'InlineKeyboardMarkup' = None,
                 input_message_content: 'InputMessageContent' = None):
        super().__init__()

        self.type = type
        self.id = id
        self.photo_url = photo_url
        self.thumb_url = thumb_url
        self.photo_width = photo_width
        self.photo_height = photo_height
        self.title = title
        self.description = description
        self.caption = caption
        self.reply_markup = reply_markup
        self.input_message_content = input_message_content


class InlineQueryResultGif(InlineQueryResult):
    """
    Represents a link to an animated GIF file. By default, this animated GIF file will be sent by the user with optional
    caption. Alternatively, you can use input_message_content to send a message with the specified content instead of
    the animation.
    :param type: (str) Type of the result, must be gif
    :param id: (str) Unique identifier for this result, 1-64 bytes
    :param gif_url: (str) A valid URL for the GIF file. File size must not exceed 1MB
    :param gif_width: (int) Optional. Width of the GIF
    :param gif_height: (int) Optional. Height of the GIF
    :param gif_duration: (int) Optional. Duration of the GIF
    :param thumb_url: (str) URL of the static thumbnail for the result (jpeg or gif)
    :param title: (str) Optional. Title for the result
    :param caption: (str) Optional. Caption of the GIF file to be sent, 0-200 characters
    :param reply_markup: (InlineKeyboardMarkup) Optional. Inline keyboard attached to the message
    :param input_message_content: (InputMessageContent) Optional. Content of the message to be sent instead of the GIF
    animation
    """

    def __init__(self, type: str,
                 id: str,
                 gif_url: str,
                 thumb_url: str,
                 gif_width: int = None,
                 gif_height: int = None,
                 gif_duration: int = None,
                 title: str = None,
                 caption: str = None,
                 reply_markup: 'InlineKeyboardMarkup' = None,
                 input_message_content: 'InputMessageContent' = None):
        super().__init__()

        self.type = type
        self.id = id
        self.gif_url = gif_url
        self.gif_width = gif_width
        self.gif_height = gif_height
        self.gif_duration = gif_duration
        self.thumb_url = thumb_url
        self.title = title
        self.caption = caption
        self.reply_markup = reply_markup
        self.input_message_content = input_message_content


class InlineQueryResultMpeg4Gif(InlineQueryResult):
    """
    Represents a link to a video animation (H.264/MPEG-4 AVC video without sound). By default, this animated MPEG-4 file
    will be sent by the user with optional caption. Alternatively, you can use input_message_content to send a message
    with the specified content instead of the animation.
    :param type: (str) Type of the result, must be mpeg4_gif
    :param id: (str) Unique identifier for this result, 1-64 bytes
    :param mpeg4_url: (str) A valid URL for the MP4 file. File size must not exceed 1MB
    :param mpeg4_width: (int) Optional. Video width
    :param mpeg4_height: (int) Optional. Video height
    :param mpeg4_duration: (int) Optional. Video duration
    :param thumb_url: (str) URL of the static thumbnail (jpeg or gif) for the result
    :param title: (str) Optional. Title for the result
    :param caption: (str) Optional. Caption of the MPEG-4 file to be sent, 0-200 characters
    :param reply_markup: (InlineKeyboardMarkup) Optional. Inline keyboard attached to the message
    :param input_message_content: (InputMessageContent) Optional. Content of the message to be sent instead of the
    video animation
    """

    def __init__(self, type: str,
                 id: str,
                 mpeg4_url: str,
                 thumb_url: str,
                 mpeg4_width: int = None,
                 mpeg4_height: int = None,
                 mpeg4_duration: int = None,
                 title: str = None,
                 caption: str = None,
                 reply_markup: 'InlineKeyboardMarkup' = None,
                 input_message_content: 'InputMessageContent' = None):
        super().__init__()

        self.type = type
        self.id = id
        self.mpeg4_url = mpeg4_url
        self.mpeg4_width = mpeg4_width
        self.mpeg4_height = mpeg4_height
        self.mpeg4_duration = mpeg4_duration
        self.thumb_url = thumb_url
        self.title = title
        self.caption = caption
        self.reply_markup = reply_markup
        self.input_message_content = input_message_content


class InlineQueryResultVideo(InlineQueryResult):
    """
    Represents a link to a page containing an embedded video player or a video file. By default, this video file will be
    sent by the user with an optional caption. Alternatively, you can use input_message_content to send a message with
    the specified content instead of the video.
    :param type: (str) Type of the result, must be video
    :param id: (str) Unique identifier for this result, 1-64 bytes
    :param video_url: (str) A valid URL for the embedded video player or video file
    :param mime_type: (str) Mime type of the content of video url, “text/html” or “video/mp4”
    :param thumb_url: (str) URL of the thumbnail (jpeg only) for the video
    :param title: (str) Title for the result
    :param caption: (str) Optional. Caption of the video to be sent, 0-200 characters
    :param video_width: (int) Optional. Video width
    :param video_height: (int) Optional. Video height
    :param video_duration: (int) Optional. Video duration in seconds
    :param description: (str) Optional. Short description of the result
    :param reply_markup: (InlineKeyboardMarkup) Optional. Inline keyboard attached to the message
    :param input_message_content: (InputMessageContent) Optional. Content of the message to be sent instead of the
    video. This field is required InlineQueryResult InlineQueryResultVideo is used to send an HTML-page as a result
    (e.g., a YouTube video).
    """

    def __init__(self, type: str,
                 id: str,
                 video_url: str,
                 mime_type: str,
                 thumb_url: str,
                 title: str,
                 caption: str = None,
                 video_width: int = None,
                 video_height: int = None,
                 video_duration: int = None,
                 description: str = None,
                 reply_markup: 'InlineKeyboardMarkup' = None,
                 input_message_content: 'InputMessageContent' = None):
        super().__init__()

        self.type = type
        self.id = id
        self.video_url = video_url
        self.mime_type = mime_type
        self.thumb_url = thumb_url
        self.title = title
        self.caption = caption
        self.video_width = video_width
        self.video_height = video_height
        self.video_duration = video_duration
        self.description = description
        self.reply_markup = reply_markup
        self.input_message_content = input_message_content


class InlineQueryResultAudio(InlineQueryResult):
    """
    Represents a link to an mp3 audio file. By default, this audio file will be sent by the user. Alternatively, you can
    use input_message_content to send a message with the specified content instead of the audio.
    :param type: (str) Type of the result, must be audio
    :param id: (str) Unique identifier for this result, 1-64 bytes
    :param audio_url: (str) A valid URL for the audio file
    :param title: (str) Title
    :param caption: (str) Optional. Caption, 0-200 characters
    :param performer: (str) Optional. Performer
    :param audio_duration: (int) Optional. Audio duration in seconds
    :param reply_markup: (InlineKeyboardMarkup) Optional. Inline keyboard attached to the message
    :param input_message_content: (InputMessageContent) Optional. Content of the message to be sent instead of the audio
    """

    def __init__(self, type: str,
                 id: str,
                 audio_url: str,
                 title: str,
                 caption: str = None,
                 performer: str = None,
                 audio_duration: int = None,
                 reply_markup: 'InlineKeyboardMarkup' = None,
                 input_message_content: 'InputMessageContent' = None):
        super().__init__()

        self.type = type
        self.id = id
        self.audio_url = audio_url
        self.title = title
        self.caption = caption
        self.performer = performer
        self.audio_duration = audio_duration
        self.reply_markup = reply_markup
        self.input_message_content = input_message_content


class InlineQueryResultVoice(InlineQueryResult):
    """
    Represents a link to a voice recording in an .ogg container encoded with OPUS. By default, this voice recording will
    be sent by the user. Alternatively, you can use input_message_content to send a message with the specified content
    instead of the the voice message.
    :param type: (str) Type of the result, must be voice
    :param id: (str) Unique identifier for this result, 1-64 bytes
    :param voice_url: (str) A valid URL for the voice recording
    :param title: (str) Recording title
    :param caption: (str) Optional. Caption, 0-200 characters
    :param voice_duration: (int) Optional. Recording duration in seconds
    :param reply_markup: (InlineKeyboardMarkup) Optional. Inline keyboard attached to the message
    :param input_message_content: (InputMessageContent) Optional. Content of the message to be sent instead of the
    voice recording
    """

    def __init__(self, type: str,
                 id: str,
                 voice_url: str,
                 title: str,
                 caption: str = None,
                 voice_duration: int = None,
                 reply_markup: 'InlineKeyboardMarkup' = None,
                 input_message_content: 'InputMessageContent' = None):
        super().__init__()

        self.type = type
        self.id = id
        self.voice_url = voice_url
        self.title = title
        self.caption = caption
        self.voice_duration = voice_duration
        self.reply_markup = reply_markup
        self.input_message_content = input_message_content


class InlineQueryResultDocument(InlineQueryResult):
    """
    Represents a link to a file. By default, this file will be sent by the user with an optional caption. Alternatively,
    you can use input_message_content to send a message with the specified content instead of the file. Currently, only
    .PDF and .ZIP files can be sent using this method.
    :param type: (str) Type of the result, must be document
    :param id: (str) Unique identifier for this result, 1-64 bytes
    :param title: (str) Title for the result
    :param caption: (str) Optional. Caption of the document to be sent, 0-200 characters
    :param document_url: (str) A valid URL for the file
    :param mime_type: (str) Mime type of the content of the file, either “application/pdf” or “application/zip”
    :param description: (str) Optional. Short description of the result
    :param reply_markup: (InlineKeyboardMarkup) Optional. Inline keyboard attached to the message
    :param input_message_content: (InputMessageContent) Optional. Content of the message to be sent instead of the file
    :param thumb_url: (str) Optional. URL of the thumbnail (jpeg only) for the file
    :param thumb_width: (int) Optional. Thumbnail width
    :param thumb_height: (int) Optional. Thumbnail height
    """

    def __init__(self, type: str,
                 id: str,
                 title: str,
                 document_url: str,
                 mime_type: str,
                 caption: str = None,
                 description: str = None,
                 reply_markup: 'InlineKeyboardMarkup' = None,
                 input_message_content: 'InputMessageContent' = None,
                 thumb_url: str = None,
                 thumb_width: int = None,
                 thumb_height: int = None):
        super().__init__()

        self.type = type
        self.id = id
        self.title = title
        self.caption = caption
        self.document_url = document_url
        self.mime_type = mime_type
        self.description = description
        self.reply_markup = reply_markup
        self.input_message_content = input_message_content
        self.thumb_url = thumb_url
        self.thumb_width = thumb_width
        self.thumb_height = thumb_height


class InlineQueryResultLocation(InlineQueryResult):
    """
    Represents a location on a map. By default, the location will be sent by the user. Alternatively, you can use
    input_message_content to send a message with the specified content instead of the location.
    :param type: (str) Type of the result, must be location
    :param id: (str) Unique identifier for this result, 1-64 Bytes
    :param latitude: (float) Location latitude in degrees
    :param longitude: (float) Location longitude in degrees
    :param title: (str) Location title
    :param live_period: (int) Optional. Period in seconds for which the location can be updated, should be between 60
    and 86400.
    :param reply_markup: (InlineKeyboardMarkup) Optional. Inline keyboard attached to the message
    :param input_message_content: (InputMessageContent) Optional. Content of the message to be sent instead of the
    location
    :param thumb_url: (str) Optional. Url of the thumbnail for the result
    :param thumb_width: (int) Optional. Thumbnail width
    :param thumb_height: (int) Optional. Thumbnail height
    """

    def __init__(self, type: str,
                 id: str,
                 latitude: float,
                 longitude: float,
                 title: str,
                 live_period: int = None,
                 reply_markup: 'InlineKeyboardMarkup' = None,
                 input_message_content: 'InputMessageContent' = None,
                 thumb_url: str = None,
                 thumb_width: int = None,
                 thumb_height: int = None):
        super().__init__()

        self.type = type
        self.id = id
        self.latitude = latitude
        self.longitude = longitude
        self.title = title
        self.live_period = live_period
        self.reply_markup = reply_markup
        self.input_message_content = input_message_content
        self.thumb_url = thumb_url
        self.thumb_width = thumb_width
        self.thumb_height = thumb_height


class InlineQueryResultVenue(InlineQueryResult):
    """
    Represents a venue. By default, the venue will be sent by the user. Alternatively, you can use input_message_content
    to send a message with the specified content instead of the venue.
    :param type: (str) Type of the result, must be venue
    :param id: (str) Unique identifier for this result, 1-64 Bytes
    :param latitude: (float) Latitude of the venue location in degrees
    :param longitude: (float) Longitude of the venue location in degrees
    :param title: (str) Title of the venue
    :param address: (str) Address of the venue
    :param foursquare_id: (str) Optional. Foursquare identifier of the venue if known
    :param reply_markup: (InlineKeyboardMarkup) Optional. Inline keyboard attached to the message
    :param input_message_content: (InputMessageContent) Optional. Content of the message to be sent instead of the venue
    :param thumb_url: (str) Optional. Url of the thumbnail for the result
    :param thumb_width: (int) Optional. Thumbnail width
    :param thumb_height: (int) Optional. Thumbnail height
    """

    def __init__(self, type: str,
                 id: str,
                 latitude: float,
                 longitude: float,
                 title: str,
                 address: str,
                 foursquare_id: str = None,
                 reply_markup: 'InlineKeyboardMarkup' = None,
                 input_message_content: 'InputMessageContent' = None,
                 thumb_url: str = None,
                 thumb_width: int = None,
                 thumb_height: int = None):
        super().__init__()

        self.type = type
        self.id = id
        self.latitude = latitude
        self.longitude = longitude
        self.title = title
        self.address = address
        self.foursquare_id = foursquare_id
        self.reply_markup = reply_markup
        self.input_message_content = input_message_content
        self.thumb_url = thumb_url
        self.thumb_width = thumb_width
        self.thumb_height = thumb_height


class InlineQueryResultContact(InlineQueryResult):
    """
    Represents a contact with a phone number. By default, this contact will be sent by the user. Alternatively, you can
    use input_message_content to send a message with the specified content instead of the contact.
    :param type: (str) Type of the result, must be contact
    :param id: (str) Unique identifier for this result, 1-64 Bytes
    :param phone_number: (str) Contact's phone number
    :param first_name: (str) Contact's first name
    :param last_name: (str) Optional. Contact's last name
    :param reply_markup: (InlineKeyboardMarkup) Optional. Inline keyboard attached to the message
    :param input_message_content: (InputMessageContent) Optional. Content of the message to be sent instead of the
    contact
    :param thumb_url: (str) Optional. Url of the thumbnail for the result
    :param thumb_width: (int) Optional. Thumbnail width
    :param thumb_height: (int) Optional. Thumbnail height
    """

    def __init__(self, type: str,
                 id: str,
                 phone_number: str,
                 first_name: str,
                 last_name: str = None,
                 reply_markup: 'InlineKeyboardMarkup' = None,
                 input_message_content: 'InputMessageContent' = None,
                 thumb_url: str = None,
                 thumb_width: int = None,
                 thumb_height: int = None):
        super().__init__()

        self.type = type
        self.id = id
        self.phone_number = phone_number
        self.first_name = first_name
        self.last_name = last_name
        self.reply_markup = reply_markup
        self.input_message_content = input_message_content
        self.thumb_url = thumb_url
        self.thumb_width = thumb_width
        self.thumb_height = thumb_height


class InlineQueryResultGame(InlineQueryResult):
    """
    Represents a Game.
    :param type: (str) Type of the result, must be game
    :param id: (str) Unique identifier for this result, 1-64 bytes
    :param game_short_name: (str) Short name of the game
    :param reply_markup: (InlineKeyboardMarkup) Optional. Inline keyboard attached to the message
    """

    def __init__(self, type: str,
                 id: str,
                 game_short_name: str,
                 reply_markup: 'InlineKeyboardMarkup' = None):
        super().__init__()

        self.type = type
        self.id = id
        self.game_short_name = game_short_name
        self.reply_markup = reply_markup


class InlineQueryResultCachedPhoto(InlineQueryResult):
    """
    Represents a link to a photo stored on the Telegram servers. By default, this photo will be sent by the user with an
    optional caption. Alternatively, you can use input_message_content to send a message with the specified content
    instead of the photo.
    :param type: (str) Type of the result, must be photo
    :param id: (str) Unique identifier for this result, 1-64 bytes
    :param photo_file_id: (str) A valid file identifier of the photo
    :param title: (str) Optional. Title for the result
    :param description: (str) Optional. Short description of the result
    :param caption: (str) Optional. Caption of the photo to be sent, 0-200 characters
    :param reply_markup: (InlineKeyboardMarkup) Optional. Inline keyboard attached to the message
    :param input_message_content: (InputMessageContent) Optional. Content of the message to be sent instead of the photo
    """

    def __init__(self, type: str,
                 id: str,
                 photo_file_id: str,
                 title: str = None,
                 description: str = None,
                 caption: str = None,
                 reply_markup: 'InlineKeyboardMarkup' = None,
                 input_message_content: 'InputMessageContent' = None):
        super().__init__()

        self.type = type
        self.id = id
        self.photo_file_id = photo_file_id
        self.title = title
        self.description = description
        self.caption = caption
        self.reply_markup = reply_markup
        self.input_message_content = input_message_content


class InlineQueryResultCachedGif(InlineQueryResult):
    """
    Represents a link to an animated GIF file stored on the Telegram servers. By default, this animated GIF file will be
    sent by the user with an optional caption. Alternatively, you can use input_message_content to send a message with
    specified content instead of the animation.
    :param type: (str) Type of the result, must be gif
    :param id: (str) Unique identifier for this result, 1-64 bytes
    :param gif_file_id: (str) A valid file identifier for the GIF file
    :param title: (str) Optional. Title for the result
    :param caption: (str) Optional. Caption of the GIF file to be sent, 0-200 characters
    :param reply_markup: (InlineKeyboardMarkup) Optional. Inline keyboard attached to the message
    :param input_message_content: (InputMessageContent) Optional. Content of the message to be sent instead of the GIF
    animation
    """

    def __init__(self, type: str,
                 id: str,
                 gif_file_id: str,
                 title: str = None,
                 caption: str = None,
                 reply_markup: 'InlineKeyboardMarkup' = None,
                 input_message_content: 'InputMessageContent' = None):
        super().__init__()

        self.type = type
        self.id = id
        self.gif_file_id = gif_file_id
        self.title = title
        self.caption = caption
        self.reply_markup = reply_markup
        self.input_message_content = input_message_content


class InlineQueryResultCachedMpeg4Gif(InlineQueryResult):
    """
    Represents a link to a video animation (H.264/MPEG-4 AVC video without sound) stored on the Telegram servers. By
    default, this animated MPEG-4 file will be sent by the user with an optional caption. Alternatively, you can use
    input_message_content to send a message with the specified content instead of the animation.
    :param type: (str) Type of the result, must be mpeg4_gif
    :param id: (str) Unique identifier for this result, 1-64 bytes
    :param mpeg4_file_id: (str) A valid file identifier for the MP4 file
    :param title: (str) Optional. Title for the result
    :param caption: (str) Optional. Caption of the MPEG-4 file to be sent, 0-200 characters
    :param reply_markup: (InlineKeyboardMarkup) Optional. Inline keyboard attached to the message
    :param input_message_content: (InputMessageContent) Optional. Content of the message to be sent instead of the video
    animation
    """

    def __init__(self, type: str,
                 id: str,
                 mpeg4_file_id: str,
                 title: str = None,
                 caption: str = None,
                 reply_markup: 'InlineKeyboardMarkup' = None,
                 input_message_content: 'InputMessageContent' = None):
        super().__init__()

        self.type = type
        self.id = id
        self.mpeg4_file_id = mpeg4_file_id
        self.title = title
        self.caption = caption
        self.reply_markup = reply_markup
        self.input_message_content = input_message_content


class InlineQueryResultCachedSticker(InlineQueryResult):
    """
    Represents a link to a sticker stored on the Telegram servers. By default, this sticker will be sent by the user.
    Alternatively, you can use input_message_content to send a message with the specified content instead of the
    sticker.
    :param type: (str) Type of the result, must be sticker
    :param id: (str) Unique identifier for this result, 1-64 bytes
    :param sticker_file_id: (str) A valid file identifier of the sticker
    :param reply_markup: (InlineKeyboardMarkup) Optional. Inline keyboard attached to the message
    :param input_message_content: (InputMessageContent) Optional. Content of the message to be sent instead of the
    sticker
    """

    def __init__(self, type: str,
                 id: str,
                 sticker_file_id: str,
                 reply_markup: 'InlineKeyboardMarkup' = None,
                 input_message_content: 'InputMessageContent' = None):
        super().__init__()

        self.type = type
        self.id = id
        self.sticker_file_id = sticker_file_id
        self.reply_markup = reply_markup
        self.input_message_content = input_message_content


class InlineQueryResultCachedDocument(InlineQueryResult):
    """
    Represents a link to a file stored on the Telegram servers. By default, this file will be sent by the user with an
    optional caption. Alternatively, you can use input_message_content to send a message with the specified content
    instead of the file.
    :param type: (str) Type of the result, must be document
    :param id: (str) Unique identifier for this result, 1-64 bytes
    :param title: (str) Title for the result
    :param document_file_id: (str) A valid file identifier for the file
    :param description: (str) Optional. Short description of the result
    :param caption: (str) Optional. Caption of the document to be sent, 0-200 characters
    :param reply_markup: (InlineKeyboardMarkup) Optional. Inline keyboard attached to the message
    :param input_message_content: (InputMessageContent) Optional. Content of the message to be sent instead of the file
    """

    def __init__(self, type: str,
                 id: str,
                 title: str,
                 document_file_id: str,
                 description: str = None,
                 caption: str = None,
                 reply_markup: 'InlineKeyboardMarkup' = None,
                 input_message_content: 'InputMessageContent' = None):
        super().__init__()

        self.type = type
        self.id = id
        self.title = title
        self.document_file_id = document_file_id
        self.description = description
        self.caption = caption
        self.reply_markup = reply_markup
        self.input_message_content = input_message_content


class InlineQueryResultCachedVideo(InlineQueryResult):
    """
    Represents a link to a video file stored on the Telegram servers. By default, this video file will be sent by the
    user with an optional caption. Alternatively, you can use input_message_content to send a message with the specified
    content instead of the video.
    :param type: (str) Type of the result, must be video
    :param id: (str) Unique identifier for this result, 1-64 bytes
    :param video_file_id: (str) A valid file identifier for the video file
    :param title: (str) Title for the result
    :param description: (str) Optional. Short description of the result
    :param caption: (str) Optional. Caption of the video to be sent, 0-200 characters
    :param reply_markup: (InlineKeyboardMarkup) Optional. Inline keyboard attached to the message
    :param input_message_content: (InputMessageContent) Optional. Content of the message to be sent instead of the video
    """

    def __init__(self, type: str,
                 id: str,
                 video_file_id: str,
                 title: str,
                 description: str = None,
                 caption: str = None,
                 reply_markup: 'InlineKeyboardMarkup' = None,
                 input_message_content: 'InputMessageContent' = None):
        super().__init__()

        self.type = type
        self.id = id
        self.video_file_id = video_file_id
        self.title = title
        self.description = description
        self.caption = caption
        self.reply_markup = reply_markup
        self.input_message_content = input_message_content


class InlineQueryResultCachedVoice(InlineQueryResult):
    """
    Represents a link to a voice message stored on the Telegram servers. By default, this voice message will be sent
    by the user. Alternatively, you can use input_message_content to send a message with the specified content
    instead of the voice message. :param type: (str) Type of the result, must be voice :param id: (str) Unique
    identifier for this result, 1-64 bytes :param voice_file_id: (str) A valid file identifier for the voice message
    :param title: (str) Voice message title :param caption: (str) Optional. Caption, 0-200 characters :param
    reply_markup: (InlineKeyboardMarkup) Optional. Inline keyboard attached to the message :param
    input_message_content: (InputMessageContent) Optional. Content of the message to be sent instead of the voice
    message
    """

    def __init__(self, type: str,
                 id: str,
                 voice_file_id: str,
                 title: str,
                 caption: str = None,
                 reply_markup: 'InlineKeyboardMarkup' = None,
                 input_message_content: 'InputMessageContent' = None):
        super().__init__()

        self.type = type
        self.id = id
        self.voice_file_id = voice_file_id
        self.title = title
        self.caption = caption
        self.reply_markup = reply_markup
        self.input_message_content = input_message_content


class InlineQueryResultCachedAudio(InlineQueryResult):
    """
    Represents a link to an mp3 audio file stored on the Telegram servers. By default, this audio file will be sent by
    the user. Alternatively, you can use input_message_content to send a message with the specified content instead of
    the audio.
    :param type: (str) Type of the result, must be audio
    :param id: (str) Unique identifier for this result, 1-64 bytes
    :param audio_file_id: (str) A valid file identifier for the audio file
    :param caption: (str) Optional. Caption, 0-200 characters
    :param reply_markup: (InlineKeyboardMarkup) Optional. Inline keyboard attached to the message
    :param input_message_content: (InputMessageContent) Optional. Content of the message to be sent instead of the audio
    """

    def __init__(self, type: str,
                 id: str,
                 audio_file_id: str,
                 caption: str = None,
                 reply_markup: 'InlineKeyboardMarkup' = None,
                 input_message_content: 'InputMessageContent' = None):
        super().__init__()

        self.type = type
        self.id = id
        self.audio_file_id = audio_file_id
        self.caption = caption
        self.reply_markup = reply_markup
        self.input_message_content = input_message_content


class InputMessageContent(TelegramObjectBase):
    pass


class InputTextMessageContent(InputMessageContent):
    """
    Represents the content of a text message to be sent as the result of an inline query.
    :param message_text: (str) Text of the message to be sent, 1-4096 characters
    :param parse_mode: (str) Optional. Send Markdown or HTML, if you want Telegram apps to show bold, italic,
    fixed-width text or inline URLs in your bot's message.
    :param disable_web_page_preview: (bool) Optional. Disables link previews for links in the sent message
    """

    def __init__(self, message_text: str,
                 parse_mode: str = None,
                 disable_web_page_preview: bool = None):
        super().__init__()

        self.message_text = message_text
        self.parse_mode = parse_mode
        self.disable_web_page_preview = disable_web_page_preview


class InputLocationMessageContent(InputMessageContent):
    """
    Represents the content of a location message to be sent as the result of an inline query.
    :param latitude: (float) Latitude of the location in degrees
    :param longitude: (float) Longitude of the location in degrees
    :param live_period: (int) Optional. Period in seconds for which the location can be updated, should be between 60
    and 86400.
    """

    def __init__(self, latitude: float,
                 longitude: float,
                 live_period: int = None):
        super().__init__()

        self.latitude = latitude
        self.longitude = longitude
        self.live_period = live_period


class InputVenueMessageContent(InputMessageContent):
    """
    Represents the content of a venue message to be sent as the result of an inline query.
    :param latitude: (float) Latitude of the venue in degrees
    :param longitude: (float) Longitude of the venue in degrees
    :param title: (str) Name of the venue
    :param address: (str) Address of the venue
    :param foursquare_id: (str) Optional. Foursquare identifier of the venue, if known
    """

    def __init__(self, latitude: float,
                 longitude: float,
                 title: str,
                 address: str,
                 foursquare_id: str = None):
        super().__init__()

        self.latitude = latitude
        self.longitude = longitude
        self.title = title
        self.address = address
        self.foursquare_id = foursquare_id


class InputContactMessageContent(InputMessageContent):
    """
    Represents the content of a contact message to be sent as the result of an inline query.
    :param phone_number: (str) Contact's phone number
    :param first_name: (str) Contact's first name
    :param last_name: (str) Optional. Contact's last name
    """

    def __init__(self, phone_number: str,
                 first_name: str,
                 last_name: str = None):
        super().__init__()

        self.phone_number = phone_number
        self.first_name = first_name
        self.last_name = last_name


class ChosenInlineResult(TelegramObjectBase):
    """
    Represents a result of an inline query that was chosen by the user and sent to their chat partner.
    :param result_id: (str) The unique identifier for the result that was chosen
    :param from_: (User) The user that chose the result
    :param location: (Location) Optional. Sender location, only for bots that require user location
    :param inline_message_id: (str) Optional. Identifier of the sent inline message. Available only if there is an
    inline keyboard attached to the message. Will be also received in callback queries and can be used to edit the
    message.
    :param query: (str) The query that was used to obtain the result
    """

    def __init__(self, result_id: str,
                 from_: 'User',
                 query: str,
                 location: 'Location' = None,
                 inline_message_id: str = None):
        super().__init__()

        self.result_id = result_id
        self.from_ = from_
        self.location = location
        self.inline_message_id = inline_message_id
        self.query = query


class LabeledPrice(TelegramObjectBase):
    """
    This object represents a portion of the price for goods or services.
    :param label: (str) Portion label
    :param amount: (int) Price of the product in the smallest units of the currency (integer, not float/double). For
    example, for a price of US$ 1.45 pass amount = 145. See the exp parameter in currencies.json, it shows the number of
    digits past the decimal point for each currency (2 for the majority of currencies).
    """

    def __init__(self, label: str,
                 amount: int):
        super().__init__()

        self.label = label
        self.amount = amount


class Invoice(TelegramObjectBase):
    """
    This object contains basic information about an invoice.
    :param title: (str) Product name
    :param description: (str) Product description
    :param start_parameter: (str) Unique bot deep-linking parameter that can be used to generate this invoice
    :param currency: (str) Three-letter ISO 4217 currency code
    :param total_amount: (int) Total price in the smallest units of the currency (integer, not float/double). For
    example, for a price of US$ 1.45 pass amount = 145. See the exp parameter in currencies.json, it shows the number of
    digits past the decimal point for each currency (2 for the majority of currencies).
    """

    def __init__(self, title: str,
                 description: str,
                 start_parameter: str,
                 currency: str,
                 total_amount: int):
        super().__init__()

        self.title = title
        self.description = description
        self.start_parameter = start_parameter
        self.currency = currency
        self.total_amount = total_amount


class ShippingAddress(TelegramObjectBase):
    """
    This object represents a shipping address.
    :param country_code: (str) ISO 3166-1 alpha-2 country code
    :param state: (str) State, if applicable
    :param city: (str) City
    :param street_line1: (str) First line for the address
    :param street_line2: (str) Second line for the address
    :param post_code: (str) Address post code
    """

    def __init__(self, country_code: str,
                 state: str,
                 city: str,
                 street_line1: str,
                 street_line2: str,
                 post_code: str):
        super().__init__()

        self.country_code = country_code
        self.state = state
        self.city = city
        self.street_line1 = street_line1
        self.street_line2 = street_line2
        self.post_code = post_code


class OrderInfo(TelegramObjectBase):
    """
    This object represents information about an order.
    :param name: (str) Optional. User name
    :param phone_number: (str) Optional. User's phone number
    :param email: (str) Optional. User email
    :param shipping_address: (ShippingAddress) Optional. User shipping address
    """

    def __init__(self, name: str,
                 phone_number: str = None,
                 email: str = None,
                 shipping_address: 'ShippingAddress' = None):
        super().__init__()

        self.name = name
        self.phone_number = phone_number
        self.email = email
        self.shipping_address = shipping_address


class ShippingOption(TelegramObjectBase):
    """
    This object represents one shipping option.
    :param id: (str) Shipping option identifier
    :param title: (str) Option title
    :param prices: ('Array of LabeledPrice') List of price portions
    """

    def __init__(self, id: str,
                 title: str,
                 prices: Sequence['LabeledPrice']):
        super().__init__()

        self.id = id
        self.title = title
        self.prices = prices


class SuccessfulPayment(TelegramObjectBase):
    """
    This object contains basic information about a successful payment.
    :param currency: (str) Three-letter ISO 4217 currency code
    :param total_amount: (int) Total price in the smallest units of the currency (integer, not float/double). For
    example, for a price of US$ 1.45 pass amount = 145. See the exp parameter in currencies.json, it shows the number of
    digits past the decimal point for each currency (2 for the majority of currencies).
    :param invoice_payload: (str) Bot specified invoice payload
    :param shipping_option_id: (str) Optional. Identifier of the shipping option chosen by the user
    :param order_info: (OrderInfo) Optional. Order info provided by the user
    :param telegram_payment_charge_id: (str) Telegram payment identifier
    :param provider_payment_charge_id: (str) Provider payment identifier
    """

    def __init__(self, currency: str,
                 total_amount: int,
                 invoice_payload: str,
                 telegram_payment_charge_id: str,
                 provider_payment_charge_id: str,
                 shipping_option_id: str = None,
                 order_info: 'OrderInfo' = None):
        super().__init__()

        self.currency = currency
        self.total_amount = total_amount
        self.invoice_payload = invoice_payload
        self.shipping_option_id = shipping_option_id
        self.order_info = order_info
        self.telegram_payment_charge_id = telegram_payment_charge_id
        self.provider_payment_charge_id = provider_payment_charge_id


class ShippingQuery(TelegramObjectBase):
    """
    This object contains information about an incoming shipping query.
    :param id: (str) Unique query identifier
    :param from_: (User) User who sent the query
    :param invoice_payload: (str) Bot specified invoice payload
    :param shipping_address: (ShippingAddress) User specified shipping address
    """

    def __init__(self, id: str,
                 from_: User,
                 invoice_payload: str,
                 shipping_address: 'ShippingAddress'):
        super().__init__()

        self.id = id
        self.from_ = from_
        self.invoice_payload = invoice_payload
        self.shipping_address = shipping_address


class PreCheckoutQuery(TelegramObjectBase):
    """
    This object contains information about an incoming pre-checkout query.
    :param id: (str) Unique query identifier
    :param from_: (User) User who sent the query
    :param currency: (str) Three-letter ISO 4217 currency code
    :param total_amount: (int) Total price in the smallest units of the currency (integer, not float/double). For
    example, for a price of US$ 1.45 pass amount = 145. See the exp parameter in currencies.json, it shows the number of
    digits past the decimal point for each currency (2 for the majority of currencies).
    :param invoice_payload: (str) Bot specified invoice payload
    :param shipping_option_id: (str) Optional. Identifier of the shipping option chosen by the user
    :param order_info: (OrderInfo) Optional. Order info provided by the user
    """

    def __init__(self, id: str,
                 from_: User,
                 currency: str,
                 total_amount: int,
                 invoice_payload: str,
                 shipping_option_id: str = None,
                 order_info: 'OrderInfo' = None):
        super().__init__()

        self.id = id
        self.from_ = from_
        self.currency = currency
        self.total_amount = total_amount
        self.invoice_payload = invoice_payload
        self.shipping_option_id = shipping_option_id
        self.order_info = order_info


class Game(TelegramObjectBase):
    """
    This object represents a game. Use BotFather to create and edit games, their short names will act as unique
    identifiers.
    :param title: (str) Title of the game
    :param description: (str) Description of the game
    :param photo: ('Array of PhotoSize') Photo that will be displayed in the game message in chats.
    :param text: (str) Optional. Brief description of the game or high scores included in the game message. Can be
    automatically edited to include current high scores for the game when the bot calls setGameScore, or manually edited
    using editMessageText. 0-4096 characters.
    :param text_entities: ('Array of MessageEntity') Optional. Special entities that appear in text, such as usernames,
    URLs, bot commands, etc.
    :param animation: (Animation) Optional. Animation that will be displayed in the game message in chats. Upload via
    BotFather
    """

    def __init__(self, title: str,
                 description: str,
                 photo: 'Array of PhotoSize',
                 text: str = None,
                 text_entities: 'Array of MessageEntity' = None,
                 animation: 'Animation' = None):
        super().__init__()

        self.title = title
        self.description = description
        self.photo = photo
        self.text = text
        self.text_entities = text_entities
        self.animation = animation


class Animation(TelegramObjectBase):
    """
    You can provide an animation for your game so that it looks stylish in chats (check out Lumberjack for an example).
    This object represents an animation file to be displayed in the message containing a game.
    :param file_id: (str) Unique file identifier
    :param thumb: (PhotoSize) Optional. Animation thumbnail as defined by sender
    :param file_name: (str) Optional. Original animation filename as defined by sender
    :param mime_type: (str) Optional. MIME type of the file as defined by sender
    :param file_size: (int) Optional. File size
    """

    def __init__(self, file_id: str,
                 thumb: PhotoSize = None,
                 file_name: str = None,
                 mime_type: str = None,
                 file_size: int = None):
        super().__init__()

        self.file_id = file_id
        self.thumb = thumb
        self.file_name = file_name
        self.mime_type = mime_type
        self.file_size = file_size


class CallbackGame(TelegramObjectBase):
    """
    A placeholder, currently holds no information. Use BotFather to set up your game.
    """

    pass


class GameHighScore(TelegramObjectBase):
    """
    This object represents one row of the high scores table for a game.
    :param position: (int) Position in high score table for the game
    :param user: (User) User
    :param score: (int) Score
    """

    def __init__(self, position: int,
                 user: 'User',
                 score: int):
        super().__init__()

        self.position = position
        self.user = user
        self.score = score


class InputFile(object):
    """
    This object represents the contents of a file to be uploaded. Must be posted using multipart/form-data in the usual
    way that files are uploaded via the browser.
    This object is only present for type checking purposes and for use with the built-in
    requests-based method calling API. It will raise an exception if you try to encode
    it as JSON. If you're sending requests manually you need to upload files yourself.
    :param file: (BinaryIO) Your input file. It must be opened in binary mode
    :param mimetype: (str) The file's mimetype
    :param name: (str) Optional. Filename, overrides the original file name when sending the request. Useful when
    uploading from an in-memory buffer.
    """

    def __init__(self, file: BinaryIO, mimetype: str, name: str = None):
        self.file = file
        self.mime = mimetype
        self.name = name