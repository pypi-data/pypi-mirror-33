from pycanvass.data_bridge import _node_search
import pycanvass.global_variables as gv
import pycanvass.resiliency as res
import pycanvass.blocks as blocks
import csv
import pandas as pd
import logging
import pycanvass.complexnetworks as cn
import os
from datetime import *


def create_timestamped_node_file(timestamp, node_to_modify, **kwargs):
    """
    d
    :param timestamp:
    :param node_to_modify:
    :param args:
    :return:
    """
    new_rows = []
    n_file = gv.filepaths["nodes"]

    node_search_result = _node_search(node_to_modify)
    if node_search_result == 0:
        return

    for k, v in kwargs.items():
        if k == "new_load":
            new_load_value = v
        if k == "new_gen":
            new_gen_value = v
    load_key = "new_load"
    gen_key = "new_gen"
    status_key = "new_status"
    with open(n_file, 'r+') as f:
        csvr = csv.reader(f)
        csvr = list(csvr)
        for row in csvr:
            new_row = row
            if row[0].lstrip() == node_to_modify.lstrip() or row[9].lstrip() == node_to_modify.lstrip():

                if load_key in kwargs:
                    new_row[5] = kwargs[load_key]

                if gen_key in kwargs:
                    new_row[6] = kwargs[gen_key]

            new_rows.append(new_row)

    new_node_filename = timestamp + "-temp-node-file.csv"
    logging.info("Creating a temporary load file called {}".format(new_node_filename))

    with open(new_node_filename, 'w+', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(new_rows)

    gv.filepaths["nodes"] = new_node_filename


def create_timestamped_edge_file(timestamp, edge_to_modify, **kwargs):
    """
    d
    :param timestamp:
    :param edge_to_modify:
    :param args:
    :return:
    """
    new_rows = []
    n_file = gv.filepaths["nodes"]

    node_search_result = _node_search(edge_to_modify)
    if node_search_result == 0:
        return

    for k, v in kwargs.items():
        if k == "new_load":
            new_load_value = v
        if k == "new_gen":
            new_gen_value = v
    load_key = "new_load"
    gen_key = "new_gen"
    status_key = "new_status"
    with open(n_file, 'r+') as f:
        csvr = csv.reader(f)
        csvr = list(csvr)
        for row in csvr:
            new_row = row
            if row[0].lstrip() == edge_to_modify.lstrip() or row[9].lstrip() == edge_to_modify.lstrip():

                if load_key in kwargs:
                    new_row[5] = kwargs[load_key]

                if gen_key in kwargs:
                    new_row[6] = kwargs[gen_key]

            new_rows.append(new_row)

    new_node_filename = timestamp + "-temp-node-file.csv"
    logging.info("Creating a temporary load file called {}".format(new_node_filename))


    with open(new_node_filename, 'w+', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(new_rows)

    gv.filepaths["nodes"] = new_node_filename


def edge_timeseries(datafile):
    """
    Create a folder for that creates a folder full of data for time-series simulation.
    :param datafile:
    :return:
    """
    timeseries_file_creation_step = 0

    logging.info("Building Time Series Models")
    df = pd.read_csv(datafile, skipinitialspace=True)
    # what columns are there in the file:
    fields = list(df)
    df = pd.read_csv(datafile, skipinitialspace=True, usecols=fields)
    size = df.shape

    for r in range(1, size[1]):
        timestamp = fields[0]
        colname = fields[r]
        for q in range(1, size[0]):
            timestamp_for_filename = str(df[timestamp][q]).replace(' ', '-').replace(':', '_').replace('/', '_')
            create_timestamped_node_file(timestamp_for_filename, colname, new_load=str(df[colname][q]))


def node_timeseries(datafile):
    """
    Create a folder for that creates a folder full of data for time-series simulation. 
    :param datafile:
    :return:
    """
    timeseries_file_creation_step = 0

    logging.info("Building Time Series Models")
    df = pd.read_csv(datafile, skipinitialspace=True)
    # what columns are there in the file:
    fields = list(df)
    df = pd.read_csv(datafile, skipinitialspace=True, usecols=fields)
    size = df.shape

    for r in range(1, size[1]):
        timestamp = fields[0]
        colname = fields[r]
        for q in range(1, size[0]):
            timestamp_for_filename = str(df[timestamp][q]).replace(' ', '-').replace(':', '_').replace('/', '_')
            create_timestamped_node_file(timestamp_for_filename, colname, new_load=str(df[colname][q]))


def search_timestamp_in_df(df, val):
    a = df.index[df['timeseries'.str.contains(val)]]
    if a.empty:
        raise ValueError
    elif len(a)>1:
        raise UserWarning
        return a.tolist()
    else:
        # most usual case, only one-time stamp will be found.
        return a.item()



def timeseries_simulation(timeseries_file, start_time, interval=10):
    """

    :param start_time: must match the format on the data CSV file.
    :param interval:
    :return:
    """
    logging.info("timeseries_simulation function is called")
    df = pd.read_csv(timeseries_file, skipinitialspace=True)
    # what columns are there in the file:
    fields = ['timestamp']
    df = pd.read_csv(timeseries_file, skipinitialspace=True, usecols=fields)

    xx = search_timestamp_in_df(df, start_time)

    print(xx)

    # cwd = os.getcwd()
    # time_as_folder_name = start_time.replace(' ', '-').replace(':', '_').replace('/', '_')
    # # make a directory for the timestep
    #
    # newpath = os.path.join(cwd, time_as_folder_name)
    # if not os.path.exists(newpath):
    #     os.mkdir(newpath)





