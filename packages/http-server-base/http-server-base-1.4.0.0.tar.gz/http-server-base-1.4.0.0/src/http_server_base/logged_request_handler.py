import json
import random
import string
import warnings
from typing import Union, Callable, Optional, Tuple, Any, Dict

from tornado.httpclient import HTTPResponse, HTTPRequest, AsyncHTTPClient
from tornado import httputil
from tornado.web import RequestHandler, asynchronous, MissingArgumentError
from logging import getLogger, Logger

from http_server_base import BasicResponder
from http_server_base.tools import logging, ExtendedLogger, StyleAdapter

class RequestLogger(StyleAdapter, ExtendedLogger):
    handler: 'Logged_RequestHandler'
    def __init__(self, request_handler: 'Logged_RequestHandler', logger: Logger = None, extra=None):
        self.handler = request_handler
        super().__init__(logger, extra, style='{')
    
    def process(self, msg: str, kwargs: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        prefix = kwargs.pop('prefix', 'req')
        requ_id = kwargs.pop('requ_id', self.handler.requ_id)
        
        msg = f"{prefix}({requ_id}): {msg}"
        return super().process(msg, kwargs)

class Logged_RequestHandler(RequestHandler):
    """
    Logged_RequestHandler class
    This is a template to the handler classes.
    """
    
    # Must override
    logger_name:str
    
    # Should not override
    logger: ExtendedLogger = None
    requ_id = None
    request: httputil.HTTPServerRequest
    responder_class: BasicResponder
    _async_http_client: AsyncHTTPClient = None
    
    _ARG_DEFAULT = object()
    def get_body_or_query_argument(self, name, default=_ARG_DEFAULT, strip=True):
        all_args = self.request.body_arguments.copy()
        all_args.update(self.request.query_arguments)
        return self._get_argument(name=name, default=default, source=all_args, strip=strip)
    
    def get_body_or_query_arguments(self, name, strip=True):
        all_args = self.request.body_arguments.copy()
        all_args.update(self.request.query_arguments)
        return self._get_arguments(name=name, source=all_args, strip=strip)
    
    @property
    def async_http_client(self) -> AsyncHTTPClient:
        if (self._async_http_client is None):
            self._async_http_client = AsyncHTTPClient()
        
        return self._async_http_client
    
    def initialize(self, **kwargs):
        """
        Initializes the Logged_RequestHandler
        
        Initializes the logging.
        Logs the incoming request to the DEBUG level.
        Sets an request id.
        """
        if (getattr(self, 'logger_name', None) is None):
            self.logger_name = type(self).__name__
        
        super().initialize(**kwargs)
        
        _logger:ExtendedLogger = getLogger(self.logger_name)
        self.logger:ExtendedLogger = RequestLogger(self, _logger)
        
        request_obj = self.request
        self.requ_id = self.generate_request_id(search_in_query=True)
        
        self.logger.debug(f"Incoming HTTP: {request_obj.method} {request_obj.uri}")
        self.logger.debug(f"Headers: {json.dumps(dict(request_obj.headers))}")
        self.logger.debug(f"Query args: {request_obj.query_arguments}")
        self.logger.debug(f"Body args: {request_obj.body_arguments}")
    
    def set_default_headers(self):
        del self._headers["Content-Type"]

    def resp_error(self, code=500, reason=None, message=None, *args, **kwargs):
        if (hasattr(self, 'responder_class')):
            responder = self.responder_class
        elif (hasattr(self.application, 'responder_class')):
            responder = self.application.responder_class
        else:
            self.send_error(code, reason=reason)
            return
        
        responder.resp_error(self, code=code, reason=reason, message=message, *args, **kwargs)
    
    def resp(self, code=200, reason=None, message=None, *args, **kwargs):
        BasicResponder.resp_success(handler=self, code=code, reason=reason, message=message, *args, **kwargs)
        
    def resp_success(self, code=200, reason=None, message=None, result=None, *args, **kwargs):
        if (hasattr(self, 'responder_class')):
            responder = self.responder_class
        elif (hasattr(self.application, 'responder_class')):
            responder = self.application.responder_class
        else:
            self.set_status(code, reason=reason)
            return
        
        responder.resp_success(self, code=code, reason=reason, message=message, result=result, *args, **kwargs)


    def generate_proxy_request(self, handler):
        """
        Generate the new instance of the tornado.httpclient.HTTPRequest.
        :param handler:
        :return:
        """
        warnings.warn("The 'generate_proxy_request' method has redundant arguments, "
            "use 'generate_proxy_HTTPRequest' instead. It is going to be changed in v1.0", DeprecationWarning, 2)
        Logged_RequestHandler.generate_proxy_HTTPRequest(self)
        
    def generate_proxy_HTTPRequest(self:'Logged_RequestHandler', protocol: str = None, server: str = None, uri: str = None, **kwargs) -> HTTPRequest:
        request_obj:httputil.HTTPServerRequest = self.request
        
        if (protocol is None):
            protocol = request_obj.protocol
        if (server is None):
            server = request_obj.host
        if (uri is None):
            uri = request_obj.uri
        new_url = f"{protocol}://{server}{uri}"
        
        _method = request_obj.method.upper()
        _body = None
        if (_method == 'GET'):
            pass
        elif (_method == 'DELETE'):
            pass
        else:
            _body = request_obj.body
        
        self.logger.info("Redirecting to url: {}", new_url, prefix='proxy')
        
        _proxy_request = HTTPRequest(url=new_url, method=_method, body=_body, headers=request_obj.headers, **kwargs)
        return _proxy_request
    
    async def proxy_request_async_2(self, *, generate_request_func: Optional[Callable[['Logged_RequestHandler'], HTTPRequest]]=None, **kwargs):
        """
        Proxies current request.
        """
        
        if (generate_request_func is None):
            generate_request_func = type(self).generate_proxy_HTTPRequest
        
        _client = AsyncHTTPClient()
        _proxy_request = generate_request_func(self, **kwargs)
        
        self.logger.debug(f"Proxy request url: {_proxy_request.method} {_proxy_request.url}", prefix='proxy')
        self.logger.debug(f"Proxy request headers: {json.dumps(dict(_proxy_request.headers))}", prefix='proxy')
        self.logger.debug(f"Proxy request body args: {_proxy_request.body}", prefix='proxy')
        self.logger.debug("Fetching proxy request", prefix='proxy')
        resp = await _client.fetch(_proxy_request, raise_error=False)
        self.__proxied(resp)
    
    def proxy_request_async(self, *, generate_request_func: Optional[Callable[['Logged_RequestHandler'], HTTPRequest]]=None, **kwargs):
        """
        Proxies current request.
        """
        
        if (generate_request_func is None):
            generate_request_func = type(self).generate_proxy_HTTPRequest
        
        _client = AsyncHTTPClient()
        _proxy_request = generate_request_func(self, **kwargs)
        
        self.logger.debug(f"Proxy request url: {_proxy_request.method} {_proxy_request.url}", prefix='proxy')
        self.logger.debug(f"Proxy request headers: {json.dumps(dict(_proxy_request.headers))}", prefix='proxy')
        self.logger.debug(f"Proxy request body args: {_proxy_request.body}", prefix='proxy')
        self.logger.debug("Fetching proxy request", prefix='proxy')
        _client.fetch(_proxy_request, callback=self.__proxied, raise_error=False)
        return
    
    def __proxied(self, response: HTTPResponse):
        _code = response.code
        if (_code == 599):
            self.logger.error(f"Internal error during proxying request. Changing request code from {_code} to 500", prefix='resp')
            self.logger.error(f"{type(response.error).__name__}: {response.error}", prefix='resp')
            self.send_error(500, reason="Internal server error during proxying request")
            return
        
        self.logger.debug("Return {0}", _code, prefix='resp')
        self.set_status(_code)
        if ('content-type' in response.headers):
            self.add_header('Content-Type', response.headers['content-type'])
        elif ('content-type' in self.request.headers):
            self.add_header('Content-Type', self.request.headers['content-type'])
        if (response.body):
            self.logger.debug(f"Content {response.body[:500]}", prefix='resp')
            self.write(response.body)
        else:
            self.write(b'')
        self.finish()
        return
    
    # Overriding original finish to exclude 204/304 no body verification
    def finish(self, chunk=None):
        """Finishes this response, ending the HTTP request."""
        if (self._finished):
            raise RuntimeError("finish() called twice")
        
        if (chunk is not None):
            self.write(chunk)
        
        # Automatically support ETags and add the Content-Length header if
        # we have not flushed any content yet.
        if (not self._headers_written):
            if (self._status_code == 200 and
                self.request.method in ("GET", "HEAD") and
                    "Etag" not in self._headers):
                self.set_etag_header()
                if (self.check_etag_header()):
                    self._write_buffer = []
                    self.set_status(304)
            # if (self._status_code in (204, 304)):
            #     assert not self._write_buffer, "Cannot send body with %s" % self._status_code
            #     self._clear_headers_for_304()
            elif ("Content-Length" not in self._headers):
                content_length = sum(len(part) for part in self._write_buffer)
                self.set_header("Content-Length", content_length)
        
        if hasattr(self.request, "connection"):
            # Now that the request is finished, clear the callback we
            # set on the HTTPConnection (which would otherwise prevent the
            # garbage collection of the RequestHandler when there
            # are keepalive connections)
            self.request.connection.set_close_callback(None)
        
        self.flush(include_footers=True)
        self.request.finish()
        self._log()
        self._finished = True
        self.on_finish()
        self._break_cycles()
    
    @classmethod
    def generate_random_string(cls, N):
        return ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=N))
    def generate_request_id(self, *, search_in_query:bool = False):
        _from_query = self.get_query_argument('requuid', None)
        if (search_in_query and _from_query):
            return _from_query
        else:
            return "{0:x}".format(random.randint(0, 0xffffff))
    
    # def _log(self):
    #     if (self.get_status() < 400):
    #         log_method = self.logger.info
    #     elif (self.get_status() < 500):
    #         log_method = self.logger.warning
    #     else:
    #         log_method = self.logger.error
    #     request_time = 1000.0 * self.request.request_time()
    #     log_method("%d %s %.2fms", self.get_status(), self._request_summary(), request_time, style='%', prefix='resp')
