# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
"""Actions for security responses."""

import logging
from collections import defaultdict
from time import time

from .list_filters import IPNetworkListFilter

LOGGER = logging.getLogger(__name__)


class ActionName(object):
    """Enumeration of action names."""

    BLOCK_IP = "block_ip"
    REDIRECT_IP = "redirect_ip"
    BLOCK_USER = "block_user"


_AVAILABLE_ACTIONS = {}


def register_action(name):
    """Decorator function to register an action."""

    def decorator(action_cls):
        _AVAILABLE_ACTIONS[name] = action_cls
        action_cls.name = name
        return action_cls

    return decorator


class BaseAction(object):
    """Base class for actions."""

    name = None

    def __init__(self, iden, params, duration=None, send_response=True):
        self.iden = iden
        self.params = params
        self.duration = duration
        if duration is not None:
            self.timeout = time() + duration
        else:
            self.timeout = None
        self.send_response = send_response

    def __repr__(self):
        return "{}({!r}, {!r}, {!r}, {!r})".format(
            self.__class__.__name__,
            self.iden,
            self.params,
            self.duration,
            self.send_response,
        )

    def to_dict(self):
        """Convert the action into a dict."""
        return {
            "action": self.name,
            "action_id": self.iden,
            "parameters": self.params,
            "duration": self.duration,
            "send_response": self.send_response,
        }


@register_action(ActionName.BLOCK_IP)
class BlockIPAction(BaseAction):
    """Deny access based on IP blacklist."""

    def __init__(self, *args, **kwargs):
        super(BlockIPAction, self).__init__(*args, **kwargs)
        self.ip_networks = IPNetworkListFilter(self.params["ip_cidr"])


@register_action(ActionName.REDIRECT_IP)
class RedirectIPAction(BlockIPAction):
    """Redirect an IP address on a given URL."""

    def __init__(self, *args, **kwargs):
        super(RedirectIPAction, self).__init__(*args, **kwargs)
        self.target_url = self.params["url"]


@register_action(ActionName.BLOCK_USER)
class BlockUserAction(BaseAction):
    """Block an authentified user."""

    def __init__(self, *args, **kwargs):
        super(BlockUserAction, self).__init__(*args, **kwargs)
        self.users = self.params["users"]


class UnsupportedAction(Exception):
    """Exception raised when an action is not supported."""

    def __init__(self, action_name):
        self.action_name = action_name


def action_from_dict(data):
    """Load an action from a dict."""
    action_name = data["action"]
    if action_name not in _AVAILABLE_ACTIONS:
        raise UnsupportedAction(action_name)
    action_cls = _AVAILABLE_ACTIONS[action_name]
    action = action_cls(
        iden=data.get("action_id"),
        params=data.get("parameters"),
        duration=data.get("duration"),
        send_response=data.get("send_response", True),
    )
    return action


class ActionStore:
    """A store to manage all actions."""

    def __init__(self):
        self._actions = defaultdict(list)

    def clear(self):
        """Remove all actions from the store."""
        self._actions.clear()

    def add(self, action):
        """Add an action to the store."""
        self._actions[action.name].append(action)

    def _delete_expired(self, action_name, now):
        """Delete expired actions with name *action_name*."""
        self._actions[action_name] = [
            action
            for action in self._actions[action_name]
            if not action.timeout or action.timeout >= now
        ]

    def _get_for_ip(self, action_name, ip, now):
        """Return the action matching an IP address, or None."""
        self._delete_expired(action_name, now)
        for action in self._actions[action_name]:
            if action.ip_networks.match(ip):
                return action
        return None

    def get_for_ip(self, ip):
        """Return the action matching an IP address, or None."""
        now = time()
        action = self._get_for_ip(
            ActionName.BLOCK_IP, ip, now
        ) or self._get_for_ip(ActionName.REDIRECT_IP, ip, now)
        return action

    def get_for_user(self, user_dict):
        """Return the action matching the given user, or None."""
        self._delete_expired(ActionName.BLOCK_USER, time())
        for action in self._actions[ActionName.BLOCK_USER]:
            for action_user in action.users:
                if action_user == user_dict:
                    return action
        return None

    def reload_from_dicts(self, data):
        """Reload actions from a list of dicts.

        Unsupported actions are skipped and logged but do not trigger an error.
        The list of their names is returned at the end.
        """
        self.clear()
        unsupported = []
        for action_data in data:
            try:
                action = action_from_dict(action_data)
            except UnsupportedAction:
                unsupported.append(action_data["action"])
            else:
                LOGGER.debug("Adding action %r" % action_data)
                self.add(action)
        if unsupported:
            LOGGER.error("Skipped unsupported actions: %r", unsupported)
        return unsupported


ACTION_STORE = ActionStore()
