"""
Test the JsonTaskCollector class
"""

from pathlib import Path
import json

from pii_extract.defs import LANG_ANY

import pii_extract.gather.collector.json as mod


_TASKFILE = Path(__file__).parents[3] / "data" / "tasklist-example.json"



# ---------------------------------------------------------------------

def test100_lang_file():
    """
    Check the list of languages, add config file
    """
    tc = mod.JsonTaskCollector()
    tc.add_tasks(_TASKFILE)
    got = tc.language_list()
    assert [LANG_ANY, "en"] == got


def test110_lang_dict():
    """
    Check the list of languages, add dict of task
    """
    with open(_TASKFILE, encoding="utf-8") as f:
        tasks = json.load(f)

    tc = mod.JsonTaskCollector()
    tc.add_tasks(tasks)
    got = tc.language_list()
    assert [LANG_ANY, "en"] == got


def test120_gather_all_lang():
    """
    """
    tc = mod.JsonTaskCollector()
    tc.add_tasks(_TASKFILE)

    got = list(tc.gather_tasks(LANG_ANY))
    assert len(got) == 1
    assert got[0]["pii"][0]["type"] == "CREDIT_CARD"

    got = list(tc.gather_tasks("en"))
    assert len(got) == 1
    assert got[0]["pii"][0]["type"] == "PHONE_NUMBER"

    got = list(tc.gather_tasks(["en", LANG_ANY]))
    assert len(got) == 2
    assert got[0]["pii"][0]["type"] == "CREDIT_CARD"
    assert got[1]["pii"][0]["type"] == "PHONE_NUMBER"

    got = list(tc.gather_tasks(["en", LANG_ANY, "es"]))
    assert len(got) == 2

    got = list(tc.gather_tasks(["es"]))
    assert len(got) == 0


def test130_gather_all():
    """
    """
    tc = mod.JsonTaskCollector()
    tc.add_tasks(_TASKFILE)

    got = list(tc.gather_tasks())
    #import pprint; pprint.pprint(got)
    assert len(got) == 2

    exp0 = {
        "class": "PiiTask",
        "task": "taux.modules.any.credit_card_mock.CreditCardMock",
        "source": "piisa:pii-extract-base:test",
        "version": "0.0.1",
        "pii": [{
            "type": "CREDIT_CARD",
            "country": "any",
            "lang": "any"
        }]
    }
    assert exp0 == got[0]


    exp1 = {
        "class": "regex-external",
        "task": "taux.modules.en.any.international_phone_number.PATTERN_INT_PHONE",
        "doc": "detect phone numbers that use international notation. Uses context",
        "source": "piisa:pii-extract-base:test",
        "version": "0.0.1",
        "pii": [{
            "type": "PHONE_NUMBER",
            "subtype": "international phone number",
            "lang": "en",
            "country": "any",
            "context": {
                "value": ["ph", "phone", "fax"],
                "width": [16, 0],
                "type": "word"
            }
        }]
    }
    assert exp1 == got[1]
