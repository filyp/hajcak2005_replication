# TODO this file could be made more general, or even moved to individual task code


import os
import codecs

from psychopy import event, logging, visual, core


def read_text_from_file(file_name, insert=""):
    """
    Method that read message from text file, and optionally add some
    dynamically generated info.
    :param file_name: Name of file to read
    :param insert: dynamically generated info
    :return: message
    """
    if not isinstance(file_name, str):
        raise TypeError("file_name must be a string")
    msg = list()
    with codecs.open(file_name, encoding="utf-8", mode="r") as data_file:
        for line in data_file:
            if not line.startswith("#"):  # if not commented line
                msg.append(line)
    whole_message = "".join(msg)
    final_message = whole_message.replace("<--insert-->", insert)
    return final_message


def show_info(
    file_name,
    exp,
    insert="",
    alignText="center",
    pos=(0, 0),
    duration=None,
    custom_text=None,
    required_click="left",
):
    """
    Clear way to show info message into screen.
    :param win:
    :param file_name:
    :param screen_width:
    :param text_size:
    :param text_color:
    :param insert: extra text for read_text_from_file
    :return:
    """

    screen_width = exp.screen_res["width"]

    if custom_text is not None:
        hello_msg = custom_text
    else:
        hello_msg = read_text_from_file(
            os.path.join("messages", file_name), insert=insert
        )
    hello_msg = visual.TextStim(
        win=exp.win,
        antialias=True,
        font=exp.config["Text_font"],
        text=hello_msg,
        height=exp.config["Text_size"],
        wrapWidth=screen_width,
        color=exp.config["Text_color"],
        alignText=alignText,
        pos=pos,
    )
    hello_msg.draw()
    exp.win.flip()
    if duration is None:
        
        # wait for key press or mouse click
        event.clearEvents()
        exp.mouse.clickReset()
        while True:
            _, press_times = exp.mouse.getPressed(getTime=True)
            keys = event.getKeys(keyList=["f7", "return", "space"])

            if "f7" in keys:
                exp.data_saver.save_beh()
                exp.data_saver.save_triggers()
                logging.critical("Experiment finished by user! {} pressed".format(keys))
                exit(1)
            if "return" in keys or "space" in keys:
                break
            if press_times[0] > 0 and required_click == "left":
                break
            if press_times[2] > 0 and required_click == "right":
                break
                
            core.wait(0.030)
            

    else:
        # wait for duration
        core.wait(duration)
