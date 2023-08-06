# -*- coding: utf-8 -*

import asyncio

from tornado.web import RequestHandler as TornadoRequestHandler
from tornado.web import asynchronous
import tornado.ioloop
from kwikapi import BaseRequest, BaseResponse, BaseRequestHandler

from deeputil import Dummy

DUMMY_LOG = Dummy()

class TornadoRequest(BaseRequest):

    def __init__(self, req_hdlr):
        super().__init__()
        self._request = req_hdlr.request
        self.response = TornadoResponse(req_hdlr)

    @property
    def url(self):
        return self._request.uri

    @property
    def method(self):
        return self._request.method

    @property
    def body(self):
        return self._request.body

    @property
    def headers(self):
        return self._request.headers

class TornadoResponse(BaseResponse):
    def __init__(self, req_hdlr):
        super().__init__()
        self._req_hdlr = req_hdlr
        self.headers = {}

    def write(self, data, proto, stream=False):
        n, t = super().write(data, proto, stream=stream)

        if not stream:
            self.headers['Content-Length'] = n.value

        self._stream = stream

        '''for k, v in self.headers.items():
            self._req_hdlr.set_header(k, v)

        d = self._data

        if not stream:
            self._req_hdlr.write(d)
            return n, t

        for x in d:
            self._req_hdlr.write(x)'''

        return n, t

    def flush(self):
        #self._req_hdlr.flush()
        pass

    def close(self):
        #self._req_hdlr.finish()
        pass

class RequestHandler(TornadoRequestHandler):
    PROTOCOL = BaseRequestHandler.DEFAULT_PROTOCOL

    def __init__(self, *args, **kwargs):
        self.api = kwargs.pop('api')
        self.log = kwargs.pop('log', DUMMY_LOG)
        default_version = kwargs.pop('default_version', None)
        default_protocol = kwargs.pop('default_protocol', self.PROTOCOL)
        self.kwik_req_hdlr = BaseRequestHandler(self.api,
                default_version, default_protocol, log=self.log)

        super().__init__(*args, **kwargs)

    async def _handle(self):
        threadpool = self.api.threadpool

        def fn():
            req = TornadoRequest(self)
            self.kwik_req_hdlr.handle_request(req)
            return req.response

        if threadpool:
            loop = tornado.ioloop.IOLoop.current()
            res = await loop.run_in_executor(threadpool, fn)
        else:
            res = fn()

        for k, v in res.headers.items():
            self.set_header(k, v)

        if not res._stream:
            self.write(res._data)
        else:
            for x in res._data:
                self.write(x)

        self.flush()
        self.finish()

    get = post = _handle
