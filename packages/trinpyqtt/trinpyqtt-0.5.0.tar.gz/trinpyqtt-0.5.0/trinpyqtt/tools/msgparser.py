import json
from .constants import *


class GenParseException(Exception):
    pass


class PayloadEmptyException(Exception):
    pass


class UnknownMsgTypeException(Exception):
    pass


class CmdPlNotListException(Exception):
    pass


class CmdEmptyException(Exception):
    pass


class CmdNotStringException(Exception):
    pass


class EvtPlNotListException(Exception):
    pass


class EvtPlEmptyException(Exception):
    pass


class SomeEventsFailedException(Exception):
    pass


class AllEventsFailedException(Exception):
    pass


class MsgPayloadNotListException(Exception):
    pass


class MsgPayloadTooShort(Exception):
    pass


class MsgPayloadTooLong(Exception):
    pass


def parse_msg(topic, msg, user_data):
    """
    :param topic:
    :param msg:
    :return:
    """
    rc = 0
    nld = {
        'type': None,
        'ts': None,
        'code': None,
        'user_data': user_data
    }
    try:
        cmd = json.loads(msg)

        if not len(cmd.keys()):
            raise PayloadEmptyException

        msg_type = list(cmd.keys())[0]
        if msg_type not in 'cdexi':
            raise UnknownMsgTypeException
        nld['type'] = msg_type

        msg_pl = cmd[msg_type]
        if not isinstance(msg_pl, list):
            raise MsgPayloadNotListException
        if len(msg_pl) < 2:
            raise MsgPayloadTooShort()
        if (msg_type == 'x' and len(msg_pl) > 4) or len(msg_pl) > 3:
            raise MsgPayloadTooLong()

        # Check the timestamp. This does not raise, and message parsing can
        # continue even if the timestamp is broken, but we need to let
        # the on-consumer know.
        ts = msg_pl.pop(0)
        if not isinstance(ts, int):
            rc = 1
        nld['ts'] = ts

        next_token = msg_pl.pop(0)

        if isinstance(next_token, str):
            nld['tct'] = next_token
            msg_arr = msg_pl.pop(0)
        elif isinstance(next_token, list):
            msg_arr = next_token
        else:
            raise GenParseException

        if msg_type == 'c':
            nld['command'] = {}
            if not isinstance(msg_arr, list):
                raise CmdPlNotListException
            if not len(msg_arr):
                raise CmdEmptyException
            cmd = msg_arr.pop(0)
            if not isinstance(cmd, str):
                raise CmdNotStringException
            nld['command'][cmd] = msg_arr

        elif msg_type == 'e':
            nld['events'] = {}
            nld['broken'] = {
                str(F_E_NOT_LIST): [],
                str(F_E_EMPTY): [],
                str(F_EC_NOT_INT): []
            }
            if not isinstance(msg_arr, list):
                raise EvtPlNotListException
            if not len(msg_arr):
                raise EvtPlEmptyException
            for event in msg_arr:
                if not isinstance(event, list):
                    nld['broken'][str(F_E_NOT_LIST)] = event
                    break
                if not len(event) or len(event) < 2 or len(event) > 3:
                    nld['broken'][str(F_E_EMPTY)] = event
                    break
                ec = event.pop(1)
                if not isinstance(ec, int):
                    nld['broken'][str(F_EC_NOT_INT)] = event
                    break
                nld['events'][ec] = event
            if not len(nld['events'].keys()):
                raise AllEventsFailedException
            if not len(msg_arr) == len(nld['events'].keys()):
                for k, v in nld['broken'].items():
                    if not len(v):
                        del nld['broken'][k]
                raise SomeEventsFailedException
            del nld['broken']

        elif msg_type == 'd':
            nld['data'] = msg_arr

    except GenParseException:
        rc = F_ERROR
    except AllEventsFailedException:
        rc = F_ALL_EVENTS_BROKEN
    except json.decoder.JSONDecodeError:
        rc = F_PL_NOT_JSON
    except EvtPlEmptyException:
        rc = F_ET_EMPTY
    except EvtPlNotListException:
        rc = F_ET_NOT_LIST
    except CmdNotStringException:
        rc = F_C_NOT_STRING
    except CmdEmptyException:
        rc = F_CTL_EMPTY
    except CmdPlNotListException:
        rc = F_CT_NOT_LIST
    except UnknownMsgTypeException:
        rc = F_MSG_TYPE
    except MsgPayloadTooLong:
        rc = F_PL_TOO_LONG
    except MsgPayloadTooShort:
        rc = F_PL_TOO_SHORT
    except MsgPayloadNotListException:
        rc = F_PL_NOT_LIST
    except PayloadEmptyException:
        rc = F_PL_EMPTY
    except SomeEventsFailedException:
        rc = P_SOME_EVENTS_BROKEN

    nld['code'] = rc
    return nld



