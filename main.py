import atexit
import csv
import random
from os.path import join
import pandas as pd
from psychopy import visual, event, core

from code.load_data import load_config, load_images, prepare_block_stimulus
from code.screen_misc import get_screen_res
from code.show_info import part_info, show_info
from code.check_exit import check_exit
from code.generate_stimulus import generate_stimulus

RESULTS = []
PART_ID = ""


@atexit.register
def save_beh_results():
    num = random.randint(100, 999)
    with open(join('results', '{}_beh_{}.csv'.format(PART_ID, num)), 'w', newline='') as beh_file:
        dict_writer = csv.DictWriter(beh_file, RESULTS[0].keys())
        dict_writer.writeheader()
        dict_writer.writerows(RESULTS)


def show_stim(stim, stim_time, clock, win):
    if stim is not None:
        stim.setAutoDraw(True)
    win.callOnFlip(clock.reset)
    win.callOnFlip(event.clearEvents)
    win.flip()
    while clock.getTime() < stim_time:
        check_exit()
        win.flip()
    if stim is not None:
        stim.setAutoDraw(False)
    win.flip()


def block(config, stimulus_list, block_type, win, fixation, clock, screen_res, feedback):
    show_info(win, join('.', 'messages', f'instruction_{block_type}.txt'), text_color=config["text_color"],
              text_size=config["text_size"], screen_res=screen_res)

    n = -1
    for trial in stimulus_list:
        key = None
        reaction_time = None
        acc = -1
        n += 1
        stimulus = visual.TextStim(win, color=config["stimulus_color"], text=trial["stimulus"],
                                   height=config["stimulus_size"], pos=config["stimulus_pos"])

        # fixation
        show_stim(fixation, config["fixation_time"], clock, win)

        stimulus.setAutoDraw(True)
        win.callOnFlip(clock.reset)

        win.flip()
        while clock.getTime() < config["answer_time"]:
            key = event.getKeys(keyList=config["reaction_keys"])
            if key:
                reaction_time = clock.getTime()
                key = key[0]
                break
            check_exit()
            win.flip()

        # cleaning
        stimulus.setAutoDraw(False)
        win.callOnFlip(clock.reset)
        win.callOnFlip(event.clearEvents)
        win.flip()

        print(key)
        print(trial["target"])
        print(key and trial["target"])
        print(not key and not trial["target"])
        print((key and trial["target"]) or (not key and not trial["target"]))
        acc = 1 if (key and trial["target"]) or (not key and not trial["target"]) else 0

        trial_results = {"n": n, "block_type": block_type,
                         "rt": reaction_time, "acc": acc,
                         "stimulus": trial["stimulus"],
                         "answer": key,
                         "target": trial["target"]}
        RESULTS.append(trial_results)

        if config[f"fdbk_{block_type}"]:
            show_stim(feedback[acc], config["fdbk_show_time"], clock, win)

        wait_time = config["wait_time"] + random.random() * config["wait_jitter"]
        show_stim(None, wait_time, clock, win)


def main():
    global PART_ID
    config = load_config()
    info, PART_ID = part_info(test=True)

    screen_res = dict(get_screen_res())
    win = visual.Window(list(screen_res.values()), fullscr=True, units='pix', screen=0, color=config["screen_color"])
    event.Mouse(visible=False)

    clock = core.Clock()
    fixation = visual.TextStim(win, color=config["fixation_color"], text=config["fixation_text"],
                               height=config["fixation_size"])

    feedback_text = (config["fdbk_incorrect"], config["fdbk_no_answer"], config["fdbk_correct"])
    feedback = {i: visual.TextStim(win, color=config["fdbk_color"], text=text, height=config["fdbk_size"])
                for (i, text) in zip([0, -1, 1], feedback_text)}

    # run training
    training_stimulus = generate_stimulus(config["training_len"],
                                          stimulus_1=config["stimulus_1"],
                                          stimulus_2=config["stimulus_2"],
                                          target_pair=config["target_pair"])
    block(config=config, stimulus_list=training_stimulus, block_type="training", win=win, fixation=fixation,
          clock=clock, screen_res=screen_res, feedback=feedback)

    # run experiment
    experimental_stimulus = generate_stimulus(config["experiment_len"],
                                              stimulus_1=config["stimulus_1"],
                                              stimulus_2=config["stimulus_2"],
                                              target_pair=config["target_pair"])
    block(config=config, stimulus_list=experimental_stimulus, block_type="experiment", win=win, fixation=fixation,
          clock=clock, screen_res=screen_res, feedback=feedback)

    # end info
    show_info(win, join('.', 'messages', f'end.txt'), text_color=config["text_color"],
              text_size=config["text_size"], screen_res=screen_res)


if __name__ == "__main__":
    main()
