"""
FractionFst: ITN теггер для дробів та адрес з "дріб".

Вхід:  "шістнадцять дріб один"
Вихід: fraction { numerator: "16" denominator: "1" }

Після verbalizer:
  fraction { numerator: "16" denominator: "1" } -> "16/1"

Використання:
  - Адреси:  "Архипенка шістнадцять дріб один"  -> "Архипенка 16/1"
  - Дроби:   "три дріб чотири"                  -> "3/4"
  - Корпуси: "будинок п'ять дріб два"            -> "будинок 5/2"
"""
import pynini
from pynini.lib import pynutil

from ukr.graph_utils import GraphFst, delete_space
from ukr.taggers.cardinal import CardinalFst


class FractionFst(GraphFst):
    """
    Теггер для дробових виразів формату "число дріб число".

    Використовує cardinal.graph для розпізнавання числівників
    у всіх відмінках (оскільки CardinalFst вже об'єднує всі відмінки).
    """

    def __init__(self, cardinal: CardinalFst):
        super().__init__(name="fraction", kind="classify")

        # cardinal.graph — повний граф числівника (всі відмінки, без leading zeros)
        # cardinal.graph_zeroth — з leading zeros (для нумератора не потрібно)
        number = cardinal.graph

        # Роздільник "дріб" (і можливі варіанти вимови)
        delete_slash_word = pynutil.delete(
            pynini.union("дріб", "через", "слеш")
        )

        numerator = (
            pynutil.insert("numerator: \"")
            + number
            + pynutil.insert("\"")
        )

        denominator = (
            pynutil.insert("denominator: \"")
            + number
            + pynutil.insert("\"")
        )

        graph = (
            numerator
            + delete_space
            + delete_slash_word
            + delete_space
            + denominator
        )

        final_graph = self.add_tokens(graph)
        self.fst = final_graph.optimize()