# -*- coding: utf-8 -*-

"""Main module."""
import copy
import logging
import json
import threading

import requests
import websocket

_LOGGER = logging.getLogger(__name__)

USER_AGENT = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) "
              "AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/42.0.2311.90 Safari/537.36")
WF_LOGIN_URL = 'https://symphony.mywaterfurnace.com/account/login'

FURNACE_MODE = (
    'Standby',
    'Fan Only',
    'Cooling 1',
    'Cooling 2',
    'Reheat',
    'Heating 1',
    'Heating 2',
    'E-Heat',
    'Aux Heat',
    'Lockout')

FAILED_LOGIN = ("Your login failed. Please check your email address "
                "/ password and try again.")

TIMEOUT = 15

DATA_REQUEST = {
    "cmd": "read",
    "tid": None,
    "awlid": None,
    "zone": 0,
    "rlist": [  # the list of sensors to return readings for
        "compressorpower",
        "fanpower",
        "auxpower",
        "looppumppower",
        "totalunitpower",
        "AWLABCType",
        "ModeOfOperation",
        "ActualCompressorSpeed",
        "AirflowCurrentSpeed",
        "AuroraOutputEH1",
        "AuroraOutputEH2",
        "AuroraOutputCC",
        "AuroraOutputCC2",
        "TStatDehumidSetpoint",
        "TStatHumidSetpoint",
        "TStatRelativeHumidity",
        "LeavingAirTemp",
        "TStatRoomTemp",
        "EnteringWaterTemp",
        "AOCEnteringWaterTemp",
        "lockoutstatus",
        "lastfault",
        "lastlockout",
        "humidity_offset_settings",
        "humidity",
        "outdoorair",
        "homeautomationalarm1",
        "homeautomationalarm2",
        "roomtemp",
        "activesettings",
        "TStatActiveSetpoint",
        "TStatMode",
        "TStatHeatingSetpoint",
        "TStatCoolingSetpoint",
        "AWLTStatType"],
    "source": "consumer dashboard"}


class WFException(Exception):
    pass


class WFCredentialError(WFException):
    pass


class WFWebsocketClosedError(WFException):
    pass


class WFError(WFException):
    pass


class WaterFurnace(object):

    def __init__(self, user, passwd, unit):
        self.user = user
        self.passwd = passwd
        self.unit = unit
        self.sessionid = None
        self.tid = 0

    def next_tid(self):
        self.tid = (self.tid + 1) % 100

    def _get_session_id(self):
        data = dict(emailaddress=self.user, password=self.passwd, op="login")
        headers = {"user-agent": USER_AGENT}
        res = requests.post(WF_LOGIN_URL, data=data, headers=headers,
                            timeout=TIMEOUT,
                            allow_redirects=False)
        try:
            self.sessionid = res.cookies["sessionid"]
        except KeyError:
            if FAILED_LOGIN in res.content:
                raise WFCredentialError()
            else:
                raise WFError()

    def _login_ws(self):
        self.ws = websocket.create_connection(
            "wss://awlclientproxy.mywaterfurnace.com/", timeout=TIMEOUT)
        login = {"cmd": "login", "tid": self.tid,
                 "source": "consumer dashboard",
                 "sessionid": self.sessionid}
        self.ws.send(json.dumps(login))
        # TODO(sdague): we should probably check the response, but
        # it's not clear anything is useful in it.
        recv = self.ws.recv()
        _LOGGER.debug("Login response: %s" % recv)
        self.next_tid()

    def login(self):
        self._get_session_id()
        # reset the transaction id if we start over
        self.tid = 1
        self._login_ws()

    def _abort(self, *args, **kwargs):
        _LOGGER.warning("Aborted read request")
        self.ws.abort()

    def _ws_read(self):
        req = copy.deepcopy(DATA_REQUEST)
        req["tid"] = self.tid
        req["awlid"] = self.unit

        _LOGGER.debug("Req: %s" % req)
        timer = threading.Timer(1.0, self._abort, [self])
        timer.start()
        self.ws.send(json.dumps(req))
        _LOGGER.debug("Successful send")
        data = self.ws.recv()
        _LOGGER.debug("Successful recv")
        timer.cancel()
        return data

    def read(self):
        try:
            data = self._ws_read()
            self.next_tid()
            datadecoded = json.loads(data)
            _LOGGER.debug("Resp: %s" % datadecoded)
            if not datadecoded['err']:
                return WFReading(datadecoded)
            else:
                raise WFError(datadecoded['err'])
        except websocket.WebSocketConnectionClosedException:
            raise WFWebsocketClosedError()
        except Exception:
            _LOGGER.exception("Unknown exception, socket probably failed")
            raise WFWebsocketClosedError()


class WFReading(object):

    def __init__(self, data={}):
        self.zone = data.get('zone', 0)
        self.err = data.get('err', '')
        self.awlid = data.get('awlid', '')
        self.tid = data.get('tid', 0)

        # power (Watts)
        self.compressorpower = data.get('compressorpower')
        self.fanpower = data.get('fanpower')
        self.auxpower = data.get('auxpower')
        self.looppumppower = data.get('looppumppower')
        self.totalunitpower = data.get('totalunitpower')

        # modes (0 - 10)
        self.modeofoperation = data.get('modeofoperation')

        # fan speed (0 - 10)
        self.airflowcurrentspeed = data.get('airflowcurrentspeed')

        # humidity (%)
        self.tstatdehumidsetpoint = data.get('tstatdehumidsetpoint')
        self.tstathumidsetpoint = data.get('tstathumidsetpoint')
        self.tstatrelativehumidity = data.get('tstatrelativehumidity')

        # temps (degrees F)
        self.leavingairtemp = data.get('leavingairtemp')
        self.tstatroomtemp = data.get('tstatroomtemp')
        self.enteringwatertemp = data.get('enteringwatertemp')

        # setpoints (degrees F)
        self.tstatheatingsetpoint = data.get('tstatheatingsetpoint')
        self.tstatcoolingsetpoint = data.get('tstatcoolingsetpoint')
        self.tstatactivesetpoint = data.get('tstatactivesetpoint')

    @property
    def mode(self):
        return FURNACE_MODE[self.modeofoperation]

    def __str__(self):
        return ("<FurnaceReading power=%d, mode=%s, looptemp=%.1f, "
                "airtemp=%.1f, roomtemp=%.1f, setpoint=%d>" % (
                    self.totalunitpower,
                    self.mode,
                    self.enteringwatertemp,
                    self.leavingairtemp,
                    self.tstatroomtemp,
                    self.tstatactivesetpoint))
