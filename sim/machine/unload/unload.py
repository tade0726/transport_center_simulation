# -*- coding: utf-8 -*-


"""
author: Ted
date: 2017-07-11
des:

unload modules
"""

import simpy
import numpy as np

from collections import defaultdict
from sim.vehicles import Package, Truck
from sim.config import LOG
from sim.utils import PackageRecordDict, TruckRecordDict


class Unload:

    def __init__(self,
                 env: simpy.Environment,
                 equipment_port: str,
                 unload_setting_dict: dict,
                 reload_setting_dict: dict,
                 trucks_q: simpy.FilterStore,
                 done_trucks_q: simpy.Store,
                 pipelines_dict: dict,
                 resource_dict: defaultdict,
                 equipment_resource_dict: dict,
                 equipment_parameters: dict,
                 open_time_dict: dict,
                 all_keep_open:bool = False,
                 ):

        self.env = env
        self.equipment_port = equipment_port
        self.unload_setting_dict = unload_setting_dict
        self.reload_setting_dict = reload_setting_dict
        self.trucks_q = trucks_q
        self.done_trucks_q = done_trucks_q
        self.pipelines_dict = pipelines_dict
        self.resource_dict = resource_dict
        self.equipment_resource_dict = equipment_resource_dict
        self.equipment_parameters = equipment_parameters

        # add machine switch
        self.resource_set = self._set_machine_resource()

        # open close time table
        self.open_time = open_time_dict.get(self.equipment_port, [])
        self.open_time_save = tuple(self.open_time)

        # keep open all the time
        self.keep_open = all_keep_open

    def _set_machine_resource(self):
        """"""
        if self.equipment_resource_dict:
            self.equipment_name = self.equipment_port.split('_')[0] # r1, ect
            self.resource_id = self.equipment_resource_dict[self.equipment_port]
            self.resource = self.resource_dict[self.resource_id]['resource']
            self.process_time = self.resource_dict[self.resource_id]['process_time']
            self.truck_types = self.unload_setting_dict[self.equipment_port]
            self.vehicle_turnaround_time = self.equipment_parameters[self.equipment_name]["vehicle_turnaround_time"]

        else:
            raise RuntimeError('unload machine',
                               self.equipment_port,
                               'not initial equipment_resource_dict!')

    def process_package(self, package: Package):
        """处理单个包裹"""
        with self.resource.request() as req:
            yield req

            package.insert_data(
                PackageRecordDict(
                    equipment_id=self.equipment_port,
                    time_stamp=self.env.now,
                    action="start", ))

            yield self.env.timeout(self.process_time)

            package.insert_data(
                PackageRecordDict(
                    equipment_id=self.equipment_port,
                    time_stamp=self.env.now,
                    action="end", ))

            # deal with nc parcel
            if package.attr['parcel_type'] == 'nc':
                self.pipelines_dict["unload_error"].put(package)
            else:
                # error package store in
                try:
                    package.set_path(package_start=self.equipment_port)
                    self.pipelines_dict[package.next_pipeline].put(package)
                except Exception as exc:
                    msg = f"error: {exc}, package: {package}, reload_port: {self.equipment_port}"
                    LOG.logger_font.error(msg)
                    LOG.logger_font.exception(exc)
                    self.pipelines_dict["unload_error"].put(package)

    def process_truck(self, truck: Truck):

        """process one truck"""

        # truck start
        truck.insert_data(
            TruckRecordDict(
                equipment_id=self.equipment_port,
                time_stamp=self.env.now,
                action="start", ))

        packages = truck.get_all_package()

        events_processes = list()

        for package in packages:

            # add package wait data
            package.insert_data(
                PackageRecordDict(
                    equipment_id=self.equipment_port,
                    time_stamp=truck.come_time,
                    action="wait", ))

            events_processes.append(self.env.process(self.process_package(package)))

        # all packages are processed
        yield self.env.all_of(events_processes)

        # truck end
        truck.insert_data(
            TruckRecordDict(
                equipment_id=self.equipment_port,
                time_stamp=self.env.now,
                action="end", ))

        # truck is out
        self.done_trucks_q.put(truck)

    def run(self):
        yield self.env.timeout(0)

        if self.keep_open:
            self.env.process(self.all_run())

        else:
            for start, end in self.open_time:
                self.env.process(self.real_run(start, end))

    def all_run(self):
        while True:
            truck = yield self.trucks_q.get(lambda x: x.truck_type in self.truck_types)
            self.trucks_q.put(truck)
            # 等待货车处理完
            yield self.env.process(self.process_truck(truck))
            # vehicle turnaround time
            yield self.env.timeout(self.vehicle_turnaround_time)

    def real_run(self, start, end):

        yield self.env.timeout(start)

        while True:

            # filter out the match truck(LL/LA/AL/AA)
            truck = yield self.trucks_q.get(lambda x: x.truck_type in self.truck_types)
            LOG.logger_font.debug(f"sim time: {self.env.now}, get truck {truck}, unload_port: {self.equipment_port}")

            if self.env.now > end:
                self.trucks_q.put(truck)
                LOG.logger_font.debug(f"sim time: {self.env.now}, put back truck {truck}, unload_port: {self.equipment_port}")
                self.env.exit()

            # 等待货车处理完
            yield self.env.process(self.process_truck(truck))
            # vehicle turnaround time
            yield self.env.timeout(self.vehicle_turnaround_time)


