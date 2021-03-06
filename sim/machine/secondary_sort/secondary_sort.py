# -*- coding: utf-8 -*-

"""
==================================================================================================================================================
                                                     杭州HUB仿真项目

                                    项目启动日期：2017年7月6日
                                    项目启动标识：AIRPORT OF EZHOU'S PROJECT  -- HZ
                                    ===========================================
                                    代码创建日期：2017年7月6日
                                    代码创建工程师：韩蓝毅
                                    代码版本：1.0
                                    版本更新日期：2017年7月6日
                                    版本更新工程师：韩蓝毅

                                    代码整体功能描述：终分拣模块，
                                                      1、终分拣模拟



==================================================================================================================================================
"""


import simpy
from sim.config import LOG


class SecondarySort(object):

    def __init__(self,
                 env: simpy.Environment,
                 equipment_port: tuple,
                 pipelines_dict: dict,
                 share_queue_dict: dict,
                 ):

        self.env = env
        self.equipment_port = equipment_port
        self.pipelines_dict = pipelines_dict
        self.share_queue_dict = share_queue_dict

        self._set_machine()

    def _set_machine(self):
        """
        """
        self.input_pip_line = self.share_queue_dict[self.equipment_port]

    def run(self):
        while True:
            package = yield self.input_pip_line.get()
            try:
                self.pipelines_dict[package.next_pipeline].put(package)
            except Exception as exc:
                self.pipelines_dict['error'].put(package)
                msg = f"error: {exc}, package: {package}, equipment_id: {self.equipment_port}"
                LOG.logger_font.error(msg)
                LOG.logger_font.exception(exc)
