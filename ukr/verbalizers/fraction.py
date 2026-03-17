"""
FractionFst verbalizer:
  fraction { numerator: "16" denominator: "1" } -> "16/1"
"""
import pynini
from pynini.lib import pynutil

from ukr.graph_utils import GraphFst, delete_space, NEMO_NOT_QUOTE


class FractionFst(GraphFst):
    def __init__(self):
        super().__init__(name="fraction", kind="verbalize")

        number = pynini.closure(NEMO_NOT_QUOTE, 1)

        numerator = (
            pynutil.delete("numerator:")
            + delete_space
            + pynutil.delete("\"")
            + number
            + pynutil.delete("\"")
        )

        denominator = (
            pynutil.insert("/")
            + pynutil.delete("denominator:")
            + delete_space
            + pynutil.delete("\"")
            + number
            + pynutil.delete("\"")
        )

        graph = numerator + delete_space + denominator

        self.fst = self.delete_tokens(graph).optimize()