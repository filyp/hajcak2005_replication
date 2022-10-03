class TriggerTypes:
    BLINK = "BLINK"
    CUE = "CUE_____"
    TARGET = "TARGET__"
    REACTION = "REACTION"
    FLANKER = "FLANKER_"
    FEEDB_GOOD = "F_GOOD__"
    FEEDB_BAD = "F_BAD___"
    SECOND_REACTION = "SECOND_R"
    FIXATION = "FIXATION"
    BLOCK_START = "BLOCK_START"


def get_trigger_name(
    trigger_type,
    block,
    trial=None,
    response="{}",
):
    block_type = block["type"]
    if trial is not None:
        target_name = trial["target_name"]
        cue_name = str(trial["cue"].text)
        # make the cues take always 3 chars for better readability
        if len(cue_name) == 1:
            cue_name = "_" + cue_name + "_"
    else:
        cue_name = "---"
        target_name = "---"

    return f"{trigger_type}*{block_type[:2]}*{cue_name}*{target_name[-3:]}*{response}"
