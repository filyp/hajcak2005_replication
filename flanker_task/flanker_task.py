import random
from collections import OrderedDict

from psychopy import core, event, logging

from psychopy_experiment_helpers.show_info import show_info
from flanker_task.load_data import load_stimuli
from flanker_task.triggers import TriggerTypes, get_trigger_name
from psychopy_experiment_helpers.triggers_common import TriggerHandler, create_eeg_port
from flanker_task.prepare_experiment import prepare_trials


def check_response(exp, block, trial, response_data):
    config = exp.config
    keylist = [key for group in config["Keys"] for key in group]
    keys = event.getKeys(keyList=keylist)
    _, mouse_press_times = exp.mouse.getPressed(getTime=True)

    if mouse_press_times[0] != 0.0:
        keys.append("mouse_left")
    elif mouse_press_times[1] != 0.0:
        keys.append("mouse_middle")
    elif mouse_press_times[2] != 0.0:
        keys.append("mouse_right")

    if keys:
        reaction_time = exp.clock.getTime()
        if response_data == []:
            trigger_type = TriggerTypes.REACTION
        else:
            trigger_type = TriggerTypes.SECOND_REACTION
        if keys[0] in config["Keys"][0]:
            response_side = "l"
        elif keys[0] in config["Keys"][1]:
            response_side = "r"

        trigger_name = get_trigger_name(trigger_type, block, trial, response_side)
        exp.trigger_handler.prepare_trigger(trigger_name)
        exp.trigger_handler.send_trigger()
        exp.mouse.clickReset()
        event.clearEvents()
        return response_side, reaction_time
    else:
        return None


def flanker_task(exp, config, data_saver):
    # load stimulus
    stimulus = load_stimuli(win=exp.win, config=exp.config, screen_res=exp.screen_res)

    # EEG triggers
    port_eeg = create_eeg_port() if config["Send_EEG_trigg"] else None
    exp.trigger_handler = TriggerHandler(port_eeg, data_saver=data_saver)

    for block in exp.config["Experiment_blocks"]:
        trigger_name = get_trigger_name(TriggerTypes.BLOCK_START, block)
        exp.trigger_handler.prepare_trigger(trigger_name)
        exp.trigger_handler.send_trigger()
        logging.data(f"Entering block: {block}")
        logging.flush()

        if block["type"] == "break":
            show_info(block["file_name"], exp)
            continue
        elif block["type"] in ["experiment", "training"]:
            block["trials"] = prepare_trials(block, stimulus)
        else:
            raise Exception(
                "{} is bad block type in config Experiment_blocks".format(block["type"])
            )

        for trial in block["trials"]:
            response_data = []

            # ! show empty screen between trials
            empty_screen_between_trials = random.uniform(*config["Empty_screen_between_trials"])
            exp.display_for_duration(empty_screen_between_trials, stimulus["fixation"])

            if config["Show_cues"]:
                # it's a version of the experiment where we show cues before stimuli
                # ! draw cue
                trigger_name = get_trigger_name(TriggerTypes.CUE, block, trial)
                cue_show_time = random.uniform(*config["Cue_show_time"])
                exp.display_for_duration(cue_show_time, trial["cue"], trigger_name)

                # ! draw empty screen
                empty_screen_after_cue = random.uniform(*config["Empty_screen_after_cue_show_time"])
                exp.display_for_duration(empty_screen_after_cue, stimulus["fixation"])

            # ! draw target
            trigger_name = get_trigger_name(TriggerTypes.TARGET, block, trial)
            target_show_time = random.uniform(*config["Target_show_time"])
            event.clearEvents()
            exp.win.callOnFlip(exp.mouse.clickReset)
            exp.win.callOnFlip(exp.clock.reset)
            exp.display(trial["target"], trigger_name)

            while exp.clock.getTime() < target_show_time:
                res = check_response(exp, block, trial, response_data)
                if res is not None:
                    response_data.append(res)
                    break  # if we got a response, break out of this stage
                data_saver.check_exit()
                exp.win.flip()
            for target in trial["target"]:
                target.setAutoDraw(False)
            exp.win.flip()

            # ! draw empty screen and await response
            empty_screen_show_time = random.uniform(*config["Blank_screen_for_response_show_time"])
            exp.display(trial["fixation"], trigger_name=None)
            while exp.clock.getTime() < target_show_time + empty_screen_show_time:
                res = check_response(exp, block, trial, response_data)
                if res is not None:
                    response_data.append(res)
                data_saver.check_exit()
                exp.win.flip()
            stimulus["fixation"].setAutoDraw(False)
            data_saver.check_exit()

            # check if reaction was correct
            if trial["target_name"] in ["congruent_lll", "incongruent_rlr"]:
                # left is correct
                correct_side = "l"
            elif trial["target_name"] in ["congruent_rrr", "incongruent_lrl"]:
                # right is correct
                correct_side = "r"

            response_side, reaction_time = response_data[0] if response_data != [] else (None, None)
            if response_side == correct_side:
                reaction = "correct"
            else:
                reaction = "incorrect"

            # save beh
            # fmt: off
            cue_name = trial["cue"].text
            behavioral_data = OrderedDict(
                block_type=block["type"],
                trial_type=trial["type"],
                cue_name=cue_name,
                target_name=trial["target_name"],
                response=response_side,
                rt=reaction_time,
                reaction=reaction,
                empty_screen_between_trials=empty_screen_between_trials,
                cue_show_time=cue_show_time if config["Show_cues"] else None,
                empty_screen_after_cue_show_time=empty_screen_after_cue if config["Show_cues"] else None,
                target_show_time=target_show_time,
            )
            # fmt: on
            data_saver.beh.append(behavioral_data)

            logging.data(f"Behavioral data: {behavioral_data}\n")
            logging.flush()
