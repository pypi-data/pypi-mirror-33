# author Kashirin Alex

import base64
import datetime
import random
import string
import time
import calendar

try:
    import requests
except:
    requests = None

try:
    from Cryptodome.Cipher import AES
except:
    AES = None

# get available compression lib
try:
    import zlib
    compressor = ('zlib', zlib.compress)
except:
    compressor = None
#
chars = string.ascii_letters+string.digits
pads_len = 8


class FlowMetricsStatisticsClient(object):
    __slots__ = ['u_push', 'u_get', 'fid', 'ps', 'cph', 'json', 's', 'ka', 'requests_args']

    api_version = 'v201807'
    root_url = '://thither.direct/api/fms-'
    except_errs = {
        'AES': 'requested cipher AES, pkg Cryptodome is not installed!',
        'AES_ps': 'AES cipher require key(pass-phrase) 16, 24 or 32 in chars length!',
        'requests': 'pkg requests is not installed!',
        'fid': 'flow_id_is_required'
    }

    def __init__(self, fid, **kwargs):
        """
            Initiate a new Client.

            from libthither.api.fms import FlowMetricsStatisticsClient
            client = FlowMetricsStatisticsClient(
                        'YourFlowID',
                        pass_phrase='YourPassPhrase',
                        https=True,
                        cipher='',
                        keep_alive=True,
                        json=False
                        requests_args={},
                        )
            after initiated, client can be called with:
            client.push_single(YourMetricId, DateAndTime, Value)
            client.push_list([[Metric ID, DateTime, Value],])
            client.push_csv_data("mid,dt,v\nYourMetricId,DateAndTime,Value")

            Parameters
            ----------
            fid : str
                Your FlowID

            Keyword Args
            ----------
            version : str
                applicable API version
            pass_phrase : str
                Your API pass-phrase,
                optional depends on Flow configurations
            https : bool
                Whether to use https,
                default True
            cipher : str
                Authentication Cipher AES(the only available for now),
                optional depends on Flow configurations
            keep_alive : bool
                Whether to keep session alive,
                default False
            json : bool
                Whether to use only JSON Content-Type,
                default False
            requests_args : dict
                Passed kwargs to 'requests' library

            Returns
            -------
            FlowMetricsStatisticsClient instance
        """
        u = 'http'+('s' if kwargs.get('https', True) else '')+self.root_url+kwargs.get('version', self.api_version)
        self.u_push = u+"/post/"
        self.u_get = u+"/get/"

        self.fid = fid
        if not self.fid:
            raise Exception('error', self.except_errs['fid'])

        self.ps = kwargs.get('pass_phrase', '')

        self.cph = kwargs.get('cipher', '')
        if self.cph == 'AES':
            if AES is None:
                raise Exception('error', self.except_errs['AES'])
            if len(self.ps) not in [16, 24, 32]:
                raise Exception('error', self.except_errs['AES_ps'])

        if requests is None:
            raise Exception('error', self.except_errs['requests'])
        self.s = requests.Session() if kwargs.get('keep_alive', False) else None

        self.json = kwargs.get('json', False)
        self.requests_args = kwargs.get('requests_args', None)
        #

    @staticmethod
    def utc_seconds():
        return int(calendar.timegm(time.gmtime(time.time())))
        #

    def set_params(self, params):
        """
            Set the corresponding parameters for a request.

            The function set the predefined parameters in the instance
            and if cipher is used computes a token for authenticating

            Parameters
            ----------
            params : dict
                a reference to the dict to work with
            Returns
            -------
            None
        """
        params['fid'] = self.fid  # Flow Metrics Statistics ID
        if not self.cph:
            params['ps'] = self.ps
            return
        if self.cph == "AES":
            cipher = AES.new(b'' + self.ps.encode("utf-8"), AES.MODE_EAX)
            crp, tag = cipher.encrypt_and_digest(
                '|'.join([''.join(random.choice(chars) for _ in range(pads_len)),
                          str(self.utc_seconds()),
                          self.fid,
                          str(pads_len),
                          ''.join(random.choice(chars) for _ in range(pads_len))]
                         ).encode("utf-8"))
            params['token'] = '|'.join([base64.b64encode(cipher.nonce), base64.b64encode(tag), base64.b64encode(crp)])
        #

    @staticmethod
    def set_compression(params, data):
        params['comp'] = compressor[0]
        return compressor[1](data.encode("utf-8"))
        #

    def push_single(self, mid, dt, v):
        """
            Push a single item to the server.

            Parameters
            ----------
            mid : str
                Your MetricID
            dt : str/int
                Unix Timestamp
                or
                Date and time in format '%Y-%m-%d %H:%M:%S' unless otherwise specified on the metric configurations
            v : str/int
                value positive, negative or =equal

            Returns
            -------
            requests lib response or an rsp object with status_code and content {'status': 'bad_request', 'error': desc}
        """
        if not mid or not dt or (not v and v != 0):
            return BadReq(0)
        if not isinstance(v, int):
            try:
                tmp = int(v if v[0] != '=' else v[1:])
            except:
                return BadReq(0)

        params = {'mid': mid, 'dt': dt, 'v': v}
        self.set_params(params)
        if self.json:
            return self.post(self.u_push+"stats/item", json=params)
        else:
            return self.post(self.u_push+"stats/item",
                             headers={'Content-Type': 'application/x-www-form-urlencoded'}, params=params)
        #

    def push_list(self, items):
        """
            Push a list to the server.

            Extended description of function.

            Parameters
            ----------
            items : list
                list of items [[Metric ID, DateTime, Value],]
            Returns
            -------
            requests lib response or an rsp object with status_code and content {'status': 'bad_request', 'error': desc}
        """
        if not items:
            return BadReq(1)

        params = {}
        self.set_params(params)

        if self.json:
            params['items'] = items
            return self.post(self.u_push+"stats/items_json", json=params)
        else:
            # list converted to csv preferred for data-transfer
            csv_data = "\n".join(["mid,dt,v"] + [','.join([str(v) for v in item]) for item in items])
            if compressor is not None:
                csv_data = self.set_compression(params, csv_data)
            return self.post(self.u_push+"stats/items_csv", params=params, files={'csv': csv_data})
        #

    def push_csv_data(self, csv_data):
        """
            Push a csv data to the server.

            Extended description of function.

            Parameters
            ----------
            csv_data : str
                a csv data with 'mid', 'dt', 'v' columns
            Returns
            -------
            requests lib response or an rsp object with status_code and content {'status': 'bad_request', 'error': desc}
        """
        if not csv_data:
            return BadReq(2)

        params = {}
        self.set_params(params)
        if self.json:
            params['csv'] = csv_data
            return self.post(self.u_push+"stats/items_csv", json=params)
        else:
            if compressor is not None:
                csv_data = self.set_compression(params, csv_data)
            return self.post(self.u_push+"stats/items_csv", params=params, files={'csv': csv_data})
        #

    def post(self, u, **kwargs):
        if self.requests_args is not None:
            kwargs.update(self.requests_args)
        if self.s is not None:
            return self.s.post(u, **kwargs)
        else:
            return requests.post(u, **kwargs)
        #

    def get_definitions(self, typ='', **kwargs):
        """
            Get Flow Definitions.

            Arguments
            ----------
            typ : str
                Type of Definition units/sections/metrics
                or selects all definitions

            Keyword Args
            ----------
            section : str
                Only on this section level
                apply only to sections and metrics types
            unit : str
                Only metrics with this Unit ID
            operation : str
                Only metrics that timebase join operation is sum/avg
            timebase : str/int
                Only metrics that with this timebase(minutes)

            Returns
            -------
            'requests' lib response with JSON content of a dict{DEFINITION_TYPE: {TYPE_ID: {INFO_NAME: VALUE}}
        """

        if typ not in ['', 'units', 'sections', 'metrics']:
            return BadReq(5)

        params = {}
        self.set_params(params)
        if typ == 'units':
            pass
        else:
            v = kwargs.get('section', False)
            if v:
                params['section'] = v
            if typ == 'metrics':
                for k in ['unit', 'operation', 'timebase', 'tz']:
                    v = kwargs.get(k, False)
                    if not v:
                        continue
                    params[k] = v
        return self.get(self.u_get+"definitions/"+typ+"/", params=params)
        #

    def get_stats(self, mid, from_ts, to_ts, **kwargs):
        """
            Get Metric Statistics Data.

            Arguments
            ----------
            mid : str
                Your Metric ID
            from_ts : int
                select only from timestamp
            to_ts : int
                select only to timestamp

            Keyword Args
            ----------
            base : int
                time frame base - minutes
            tz : int
                timezone align to GMT +/- minutes
            time_format : str
                default '%Y/%m/%d %H:%M' decreased with higher base
            limit : int
                results limit, 0:no-limit (max 1,000,000)
            page : int
                start from page number
            Returns
            -------
            'requests' lib response with JSON content of:
             a dict{
                    'items': [[date-time, value],],
                    'next_page': INT, # False for no more items
             }
        """
        if not isinstance(from_ts, int) or not isinstance(to_ts, int) or from_ts > to_ts:
            return BadReq(6)

        if not mid:
            return BadReq(0)

        params = {'mid': mid, 'from': from_ts, 'to': to_ts}
        self.set_params(params)

        v = kwargs.pop('time_format', None)
        if v is not None:
            try:
                datetime.datetime.now().strftime(v)
                params['tf'] = v
            except:
                return BadReq(8)

        for k in ['base', 'tz', 'limit', 'page']:
            v = kwargs.get(k, False)
            if not v:
                continue
            if not isinstance(v, int):
                return BadReq(7)
            params[k] = v
        return self.get(self.u_get+"stats/", params=params)
        #

    def get(self, u, **kwargs):
        if self.requests_args is not None:
            kwargs.update(self.requests_args)
        if self.s is not None:
            return self.s.get(u, **kwargs)
        else:
            return requests.get(u, **kwargs)
        #

    def close(self):
        if self.s is not None:
            self.s.close()
        #
#


class BadReq(object):
    __slots__ = ['status_code', 'content']
    errors = {
        0: 'param_empty',
        1: 'list_empty',
        2: 'csv_data_empty',
        5: 'bad_definition_type',
        6: 'bad_timestamps',
        7: 'bad_kwarg_value',
        8: 'bad_time_format',
    }

    def __init__(self, c):
        self.status_code = c
        self.content = {'status': 'bad_request', 'msg': self.errors[c]}
        #
#
