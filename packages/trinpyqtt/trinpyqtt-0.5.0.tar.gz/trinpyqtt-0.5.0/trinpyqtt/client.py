from threading import Timer
import os
from subprocess import call
import errno
from time import sleep
import paho.mqtt.client as mqtt
from paho.mqtt.client import MQTT_LOG_INFO
import json
import configparser
import pkg_resources
from os.path import expanduser
from trinpyqtt.tools.cryptools import get_now_timestamp, get_password, read_cid
from trinpyqtt.tools.msgparser import parse_msg
from trinpyqtt.tools.constants import (
    SUCCESS, F_EXCEPTION, F_BROKEN_TOPIC, F_UNKNOWN_PID, F_NO_RPC,
    F_DW_NOT_EXPOSED, EC_LWT, EC_CONNECT_SUCCESS, F_NOT_A_BOOLEAN)
from trinpyqtt.tools.utils import (
    get_my_ip, safe_get, convert_to_boolean, restart_program)

DELIM = ','

TRUSTED_SERVER = '000000000000000'


class MissingCidException(Exception):
    pass


class MissingModelException(Exception):
    pass


class TcTException(Exception):
    pass


class TargetHidException(Exception):
    pass


def lookup(dic, key, *keys):
    """
    Helper method to drill into the exposed settings via a list of keys
    :param dic:
    :param key:
    :param keys:
    :return:
    """
    if keys:
        return lookup(dic.get(key, {}), *keys)
    return dic.get(key)


# ------------------------------------------------------------------------------
class TrinClient(mqtt.Client):
    def __init__(self, *args, **kwargs):
        self._cid = read_cid()
        if not self._cid:
            raise MissingCidException('Could not find a valid CID. '
                                      'Try the auto-register procedure to '
                                      'fix this')

        self._model = kwargs.pop('model', None)
        if not self._model:
            raise MissingModelException

        self._cnf = '{}/.config/trinmqtt/trinmqtt.ini'.format(expanduser('~'))

        self._use_rtc = kwargs.pop('use_rtc', False)
        self._iah_interval = kwargs.pop('iah_interval', 0)
        self._given_host = kwargs.pop('host', 'mqttdev.trintel.co.za')
        self._given_port = kwargs.pop('port', 1883)
        self._given_clean_session = kwargs.pop('clean_session', True)
        self._pdr_interval = kwargs.pop('pdr_interval', 60 * 60)  # One hour
        self._hid = self._model.get_uid()
        self._given_keep_alive = kwargs.pop('ping_interval', 60)
        self._gen_qos = kwargs.pop('qos', 1)
        self._trusted_senders = []

        # Read config
        self._read_config()

        super(TrinClient, self).__init__(
            *args,
            client_id=self._hid,
            clean_session=self._given_clean_session,
            **kwargs)

        # Make sure a reconnect gets a new password
        username, password = self._get_username_password()
        self.username_pw_set(username, password=password)
        self.command_receivers = {
            '0': self._command_handler
        }

        # Wire up callbacks
        self.on_connect = self._on_trin_connect
        self.on_message = self._on_trin_message
        self.on_disconnect = self._on_trin_disconnect

        # Declare threads
        self._iah_thread = None  # I-am-here thread
        self._pdr_thread = None  # Periodic data report thread

        # Save config
        self._write_config()

    # ------------------------------------------------------[ Public Utility ]--
    def log(self, msg, obj=None):
        msg = msg if msg else ''
        j = ''
        if obj:
            try:
                j = json.dumps(obj)
            except Exception as ex:
                j = ex
        msg = '{}{}'.format(msg, j)
        self._easy_log(MQTT_LOG_INFO, msg)

    # -----------------------------------------------------[ Private Utility ]--
    def _sender_is_trusted(self, sender_hid):
        is_server = sender_hid == TRUSTED_SERVER
        return is_server or sender_hid in self._trusted_senders

    def _read_config(self):
        config = configparser.ConfigParser()
        config.read(self._cnf)
        defs = config['DEFAULT']
        for key in defs:
            if key == 'pdrinterval':
                self._pdr_interval = defs.getint('pdrinterval')
            if key == 'host':
                self._given_host = defs['host']
            if key == 'defaultqos':
                self._gen_qos = defs.getint('defaultqos')
            if key == 'usertc':
                self._use_rtc = defs.getboolean('usertc')
            if key == 'iahinterval':
                self._iah_interval = defs.getint('iahinterval')
            if key == 'keepalive':
                self._given_keep_alive = defs.getint('keepalive')
            if key == 'port':
                self._given_port = defs.getint('port')
            if key == 'cleansession':
                self._given_clean_session = defs.getboolean('cleansession')
            if key == 'trustedsenders':
                ts = defs['trustedsenders']
                if ts and ts != '':
                    self._trusted_senders = defs['trustedsenders'].split(DELIM)

    def _write_config(self):
        dir_name = os.path.dirname(self._cnf)
        try:
            os.makedirs(dir_name)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        if not os.path.exists(self._cnf):
            os.mknod(self._cnf)

        config = configparser.ConfigParser()
        config['DEFAULT'] = {
            'pdrinterval': self._pdr_interval,
            'host': self._given_host,
            'defaultqos': self._gen_qos,
            'usertc': self._use_rtc,
            'iahinterval': self._iah_interval,
            'keepalive': self._given_keep_alive,
            'trustedsenders': DELIM.join(self._trusted_senders),
            'cleansession': self._given_clean_session
        }
        with open(self._cnf, 'w') as configfile:
            config.write(configfile)

    def _get_username_password(self):
        username = '{ROOT}{HID}'.format(
            ROOT=self._cid,
            HID=self._hid)
        password = get_password()
        return username, password

    def _collect_settings(self):
        return {
            'client': {
                'trinpyqtt': pkg_resources.get_distribution(
                    'trinpyqtt').version,
                'paho-mqtt': pkg_resources.get_distribution(
                    'paho-mqtt').version
            },
            'settings': {
                'use_rtc': self._use_rtc,
                'iah_interval': self._iah_interval,
                'pdr_interval': self._pdr_interval,
                'keep_alive': self._keepalive,
                'default_qos': self._gen_qos,
                'clean_session': self._given_clean_session,
                'trusted_senders': DELIM.join(
                    self._trusted_senders)
            }
        }

    def _collect_dump(self):
        ip_data, err = get_my_ip()
        if err:
            self.log(err)
        hw_data = self._model.collect_data(basic=False)
        settings_data = self._collect_settings()
        dump = ip_data.copy()
        dump.update(hw_data)
        dump.update(settings_data)
        return dump

    def _upgrade_self(self):
        call(['pip3', 'install', '--upgrade', 'trinpyqtt'])
        restart_program()

    # ------------------------------------------------------[ Topic Builders ]--
    def _get_sub_home_topic(self):
        return '{ROOT}/{HID}/+/</#'.format(
            ROOT=self._cid,
            HID=self._hid)

    def _get_pub_topic(self, pid='0'):
        return '{ROOT}/{HID}/{PID}/>'.format(
            ROOT=self._cid,
            HID=self._hid,
            PID=pid)

    def _get_reply_topic(self, pid='0', tct=None):
        if not tct:
            raise TcTException
        return '{ROOT}/{HID}/{PID}/>/{TCT}'.format(
            ROOT=self._cid,
            HID=self._hid,
            PID=pid,
            TCT=tct)

    def _get_pub_targeted_topic(self, target_hid=None, target_pid='0'):
        if not target_hid:
            raise TargetHidException
        return '{ROOT}/{HID_TARGET}/{PID_TARGET}/</{HID}'.format(
            ROOT=self._cid,
            HID_TARGET=target_hid,
            PID_TARGET=target_pid,
            HID=self._hid)

    def _get_pub_iah_topic(self, pid='0'):
        return 'iah_{ROOT}/{HID}/{PID}/>'.format(
            ROOT=self._cid,
            HID=self._hid,
            PID=pid)

    # ----------------------------------------------------[ Payload Builders ]--
    def _get_payload_ts(self):
        return get_now_timestamp() if self._use_rtc else 0

    def _build_iah_payload(self):
        ts = self._get_payload_ts()
        return json.dumps({'i': ts})

    def _build_data_payload(self, data=None):
        ts = self._get_payload_ts()
        payload = data if data is not None else []
        d = {'d': [ts, payload]}
        s = json.dumps(d)
        return s

    def _build_event_payload(self, events=None):
        events = events if events else []
        ts = self._get_payload_ts()
        e = {'e': [ts, events]}
        return json.dumps(e)

    def _build_reply_payload(self, code=SUCCESS, reply=None):
        ts = self._get_payload_ts()
        x = {'x': [ts, code]}
        if reply:
            x.get('x').append(reply)
        j = json.dumps(x)
        self._easy_log(MQTT_LOG_INFO, j)
        return j

    # ----------------------------------------------------[ Periodic Publish ]--
    def _publish_iah(self):
        self.publish(
            self._get_pub_iah_topic(),
            payload=self._build_iah_payload(),
            qos=self._gen_qos)
        if self._iah_interval:
            self._iah_thread = Timer(
                self._iah_interval, self._publish_iah).start()

    def _publish_pdr(self, basic=True, skip=False):
        if not skip:
            data = self._model.collect_data(basic=basic)
            self.publish(
                self._get_pub_topic(),
                payload=self._build_data_payload(data=data),
                qos=self._gen_qos)
        if self._pdr_interval:
            self._pdr_thread = Timer(
                self._pdr_interval, self._publish_pdr, ).start()

    # ---------------------------------------------[ Private Publish Helpers ]--
    def _publish_trusted_senders(self):
        self._read_config()
        config = self._collect_settings()
        t_send = safe_get(config, 'settings', 'trusted_senders')
        trusted_settings_data = {'settings': {'trusted_senders': t_send}}
        self.publish_data(trusted_settings_data)

    # ---------------------------------------------------------[ Publish API ]--
    def publish_event(self, event, pid='0', qos=None, ):
        qos = qos if qos is not None else self._gen_qos
        events = [event]
        self.publish_events(events, pid=pid, qos=qos)

    def publish_events(self, events, pid='0', qos=None, ):
        qos = qos if qos is not None else self._gen_qos
        self.publish(
            self._get_pub_topic(pid=pid),
            payload=self._build_event_payload(events=events),
            qos=qos)

    def publish_data(self, data, pid='0', qos=None):
        qos = qos if qos is not None else self._gen_qos
        self.publish(
            self._get_pub_topic(pid=pid),
            payload=self._build_data_payload(data=data),
            qos=qos)

    def publish_reply(self, tct, code, reply, pid='0', qos=None, wait=False):
        qos = qos if qos is not None else self._gen_qos
        if not tct:
            return
        info = self.publish(
            self._get_reply_topic(pid=pid, tct=tct),
            payload=self._build_reply_payload(code=code, reply=reply),
            qos=qos)

        # Block until I know my message was sent
        if qos > 0 and wait:
            info.wait_for_publish()

    # -----------------------------------------------------------[ Callbacks ]--
    def _on_trin_connect(self, mqttc, obj, flags, rc):
        # 6-255: Currently unused.
        # result_codes = {
        #     0: 'Connection successful',
        #     1: 'Connection refused - incorrect protocol version ',
        #     2: 'Connection refused - invalid client identifier',
        #     3: 'Connection refused - server unavailable',
        #     4: 'Connection refused - bad username or password',
        #     5: 'Connection refused - not authorised',
        # }
        if not rc:
            # Subscribing in on_connect() means that if we lose the
            # connection and reconnect then subscriptions will be renewed.
            mqttc.subscribe(self._get_sub_home_topic(), qos=self._gen_qos)

            # Publish and event on successful connect
            self.publish_event([
                self._get_payload_ts(), EC_CONNECT_SUCCESS, 'Connect Success'])

            # Dump settings and data each time we connect.
            self.publish_data(self._collect_dump())

            # Publish I-am-here
            if self._iah_interval:
                self._publish_iah()

            # Publish periodic data report if needed.
            if self._pdr_interval:
                self._publish_pdr(skip=True)

    def _on_trin_disconnect(self, mqttc, userdata, rc):
        if rc != 0:
            # Because of the security module's password replay protection
            # we need to set a new password here...
            u, p = self._get_username_password()
            mqttc.username_pw_set(u, password=p)
            sleep(1)
            self.run()

    # The callback for when a PUBLISH message is received from the server.
    def _on_trin_message(self, client, user_data, msg):
        topic = msg.topic
        payload = msg.payload.decode()

        retain = msg.retain
        if retain:
            self.log('Received retained message on topic {topic}'.format(
                topic=topic))

        nld = parse_msg(topic, payload, user_data)
        tct = nld['tct']
        if tct and nld['code'] < 0:
            self.publish_reply(tct, nld['code'], 'Error')
        else:
            try:
                tokens = topic.split('/')
                sender = tokens[4]
                receiver = tokens[2]
                if self._sender_is_trusted(sender):
                    try:
                        self.command_receivers[receiver](self, nld, topic,
                                                         payload, sender)
                    except KeyError:
                        if tct:
                            self.publish_reply(tct, F_UNKNOWN_PID,
                                               'Unknown PID')
            except IndexError:
                # Malformed topic structure.
                if tct:
                    self.publish_reply(tct, F_BROKEN_TOPIC, 'Malformed topic')

    # ----------------------------------------------------[ Command Handling ]--
    def _command_handler(self, mqttc, nld, topic, msg, sender):
        """
        Commands destined for me i.e command with a '0' PID comes here.
        """
        # None of these commands can be sent by anyone except the
        # trusted server.
        if sender != TRUSTED_SERVER:
            self.log('{s} is not the server. The server is {ts}'.format(
                s=sender, ts=TRUSTED_SERVER))
            return

        # A map of local valid RPCs
        rpcs = {
            'data_write': self._data_write,
            'set_iah_interval': self._set_iah_interval,
            'set_pdr_interval': self._set_pdr_interval,
            'set_use_rtc': self._set_use_rtc,
            'set_ping_interval': self._set_keep_alive_interval,
            'set_clean_session': self._set_clean_session,
            'set_host': self._set_host,
            'take_a_break': self._take_a_break,
            'get': self._get_var_val,
            'pub_full_data': self._pub_full_data,
            'pub_all_settings': self._pub_all_settings,
            'pup_ip_address': self._pub_ip_address,
            'reboot_hardware': self._reboot_hardware,
            'add_trusted_sender': self._add_trusted_sender,
            'remove_trusted_sender': self._remove_trusted_sender,
            'clear_all_trusted_sender': self._clear_all_trusted_sender,
            'restart_client': self._restart_client,
            'upgrade_client': self._upgrade_client,
        }

        # The code will be 0 if the message parse OK
        if nld['code'] > -1:
            if nld['type'] == 'c':
                tct = nld['tct']
                for c, args in nld['command'].items():
                    try:
                        code, result = rpcs[c](*args)
                        if tct:
                            self.publish_reply(tct, code, result)
                    except KeyError:
                        if tct:
                            self.publish_reply(tct, F_NO_RPC,
                                               'RPC Not implemented')

    def register_command_receiver(self, pid, f):
        if str(pid) != '0':
            self.command_receivers[pid] = f

    # ----------------------------------------------------------------[ RPCs ]--
    def _data_write(self, path, data):
        """
        :param path: A string like '/settings', or '/', or '/a/b/c'
        :param data: An object like {'iah_interval': 60}
        :return:
        """
        path_list = path.split('/')
        path_list.pop(0)
        exposed_settings = {
            'settings': {
                'use_rtc': self._set_use_rtc,
                'iah_interval': self._set_iah_interval,
                'pdr_interval': self._set_pdr_interval,
                'keep_alive': self._set_keep_alive_interval,
                'default_qos': self._set_gen_qos,
                'clean_session': self._set_clean_session,
            }
        }

        # Just randomly choose a key out the dict. We don't support multi
        # data write payloads yet.
        key = list(data.keys())[0]
        value = data[key]
        path_list.append(key)
        f = lookup(exposed_settings, *path_list)
        if not f:
            self._easy_log(MQTT_LOG_INFO, 'This is not exposed')
            return F_DW_NOT_EXPOSED, 'Data Write not exposed'
        return f(value)

    def _reboot_hardware(self):
        code = SUCCESS
        try:
            reply = 'OK Reboot scheduled'
            self._model.reboot(self)
        except Exception as ex:
            reply = 'NAC {ex}'.format(ex=ex)
            code = F_EXCEPTION
        return code, reply

    def _pub_all_settings(self):
        code = SUCCESS
        try:
            data = self._collect_settings()
            self.publish(
                self._get_pub_topic(),
                payload=self._build_data_payload(data=data),
                qos=self._gen_qos)

            reply = 'OK. Settings published'
        except Exception as ex:
            reply = 'NAC {ex}'.format(ex=ex)
            code = F_EXCEPTION
        return code, reply

    def _pub_full_data(self):
        code = SUCCESS
        try:
            data = self._model.collect_data(basic=False)
            self.publish(
                self._get_pub_topic(),
                payload=self._build_data_payload(data=data),
                qos=self._gen_qos)
            reply = 'OK. Full data published'
        except Exception as ex:
            reply = 'NAC {ex}'.format(ex=ex)
            code = F_EXCEPTION
        return code, reply

    def _pub_ip_address(self):
        code = SUCCESS
        try:
            ip_data, err = get_my_ip()
            if err:
                self.log(err)
            self.publish_data(ip_data)
            reply = 'OK. IP Published: {}'.format(ip_data)
        except Exception as ex:
            reply = 'NAC {ex}'.format(ex=ex)
            code = F_EXCEPTION
        return code, reply

    def _get_var_val(self, var_name):
        code = SUCCESS
        try:
            reply = self.__getattribute__(var_name)
        except Exception as ex:
            reply = 'NAC {ex}'.format(ex=ex)
            code = F_EXCEPTION
        return code, reply

    def _take_a_break(self, interval):
        reply = 'OK. Took a {i} sec break.'.format(i=interval)
        code = SUCCESS
        try:
            self.rerun(delay=interval)
        except Exception as ex:
            reply = 'NAC {ex}'.format(ex=ex)
            code = F_EXCEPTION
        return code, reply

    def _set_iah_interval(self, interval):
        reply = 'OK. Set IAH to: {i} sec.'.format(i=interval)
        code = SUCCESS
        try:
            if int(interval) != self._iah_interval:
                self._iah_interval = int(interval)
                self._write_config()
                data = {'settings': {'iah_interval': self._iah_interval}}
                self.publish_data(data)
                if self._iah_thread:
                    self._iah_thread.cancel()
                if self._iah_interval:
                    self._publish_iah()
        except Exception as ex:
            reply = 'NAC {ex}'.format(ex=ex)
            code = F_EXCEPTION
        return code, reply

    def _set_pdr_interval(self, interval):
        reply = 'OK. Set PDR to: {i} sec.'.format(i=interval)
        code = SUCCESS
        try:
            if int(interval) != self._pdr_interval:
                self._pdr_interval = int(interval)
                self._write_config()
                data = {'settings': {'pdr_interval': self._pdr_interval}}
                self.publish_data(data)
                if self._pdr_thread:
                    self._pdr_thread.cancel()
                if self._pdr_interval:
                    self._publish_pdr()
        except Exception as ex:
            reply = 'NAC {ex}'.format(ex=ex)
            code = F_EXCEPTION
        return code, reply

    def _set_use_rtc(self, boolean):
        reply = 'OK. Set RTC use to: {i}'.format(i=boolean)
        code = SUCCESS

        try:
            a_bool = convert_to_boolean(boolean)
            try:
                self._use_rtc = a_bool
                self._write_config()
                data = {'settings': {'use_rtc': self._use_rtc}}
                self.publish_data(data)
            except Exception as ex:
                reply = 'NAC {ex}'.format(ex=ex)
                code = F_EXCEPTION
        except ValueError as ex:
            reply = 'NAC {ex}'.format(ex=ex)
            code = F_NOT_A_BOOLEAN

        return code, reply

    def _set_clean_session(self, boolean):
        reply = 'OK. Set clean session flag to: {i}.'.format(i=boolean)
        code = SUCCESS
        try:
            a_bool = convert_to_boolean(boolean)
            try:
                self._given_clean_session = a_bool
                self._write_config()
                # data = {
                #     'settings': {'clean_session': self._given_clean_session}}
                # self.publish_data(data)
                Timer(10, restart_program).start()
            except Exception as ex:
                reply = 'NAC {ex}'.format(ex=ex)
                code = F_EXCEPTION
        except ValueError as ex:
            reply = 'NAC {ex}'.format(ex=ex)
            code = F_NOT_A_BOOLEAN

        return code, reply

    def _set_keep_alive_interval(self, interval):
        reply = 'OK. Set PING interval to: {i} sec.'.format(i=interval)
        code = SUCCESS
        try:
            self._given_keep_alive = interval
            self._write_config()
            self.rerun()
        except Exception as ex:
            reply = 'NAC {ex}'.format(ex=ex)
            code = F_EXCEPTION
        return code, reply

    def _set_host(self, host):
        reply = 'OK. Set host to: {i}'.format(i=host)
        code = SUCCESS
        try:
            self._given_host = host
            self._write_config()
            self.rerun()
        except Exception as ex:
            reply = 'NAC {ex}'.format(ex=ex)
            code = F_EXCEPTION
        return code, reply

    def _set_gen_qos(self, qos):
        reply = 'OK. Set general QOS to:{i}'.format(i=qos)
        code = SUCCESS
        try:
            v = int(qos)
            if v < 0 or v > 2:
                reply = 'NAC QOS out of range'
            else:
                self._gen_qos = int(qos)
                self._write_config()

                # Re-subscribe with the new QoS
                self.subscribe(self._get_sub_home_topic(), qos=self._gen_qos)
        except Exception as ex:
            reply = 'NAC {ex}'.format(ex=ex)
            code = F_EXCEPTION
        return code, reply

    def _add_trusted_sender(self, sdr):
        reply = 'OK. Added {s} to trusted senders list.'.format(s=sdr)
        code = SUCCESS
        try:
            self._trusted_senders.append(sdr)
            self._trusted_senders = list(set(self._trusted_senders))
            self._write_config()

            # Verify
            self._publish_trusted_senders()
        except Exception as ex:
            reply = 'NAC {ex}'.format(ex=ex)
            code = F_EXCEPTION
        return code, reply

    def _remove_trusted_sender(self, sdr):
        reply = 'OK. Removed {s} from trusted senders list.'.format(s=sdr)
        code = SUCCESS
        try:
            trusted_senders = filter(lambda a: a != sdr, self._trusted_senders)
            self._trusted_senders = list(set(trusted_senders))
            self._write_config()

            # Verify
            self._publish_trusted_senders()
        except Exception as ex:
            reply = 'NAC {ex}'.format(ex=ex)
            code = F_EXCEPTION
        return code, reply

    def _clear_all_trusted_sender(self):
        reply = 'OK. Removed all trusted senders.'
        code = SUCCESS
        try:
            self._trusted_senders = []
            self._write_config()

            # Verify
            self._publish_trusted_senders()
        except Exception as ex:
            reply = 'NAC {ex}'.format(ex=ex)
            code = F_EXCEPTION
        return code, reply

    def _restart_client(self):
        reply = 'OK. Restarting client in 10 seconds'
        code = SUCCESS
        try:
            Timer(10, restart_program).start()
        except Exception as ex:
            reply = 'NAC {ex}'.format(ex=ex)
            code = F_EXCEPTION
        return code, reply

    def _upgrade_client(self):
        reply = 'OK. Upgrading client in 10 seconds'
        code = SUCCESS
        try:
            Timer(10, self._upgrade_self).start()
        except Exception as ex:
            reply = 'NAC {ex}'.format(ex=ex)
            code = F_EXCEPTION
        return code, reply

    # --------------------------------------------------------------------------
    def run(self):
        self.will_set(
            self._get_pub_topic(),
            self._build_event_payload(
                [[self._get_payload_ts(), EC_LWT, 'LWT Published']]),
            qos=1)
        self.connect_async(self._given_host, port=self._given_port, keepalive=self._given_keep_alive)
        self.loop_start()

    def rerun(self, delay=1):
        self.disconnect()
        sleep(delay)
        self.run()

