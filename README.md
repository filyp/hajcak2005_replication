# Installation on windows

1. Install PsychoPy - [Installation — PsychoPy](https://www.psychopy.org/download.html)
2. Clone this repository (run this command in windows cmd or in [git bash](https://git-scm.com/downloads)):
```
git clone https://github.com/filyp/hajcak2005_replication.git
```
3. Run the `install.bat` script (just click it).
4. Verify installation by running test script: `run_short_test_experiment_without_triggers.bat`

# Running the experiment

## On Windows
Click `run_experiment_with_cues.bat` or `run_experiment_without_cues.bat` to run the experiments.

## From bash

```bash
python main.py config/flankers_hajcak2005_with_cues.yaml
```
or
```bash
python main.py config/flankers_hajcak2005_without_cues.yaml
```

## Running the rest procedure
```bash
python rest.py open
```
or
```bash
python rest.py closed
```

## Adaptation
You may need to adapt the mechanism of sending triggers to your setup. Edit the file `psychopy_experiment_helpers/triggers_common.py` to do so.