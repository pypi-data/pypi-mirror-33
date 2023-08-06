#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import typing

from flask import request, render_template, abort

from . import wsgi, controller


def add_route(path: str, ctrl: typing.Union[controller.Controller, typing.Type], methods=None):
    """
    add router class to system
    :param path: url (see Flask reference)
    :param ctrl: control class or class instance
    :param methods: http methods (optional)
    """
    if not isinstance(ctrl, controller.Controller):
        ctrl = ctrl()

    @wsgi.app.route(path, methods=methods)
    def router(**kwargs):
        method = request.method
        if method == "GET":
            res = ctrl.get(**kwargs)
        elif method == "POST":
            res = ctrl.post(**kwargs)
        elif method == "PUT":
            res = ctrl.put(**kwargs)
        elif method == "DELETE":
            res = ctrl.delete(**kwargs)
        else:
            return abort(405)

        if res is None or isinstance(res, controller.RenderParameter):
            view = ctrl.VIEW
            params = {}
            if res is not None:
                params = res.params
                if res.view is not None:
                    view = res.view

            res = render_template(view, **params)
        return res


def route(path: str, methods=None):
    """
    add router class to system as decorator
    :param path: url (see Flask reference)
    :param methods: http methods (optional)
    """
    def route_deco(cls):
        add_route(path, cls, methods=methods)
    return route_deco
