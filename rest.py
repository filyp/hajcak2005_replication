# usage: there are two variants of the rest procedure:
# python rest.py open
# python rest.py closed

#trigger key
# 1 - closed
# 2 - open
# 3 - end

import json
import os
import random
import time
import sys

import playsound
from psychopy import clock, core, event, logging, prefs, sound, visual

# ERROR, WARNING, DATA, EXP, INFO and DEBUG
# logging.console.setLevel(logging.EXP)
logging.console.setLevel(logging.DATA)

from psychopy_experiment_helpers.experiment_info import (
    display_eeg_info,
    get_participant_info,
)
from psychopy_experiment_helpers.save_data import DataSaver
from psychopy_experiment_helpers.screen import create_win
from psychopy_experiment_helpers.triggers_common import TriggerHandler, create_eeg_port

# starting_instructions = """\
# Teraz nagramy 8 minut danych w spoczynku. W tym czasie będziesz siedział/a wygodnie w fotelu, z zamkniętymi lub otwartymi oczami. W trakcie nagrywania usłyszysz komendy głosowe, które będą Ci mówić, kiedy masz otworzyć lub zamknąć oczy. 

# Kliknij myszką, aby rozpocząć.
# """

# We will record 8 minutes of resting state data, of which 4 minutes are recorded while eyes are closed and 4 minutes while eyes are opened. Conditions will vary in 1 minute blocks.
# The voice commands are given to the participants to open and close their eyes, or keep their eyes open/closed. The presentation software should display instructions in the language of your choice (if available, see below), deliver the voice commands, and send EEG triggers.

display_eeg_info()
# participant_info, experiment_version = get_participant_info(False)

# blocks = ["open", "open", "open", "open", "closed", "closed", "closed", "closed"]
# random.shuffle(blocks)
blocks1 = ["open", "closed", "closed", "open", "closed", "open", "open", "closed"]
blocks2 = ["closed", "open", "open", "closed", "open", "closed", "closed", "open"]

version = sys.argv[1]
if version == "open":
    condition_trigger = 7  # Condition 1
    blocks = blocks1
elif version == "closed":
    condition_trigger = 8  # Condition 2
    blocks = blocks2
else:
    raise ValueError(f"Unknown version: {version} (should be 'open' or 'closed')")

for i in range(len(blocks) - 1):
    b1 = blocks[i]
    b2 = blocks[i + 1]
    if b1[-4:] == b2[-4:]:
        blocks[i + 1] = "keep_" + b2
print(blocks)

# # save blocks
# dir_name = os.path.join("results", "rest")
# if not os.path.exists(dir_name):
#     os.makedirs(dir_name)
# filename = os.path.join("results", "rest", participant_info + ".json")
# with open(filename, "w") as f:
#     json.dump(blocks, f, indent=4)


port_eeg = create_eeg_port()


win, screen_res = create_win(
    screen_color="black",
    screen_number=-1,
)
mouse = event.Mouse(win=win, visible=False)

fixation = visual.TextStim(
    win=win,
    text="+",
    color="grey",
    height=0.0435,
    name="fixation",
)
start_msg = visual.TextStim(
    text="Naciśnij spację, aby rozpocząć.",
    win=win,
    antialias=True,
    font="Arial",
    height=0.04,
    # wrapWidth=screen_width,
    color="white",
    alignText="center",
    pos=(0, 0),
)

# # wait for key press or mouse click
# mouse.clickReset()
# while True:
#     _, press_times = mouse.getPressed(getTime=True)
#     if press_times[0] > 0:
#         break
#     core.wait(0.030)

start_msg.draw()
win.flip()
# wait for space key press
event.waitKeys(keyList=["space"])
fixation.draw()
win.flip()

# Send condition trigger
port_eeg.setData(condition_trigger)
time.sleep(0.005)
port_eeg.setData(0x00)
time.sleep(0.005)

# instructions
sound_file = os.path.join("rest_remy_pl", f"instruction.wav")
playsound.playsound(sound_file, block=True)

# wait for space key press
event.waitKeys(keyList=["space"])

# start recording
sound_file = os.path.join("rest_remy_pl", f"start_recording.wav")
playsound.playsound(sound_file, block=True)

fixation.draw()
win.flip()

block_time = 63
start_time = time.time()
for i, block in enumerate(blocks):
    if block.split("_")[-1] == "open":
        trigger_no = 2
    elif block.split("_")[-1] == "closed":
        trigger_no = 1
    else:
        raise ValueError(f"Unknown block type: {block}")

    # send trigger
    port_eeg.setData(trigger_no)
    time.sleep(0.005)
    port_eeg.setData(0x00)
    time.sleep(0.005)

    sound_file = os.path.join("rest_remy_pl", f"{block}.wav")
    playsound.playsound(sound_file, block=True)

    # time.sleep(0.5)
    # sound_file = os.path.join("rest_remy_pl", f"relax.wav")
    # playsound.playsound(sound_file, block=True)

    block_end = start_time + block_time * (i + 1)
    time.sleep(block_end - time.time())

# send trigger
# 3 means the end
port_eeg.setData(3)
time.sleep(0.005)
port_eeg.setData(0x00)
time.sleep(0.005)


msg = visual.TextStim(
    text="Zakończyliśmy rejestrację sygnału EEG.\n\nZaczekaj na eksperymentatora.\n\n(Naciśnij spację, aby wyjść.)",
    win=win,
    antialias=True,
    font="Arial",
    height=0.04,
    # wrapWidth=screen_width,
    color="white",
    alignText="center",
    pos=(0, 0),
)
msg.draw()
win.flip()

sound_file = os.path.join("rest_remy_pl", f"end_recording.wav")
playsound.playsound(sound_file, block=True)

# wait for space key press
event.waitKeys(keyList=["space"])

# play it with psychopy
# sound = sound.Sound(sound_file)
# sound.play()

# core.wait(3)

# from pprint import pprint
# import psychtoolbox.audio
# pprint(psychtoolbox.audio.get_devices())
# set  prefs.hardware[‘audioDevice’]
# to 0
# prefs.hardware["audioDevice"] = "HDA Intel PCH: ALC285 Analog (hw:0,0)"
# prefs.hardware["audioLib"] = "sounddevice"
# prefs.hardware["audioLatencyMode"] = 0
# print(prefs.hardware["audioDevice"])
