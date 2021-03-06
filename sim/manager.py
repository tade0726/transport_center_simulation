# -*- coding: utf-8 -*-


"""
Author: Ted
Date: 2017-07-13
des:
    main_demo.py

notes:
    恢复到一个正常的版本号

"""


import simpy
from datetime import datetime, timedelta
import pandas as pd
from collections import defaultdict

from queue import Queue
import threading

from sim.db import *
from sim.controllers import TruckController, ResourceController
from sim.utils import *
from sim.vehicles import Pipeline, PipelineRes, BasePipeline,PipelineReplace
from sim.machine import *
from sim.config import MainConfig, TimeConfig, LOG


__all__ = ["main"]


def simulation(data_pipeline: Queue, run_time):

    # start time
    t_start = run_time

    # simpy env init
    env = simpy.Environment()
    # init trucks queues
    trucks_queue = simpy.FilterStore(env)
    done_trucks_queue = simpy.Store(env)

    LOG.logger_font.info("loading config data")

    # raw data prepare
    pipelines_table = get_pipelines()
    unload_setting_dict = get_unload_setting()
    reload_setting_dict = get_reload_setting()
    resource_table = get_resource_limit()
    equipment_resource_dict = get_resource_equipment_dict()
    equipment_process_time_dict = get_equipment_process_time()
    equipment_parameters = get_parameters()
    equipment_store_dict = get_equipment_store_dict()
    open_time_dict, switch_machine_names = get_equipment_timetable()
    equipment_ports_type_dict = get_equipment_port_type()

    # all ports
    all_ports = list()
    for x in equipment_ports_type_dict.values():
        all_ports.extend(x)

    # init resource
    resource_dict = defaultdict(dict)
    for _, row in resource_table.iterrows():
        resource_id = row['resource_id']
        process_time = row['process_time']
        # 设置资源为理论最大值，以便进行动态修改
        resource_max = row['resource_number']
        resource_dict[resource_id]["resource"] = simpy.PriorityResource(env=env, capacity=resource_max)
        resource_dict[resource_id]["process_time"] = process_time

    # init share store
    share_store_dict = dict()
    for x in set([x['store_id'] for x in equipment_store_dict.values()]):
        share_store_dict[x] = simpy.Store(env)

    # init share queue
    share_queue_dict = dict()
    for x in all_ports:
        share_queue_dict[x] = simpy.Store(env)

    # init pipelines
    pipelines_dict = dict()
    for _, row in pipelines_table.iterrows():
        pipeline_type = row["pipeline_type"]
        machine_type = row['machine_type']
        queue_id = row['queue_id']
        delay_time = row['process_time']
        pipeline_id = row['equipment_port_last'], row['equipment_port_next']

        equipment_name = row['equipment_port_next'][0]
        all_keep_open = True if equipment_name not in switch_machine_names else False

        if pipeline_type == "pipeline":
            pipelines_dict[pipeline_id] = Pipeline(env,
                                                   delay_time,
                                                   pipeline_id,
                                                   queue_id,
                                                   machine_type,
                                                   open_time_dict,
                                                   all_keep_open,
                                                   share_queue_dict)

        elif pipeline_type == 'pipeline_res':
            pipelines_dict[pipeline_id] = PipelineRes(env,
                                                      resource_dict,
                                                      equipment_resource_dict,
                                                      delay_time,
                                                      pipeline_id,
                                                      queue_id,
                                                      machine_type,
                                                      equipment_process_time_dict,
                                                      open_time_dict,
                                                      all_keep_open,
                                                      share_queue_dict)

        elif pipeline_type == 'pipeline_replace':
            pipelines_dict[pipeline_id] = PipelineReplace(env,
                                                          delay_time,
                                                          pipeline_id,
                                                          queue_id,
                                                          machine_type,
                                                          share_store_dict,
                                                          equipment_store_dict,
                                                          open_time_dict,
                                                          all_keep_open,
                                                          share_queue_dict)
        else:
            raise ValueError("Pipeline init error!!")

    # for unload error
    pipelines_dict["unload_error"] = BasePipeline(env,
                                                  pipeline_id="unload_error",
                                                  equipment_id="unload_error",
                                                  machine_type="error")

    # for unload error
    pipelines_dict["error"] = BasePipeline(env,
                                           pipeline_id="error",
                                           equipment_id="error",
                                           machine_type="error")

    # for small sort bin
    pipelines_dict["small_bag_done"] = BasePipeline(env,
                                                    pipeline_id="small_bag_done",
                                                    equipment_id="small_bag_done",
                                                    machine_type="small_bag_done",
                                                    is_record=False)

    # for small_primary_error
    pipelines_dict["small_primary_error"] = BasePipeline(env,
                                                         pipeline_id="small_primary_error",
                                                         equipment_id="small_primary_error",
                                                         machine_type="error",
                                                         is_record=True)  # data will be collected

    # for small_reload_error
    pipelines_dict["small_reload_error"] = BasePipeline(env,
                                                        pipeline_id="small_reload_error",
                                                        equipment_id="small_reload_error",
                                                        machine_type="error",
                                                        is_record=True)  # data will be collected

    # prepare init machine dict
    machine_init_dict = defaultdict(list)
    for pipeline_id, pipeline in pipelines_dict.items():
        machine_init_dict[pipeline.machine_type].append(pipeline_id)

    # init unload machines
    machines_dict = defaultdict(list)

    for equipment_port, truck_types in unload_setting_dict.items():
        machines_dict["unload"].append(
            Unload(env,
                   equipment_port=equipment_port,
                   unload_setting_dict=unload_setting_dict,
                   reload_setting_dict=reload_setting_dict,
                   trucks_q=trucks_queue,
                   done_trucks_q=done_trucks_queue,
                   pipelines_dict=pipelines_dict,
                   resource_dict=resource_dict,
                   equipment_resource_dict=equipment_resource_dict,
                   equipment_parameters=equipment_parameters,
                   open_time_dict=open_time_dict, )
        )

    # init presort machines
    for equipment_port in equipment_ports_type_dict["presort"]:
        machines_dict["presort"].append(
            Presort(env,
                    equipment_port=equipment_port,
                    pipelines_dict=pipelines_dict,
                    resource_dict=resource_dict,
                    equipment_resource_dict=equipment_resource_dict,
                    share_queue_dict=share_queue_dict,
            )
        )

    # init cross machines
    for equipment_port in equipment_ports_type_dict["cross"]:
        machines_dict["cross"].append(
            Cross(
                env,
                equipment_port=equipment_port,
                pipelines_dict=pipelines_dict,
                resource_dict=resource_dict,
                equipment_resource_dict=equipment_resource_dict,
                share_queue_dict=share_queue_dict,
            )
        )

    # init secondary_sort machines
    for equipment_port in equipment_ports_type_dict["secondary_sort"]:
        machines_dict["secondary_sort"].append(
            SecondarySort(
                env,
                equipment_port=equipment_port,
                pipelines_dict=pipelines_dict,
                share_queue_dict=share_queue_dict,
            )
        )

    # init hospital machines
    for equipment_port in equipment_ports_type_dict["hospital"]:
        machines_dict["hospital"].append(
            Hospital(
                env,
                equipment_port=equipment_port,
                pipelines_dict=pipelines_dict,
                resource_dict=resource_dict,
                equipment_resource_dict=equipment_resource_dict,
                share_queue_dict=share_queue_dict,
            )
        )

    # init security machines
    for equipment_port in equipment_ports_type_dict["security"]:
        machines_dict["security"].append(
            Security(
                env,
                equipment_port=equipment_port,
                pipelines_dict=pipelines_dict,
                resource_dict=resource_dict,
                equipment_resource_dict=equipment_resource_dict,
                share_queue_dict=share_queue_dict,
            )
        )

    # init small_primary machines
    for equipment_port in equipment_ports_type_dict["small_primary"]:
        machines_dict["small_primary"].append(
            SmallPrimary(
                env,
                equipment_port=equipment_port,
                pipelines_dict=pipelines_dict,
                resource_dict=resource_dict,
                equipment_resource_dict=equipment_resource_dict,
                share_queue_dict=share_queue_dict,
            )
        )

    # init small_secondary machines
    for equipment_port in equipment_ports_type_dict["small_secondary"]:
        machines_dict["small_secondary"].append(
            SecondarySort(
                env,
                equipment_port=equipment_port,
                pipelines_dict=pipelines_dict,
                share_queue_dict=share_queue_dict,
            )
        )

    # init small_reload machines
    for equipment_port in equipment_ports_type_dict['small_reload']:
        machines_dict["small_reload"].append(
            SmallReload(
                env,
                equipment_port=equipment_port,
                pipelines_dict=pipelines_dict,
                equipment_process_time_dict=equipment_process_time_dict,
                equipment_parameters=equipment_parameters,
                data_pipeline=data_pipeline,
                share_queue_dict=share_queue_dict,
            )
        )

    # adding machines into processes
    def setup_process_start():

        for machine_type, machines in machines_dict.items():
            LOG.logger_font.info(f"init {machine_type} machines")
            for machine in machines:
                env.process(machine.run())

        for pipeline in pipelines_dict.values():
            if isinstance(pipeline, Pipeline):
                env.process(pipeline.run())

        env.run()

    # init trucks controllers
    LOG.logger_font.info("init controllers")
    truck_controller = TruckController(env,
                                       trucks=trucks_queue,
                                       is_test=MainConfig.IS_TEST,
                                       is_parcel_only=MainConfig.IS_PARCEL_ONLY,
                                       is_land_only=MainConfig.IS_LAND_ONLY,
                                       data_pipeline=data_pipeline)
    truck_controller.controller()

    # init resource controller
    resource_controller = ResourceController(env,
                                             resource_dict,)
    resource_controller.controller()

    LOG.logger_font.info("init resource machine controllers..")
    LOG.logger_font.info("sim start..")

    # setup
    setup_process_start()

    data_pipeline.put(None)

    num_of_trucks = len(trucks_queue.items)
    LOG.logger_font.info(f"{num_of_trucks} trucks leave in queue")
    assert num_of_trucks == 0, ValueError("Truck queue should be empty!!")

    LOG.logger_font.info("sim end..")
    t_end = datetime.now()
    total_time = t_end - t_start
    LOG.logger_font.info(f"total time: {total_time.total_seconds()} s")


def pumper(data_pipeline: Queue, write_rows: int=10_000,):

    QUEUE_DONE = False

    while True:

        machine_data = list()
        pipeline_data = list()
        truck_data = list()
        path_data = list()

        for _ in range(write_rows):

            record = data_pipeline.get()
            if record is None:
                # leave for loop
                QUEUE_DONE = True
                data_pipeline.put(None)
                break

            if isinstance(record, PackageRecord):
                machine_data.append(record)
            elif isinstance(record, PipelineRecord):
                pipeline_data.append(record)
            elif isinstance(record, TruckRecord):
                truck_data.append(record)
            elif isinstance(record, PathRecord):
                path_data.append(record)
            else:
                raise ValueError("Wrong record in data pipeline!!")

        # time stamp for db
        db_insert_time = run_time

        # output machine table only
        if MainConfig.OUTPUT_MACHINE_TABLE_ONLY:
            machine_table = pd.DataFrame.from_records(machine_data, columns=PackageRecord._fields, )
            machine_table = add_time(machine_table)
            write_mysql("machine_table", machine_table, OutputTableColumnType.package_columns)

        else:
            truck_table = pd.DataFrame.from_records(truck_data, columns=TruckRecord._fields, )
            pipeline_table = pd.DataFrame.from_records(pipeline_data, columns=PipelineRecord._fields, )
            machine_table = pd.DataFrame.from_records(machine_data, columns=PackageRecord._fields, )
            path_table = pd.DataFrame.from_records(path_data, columns=PathRecord._fields, )

            truck_table = add_time(truck_table)
            pipeline_table = add_time(pipeline_table)
            machine_table = add_time(machine_table)
            path_table["run_time"] = db_insert_time

            write_mysql("machine_table", machine_table, OutputTableColumnType.package_columns)
            write_mysql("pipeline_table", pipeline_table, OutputTableColumnType.pipeline_columns)
            write_mysql("truck_table", truck_table, OutputTableColumnType.truck_columns)
            write_mysql('path_table', path_table, OutputTableColumnType.path_columns)

        # process data
        LOG.logger_font.info(msg="inserted data to mysql ..")

        # 结束 while True
        if QUEUE_DONE:
            break


def add_time(table: pd.DataFrame):
    """添加仿真的时间戳， 以及运行的日期"""
    table["real_time_stamp"] = table["time_stamp"].apply(lambda x: TimeConfig.ZERO_TIMESTAMP + timedelta(seconds=x))
    table["run_time"] = run_time
    return table


def create_tables():
    # create table for output data
    machine_table_sche.create(checkfirst=True)

    if not MainConfig.OUTPUT_MACHINE_TABLE_ONLY:
        truck_table_sche.create(checkfirst=True)
        pipeline_table_sche.create(checkfirst=True)
        path_table_sche.create(checkfirst=True)


def main(run_time):

    create_tables()
    data_pipeline_queue = Queue()

    threads = []

    sim = threading.Thread(target=simulation, args=(data_pipeline_queue, run_time))
    sim.start()

    for _ in range(3):
        p = threading.Thread(target=pumper, args=(data_pipeline_queue, 100_000))
        threads.append(p)

    for p in threads:
        p.start()

    for p in threads:
        p.join()

    LOG.logger_font.info(f"All Done.")


if __name__ == '__main__':

    run_time = datetime.now()
    main(run_time)



