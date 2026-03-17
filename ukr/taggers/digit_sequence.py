"""
DigitSequenceFst: ITN теггер для послідовностей цифр вимовлених по одній або групами.

Вхід:  "один два три чотири"
Вихід: digit_sequence { value: "1234" }

Після verbalizer:
  digit_sequence { value: "1234" } -> "1234"

Використання:
  - Коди:       "один два три чотири"         -> "1234"
  - Артикули:   "нуль нуль сім вісім"         -> "0078"
  - Рейси:      "два три нуль п'ять"          -> "2305"
  - Індекси:    "нуль дев'ять вісім сім шість" -> "09876"

Пріоритет: найнижчий серед числових класів (вище тільки word).
Спрацьовує лише для послідовностей від 4+ токенів щоб не конкурувати
з cardinal (1-3 цифри) та telephone (фіксований формат).
"""
import pynini
from pynini.lib import pynutil

from ukr.graph_utils import GraphFst, delete_space
from ukr.taggers.cardinal import CardinalFst


class DigitSequenceFst(GraphFst):
    """
    Теггер для довільних послідовностей цифр/груп.

    Кожен токен — одна цифра (0-9) або двозначне число (10-99)
    або трицифрове (100-999). FST склеює їх у єдиний рядок цифр.

    Мінімальна довжина: 4 цифри у результаті — щоб не перетинатись
    з cardinal який вже покриває 1-3 значні числа.
    """

    def __init__(self, cardinal: CardinalFst):
        super().__init__(name="digit_sequence", kind="classify")

        sp = delete_space

        # Використовуємо вже готові графи з cardinal
        # graph_zero:   "нуль" → "0"
        # graph_digit:  "сім"  → "7"
        # graph_teen:   "тринадцять" → "13"
        # graph_ties:   "п'ятдесят" → "5" (множник!)
        zero    = cardinal.graph_zero
        digit   = cardinal.graph_digit
        teen    = cardinal.graph_teen
        ties    = cardinal.graph_ties
        hundred = cardinal.graph_hundred

        # ── Один слот = одна цифра або група цифр ────────────────────────────

        # Одна цифра: 0–9
        d1 = zero | digit

        # Двозначне: 10–99
        d2 = (
            teen
            | ties + sp + digit
            | ties + pynutil.insert("0")
        )

        # Трицифрове: 100–999
        d3 = (
            hundred + sp + ties + sp + digit
            | hundred + sp + teen
            | hundred + sp + ties + pynutil.insert("0")
            | hundred + pynutil.insert("0") + sp + digit
            | hundred + pynutil.insert("00")
        )

        # Один слот: будь-яке число (пріоритет: d3 > d2 > d1)
        slot = d3 | d2 | d1

        # ── Послідовність слотів ──────────────────────────────────────────────
        # Мінімум: 2 слоти (щоб отримати 4+ цифри у більшості випадків)
        # Максимум: не обмежуємо

        # Перший слот — без пробілу перед ним
        # Наступні слоти — з пробілом перед кожним
        sequence = slot + pynini.closure(sp + slot, 1)  # 2+ слоти

        # ── Фільтр: результат має бути 4+ цифри ──────────────────────────────
        # Це не дає DigitSequence перехопити "двадцять два" (cardinal)
        # або "сімсот" (теж cardinal)
        from ukr.graph_utils import NEMO_DIGIT
        sequence = sequence @ pynini.closure(NEMO_DIGIT, 4)

        graph = (
            pynutil.insert("value: \"")
            + sequence
            + pynutil.insert("\"")
        )

        final_graph = self.add_tokens(graph)
        self.fst = final_graph.optimize()