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
