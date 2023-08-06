from clustaar.schemas.v1 import ASSIGN_INTERCOM_CONVERSATION_ACTION
from clustaar.schemas.models import AssignIntercomConversationAction
import pytest


@pytest.fixture
def action():
    return AssignIntercomConversationAction(assignee_id="FJNBDDHH654789")


@pytest.fixture
def data():
    return {
        "type": "assign_intercom_conversation_action",
        "assigneeID": "FJNBDDHH654789"
    }


class TestDump(object):
    def test_returns_a_dict(self, action, data, mapper):
        result = ASSIGN_INTERCOM_CONVERSATION_ACTION.dump(action, mapper)
        assert result == data


class TestLoad(object):
    def test_returns_an_action(self, data, mapper):
        action = mapper.load(data, ASSIGN_INTERCOM_CONVERSATION_ACTION)
        assert isinstance(action, AssignIntercomConversationAction)
        assert action.assignee_id == "FJNBDDHH654789"
