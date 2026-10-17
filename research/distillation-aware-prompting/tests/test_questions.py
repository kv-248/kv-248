from dap.questions import geneval_intent, load_geneval, plural
from dap.rewrite import assertion, failed_entities, parse_list, rule_mutations

from conftest import GENEVAL_ROWS


def test_geneval_questions():
    qs = [geneval_intent(r).questions for r in GENEVAL_ROWS]
    assert qs[0] == ["Is there a bench in the image?"]
    assert qs[1] == ["Are there exactly two clocks in the image?"]
    assert qs[2] == ["Is there a wine glass in the image?", "Is the wine glass purple?",
                     "Is there a apple in the image?", "Is the apple black?"]
    assert qs[3][-1] == "Is the dog to the right of the teddy bear?"
    assert plural("bus") == "buses" and plural("wine glass") == "wine glasses"


def test_load_geneval_local(geneval_file):
    its = load_geneval(geneval_file, tags=["counting", "position"])
    assert [i.tag for i in its] == ["counting", "position"]


def test_rule_operators():
    assert assertion("Is the dog to the right of the teddy bear?") == "The dog is to the right of the teddy bear."
    assert assertion("Are there exactly two clocks in the image?") == "There are exactly two clocks in the image."
    assert assertion("Is the apple black?") == "The apple is black."
    assert failed_entities("Is the apple black?") == ["black apple"]
    assert failed_entities("Is the dog to the right of the teddy bear?") == ["dog", "teddy bear"]
    muts = rule_mutations("a photo of a purple wine glass and a black apple", ["Is the apple black?"])
    assert muts[0] == "black apple, a photo of a purple wine glass and a black apple"
    assert parse_list('Here: ["a", "b", "c"]', 2) == ["a", "b"]


def test_geneval_detector_logic():
    from PIL import Image

    from dap.geneval_judge import Detection, GenEvalDetectorJudge
    from dap.judges import score_intent

    dets = {
        "two_clocks": [Detection("clock", 0.95, (0, 0, 10, 10)), Detection("clock", 0.93, (20, 0, 30, 10))],
        "three_clocks": [Detection("clock", 0.95, (0, 0, 10, 10))] * 3,
        "dog_right": [Detection("teddy bear", 0.8, (0, 0, 10, 10)), Detection("dog", 0.8, (30, 0, 40, 10))],
        "dog_left": [Detection("teddy bear", 0.8, (30, 0, 40, 10)), Detection("dog", 0.8, (0, 0, 10, 10))],
        "colors_ok": [Detection("wine glass", 0.9, (0, 0, 5, 5)), Detection("apple", 0.9, (10, 0, 15, 5))],
    }
    colors = {"wine glass": "purple", "apple": "black"}
    judge = GenEvalDetectorJudge(detector=lambda im: dets[im.info["case"]], color_of=lambda im, d, c: colors[c])

    def img(case):
        im = Image.new("RGB", (8, 8))
        im.info["case"] = case
        return im

    its = {i.tag: i for i in load_geneval_rows()}
    assert [r["success"] for r in score_intent(judge, [img("two_clocks"), img("three_clocks")], its["counting"])] == [True, False]
    assert [r["success"] for r in score_intent(judge, [img("dog_right"), img("dog_left")], its["position"])] == [True, False]
    r = score_intent(judge, [img("colors_ok")], its["color_attr"])[0]
    assert r["success"] and len(r["probs"]) == len(its["color_attr"].questions)


def load_geneval_rows():
    from dap.questions import geneval_intent

    return [geneval_intent(r) for r in GENEVAL_ROWS]
