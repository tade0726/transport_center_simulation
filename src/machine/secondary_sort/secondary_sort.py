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
from src.utils import PackageRecord

class SecondarySort(object):

    def __init__(self,
                 env: simpy.Environment(),
                 machine_id: tuple,
                 pipelines_dict: dict,):

        self.env = env
        self.machine_id = machine_id
        self.pipelines_dict = pipelines_dict
        self._setting()

    def _setting(self):
        self.equipment_id = self.machine_id[1]
        self.last_pipeline = self.pipelines_dict[self.machine_id]

    def run(self):
        while True:
            package = yield self.last_pipeline.get()
            next_pipeline = package.next_pipeline

            # package start for process
            package.insert_data(
                PackageRecord(
                    equipment_id=self.equipment_id,
                    package_id=package.item_id,
                    time_stamp=self.env.now,
                    action="start", ))

            # package end for process
            package.insert_data(
                PackageRecord(
                    equipment_id=self.equipment_id,
                    package_id=package.item_id,
                    time_stamp=self.env.now,
                    action="end", ))

            self.pipelines_dict[next_pipeline].put(package)

