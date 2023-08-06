"""
Module which defines constants and types needed for JIM.
"""
from enum import Enum


class HTTPCode:
    """
    A list of HTTP codes. Only needed codes are specified, so can be updated later on.
    """
    ###########################################################################
    # 2XX Success
    ###########################################################################

    # Contains data corresponding to the request. Also used as a response for
    # the successful HTTP request.
    OK = 200

    # Request has been accepted for processing
    ACCEPTED = 202

    ###########################################################################
    # 4XX Client errors
    ###########################################################################

    # Request can not be handled dua to an error (incorrect syntax, invalid size and etc.)
    BAD_REQUEST = 400

    # Authentication has failed
    UNAUTHORIZED = 401

    # The requested resource could not be found or does not exist at all
    NOT_FOUND = 404

    # Time for client to respond to the server request has elapsed
    REQUEST_TIMEOUT = 408

    ###########################################################################
    # 5XX Server errors
    ###########################################################################

    # Error code is used for the unexpected server behavior which leads to an error
    INTERNAL_SERVER_ERROR = 500


class JIMMsgKey:
    """
    A list of keys used in JIM dictionaries. Formed in alphabetical order.
    """
    ACTION = 'action'
    ALERT = 'alert'
    ENCODING = 'encoding'
    ERROR = 'error'
    FROM = 'from'
    LOGIN = 'login'
    MESSAGE = 'message'
    PASSWORD = 'password'
    QUANTITY = 'quantity'
    ROOM = 'room'
    REGISTER = 'register'
    RESPONSE = 'response'
    STATUS = 'status'
    TIME = 'time'
    TYPE = 'type'
    TO = 'to'
    USER = 'user'


class JIMMsgType(Enum):
    """
    A list of JIM message types. Used notation:
    CTS_* - client-to-server message.
    STC_* - server-to-client message.
    """
    UNDEFINED_TYPE = -1,
    CTS_AUTHENTICATE = 0,
    CTS_QUIT = 1,
    CTS_PRESENCE = 2,
    CTS_PERSONAL_MSG = 3,
    CTS_CHAT_MSG = 4,
    CTS_JOIN_CHAT = 5,
    CTS_LEAVE_CHAT = 6,
    CTS_GET_CONTACTS = 7,
    CTS_ADD_CONTACT = 8,
    CTS_DEL_CONTACT = 9,
    CLS_REGISTER = 10,
    STC_ALERT = 50,
    STC_ERROR = 51,
    STC_PROBE = 52,
    STC_QUANTITY = 53,
    STC_CONTACTS_LIST = 54
