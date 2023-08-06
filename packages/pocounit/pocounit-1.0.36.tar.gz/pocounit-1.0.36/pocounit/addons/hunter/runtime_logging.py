# coding=utf-8
from __future__ import unicode_literals

from pocounit.addons import PocoUnitAddon
from hunter_cli.device_output import trace


class AppRuntimeLogging(PocoUnitAddon):
    def __init__(self, hunter):
        self.hunter = hunter
        self.logger = None

    def initialize(self, Case):
        self.logger = Case.get_result_emitter('appRuntimeLog')
        central_server_url = 'http://hunter.nie.netease.com/webterm'
        trace(self.hunter.tokenid, self.hunter.device_info['id'], central_server_url, self.on_app_runtime_log)

    def on_app_runtime_log(self, data):
        content = '[{data[level]}] {data[data]}\n'.format(data=data)
        self.logger.log(content)
