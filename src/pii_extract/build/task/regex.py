"""
Define the RegexPiiTask subclass
"""
import regex

from typing import Iterable

from pii_data.types import PiiEntity
from pii_data.types.doc import DocumentChunk

from .base import BasePiiTask


class RegexPiiTask(BasePiiTask):
    """
    A wrapper for a PII implemented as a regex pattern
    Instead of the standard "re" package it uses the "regex" package (in
    backwards-compatible mode).
    Since it inherits from BasePiiTask, it will automatically apply context
    validation after regex matching, if a suitable context argument is added
    """

    def __init__(self, pattern: str, **kwargs):
        """
          :param pattern: a string containing a regex pattern
        """
        super().__init__(**kwargs)
        self.regex = regex.compile(pattern, flags=regex.X | regex.VERSION0)


    def find(self, chunk: DocumentChunk) -> Iterable[PiiEntity]:
        """
        Iterate over the regex and produce Pii objects
        """
        defaults = self.get_pii_defaults()
        for cc in self.regex.finditer(chunk.data):
            g = 1 if cc.lastindex is not None else 0
            yield PiiEntity(self.pii_info, cc.group(g), chunk.id, cc.start(g),
                            **defaults)
