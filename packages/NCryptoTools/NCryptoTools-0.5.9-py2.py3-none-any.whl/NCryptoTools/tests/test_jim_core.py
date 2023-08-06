"""
Module for jim.py testing.
"""
import pytest
import unittest
import datetime

from NCryptoTools.jim.jim_constants import JIMMsgType
from NCryptoTools.jim.jim_core import JIMMessage, type_of


@pytest.mark.parametrize('test_input, expected', [
    ({'action': 'authenticate',
      'time': datetime.datetime.now().timestamp(),
      'user': {'login': 'Dreqn1te',
               'password': 'abcd1234'}
      }, JIMMsgType.CTS_AUTHENTICATE),

    ({'action': 'presence',
      'time': datetime.datetime.now().timestamp(),
      'type': 'status',
      'user': {'login': 'Dreqn1te',
               'status': 'Greetings!'}
      }, JIMMsgType.CTS_PRESENCE),

    ({'action': 'probe',
      'time': datetime.datetime.now().timestamp()}, JIMMsgType.STC_PROBE),

    ({'action': 'msg',
      'time': datetime.datetime.now().timestamp(),
      'to': 'Ivan Ivanov',
      'from': 'Andrew',
      'encoding': 'utf-8',
      'message': 'Hi!'}, JIMMsgType.CTS_PERSONAL_MSG),

    ({'action': 'msg',
      'time': datetime.datetime.now().timestamp(),
      'to': '#GeekBrains',
      'from': 'Andrew',
      'message': 'Hi!'}, JIMMsgType.CTS_CHAT_MSG),

    ({'action': 'join',
      'time': datetime.datetime.now().timestamp(),
      'login': 'Andrew',
      'room': '#StackOverflow'}, JIMMsgType.CTS_JOIN_CHAT),

    ({'action': 'leave',
      'time': datetime.datetime.now().timestamp(),
      'login': 'Andrew',
      'room': '#CodeWars'}, JIMMsgType.CTS_LEAVE_CHAT),

    ({'action': 'get_contacts',
      'time': datetime.datetime.now().timestamp()}, JIMMsgType.CTS_GET_CONTACTS),

    ({'action': 'add_contact',
      'time': datetime.datetime.now().timestamp(),
      'login': 'Ivan'}, JIMMsgType.CTS_ADD_CONTACT),

    ({'action': 'del_contact',
      'time': datetime.datetime.now().timestamp(),
      'login': 'Peter'}, JIMMsgType.CTS_DEL_CONTACT),

    ({'action': 'contacts_list',
      'login': 'Vasya'}, JIMMsgType.STC_CONTACTS_LIST),

    ({'response': '200',
      'alert': 'OK'}, JIMMsgType.STC_ALERT),

    ({'response': '404',
      'error': 'Not Found!'}, JIMMsgType.STC_ERROR),

    ({'response': '200',
      'quantity': '5'}, JIMMsgType.STC_QUANTITY),

    ({'something_wrong': 'not_action'}, JIMMsgType.UNDEFINED_TYPE)
])
def test_type_of(test_input, expected):
    assert type_of(test_input) == expected


class TestJIMMessage(unittest.TestCase):
    """
    Tests for JIMMessage class which manages JIM protocol and messages.
    """
    def setUp(self):
        self._correct_msg = JIMMessage(JIMMsgType.CTS_JOIN_CHAT, action='join',
                                       time=datetime.datetime.now().timestamp(),
                                       login='Andrew', room='#StackOverflow')

    def test_serialize(self):
        msg_bytes = self._correct_msg.serialize()
        assert isinstance(msg_bytes, bytes)

    def test_deserialize(self):
        msg_bytes = self._correct_msg.serialize()
        msg_dict = JIMMessage(JIMMsgType.UNDEFINED_TYPE, 'utf-8', msg_bytes).deserialize()
        assert isinstance(msg_dict, dict)

    def test_is_valid(self):
        msg_bytes = self._correct_msg.serialize()
        assert JIMMessage(JIMMsgType.CTS_JOIN_CHAT, 'utf-8', msg_bytes).is_valid() is True
