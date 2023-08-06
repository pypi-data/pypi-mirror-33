#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test the `bors` configuration overrides"""


import unittest

from nombot.app.config import NomAppConf
from nombot.generics.config import NomConfSchema


DEFAULT_TEST_CONFIG = {
    "currencies": ["BTC", "USD", "USDT"],
    "api": {
        "ratelimit": 1,
        "calls": {"test_call1": {"AAA": 123}},
        "services": [
            {
                "name": "test_service",
                "currencies": ["BTC", "ETH", "XRP"],
                "credentials": [
                    {
                        "name": "test_api_name",
                        "apiKey": "test_key",
                        "secret": "test_secret",
                    },
                ],
                "subscriptions": {"TICKER_X": "ticker"},
                "exchanges": ["bittrex", "coinbase"],
                "endpoints": {
                    "rest": "rest_url",
                    "websocket": "sock_url",
                },
            },
        ]
    },
    "log_level": "INFO",
}


class TestConfig(unittest.TestCase):
    """Tests for nombot configuration parser"""

    def setUp(self):
        """Set up test fixtures, if any"""
        self.config = DEFAULT_TEST_CONFIG.copy()

    def tearDown(self):
        """Tear down test fixtures, if any"""

    def test_schema(self):
        """Test the schema definition"""
        assert NomConfSchema().load(self.config).data["conf"] == self.config

    def test_config_load(self):
        """Test the schema definition"""
        assert NomAppConf(self.config).raw_conf == self.config
