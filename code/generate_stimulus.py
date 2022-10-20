import random


def generate_stimulus(n, stimulus_1, stimulus_2, target_pair):
    result = []
    for i in range(int(n/2)):
        s1 = {"stimulus": random.choice(stimulus_1), "target": False}
        s2 = random.choice(stimulus_2)
        s2_target = True if s1["stimulus"] == target_pair[0] and s2 == target_pair[1] else False
        s2 = {"stimulus": s2, "target": s2_target}
        result.append(s1)
        result.append(s2)

    return result


if __name__ == "__main__":
    [print(elem) for elem in generate_stimulus(20, ["A", "B"], ["X", "Y"], ["A", "X"])]
