"""Deterministic, diverse prompt set for the EOS pilot.

Dataset hubs are not reachable from every environment, so the pilot builds its
own prompts from templates x topics. Categories differ in how "obvious" the end
of a good answer is, which is what we want to vary when studying the stopping
decision.
"""
import random

TOPICS = [
    "photosynthesis", "the French Revolution", "black holes", "compound interest",
    "the immune system", "plate tectonics", "machine translation", "the water cycle",
    "inflation", "the Roman Empire", "vaccines", "quantum entanglement", "DNA replication",
    "climate change", "the stock market", "neural networks", "the printing press",
    "volcanoes", "supply and demand", "the human heart", "renewable energy", "jazz music",
    "the Silk Road", "antibiotics", "the internet", "honeybees", "chess openings",
    "sleep", "coral reefs", "electric cars", "the Moon landing", "prime numbers",
    "coffee", "earthquakes", "the Renaissance", "batteries", "tea ceremonies",
    "glaciers", "public key cryptography", "the Olympic Games",
]

TEMPLATES = {
    # short, closed answers: the natural end is sharp
    "fact": [
        "In one sentence, what is {t}?",
        "Give a one-line definition of {t}.",
        "Answer briefly: why does {t} matter?",
    ],
    # enumerations: the end is set by a count the prompt states
    "list": [
        "List three key facts about {t}.",
        "Give me five bullet points about {t}.",
        "Name four common misconceptions about {t}.",
    ],
    # open explanations: the end is a soft, model-chosen decision
    "explain": [
        "Explain {t} to a curious teenager.",
        "Write a short paragraph explaining how {t} works.",
        "What are the main debates around {t}?",
    ],
    # creative: the end is a stylistic choice
    "creative": [
        "Write a four-line poem about {t}.",
        "Write a two-sentence story involving {t}.",
        "Write a haiku about {t}.",
    ],
}


def build_prompts(n=None, seed=0):
    rows = []
    for cat, temps in TEMPLATES.items():
        for t in TOPICS:
            for tmpl in temps:
                rows.append({"category": cat, "topic": t, "prompt": tmpl.format(t=t)})
    rng = random.Random(seed)
    rng.shuffle(rows)
    return rows if n is None else rows[:n]


if __name__ == "__main__":
    ps = build_prompts()
    print(len(ps), "prompts; e.g.", ps[:3])
