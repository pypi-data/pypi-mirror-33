import re
from lupin import Schema, fields as f, validators as v, Mapper, bind
from .constants import *
from .models import *
from .validators import ObjectID

_OBJECT_ID_VALIDATOR = ObjectID()

#
# Targets
#
STEP_TARGET = Schema({
    "id": f.String(binding="step_id", validators=_OBJECT_ID_VALIDATOR),
    "type": f.Constant(value="step", read_only=True),
    "name": f.String(optional=True, allow_none=True)
}, name="step_target")

STORY_TARGET = Schema({
    "id": f.String(binding="story_id", validators=_OBJECT_ID_VALIDATOR),
    "type": f.Constant(value="story", read_only=True),
    "name": f.String(optional=True, allow_none=True)
}, name="story_target")

ACTIONS_BLOCK_TARGET = Schema({
    "id": f.String(binding="actions_block_id", validators=_OBJECT_ID_VALIDATOR),
    "type": f.Constant(value="actions_block", read_only=True),
    "name": f.String(optional=True, allow_none=True)
}, name="actions_block_target")


#
# Button actions
#
GO_TO_ACTION = Schema({
    "type": f.Constant(value="go_to_action", read_only=True),
    "target": f.PolymorphicObject(on="type", schemas={
        "step": STEP_TARGET,
        "story": STORY_TARGET
    })
}, name="go_to_action")

LEGACY_REPLY_TO_MESSAGE_ACTION = Schema({
    "type": f.Constant(value="legacy_reply_to_message_action", read_only=True),
    "message": f.String(validators=v.Length(min=1, max=SEND_TEXT_ACTION_MESSAGE_MAX_LENGTH))
}, name="legacy_reply_to_message_action")

OPEN_URL_ACTION = Schema({
    "type": f.Constant(value="open_url_action", read_only=True),
    "url": f.String(validators=v.Length(min=1, max=EXTERNAL_URL_MAX_LENGTH) & v.URL())
}, name="open_url_action")

SHARE_ACTION = Schema({
    "type": f.Constant(value="share_action", read_only=True)
}, name="share_action")

BUTTON_ACTIONS_SCHEMAS = {
    "go_to_action": GO_TO_ACTION,
    "legacy_reply_to_message_action": LEGACY_REPLY_TO_MESSAGE_ACTION,
    "open_url_action": OPEN_URL_ACTION,
    "share_action": SHARE_ACTION
}

#
# Bot actions
#
ASK_LOCATION_ACTION = Schema({
    "type": f.Constant(value="ask_location_action", read_only=True),
    "message": f.String(validators=v.Length(min=1, max=SEND_TEXT_ACTION_MESSAGE_MAX_LENGTH)),
    "action": f.Object(schema=GO_TO_ACTION, binding="callback_action")
}, name="ask_location_action")

SEND_IMAGE_ACTION = Schema({
    "type": f.Constant(value="send_image_action", read_only=True),
    "imageURL": f.String(binding="image_url",
                         validators=(v.Length(max=EXTERNAL_URL_MAX_LENGTH) &
                                     v.URL(schemes={"https", "http"}) |
                                     v.Equal("")))
}, name="send_image_action")

SEND_TEXT_ACTION = Schema({
    "type": f.Constant(value="send_text_action", read_only=True),
    "alternatives": f.List(f.String(validators=v.Length(min=1, max=SEND_TEXT_ACTION_MESSAGE_MAX_LENGTH)),
                           validators=v.Length(min=1, max=SEND_TEXT_ACTION_MAX_MESSAGES_COUNT))
})

SEND_EMAIL_ACTION = Schema({
    "type": f.Constant(value="send_email_action", read_only=True),
    "recipient": f.String(validators=v.Length(max=SEND_EMAIL_ACTION_RECIPIENT_MAX_LENGTH)),
    "subject": f.String(validators=v.Length(max=SEND_EMAIL_ACTION_SUBJECT_MAX_LENGTH)),
    "content": f.String(validators=v.Length(max=SEND_EMAIL_ACTION_CONTENT_MAX_LENGTH))
}, name="send_text_action")

WAIT_ACTION = Schema({
    "type": f.Constant(value="wait_action", read_only=True),
    "duration": f.Number(validators=v.Between(min=WAIT_ACTION_MIN_DURATION, max=WAIT_ACTION_MAX_DURATION),
                         default=WAIT_ACTION_DEFAULT_DURATION)
}, name="wait_action")

PAUSE_BOT_ACTION = Schema({
    "type": f.Constant(value="pause_bot_action", read_only=True)
}, name="pause_bot_action")

CLOSE_INTERCOM_CONVERSATION_ACTION = Schema({
    "type": f.Constant(value="close_intercom_conversation_action", read_only=True)
}, name="close_intercom_conversation_action")

ASSIGN_INTERCOM_CONVERSATION_ACTION = Schema({
    "type": f.Constant(value="assign_intercom_conversation_action", read_only=True),
    "assigneeID": f.String(optional=True, allow_none=True, binding="assignee_id",
                           validators=v.Length(max=ASSIGN_INTERCOM_CONVERSATION_ACTION_ASSIGNEE_ID_MAX_LENGTH))
}, name="assign_intercom_conversation_action")

QUICK_REPLY = Schema({
    "title": f.String(validators=v.Length(min=1, max=QUICK_REPLY_TITLE_MAX_LENGTH)),
    "action": f.Object(GO_TO_ACTION),
    "type": f.Constant(value="quick_reply", read_only=True, optional=True)
}, name="quick_reply")

SEND_QUICK_REPLIES_ACTION = Schema({
    "type": f.Constant(value="send_quick_replies_action", read_only=True),
    "message": f.String(validators=v.Length(min=1, max=SEND_TEXT_ACTION_MESSAGE_MAX_LENGTH)),
    "buttons": f.List(f.Object(QUICK_REPLY),
                      validators=v.Length(min=1, max=SEND_QUICK_REPLIES_ACTION_MAX_BUTTONS_COUNT))
}, name="send_quick_replies_action")

BUTTON = Schema({
    "type": f.Constant(value="button", read_only=True),
    "title": f.String(validators=v.Length(min=1, max=BUTTON_TITLE_MAX_LENGTH)),
    "action": f.PolymorphicObject(on="type", schemas=BUTTON_ACTIONS_SCHEMAS)
}, name="button")

CARD = Schema({
    "type": f.Constant(value="card", read_only=True),
    "title": f.String(validators=v.Length(min=1, max=CARD_TITLE_MAX_LENGTH)),
    "subtitle": f.String(optional=True, validators=v.Length(max=CARD_SUBTITLE_MAX_LENGTH), allow_none=True),
    "imageURL": f.String(optional=True, allow_none=True, binding="image_url", validators=(
        v.Length(max=EXTERNAL_URL_MAX_LENGTH) &
        v.URL(schemes={"http", "https"}) |
        v.Equal("")
    )),
    "url": f.String(optional=True, validators=v.Length(max=EXTERNAL_URL_MAX_LENGTH) | v.Equal(""), allow_none=True),
    "buttons": f.List(f.Object(BUTTON),
                      allow_none=True,
                      default=(),
                      optional=True,
                      validators=v.Length(max=CARD_MAX_BUTTONS_COUNT))
}, name="card")

SEND_CARDS_ACTIONS = Schema({
    "type": f.Constant(value="send_cards_action", read_only=True),
    "cards": f.List(f.Object(CARD),
                    validators=v.Length(min=1, max=SEND_CARDS_ACTION_MAX_CARDS_COUNT))
}, name="send_cards_action")

STORE_SESSION_VALUE_ACTION = Schema({
    "type": f.Constant(value="store_session_value_action", read_only=True),
    "key": f.String(validators=(
        v.Length(min=1, max=STORE_SESSION_VALUE_ACTION_KEY_MAX_LENGTH) &
        v.Match(re.compile(r"^[\w\d_]+$"))
    )),
    "value": f.String(validators=v.Length(min=1, max=STORE_SESSION_VALUE_ACTION_VALUE_MAX_LENGTH))
}, name="store_session_value_action")

GOOGLE_CUSTOM_SEARCH_ACTION = Schema({
    "type": f.Constant(value="google_custom_search_action", read_only=True),
    "query": f.String(validators=v.Length(min=1, max=GOOGLE_CUSTOM_SEARCH_ACTION_QUERY_MAX_LENGTH)),
    "customEngineID": f.String(binding="custom_engine_id", validators=v.Length(min=1)),
    "limit": f.Int(validators=v.Between(min=1, max=GOOGLE_CUSTOM_SEARCH_ACTION_MAX_LIMIT))
}, name="google_custom_search_action")

ZENDESK_USER = Schema({
    "email": f.String(optional=True, validators=v.Length(max=ZENDESK_USER_EMAIL_MAX_LENGTH)),
    "name": f.String(optional=True, validators=v.Length(max=ZENDESK_USER_NAME_MAX_LENGTH)),
    "phoneNumber": f.String(optional=True, binding="phone_number"),
}, name="zendesk_user")

CREATE_ZENDESK_TICKET_ACTION = Schema({
    "user": f.Object(ZENDESK_USER),
    "type": f.Constant(value="create_zendesk_ticket_action", read_only=True),
    "ticketType": f.String(optional=True, binding="ticket_type", validators=(v.In(ZENDESK_TICKET_TYPES) | v.Equal(""))),
    "ticketPriority": f.String(optional=True, binding="ticket_priority",
                               validators=(v.In(ZENDESK_TICKET_PRIORITIES) | v.Equal(""))),
    "subject": f.String(optional=True, validators=v.Length(max=ZENDESK_TICKET_SUBJECT_MAX_LENGTH)),
    "description": f.String(validators=v.Length(min=1, max=ZENDESK_TICKET_DESCRIPTION_MAX_LENGTH)),
    "tags": f.List(f.String(validators=v.Length(max=ZENDESK_TICKET_TAG_MAX_LENGTH)), optional=True,
                   validators=v.Length(max=ZENDESK_TICKET_TAGS_MAX_COUNT)),
    "groupID": f.String(optional=True, binding="group_id",
                        validators=[
                            v.Length(max=ZENDESK_TICKET_ASSIGNEE_ID_MAX_LENGTH),
                            v.Match(re.compile(r"^\d*$"))
                        ]),
    "assigneeID": f.String(optional=True, binding="assignee_id",
                           validators=[
                               v.Length(max=ZENDESK_TICKET_ASSIGNEE_ID_MAX_LENGTH),
                               v.Match(re.compile(r"^\d*$"))
                           ])
}, name="create_zendesk_ticket_action")


ACTION_SCHEMAS = {
    "pause_bot_action": PAUSE_BOT_ACTION,
    "wait_action": WAIT_ACTION,
    "send_email_action": SEND_EMAIL_ACTION,
    "send_text_action": SEND_TEXT_ACTION,
    "send_image_action": SEND_IMAGE_ACTION,
    "close_intercom_conversation_action": CLOSE_INTERCOM_CONVERSATION_ACTION,
    "assign_intercom_conversation_action": ASSIGN_INTERCOM_CONVERSATION_ACTION,
    "send_cards_action": SEND_CARDS_ACTIONS,
    "send_quick_replies_action": SEND_QUICK_REPLIES_ACTION,
    "store_session_value_action": STORE_SESSION_VALUE_ACTION,
    "ask_location_action": ASK_LOCATION_ACTION,
    "google_custom_search_action": GOOGLE_CUSTOM_SEARCH_ACTION,
    "create_zendesk_ticket_action": CREATE_ZENDESK_TICKET_ACTION
}

COORDINATES = Schema({
    "lat": f.Number(),
    "long": f.Number()
}, name="coordinates")

#
# Webhook
#

WEBHOOK_INTERLOCUTOR = Schema({
    "id": f.String(),
    "location": f.Object(COORDINATES, allow_none=True)
}, name="webhook_interlocutor")

WEBHOOK_CONVERSATION_SESSION = Schema({
    "values": f.Dict()
}, name="webhook_conversation_session")

WEBHOOK_STEP = Schema({
    "id": f.String(),
    "name": f.String(),
    "userData": f.String(binding="user_data"),
    "actions": f.PolymorphicList(on="type", schemas=ACTION_SCHEMAS)
}, name="webhook_step")

WEBHOOK_STEP_REACHED = Schema({
    "type": f.Constant("step_reached_event", read_only=True),
    "channel": f.String(),
    "interlocutor": f.Object(schema=WEBHOOK_INTERLOCUTOR),
    "session": f.Object(schema=WEBHOOK_CONVERSATION_SESSION),
    "step": f.Object(schema=WEBHOOK_STEP)
}, name="webhook_step_reached")

WEBHOOK_STEP_REACHED_RESPONSE = Schema({
    "actions": f.PolymorphicList(on="type", schemas=ACTION_SCHEMAS),
    "session": f.Object(schema=WEBHOOK_CONVERSATION_SESSION, optional=True, allow_none=True),
}, name="webhook_step_reached_response")

WEBHOOK_REQUEST = Schema({
    "topic": f.String(),
    "botID": f.String(binding="bot_id"),
    "timestamp": f.Int(),
    "type": f.Constant("notification_event", read_only=True),
    "data": f.PolymorphicObject(binding="event", on="type", schemas={
        "step_reached_event": WEBHOOK_STEP_REACHED
    })
}, name="webhook_request")


def get_mapper(factory=bind):
    """Load mapper v1

    Returns:
        Mapper
    """
    mapper = Mapper()
    mappings = {
        AskLocationAction: ASK_LOCATION_ACTION,
        StepTarget: STEP_TARGET,
        StoryTarget: STORY_TARGET,
        GoToAction: GO_TO_ACTION,
        LegacyReplyToMessageAction: LEGACY_REPLY_TO_MESSAGE_ACTION,
        OpenURLAction: OPEN_URL_ACTION,
        ShareAction: SHARE_ACTION,
        SendImageAction: SEND_IMAGE_ACTION,
        SendTextAction: SEND_TEXT_ACTION,
        SendEmailAction: SEND_EMAIL_ACTION,
        WaitAction: WAIT_ACTION,
        PauseBotAction: PAUSE_BOT_ACTION,
        CloseIntercomConversationAction: CLOSE_INTERCOM_CONVERSATION_ACTION,
        AssignIntercomConversationAction: ASSIGN_INTERCOM_CONVERSATION_ACTION,
        QuickReply: QUICK_REPLY,
        SendQuickRepliesAction: SEND_QUICK_REPLIES_ACTION,
        Button: BUTTON,
        Card: CARD,
        SendCardsAction: SEND_CARDS_ACTIONS,
        StoreSessionValueAction: STORE_SESSION_VALUE_ACTION,
        Step: WEBHOOK_STEP,
        Interlocutor: WEBHOOK_INTERLOCUTOR,
        ConversationSession: WEBHOOK_CONVERSATION_SESSION,
        StepReached: WEBHOOK_STEP_REACHED,
        WebhookRequest: WEBHOOK_REQUEST,
        Coordinates: COORDINATES,
        StepReachedResponse: WEBHOOK_STEP_REACHED_RESPONSE,
        GoogleCustomSearchAction: GOOGLE_CUSTOM_SEARCH_ACTION,
        CreateZendeskTicketAction: CREATE_ZENDESK_TICKET_ACTION,
        ZendeskUser: ZENDESK_USER
    }

    for cls, schema in mappings.items():
        mapper.register(cls, schema, factory=factory)

    return mapper
