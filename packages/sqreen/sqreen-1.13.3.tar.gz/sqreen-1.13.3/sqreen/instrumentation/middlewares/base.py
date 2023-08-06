# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Base middleware for peripheric frameworks integration
"""
import logging

from ...constants import ACTIONS
from ...exceptions import ActionBlock, ActionRedirect, AttackBlocked
from ...rules import RuleCallback
from ...runtime_storage import runtime
from ..hook_point import (
    execute_failing_callbacks,
    execute_post_callbacks,
    execute_pre_callbacks,
)

LOGGER = logging.getLogger(__name__)


class BaseMiddleware(object):
    """ Middleware base class for frameworks middleware hooks
    """

    def __init__(self, strategy, observation_queue, queue):
        LOGGER.debug("%s for %s", self.__class__.__name__, strategy)
        self.strategy = strategy
        self.observation_queue = observation_queue
        self.queue = queue

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, repr(self.strategy))

    @classmethod
    def _record_http_code(cls, http_code):
        # With some frameworks (Flask, Pyramid, aiohttp), raising an exception
        # here will not result in failing callbacks being executed.
        RuleCallback.record_observation("http_code", str(http_code), 1)

    def execute_pre_callbacks(self, args=None, record_attack=False):
        """ Execute pre callbacks with None original and args. Only process
        valid action, in this context it's raising.
        """
        action = execute_pre_callbacks(
            self.strategy.strategy_key, self.strategy, original=None, args=args
        )

        action_status = action.get("status")

        if not action_status:
            return

        if action_status == ACTIONS["RAISE"]:
            LOGGER.debug(
                "Callback %s detected an attack", action.get("rule_name")
            )
            if record_attack is True:
                self._record_http_code(runtime.attack_http_code)
            raise AttackBlocked(action.get("rule_name"))

        elif action_status == ACTIONS["ACTION_BLOCK"]:
            if record_attack is True:
                self._record_http_code(runtime.attack_http_code)
            raise ActionBlock(action.get("action_id"))

        elif action_status == ACTIONS["ACTION_REDIRECT"]:
            if record_attack is True:
                self._record_http_code(303)
            raise ActionRedirect(action.get("action_id"), action["target_url"])

        else:
            LOGGER.warning("Invalid action status %s", action_status)

    def execute_post_callbacks(self, response, args=None, record_attack=False):
        """ Execute post callbacks with None original and args. Only process
        valid action, in this context it's raising.
        """
        action = execute_post_callbacks(
            self.strategy.strategy_key,
            self.strategy,
            original=None,
            result=response,
            args=args,
        )

        action_status = action.get("status")

        if not action_status:
            return response

        if action_status == ACTIONS["RAISE"]:
            LOGGER.debug(
                "Callback %s detected an attack", action.get("rule_name")
            )

            if record_attack is True:
                self._record_http_code(runtime.attack_http_code)

            raise AttackBlocked(action.get("rule_name"))
        else:
            LOGGER.warning("Invalid action status %s", action_status)

        return response

    def execute_failing_callbacks(self, exception, args=None):
        """ Execute failing callbacks with None original and args. Only process
        valid action, in this context it's None.
        """
        action = execute_failing_callbacks(
            self.strategy.strategy_key,
            self.strategy,
            original=None,
            exc_infos=exception,
            args=args,
        )

        action_status = action.get("status")

        if not action_status:
            return

        LOGGER.warning("Invalid action status %s", action_status)
