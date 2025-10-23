# -*- coding: utf-8 -*-
# how to run:
# venv/bin/python main.py config/some_task.yaml

import datetime
import os
import sys
import json
import shutil
import hashlib

import yaml
from psychopy import core, event, logging, clock

# ERROR, WARNING, DATA, EXP, INFO and DEBUG
# logging.console.setLevel(logging.EXP)
logging.console.setLevel(logging.DATA)

from psychopy_experiment_helpers.experiment_info import get_participant_info

from psychopy_experiment_helpers.save_data import DataSaver
from psychopy_experiment_helpers.screen import create_win
from psychopy_experiment_helpers.experiment_info import display_eeg_info

__author__ = ["ociepkam", "filyp"]


def load_config(config_path):
    try:
        with open(config_path, encoding="utf8") as yaml_file:
            config = yaml.safe_load(yaml_file)
    except:
        raise Exception("Can't load config file")

    # compute hash of config file to know for sure which config version was used
    unique_config_string = json.dumps(config, sort_keys=True, ensure_ascii=True)
    short_hash = hashlib.sha1(unique_config_string.encode("utf-8")).hexdigest()[:6]

    return config, short_hash


class Experiment:
    def __init__(self, config, data_saver):
        self.config = config
        self.data_saver = data_saver

        # screen
        self.win, self.screen_res = create_win(
            screen_color=self.config["Screen_color"],
            screen_number=self.config.get("Screen_number", -1),
        )

        self.clock = core.Clock()
        self.mouse = event.Mouse(win=self.win, visible=False)

    def display_for_duration(self, time, stimulus, trigger_name=None):
        # stimulus can be a list of stimuli or a single stimulus
        if type(stimulus) is not list:
            stimulus = [stimulus]

        ISI = clock.StaticPeriod()

        if trigger_name is not None:
            self.trigger_handler.prepare_trigger(trigger_name)
            for s in stimulus:
                s.setAutoDraw(True)

            self.win.flip()
            ISI.start(time)
            self.trigger_handler.send_trigger()
            ISI.complete()
            self.data_saver.check_exit()
            for s in stimulus:
                s.setAutoDraw(False)
        else:
            for s in stimulus:
                s.setAutoDraw(True)

            self.win.flip()
            ISI.start(time)
            ISI.complete()
            self.data_saver.check_exit()
            for s in stimulus:
                s.setAutoDraw(False)


def run(procedure):
    # Load config
    config_path = sys.argv[1]
    config, config_hash = load_config(config_path)
    experiment_name = os.path.split(config_path)[-1]
    experiment_name = experiment_name.split(".")[0]
    experiment_name = experiment_name + "_" + config_hash

    if config.get("Actiview_reminder", False):
        display_eeg_info()
    participant_info, experiment_version = get_participant_info(
        config.get("Ask_for_experiment_version", False)
    )
    config["Experiment_version"] = experiment_version
    
    # date and time
    date_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    participant_info = participant_info + "_" + date_time

    data_saver = DataSaver(participant_info, experiment_name, beh=[], triggers_list=[])
    # copy config file to results folder
    os.makedirs(data_saver.directory, exist_ok=True)
    shutil.copy2(config_path, data_saver.directory)
    logging.data(f"Experiment name: {experiment_name}")

    # create experiment object
    exp = Experiment(config, data_saver)

    # Experiment
    procedure(exp, config, data_saver)

    # Save data
    data_saver.save_beh()
    data_saver.save_triggers()
