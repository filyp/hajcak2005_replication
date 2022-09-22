class TriggerTypes:
    BLINK = "BLINK"
    CUE = "CUE_____"
    TARGET = "TARGET__"
    REACTION = "REACTION"
    FLANKER = "FLANKER_"
    FEEDB_GOOD = "F_GOOD__"
    FEEDB_BAD = "F_BAD___"
    SECOND_REACTION = "SECOND_R"
    BLOCK_START = "BLOCK_START"


def get_trigger_name(
    trigger_type,
    block_type="--",
    cue_name="-",
    target_name="---",
    response=None,
):
    return f"{trigger_type}*{block_type[:2]}*{cue_name}*{target_name[-3:]}*{response}"
