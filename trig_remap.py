# %%
import pathlib
import pandas as pd

# do it with both of these:
results_dir = pathlib.Path("results/FLA Control"); trial_delim = "TARGET__"
# results_dir = pathlib.Path("results/FLA Points"); trial_delim = "CUE_____"


for beh_file in (results_dir / "BEH").glob("*.csv"):
    name = beh_file.stem.split("_", 1)[-1]
    triggers_file = results_dir / "Full Recode" / f"triggerMap_{name}.txt"

    beh_df = pd.read_csv(beh_file)
    triggers = triggers_file.read_text().splitlines()


    trig_iter = iter(triggers)
    new_trigs = []
    next_trig = next(trig_iter)

    for trial_beh in beh_df.itertuples():
        while next_trig.endswith("*---*-"):
            new_trigs.append(next_trig)
            next_trig = next(trig_iter)

        assert trial_delim in next_trig
        trial_trigs = [next_trig]
        next_trig = next(trig_iter)
        while trial_delim not in next_trig and "BLOCK_START" not in next_trig:
            trial_trigs.append(next_trig)
            next_trig = next(trig_iter)

        ending = f"*{trial_beh.target_name[-3:]}*{trial_beh.response}"
        for trig in trial_trigs:
            if "SECOND_R" not in trig:
                assert trig.endswith(ending), f"{trig} does not end with {ending}"
        
        if trial_beh.rt == "-":
            new_trigs.extend(trial_trigs)
            continue
        
        rt = float(trial_beh.rt)
        if rt < 0.2 or rt > 0.8:
            for trig in trial_trigs:
                modified_trig = trig.split(":")[0] + ":BAD_RT"
                new_trigs.append(modified_trig)
        else:
            new_trigs.extend(trial_trigs)

    new_trigs.append(next_trig)
    # assert iter empty
    try:
        next(trig_iter)
        assert False, "Iterator is not empty"
    except StopIteration:
        pass  # Iterator is empty as expected

    assert len(new_trigs) == len(triggers)

    new_trig_file = results_dir / "Full Recode Remapped" / f"triggerMap_{name}.txt"
    # mkdir if not exists
    new_trig_file.parent.mkdir(parents=True, exist_ok=True)
    new_trig_file.write_text("\r\n".join(new_trigs) + "\r\n")

# %%
