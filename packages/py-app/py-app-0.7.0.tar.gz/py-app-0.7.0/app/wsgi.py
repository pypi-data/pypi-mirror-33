#
# Copyright (c) 2018 Eric Faurot <eric@faurot.net>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#
import importlib
import os
import time

import bottle


def run_bottle(app, **kwargs):
    bottle.run(app = app, quiet = True, **kwargs)


_apis = {}
def api(path):
    def _(setup):
        _apis[setup] = path
        return setup
    return _

class APIStack(object):

    def __init__(self, prefix = "/"):
        self.app = bottle.Bottle()
        self.prefix = prefix

    def _install(self, mount_point, setup):
        app = bottle.Bottle()
        setup(app)
        self.app.mount(mount_point, app)
        return app

    def install(self, module_name):
        module = importlib.import_module(module_name)
        for key, obj in module.__dict__.items():
            if callable(obj) and obj in _apis:
                prefix = self.prefix + _apis.get(obj) + "/"
                self._install(prefix, obj)

    def __call__(self, environ, handler):
        return self.app(environ, handler)


class EnvMiddleware(object):

    def __init__(self, app, environ = None):
        self.app = app
        self.environ = {} if environ is None else environ

    def setenv(self, key, value):
        self.environ[key] = value

    def __call__(self, environ, handler):
        environ.update(self.environ)
        return self.app(environ, handler)


class LogMiddleware(object):

    timestamp = 0
    delay = 1.0

    def __init__(self, app, logger, stream):
        self.app = app
        self.logger = logger
        self.stream = stream

    def __call__(self, environ, handler):
        t0 = time.time()
        environ['wsgi.errors'] = self
        ret = self.app(environ, handler)
        try:
            scheme, host, path, query_string, fragment = bottle.request.urlparts
            self.logger.info("%.3f %s %s %s %d %d %s %s",
                             time.time() - t0,
                             environ["REMOTE_ADDR"],
                             environ.get("HTTP_X_FORWARDED_FOR", "-"),
                             bottle.request.method,
                             bottle.response.status_code,
                             bottle.response.content_length,
                             host,
                             bottle.request.path)
        except Exception as exc:
            self.logger.error("Failed to log result", exc_info = exc)
        return ret

    def write(self, err):
        try:
            timestamp = time.time()
            if timestamp - self.timestamp > self.delay:
                self.stream.write("-------- %s\n" % time.ctime())
                self.timestamp = timestamp
            self.stream.write(err)
            self.stream.flush()
        except Exception as exc:
            self.logger.error("Failed to log WSGI error", exc_info = exc)

def abort(code, message):
    bottle.abort(code, message)

class Form(object):

    def __init__(self, request = None):
        if request is None:
            request = bottle.request
        self.request = request

    def raw(self, name):
        return self.request.forms.get(name)

    def string(self, name):
        return self.raw(name)

    def integer(self, name):
        return int(self.raw(name))

    def float(self, name):
        return float(self.raw(name))

    def date(self, name, fmt = "%d/%m/%Y"):
        return datetime.datetime.strptime(self.raw(name), fmt)

    def file(self, name):
        if name not in self.request.files:
            return None, None
        value = self.request.files[name]
        filename = os.path.basename(value.filename)
        return value.file, filename

_mandatory = object()
_unset = object()
class Parameters(object):

    def __init__(self, params):
        if not isinstance(params, dict):
            abort(400, 'Expect parameter object')
        self.params = params

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if (type, value, traceback) == (None, None, None):
            if self.params:
                abort(400, 'Unexpected parameter(s): %s' % ', '.join(self.params.keys()))

    def get(self, name, default, validate):
        value = self.params.pop(name, _unset)

        if value is _unset:
            if default is not _mandatory:
                return default
            abort(400, 'Missing parameter %s' % (name, ))

        if validate:
            try:
                validate(value)
            except TypeError as e:
                abort(400, 'Invalid parameter type: %s: %s' % (name, str(e)))
            except ValueError as e:
                abort(400, 'Invalid parameter value: %s: %s' % (name, str(e)))
        return value

    def get_list(self, name, default, validate, maxlen):
        def _(v):
            if not isinstance(v, list):
                raise TypeError('expect list')
            if maxlen is not None and len(v) > maxlen:
                raise ValueError('list too long')
            if validate:
                for e in v:
                    validate(e)
        return self.get(name, default, _)

    def any(self, name, default = _mandatory, validate = None):
        return self.get(name, default, validate)

    def string(self, name, default = _mandatory, choice = None, validate = None):
        def _(v):
            if not isinstance(v, str):
                raise TypeError('expect string')
            if choice is not None and v not in choice:
                raise ValueError('not in set of possible values')
            if validate:
                validate(v)
        return self.get(name, default, _)

    def binary(self, name, default = _mandatory, maxlen = None, validate = None):
        def _(v):
            if not isinstance(v, str):
                raise TypeError('expect base64 string')
            if maxlen is not None and len(v) > maxlen * 4:
                raise ValueError('too long')
        v = self.get(name, default, _)
        try:
            v = base64.b64decode(v)
        except:
            raise ValueError('not properly base64-encoded')
        if maxlen is not None and len(v) > maxlen:
            raise ValueError('too long')
        if validate:
            validate(v)
        return v

    def integer(self, name, default = _mandatory, min = None, max = None):
        def _(v):
            if not isinstance(v, int):
                raise TypeError('expect integer')
            if min is not None and v < min:
                raise ValueError('too small')
            if max is not None and v > max:
                raise ValueError('too large')
        return self.get(name, default, _)

    def float(self, name, default = _mandatory, min = None, max = None):
        def _(v):
            if not isinstance(v, float):
                raise TypeError('expect float')
            if min is not None and v < min:
                raise ValueError('too small')
            if max is not None and v > max:
                raise ValueError('too large')
        return self.get(name, default, _)

    def boolean(self, name, default = _mandatory):
        def _(v):
            if not isinstance(v, bool):
                raise TypeError('expect boolean')
        return self.get(name, default, _)

    def string_list(self, name, default = _mandatory, maxlen = None, choice = None, validate =
 None):
        def _(v):
            if not isinstance(v, str):
                raise TypeError('expect list of strings')
            if choice is not None and v not in choice:
                raise ValueError('not in set of possible values')
            if validate:
                validate(v)
        return self.get_list(name, default, _, maxlen)

    def integer_list(self, name, default = _mandatory, maxlen = None):
        def _(v):
            if not isinstance(v, int):
                raise TypeError('expect list of integers')
        return self.get_list(name, default, _, maxlen)

    def any_list(self, name, default = _mandatory, validate = None, maxlen = None):
        return self.get_list(name, default, validate, maxlen)

    def timestamp(self, name, default = _mandatory, min = 0, max = None):
        if max is None:
            max = int(time.time()) + 3600 * 24 * 365
        return self.integer(name, default, min = min, max = max)

    def email(self, name, default = _mandatory):
        v = self.string(name, default)
        if v is not None:
            # XXX validate email?
            return v.strip().lower()

def _request_json(request):
    try:
        return request.json
    except ValueError:
        abort(400, 'Invalid JSON content')

def params(request = None):
    if request is None:
        request = bottle.request
    return Parameters(_request_json(request) or {})

def no_params(request = None):
    if request is None:
        request = bottle.request
    if _request_json(request):
        abort(400, 'No parameter expected')
