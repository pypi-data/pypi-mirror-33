#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import subprocess
from public import public


class Response:
    cmd = None
    code = None
    out = None
    err = None

    def __init__(self, cmd, code, out, err, **kwargs):
        self.cmd = cmd
        self.out = out.rstrip()
        self.err = err.rstrip()
        self.code = code

    def _raise(self):
        if not self.ok:
            output = self.err
            if not self.err:
                output = self.out
            if output:
                raise OSError("%s exited with code %s\n%s" % (self.cmd, self.code, output))
            raise OSError("%s exited with code %s" % (self.cmd, self.code))
        return self

    @property
    def text(self):
        return "\n".join(filter(None, [self.out, self.err]))

    @property
    def ok(self):
        return self.code == 0

    def __bool__(self):
        return self.ok

    def __non_zero__(self):
        return self.ok

    def __str__(self):
        return "<Response code=%s>" % self.code


class Command:
    custom_popen_kwargs = None

    def __init__(self, **popen_kwargs):
        self.custom_popen_kwargs = dict(popen_kwargs)

    @property
    def _default_popen_kwargs(self):
        return {
            'env': os.environ.copy(),
            'stdin': subprocess.PIPE,
            'stdout': subprocess.PIPE,
            'stderr': subprocess.PIPE,
            'shell': False,
            'universal_newlines': True,
            'bufsize': 0
        }

    @property
    def popen_kwargs(self):
        kwargs = self._default_popen_kwargs
        kwargs.update(self.custom_popen_kwargs)
        return kwargs

    def run(self, args, cwd=None, env=None, background=False):
        kwargs = self.popen_kwargs
        process = subprocess.Popen(args, **kwargs)
        code, stdoutdata, stderrdata = None, "", ""
        if not background:
            stdoutdata, stderrdata = process.communicate()
            code = process.returncode
        response = Response(cmd=args, code=code, out=stdoutdata, err=stderrdata)
        return response


@public
def run(args, cwd=None, env=None, background=False):
    return Command().run(args, cwd=cwd, env=env, background=background)
