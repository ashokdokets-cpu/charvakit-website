"""
Session 41 - IELTS writing + speaking topical-relevance test harness.

Standalone. Loads ielts_engine directly and runs 6 canned cases
against the real OpenAI scorer. Asserts on the new topical_relevance
flag, the existing partial flag, and the band caps.

Usage:
    python scripts/test_ielts_relevance.py

Costs ~$0.03 in OpenAI credits per full run. Not part of pytest;
invoke manually after prompt changes.
"""
import os
import sys
import logging
from dotenv import load_dotenv

# Load env. Prefer .env.local for dev, fall back to .env.
load_dotenv(".env.local", override=True)
load_dotenv()

# Silence engine chatter
logging.disable(logging.CRITICAL)

# Make the repo root importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ielts_engine import ielts_engine  # noqa: E402


# ----------------------------------------------------------------
# Canned data
# ----------------------------------------------------------------

REMOTE_WORK_PROMPT = (
    "Some people believe that remote work will permanently reshape urban "
    "planning, while others argue cities will adapt and remain largely "
    "unchanged. Discuss both views and give your own opinion."
)

# ~270 words, on-topic
ON_TOPIC_ESSAY_FULL = """
The debate over whether remote work will permanently reshape urban planning
is one of the most consequential questions facing modern cities. While some
argue that the shift to distributed work is a temporary disruption, I believe
that the underlying changes to commuting patterns, housing demand, and
commercial real estate are structural and will leave a lasting mark on how
planners design cities.

Those who argue that cities will adapt unchanged point to the historical
resilience of urban centres. Cities have absorbed previous technological
shifts, from the automobile to the telephone, without losing their essential
function as engines of commerce and culture. They also note that many
workers have already returned to offices at least part-time, and that the
social and professional pull of dense downtowns remains strong. From this
view, the pandemic merely accelerated trends that were already underway,
and central business districts will reinvent themselves rather than disappear.

However, I would argue that the scale and duration of the shift are different
this time. When a significant fraction of white-collar work is performed
remotely, demand for office space falls, and that reduction cascades into
transport planning, retail corridors, and residential zoning. Planners must
rethink transit routes built around five-day-a-week commuting, convert
underused office towers into housing, and invest in mixed-use neighbourhoods
that reduce the need for long trips in the first place. Municipal budgets that
rely on downtown commercial taxes will need new revenue models.

In conclusion, cities will not become obsolete, but they will be forced to
adapt more deeply than the incrementalists suggest. The urban planning
profession now faces a decade of rethinking the relationship between work,
place, and community. Those cities that plan proactively for this shift will
be the ones that thrive.
""".strip()

# ~110 words, on-topic (below the 250 minimum)
ON_TOPIC_ESSAY_PARTIAL = """
Remote work is transforming cities in ways that urban planners cannot ignore.
The most immediate effect is on commuting: when millions of workers no longer
travel downtown five days a week, the rationale for sprawling transit networks
and vast parking infrastructure weakens. Planners must respond by reallocating
space toward housing, parks, and mixed-use development. Some observers argue
that cities will simply adapt, but I believe the change is structural. Office
towers in central business districts will need conversion; suburban centres
will grow. The cities that anticipate this shift will be the ones that thrive.
""".strip()

# ~265 words, OFF-TOPIC (about tea in China)
OFF_TOPIC_ESSAY_FULL = """
The history of tea in China spans more than three thousand years and reflects
the country's deep relationship with agriculture, ritual, and trade. According
to legend, tea was discovered in 2737 BCE when leaves from a wild tree blew
into the cup of the legendary Emperor Shennong while he was boiling water.
Whether or not the story is literally true, it captures the ancient roots of
a beverage that would eventually become the most widely consumed drink in the
world after water.

By the Tang dynasty, tea had become an established cultural practice. The
scholar Lu Yu wrote the Classic of Tea in the eighth century, codifying the
preparation methods, the utensils, and the aesthetics of tea drinking. During
this period, tea spread from the elites to the general population, and
ceremonies developed around its consumption. The Song dynasty, which
followed, introduced powdered tea and the whisking technique that would later
influence the Japanese tea ceremony.

Trade was central to tea's spread. The Tea Horse Road, a network of caravan
routes stretching from Sichuan and Yunnan into Tibet and beyond, carried
compressed bricks of tea in exchange for horses and other goods. In later
centuries, European traders became increasingly interested in Chinese tea,
and by the eighteenth century tea had become a major export. British demand
for Chinese tea, in particular, led to the Opium Wars and shaped the
geopolitics of the nineteenth century.

Today, tea remains a defining element of Chinese daily life. Green, oolong,
pu-erh, and many regional varieties are consumed in households and teahouses
across the country. The practices vary from region to region, but the
underlying rhythm - the careful pouring, the shared cups, the quiet
attention - persists. The history of tea in China is, in a sense, a history
of the country itself.
""".strip()

# ~80 words, OFF-TOPIC (tea), below the 250 minimum
OFF_TOPIC_ESSAY_SHORT = """
Tea has been cultivated in China for thousands of years. Legend holds that
Emperor Shennong discovered it accidentally when leaves drifted into his
boiling water. By the Tang dynasty, tea drinking had spread across all social
classes, and Lu Yu's Classic of Tea formalised the practice. Trade routes
carried tea bricks to Tibet and beyond, and European demand later shaped
global commerce. Today, oolong, green, and pu-erh teas remain central to
Chinese culture.
""".strip()

# Speaking: on-topic Parts 1+2 (missing Part 3)
HOMETOWN_TOPIC = "Describe your hometown and the place you grew up in."
SPEAKING_ON_TOPIC_PARTIAL = [
    {
        "part": 1,
        "question": "Where is your hometown?",
        "transcript": (
            "My hometown is Guntur, a city in the state of Andhra Pradesh in "
            "southern India. It is known for its chilli trade and for the "
            "many educational institutions that draw students from across "
            "the region. It is a busy but relatively compact city."
        ),
    },
    {
        "part": 1,
        "question": "What do you like most about your hometown?",
        "transcript": (
            "I like the sense of community. People know their neighbours, and "
            "there is a strong culture of shared meals and festivals. The food "
            "is excellent, especially the local Andhra-style dishes."
        ),
    },
    {
        "part": 2,
        "question": (
            "Describe a place in your hometown that is important to you. "
            "You should say where it is, what it looks like, when you go "
            "there, and why it matters to you."
        ),
        "transcript": (
            "The place that matters most to me is the small park near my "
            "childhood home. It sits at the end of a quiet street, with old "
            "banyan trees and a small pond that fills during the monsoon. "
            "When I was young, I would go there every evening with my "
            "grandfather, who would tell me stories about the city. Even "
            "now, whenever I return to Guntur, I walk to that park. It has "
            "not changed much. The benches are the same, the trees are "
            "taller, and the light in the late afternoon still looks the way "
            "I remember it. It matters to me because it holds the memory of "
            "a person and a time I do not want to forget."
        ),
    },
]

# Speaking: off-topic Parts 1+2 (about tea)
SPEAKING_OFF_TOPIC = [
    {
        "part": 1,
        "question": "Where is your hometown?",
        "transcript": (
            "Tea has been cultivated in China for over three thousand years. "
            "The earliest records describe it as a medicinal herb, and by the "
            "Tang dynasty it had become a daily beverage across all social "
            "classes. Lu Yu's Classic of Tea codified the preparation."
        ),
    },
    {
        "part": 1,
        "question": "What do you like most about your hometown?",
        "transcript": (
            "The Tea Horse Road carried compressed bricks of tea from Sichuan "
            "and Yunnan into Tibet. European traders later became interested "
            "in Chinese tea, and by the eighteenth century it was a major "
            "export commodity shaping global trade."
        ),
    },
    {
        "part": 2,
        "question": (
            "Describe a place in your hometown that is important to you."
        ),
        "transcript": (
            "Oolong, green, and pu-erh teas are produced across China. The "
            "processing methods differ region by region: oolong is partially "
            "oxidised, green is unoxidised, and pu-erh is fermented and aged. "
            "These differences produce the wide range of flavours associated "
            "with Chinese tea culture."
        ),
    },
]


# ----------------------------------------------------------------
# Test harness
# ----------------------------------------------------------------

PASS = "PASS"
FAIL = "FAIL"

results = []


def check(name, condition, detail=""):
    status = PASS if condition else FAIL
    results.append((name, status, detail))
    color = "\033[92m" if condition else "\033[91m"
    reset = "\033[0m"
    print(f"  {color}{status}{reset}  {name}")
    if detail:
        print(f"        {detail}")


def case_1_writing_on_topic_full():
    print("\n[Case 1] Writing - on-topic full (~260 words)")
    r = ielts_engine.evaluate_writing(
        essay=ON_TOPIC_ESSAY_FULL,
        task=2,
        prompt_text=REMOTE_WORK_PROMPT,
    )
    print(f"  Result: status={r.get('status')} "
          f"band={r.get('overall_band')} "
          f"task_ach={r.get('task_achievement_or_response')} "
          f"topical={r.get('topical_relevance')} "
          f"partial={r.get('partial')}")
    check("case 1 topical_relevance is truthy",
          r.get("topical_relevance") is True,
          f"got {r.get('topical_relevance')!r}")
    check("case 1 partial is False",
          r.get("partial") is False,
          f"got {r.get('partial')!r}")
    band = r.get("overall_band")
    check("case 1 overall_band >= 5.0",
          isinstance(band, (int, float)) and band >= 5.0,
          f"got {band!r}")


def case_2_writing_on_topic_partial():
    print("\n[Case 2] Writing - on-topic partial (~110 words, under 250)")
    r = ielts_engine.evaluate_writing(
        essay=ON_TOPIC_ESSAY_PARTIAL,
        task=2,
        prompt_text=REMOTE_WORK_PROMPT,
    )
    print(f"  Result: status={r.get('status')} "
          f"band={r.get('overall_band')} "
          f"task_ach={r.get('task_achievement_or_response')} "
          f"topical={r.get('topical_relevance')} "
          f"partial={r.get('partial')}")
    check("case 2 topical_relevance is truthy",
          r.get("topical_relevance") is True,
          f"got {r.get('topical_relevance')!r}")
    check("case 2 partial is True",
          r.get("partial") is True,
          f"got {r.get('partial')!r}")
    task_ach = r.get("task_achievement_or_response")
    check("case 2 task_achievement_or_response <= 5.0",
          isinstance(task_ach, (int, float)) and task_ach <= 5.0,
          f"got {task_ach!r}")


def case_3_writing_off_topic_full():
    print("\n[Case 3] Writing - OFF-TOPIC full (~265 words about tea)")
    r = ielts_engine.evaluate_writing(
        essay=OFF_TOPIC_ESSAY_FULL,
        task=2,
        prompt_text=REMOTE_WORK_PROMPT,
    )
    print(f"  Result: status={r.get('status')} "
          f"band={r.get('overall_band')} "
          f"task_ach={r.get('task_achievement_or_response')} "
          f"topical={r.get('topical_relevance')} "
          f"note={r.get('relevance_note')}")
    check("case 3 topical_relevance is False",
          r.get("topical_relevance") is False,
          f"got {r.get('topical_relevance')!r}")
    task_ach = r.get("task_achievement_or_response")
    check("case 3 task_achievement_or_response <= 3.0",
          isinstance(task_ach, (int, float)) and task_ach <= 3.0,
          f"got {task_ach!r}")


def case_4_writing_off_topic_short():
    print("\n[Case 4] Writing - OFF-TOPIC short (~80 words about tea)")
    r = ielts_engine.evaluate_writing(
        essay=OFF_TOPIC_ESSAY_SHORT,
        task=2,
        prompt_text=REMOTE_WORK_PROMPT,
    )
    print(f"  Result: status={r.get('status')} "
          f"band={r.get('overall_band')} "
          f"task_ach={r.get('task_achievement_or_response')} "
          f"topical={r.get('topical_relevance')} "
          f"partial={r.get('partial')}")
    check("case 4 topical_relevance is False",
          r.get("topical_relevance") is False,
          f"got {r.get('topical_relevance')!r}")
    check("case 4 partial is True (under word minimum)",
          r.get("partial") is True,
          f"got {r.get('partial')!r}")


def case_5_speaking_on_topic_partial():
    print("\n[Case 5] Speaking - on-topic partial (parts 1+2 only)")
    r = ielts_engine.evaluate_speaking(
        responses=SPEAKING_ON_TOPIC_PARTIAL,
        topic=HOMETOWN_TOPIC,
    )
    ev = r.get("evaluation") or {}
    print(f"  Result: status={r.get('status')} "
          f"band={ev.get('overall_band')} "
          f"topical={ev.get('topical_relevance')} "
          f"partial={r.get('partial')} "
          f"parts={r.get('parts_covered')}")
    check("case 5 partial is True (part 3 missing)",
          r.get("partial") is True,
          f"got {r.get('partial')!r}")
    band = ev.get("overall_band")
    check("case 5 overall_band > 0  (regression fix)",
          isinstance(band, (int, float)) and band > 0,
          f"got {band!r}")
    check("case 5 topical_relevance is truthy",
          ev.get("topical_relevance") is True,
          f"got {ev.get('topical_relevance')!r}")


def case_6_speaking_off_topic():
    print("\n[Case 6] Speaking - OFF-TOPIC (parts 1+2 about tea)")
    r = ielts_engine.evaluate_speaking(
        responses=SPEAKING_OFF_TOPIC,
        topic=HOMETOWN_TOPIC,
    )
    ev = r.get("evaluation") or {}
    print(f"  Result: status={r.get('status')} "
          f"band={ev.get('overall_band')} "
          f"topical={ev.get('topical_relevance')} "
          f"note={ev.get('relevance_note')}")
    check("case 6 topical_relevance is False",
          ev.get("topical_relevance") is False,
          f"got {ev.get('topical_relevance')!r}")


def main():
    print("=" * 68)
    print("Session 41 - IELTS topical-relevance test harness")
    print("=" * 68)

    for fn in (
        case_1_writing_on_topic_full,
        case_2_writing_on_topic_partial,
        case_3_writing_off_topic_full,
        case_4_writing_off_topic_short,
        case_5_speaking_on_topic_partial,
        case_6_speaking_off_topic,
    ):
        try:
            fn()
        except Exception as e:
            print(f"  \033[91mEXCEPTION\033[0m in {fn.__name__}: {e!r}")
            results.append((fn.__name__, FAIL, f"exception: {e!r}"))

    print("\n" + "=" * 68)
    passed = sum(1 for _, s, _ in results if s == PASS)
    total = len(results)
    print(f"Total: {passed}/{total} checks passed")
    print("=" * 68)

    if passed < total:
        print("\nFailed checks:")
        for name, status, detail in results:
            if status == FAIL:
                print(f"  - {name}: {detail}")
        sys.exit(1)


if __name__ == "__main__":
    main()