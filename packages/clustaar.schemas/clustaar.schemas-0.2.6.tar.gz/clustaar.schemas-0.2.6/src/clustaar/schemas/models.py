"""Model classes"""


def model(name, attr_names):
    """Generate a new class with a constructor taking attr_names as parameters.

    Args:
        name (str): class name
        attr_names (str|list): attribute names
    """
    if isinstance(attr_names, str):
        attr_names = set(attr_names.split(" "))

    def constructor(self, **kwargs):
        """Checks that kwargs are valid property names
        and then assign those properties to self.
        """
        kwarg_names = set(kwargs.keys())
        unknown_attributes = kwarg_names - attr_names
        if unknown_attributes:
            raise TypeError("Unknown properties %s for %s" % (unknown_attributes, name))

        for attr_name in attr_names:
            setattr(self, attr_name, kwargs.get(attr_name))

    return type(name, (object,), {
        "__init__": constructor
    })


# Bot actions
AskLocationAction = model("AskLocationAction", "message callback_action")
StepTarget = model("StepTarget", "step_id name")
StoryTarget = model("StoryTarget", "story_id name")
GoToAction = model("GoToAction", "target")
LegacyReplyToMessageAction = model("LegacyReplyToMessageAction", "message")
OpenURLAction = model("OpenURLAction", "url")
ShareAction = model("ShareAction", "")
SendImageAction = model("SendImageAction", "image_url")
SendTextAction = model("SendTextAction", "alternatives")
SendEmailAction = model("SendEmailAction", "content subject recipient")
WaitAction = model("WaitAction", "duration")
PauseBotAction = model("PauseBotAction", "")
CloseIntercomConversationAction = model("CloseIntercomConversationAction", "")
AssignIntercomConversationAction = model("AssignIntercomConversationAction", "assignee_id")
SendQuickRepliesAction = model("SendQuickRepliesAction", "buttons message")
QuickReply = model("QuickReply", "title action")
Button = model("Button", "title action")
Card = model("Card", "title subtitle buttons image_url url")
SendCardsAction = model("SendCardsAction", "cards")
StoreSessionValueAction = model("StoreSessionValueAction", "key value")
GoogleCustomSearchAction = model("GoogleCustomSearchAction", "query limit custom_engine_id")
CreateZendeskTicketAction = model(
    "CreateZendeskTicketAction",
    "ticket_type ticket_priority subject description assignee_id group_id tags user"
)
ZendeskUser = model("ZendeskUser", "email name phone_number")

# Webhook
Step = model("Step", "actions name id user_data")
Coordinates = model("Coordinates", "lat long")
Interlocutor = model("Interlocutor", "id location")
ConversationSession = model("ConversationSession", "values")
StepReached = model("StepReached", "step session interlocutor channel")
StepReachedResponse = model("StepReachedResponse", "actions session")
WebhookRequest = model("WebhookRequest", "event bot_id timestamp topic")
