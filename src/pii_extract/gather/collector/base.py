"""
Base class to create TaskCollector objects
"""

import sys

from typing import Dict, List, Iterable

from pii_data.helper.exception import UnimplementedException

from ...helper.types import TYPE_STR_LIST
from ...helper.utils import union_sets, taskd_field
from ...helper.logger import PiiLogger



# --------------------------------------------------------------------------

class BaseTaskCollector:
    """
    The base class to define objects for collecting PII Task implementations

    Subclasses need to implement _gather_tasks(lang), which must deliver an
    iterable of *normalized* raw task descriptors (possibly restricted to a
    given language)
    They can also reimplement language_list(), country_list() and/or
    gather_tasks(), if they can be made more efficient than the base class
    implementations.
    """

    def __init__(self, debug: bool = False):
        """
          :param pkg: basename for the package
          :param basedir: base directory where the task implementations are
          :param debug: print out debug information
        """
        self._debug = debug
        self._country = None
        self._log = PiiLogger(__name__, debug)


    def language_list(self) -> List[str]:
        """
        Return all languages defined
        """
        return union_sets(taskd_field(t["pii"], "lang")
                          for t in self._gather_tasks())


    def country_list(self, lang: str = None) -> List[str]:
        """
        Return the list of available countries
        """
        return union_sets(taskd_field(t["pii"], "country")
                          for t in self._gather_tasks())


    def gather_tasks_lang_country(self, lang: TYPE_STR_LIST = None,
                                  country: str = None) -> Iterable[Dict]:
        """
        Deliver descriptors for all task processors available for a given lang
        & country
        Needs a _gather_tasks() method in the subclass
        """
        # Get an iterator over all available tasks
        tasklist = self._gather_tasks(lang=lang)

        # All languages & countries
        if not lang and not country:
            yield from iter(tasklist)
            return

        # Specific language(s)
        if isinstance(lang, str):
            lang = [lang]
        if lang:
            lang = set(lang)

        # Specific country(s)
        if isinstance(country, str):
            country = [country]
        if country:
            country = set(country)

        for task in tasklist:
            if (not lang or taskd_field(task["pii"], "lang") & lang) and \
               (not country or taskd_field(task["pii"], "country") & country):
                yield task


    def gather_tasks(self, lang: TYPE_STR_LIST = None) -> Iterable[Dict]:
        """
        Build and return an iterable with all gathered tasks
         :param lang: list of languages for which tasks are searched for. If
           not passed, all available languages will be gathered
        """
        if lang is None:
            lang = self.language_list()
        elif isinstance(lang, str):
            lang = [lang]
        self._log(". gather-tasks lang=%s", lang)

        yield from self.gather_tasks_lang_country(lang, None)


    def _gather_tasks(self, lang: TYPE_STR_LIST) -> Iterable[Dict]:
        """
        Deliver an iterable of finalized task descriptors, to be implemented
        by subclasses.
        """
        raise UnimplementedException("missing _gather_tasks() method")
