"""
Core module for the JSON Instant Messaging protocol. Defines basic
methods and types needed for data transmission between client and server.
"""
import json

from NCryptoTools.jim.jim_constants import JIMMsgKey, JIMMsgType


class UnknownJIMObjectException(Exception):
    """
    Class for exceptions related to unknown JIM objects.
    """
    def __init__(self, jim_object_type):
        self._jim_object_type = jim_object_type

    def __str__(self):
        return 'Undefined type of JIM object: %s' % self._jim_object_type


class InvalidHTTPCodeException(Exception):
    """
    Class for exceptions related to incorrect values of HTTP codes.
    """
    def __init__(self, http_code):
        self._http_code = http_code

    def __str__(self):
        return 'Incorrect value of HTTP code: %s' % self._http_code


class InvalidNameException(Exception):
    """
    Class for exceptions related to incorrect names including chat room names
    and user names.
    """
    def __init__(self, chat_room_name):
        self._chat_room_name = chat_room_name

    def __str__(self):
        return 'Incorrect chat room name: %s' % self._chat_room_name


class JIMMessage:
    def __init__(self, msg_type=JIMMsgType.UNDEFINED_TYPE, msg_encoding='utf-8', *args, **kwargs):
        """
        Constructor of JIM message.
        @param msg_type: type of JIM message.
        @param msg_encoding: message encoding system. UTF-8 is being used by default.
        @param args: list of message data.
        @param kwargs: key-value pairs of message data.
        """
        self._msg_type = msg_type
        self._encoding = msg_encoding

        args_not_null = len(args) > 0
        kwargs_not_null = len(kwargs) > 0

        # One of additional arguments should not be empty
        if (args_not_null ^ kwargs_not_null) is False:
            raise RuntimeError('Error! Incorrect args (kwargs) arguments!')

        if args_not_null and isinstance(args[0], bytes):
            self._serialized = True
            self._message = args[0]
        elif kwargs_not_null and isinstance(kwargs, dict):
            self._serialized = False
            self._message = kwargs
        else:
            raise TypeError('Incorrect data type! Expected: bytes or dict. Received: args=%s, kwargs=%s' %
                            (type(args), type(kwargs)))

    def serialize(self):
        """
        Performs data serialization for the following transmission.
        @return: JSON message in bytes.
        """
        return to_bytes(self.to_dict(), self._encoding)

    def deserialize(self):
        """
        Performs data deserialization for the following reading and handling.
        @return: JSON message (dictionary).
        """
        return to_dict(self._message, self._encoding)

    def to_dict(self):
        """
        Converts message to a properly formed JSON dictionary.
        @return: JSON dictionary.
        """
        if self._msg_type == JIMMsgType.CTS_AUTHENTICATE:
            return {JIMMsgKey.ACTION: self._message['action'],
                    JIMMsgKey.TIME: self._message['time'],
                    JIMMsgKey.USER: {JIMMsgKey.LOGIN: self._message['login'],
                                     JIMMsgKey.PASSWORD: self._message['password']}
                    }

        if self._msg_type == JIMMsgType.CTS_QUIT:
            return {JIMMsgKey.ACTION: self._message['action']}

        if self._msg_type == JIMMsgType.CTS_PRESENCE:
            return {JIMMsgKey.ACTION: self._message['action'],
                    JIMMsgKey.TIME: self._message['time'],
                    JIMMsgKey.TYPE: self._message['type'],
                    JIMMsgKey.USER: {JIMMsgKey.LOGIN: self._message['login'],
                                     JIMMsgKey.PASSWORD: self._message['password']}
                    }

        if self._msg_type == JIMMsgType.STC_PROBE:
            return {JIMMsgKey.ACTION: self._message['action'],
                    JIMMsgKey.TIME: self._message['time']}

        if self._msg_type == JIMMsgType.CTS_PERSONAL_MSG:
            return {JIMMsgKey.ACTION: self._message['action'],
                    JIMMsgKey.TIME: self._message['time'],
                    JIMMsgKey.TO: self._message['to'],
                    JIMMsgKey.FROM: self._message['from'],
                    JIMMsgKey.ENCODING: self._message['encoding'],
                    JIMMsgKey.MESSAGE: self._message['message']}

        if self._msg_type == JIMMsgType.CTS_CHAT_MSG:
            return {JIMMsgKey.ACTION: self._message['action'],
                    JIMMsgKey.TIME: self._message['time'],
                    JIMMsgKey.TO: self._message['to'],
                    JIMMsgKey.FROM: self._message['from'],
                    JIMMsgKey.MESSAGE: self._message['message']}

        if self._msg_type == JIMMsgType.CTS_JOIN_CHAT:
            return {JIMMsgKey.ACTION: self._message['action'],
                    JIMMsgKey.TIME: self._message['time'],
                    JIMMsgKey.LOGIN: self._message['login'],
                    JIMMsgKey.ROOM: self._message['room']}

        if self._msg_type == JIMMsgType.CTS_LEAVE_CHAT:
            return {JIMMsgKey.ACTION: self._message['action'],
                    JIMMsgKey.TIME: self._message['time'],
                    JIMMsgKey.LOGIN: self._message['login'],
                    JIMMsgKey.ROOM: self._message['room']}

        if self._msg_type == JIMMsgType.STC_ALERT:
            return {JIMMsgKey.RESPONSE: self._message['response'],
                    JIMMsgKey.ALERT: self._message['alert']}

        if self._msg_type == JIMMsgType.STC_ERROR:
            return {JIMMsgKey.RESPONSE: self._message['response'],
                    JIMMsgKey.ERROR: self._message['error']}

        if self._msg_type == JIMMsgType.CTS_GET_CONTACTS:
            return {JIMMsgKey.ACTION: self._message['action'],
                    JIMMsgKey.TIME: self._message['time']}

        if self._msg_type == JIMMsgType.STC_QUANTITY:
            return {JIMMsgKey.RESPONSE: self._message['response'],
                    JIMMsgKey.QUANTITY: self._message['quantity']}

        if self._msg_type == JIMMsgType.STC_CONTACTS_LIST:
            return {JIMMsgKey.ACTION: self._message['action'],
                    JIMMsgKey.LOGIN: self._message['login']}

        if self._msg_type == JIMMsgType.CTS_ADD_CONTACT:
            return {JIMMsgKey.ACTION: self._message['action'],
                    JIMMsgKey.TIME: self._message['time'],
                    JIMMsgKey.LOGIN: self._message['login']}

        if self._msg_type == JIMMsgType.CTS_DEL_CONTACT:
            return {JIMMsgKey.ACTION: self._message['action'],
                    JIMMsgKey.TIME: self._message['time'],
                    JIMMsgKey.LOGIN: self._message['login']}

        raise UnknownJIMObjectException(type(self._msg_type))

    def is_valid(self):
        """
        Validates JSON message (dictionary). Made for convenience of calling
        methods in chain.
        @return: boolean result of validation.
        """
        if self._serialized:
            self._message = self.deserialize()
        return is_valid_msg(self._msg_type, self._message)


def to_dict(msg_bytes, encoding='utf-8'):
    """
    Converts bytes into JSON message (dictionary).
    @param msg_bytes: serialized JSON message (bytes).
    @param encoding: encoding system.
    @return: JSON message (dictionary).
    """
    if not isinstance(msg_bytes, bytes):
        raise TypeError('Incorrect data type! Expected: bytes. Received: %s' % type(msg_bytes))
    json_str = msg_bytes.decode(encoding)  # Converts message into JSON string
    msg_dict = json.loads(json_str)  # Converts message into dictionary
    if not isinstance(msg_dict, dict):
        raise TypeError('Incorrect data type! Expected: dict. Received: %s' % type(msg_dict))
    return msg_dict


def to_bytes(msg_dict, encoding='utf-8'):
    """
    Converts JSON message (dictionary) into bytes.
    @param msg_dict: JSON message (dictionary).
    @param encoding: encoding system.
    @return: serialized JSON message (bytes).
    """
    if not isinstance(msg_dict, dict):
        raise TypeError('Incorrect data type! Expected: dict. Received: %s' % type(msg_dict))
    json_str = json.dumps(msg_dict)  # Converts message into JSON string
    msg_bytes = json_str.encode(encoding)  # Converts message into bytes
    if not isinstance(msg_bytes, bytes):
        raise TypeError('Incorrect data type! Expected: bytes. Received: %s' % type(msg_bytes))
    return msg_bytes


def is_valid_msg(msg_type, msg_dict):
    """
    Validates JSON message (dictionary).
    @param msg_type: type of message to be checked.
    @param msg_dict: JSON message (dictionary) to validate.
    @return: boolean result of validation.
    """
    if msg_type == JIMMsgType.CTS_AUTHENTICATE:
        return {JIMMsgKey.ACTION, JIMMsgKey.TIME, JIMMsgKey.USER} <= set(msg_dict) and \
               {JIMMsgKey.LOGIN, JIMMsgKey.PASSWORD} <= set(msg_dict['user'])

    if msg_type == JIMMsgType.CTS_QUIT:
        return JIMMsgKey.ACTION in msg_dict

    if msg_type == JIMMsgType.CTS_PRESENCE:
        return {JIMMsgKey.ACTION, JIMMsgKey.TIME, JIMMsgKey.TYPE, JIMMsgKey.USER} <= set(msg_dict) and \
               {JIMMsgKey.LOGIN, JIMMsgKey.STATUS} <= set(msg_dict['user'])

    if msg_type == JIMMsgType.STC_PROBE:
        return {JIMMsgKey.ACTION, JIMMsgKey.TIME} <= set(msg_dict)

    if msg_type == JIMMsgType.CTS_PERSONAL_MSG:
        return {JIMMsgKey.ACTION, JIMMsgKey.TIME, JIMMsgKey.TO, JIMMsgKey.FROM,
                JIMMsgKey.ENCODING, JIMMsgKey.MESSAGE} <= set(msg_dict)

    if msg_type == JIMMsgType.CTS_CHAT_MSG:
        return {JIMMsgKey.ACTION, JIMMsgKey.TIME, JIMMsgKey.TO, JIMMsgKey.FROM,
                JIMMsgKey.MESSAGE} <= set(msg_dict)

    if msg_type == JIMMsgType.CTS_JOIN_CHAT:
        return {JIMMsgKey.ACTION, JIMMsgKey.TIME, JIMMsgKey.LOGIN, JIMMsgKey.ROOM} <= set(msg_dict)

    if msg_type == JIMMsgType.CTS_LEAVE_CHAT:
        return {JIMMsgKey.ACTION, JIMMsgKey.TIME, JIMMsgKey.LOGIN, JIMMsgKey.ROOM} <= set(msg_dict)

    if msg_type == JIMMsgType.STC_ALERT:
        return {JIMMsgKey.RESPONSE, JIMMsgKey.ALERT} <= set(msg_dict)

    if msg_type == JIMMsgType.STC_ERROR:
        return {JIMMsgKey.RESPONSE, JIMMsgKey.ERROR} <= set(msg_dict)

    if msg_type == JIMMsgType.CTS_GET_CONTACTS:
        return {JIMMsgKey.ACTION, JIMMsgKey.TIME} <= set(msg_dict)

    if msg_type == JIMMsgType.STC_QUANTITY:
        return {JIMMsgKey.RESPONSE, JIMMsgKey.QUANTITY} <= set(msg_dict)

    if msg_type == JIMMsgType.STC_CONTACTS_LIST:
        return {JIMMsgKey.ACTION, JIMMsgKey.LOGIN} <= set(msg_dict)

    if msg_type == JIMMsgType.CTS_ADD_CONTACT:
        return {JIMMsgKey.ACTION, JIMMsgKey.LOGIN, JIMMsgKey.TIME} <= set(msg_dict)

    if msg_type == JIMMsgType.CTS_DEL_CONTACT:
        return {JIMMsgKey.ACTION, JIMMsgKey.LOGIN, JIMMsgKey.TIME} <= set(msg_dict)

    raise UnknownJIMObjectException(msg_type)


def type_of(msg_dict):
    """
    Determines JIM message type.
    @param msg_dict: JSON message (dictionary).
    @return: type of JIM message.
    """
    if not isinstance(msg_dict, dict):
        raise TypeError('Incorrect data type! Expected: dict. Received: %s' % type(msg_dict))

    if len(msg_dict) == 0:
        raise UnknownJIMObjectException(msg_dict)

    if 'action' in msg_dict:
        action_types = {
            'authenticate': JIMMsgType.CTS_AUTHENTICATE,
            'quit': JIMMsgType.CTS_QUIT,
            'presence': JIMMsgType.CTS_PRESENCE,
            'probe': JIMMsgType.STC_PROBE,
            'msg': {'empty': JIMMsgType.CTS_CHAT_MSG,
                    'encoding': JIMMsgType.CTS_PERSONAL_MSG},
            'join': JIMMsgType.CTS_JOIN_CHAT,
            'leave': JIMMsgType.CTS_LEAVE_CHAT,
            'get_contacts': JIMMsgType.CTS_GET_CONTACTS,
            'add_contact': JIMMsgType.CTS_ADD_CONTACT,
            'del_contact': JIMMsgType.CTS_DEL_CONTACT,
            'contacts_list': JIMMsgType.STC_CONTACTS_LIST,
        }
        action_type = msg_dict['action']
        type_to_check = action_types[action_type]
        if action_type == 'msg':
            if 'encoding' in msg_dict:
                type_to_check = type_to_check['encoding']
            else:
                type_to_check = type_to_check['empty']
        if JIMMessage(type_to_check, **msg_dict).is_valid():
            return type_to_check
        raise UnknownJIMObjectException(msg_dict)

    if 'response' in msg_dict:
        if 'alert' in msg_dict and JIMMessage(JIMMsgType.STC_ALERT, **msg_dict).is_valid():
            return JIMMsgType.STC_ALERT
        if 'error' in msg_dict and JIMMessage(JIMMsgType.STC_ERROR, **msg_dict).is_valid():
            return JIMMsgType.STC_ERROR
        if 'quantity' in msg_dict and JIMMessage(JIMMsgType.STC_QUANTITY, **msg_dict).is_valid():
            return JIMMsgType.STC_QUANTITY

    return JIMMsgType.UNDEFINED_TYPE
