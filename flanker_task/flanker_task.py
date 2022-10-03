import random
import numpy as np
from collections import OrderedDict

from psychopy import core, event, logging

from psychopy_experiment_helpers.show_info import show_info
from flanker_task.load_data import load_stimuli
from flanker_task.triggers import TriggerTypes, get_trigger_name
from psychopy_experiment_helpers.triggers_common import TriggerHandler, create_eeg_port
from flanker_task.prepare_experiment import prepare_trials


def check_response(exp, block, trial, response_data):
    _, press_times = exp.mouse.getPressed(getTime=True)

    second_key = None
    if press_times[0] == 0.0 and press_times[2] == 0.0:
        return
    elif press_times[0] != 0.0 and press_times[2] == 0.0:
        key = "l"
        reaction_time = press_times[0]
    elif press_times[0] == 0.0 and press_times[2] != 0.0:
        key = "r"
        reaction_time = press_times[2]
    else:
        if press_times[0] < press_times[2]:
            key = "l"
            second_key = "r"
            reaction_time = press_times[0]
        else:
            key = "r"
            second_key = "l"
            reaction_time = press_times[2]

    if response_data == []:
        trigger_type = TriggerTypes.REACTION
    else:
        trigger_type = TriggerTypes.SECOND_REACTION

    # logging.data(press_times)

    trigger_name = get_trigger_name(trigger_type, block, trial, key)
    exp.trigger_handler.prepare_trigger(trigger_name)
    exp.trigger_handler.send_trigger()
    response_data.append((key, reaction_time))

    if second_key is not None:
        trigger_name = get_trigger_name(TriggerTypes.SECOND_REACTION, block, trial, second_key)
        exp.trigger_handler.prepare_trigger(trigger_name)
        exp.trigger_handler.send_trigger()
        response_data.append((second_key, None))

    exp.mouse.clickReset()


def random_time(min_time, max_time, step=0.100):
    steps = int((max_time - min_time) / step + 1)
    possible_times = np.linspace(min_time, max_time, steps)
    return random.choice(possible_times)


def flanker_task(exp, config, data_saver):
    # unpack necessary objects for easier access
    win = exp.win
    mouse = exp.mouse
    clock = exp.clock

    # load stimulus
    stimulus = load_stimuli(win=win, config=exp.config, screen_res=exp.screen_res)

    # EEG triggers
    port_eeg = create_eeg_port() if config["Send_EEG_trigg"] else None
    trigger_handler = TriggerHandler(port_eeg, data_saver=data_saver)
    exp.trigger_handler = trigger_handler

    for block in config["Experiment_blocks"]:
        trigger_name = get_trigger_name(TriggerTypes.BLOCK_START, block, response="-")
        trigger_handler.prepare_trigger(trigger_name)
        trigger_handler.send_trigger()
        logging.data(f"Entering block: {block}")
        logging.flush()

        if block["type"] == "break":
            show_info(block["file_name"], exp)
            continue
        elif block["type"] == "rest":
            show_info(block["file_name"], exp, duration=block["info_duration"])
            trigger_name = get_trigger_name(TriggerTypes.FIXATION, block, response="-")
            exp.display_for_duration(block["duration"], stimulus["fixation"], trigger_name)
            continue
        elif block["type"] in ["experiment", "training"]:
            block["trials"] = prepare_trials(block, stimulus)
        else:
            raise Exception(
                "{} is bad block type in config Experiment_blocks".format(block["type"])
            )

        # ! draw empty screen
        trigger_name = get_trigger_name(TriggerTypes.FIXATION, block, response="-")
        empty_screen_time = random_time(*config["Blank_screen_for_response_show_time"])
        exp.display_for_duration(empty_screen_time, stimulus["fixation"], trigger_name)

        for trial in block["trials"]:
            response_data = []
            trigger_handler.open_trial()

            if config["Show_cues"]:
                # it's a version of the experiment where we show cues before stimuli
                # ! draw cue
                trigger_name = get_trigger_name(TriggerTypes.CUE, block, trial)
                cue_show_time = random_time(*config["Cue_show_time"])
                exp.display_for_duration(cue_show_time, trial["cue"], trigger_name)

                # ! draw empty screen
                trigger_name = get_trigger_name(TriggerTypes.FIXATION, block, trial)
                empty_screen_after_cue = random_time(*config["Empty_screen_after_cue_show_time"])
                exp.display_for_duration(empty_screen_after_cue, stimulus["fixation"], trigger_name)

            # ! draw target
            trigger_name = get_trigger_name(TriggerTypes.TARGET, block, trial)
            target_show_time = random_time(*config["Target_show_time"])
            event.clearEvents()
            win.callOnFlip(mouse.clickReset)
            win.callOnFlip(clock.reset)
            trigger_handler.prepare_trigger(trigger_name)
            for s in trial["target"]:
                s.setAutoDraw(True)
            win.flip()
            trigger_handler.send_trigger()
            while clock.getTime() < target_show_time:
                check_response(exp, block, trial, response_data)
                win.flip()
            for s in trial["target"]:
                s.setAutoDraw(False)
            win.flip()

            # ! draw empty screen and await response
            trigger_name = get_trigger_name(TriggerTypes.FIXATION, block, trial)
            empty_screen_show_time = random_time(*config["Blank_screen_for_response_show_time"])
            trigger_handler.prepare_trigger(trigger_name)
            stimulus["fixation"].setAutoDraw(True)
            win.flip()
            trigger_handler.send_trigger()
            while clock.getTime() < target_show_time + empty_screen_show_time:
                check_response(exp, block, trial, response_data)
                win.flip()
            stimulus["fixation"].setAutoDraw(False)
            data_saver.check_exit()

            # check if reaction was correct
            if trial["target_name"] in ["congruent_lll", "incongruent_rlr"]:
                # left is correct
                correct_side = "l"
            elif trial["target_name"] in ["congruent_rrr", "incongruent_lrl"]:
                # right is correct
                correct_side = "r"

            response_side, reaction_time = response_data[0] if response_data != [] else ("-", "-")
            if response_side == correct_side:
                reaction = "correct"
            else:
                reaction = "incorrect"

            # save beh
            # fmt: off
            behavioral_data = OrderedDict(
                block_type=block["type"],
                trial_type=trial["type"],
                cue_name=trial["cue"].text,
                target_name=trial["target_name"],
                response=response_side,
                rt=reaction_time,
                reaction=reaction,
                cue_show_time=cue_show_time if config["Show_cues"] else None,
                empty_screen_after_cue_show_time=empty_screen_after_cue if config["Show_cues"] else None,
                target_show_time=target_show_time,
            )
            # fmt: on
            data_saver.beh.append(behavioral_data)
            trigger_handler.close_trial(response_side)

            logging.data(f"Behavioral data: {behavioral_data}\n")
            logging.flush()
