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
        ],
        "calls": {"test_call1": {"AAA": 123}},
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
        del self.config["api"]["ratelimit"]  # bors field unused by nombot
        config = NomConfSchema().load(self.config).data["conf"]
        self.assertDictEqual(config, self.config)

    def test_config_load(self):
        """Test the load of a configuration"""
        config = NomAppConf(self.config).raw_conf
        self.assertDictEqual(config, self.config)

    def test_get_currencies(self):
        """Test the schema definition"""
        config = NomAppConf(self.config)
        self.assertListEqual(config.get_currencies(),
                             self.config["currencies"])

    def test_get_service_currencies(self):
        """Test the schema definition"""
        config = NomAppConf(self.config)

        start_curr = self.config["api"]["services"][0]["currencies"] + \
            self.config["currencies"]
        result_curr = config.get_currencies("test_service")

        self.assertListEqual(start_curr, result_curr)

    def test_get_global_currencies_from_service(self):
        """If no service currencies, return only global"""
        self.config["api"]["services"][0]["currencies"]
        del self.config["api"]["services"][0]["currencies"]
        config = NomAppConf(self.config)

        start_curr = self.config["currencies"]
        result_curr = config.get_currencies("test_service")

        self.assertListEqual(start_curr, result_curr)
