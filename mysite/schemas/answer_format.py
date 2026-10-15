"""Обычный текст без Markdown и переносов строк внутри JSON-ответа."""
import re


def single_line_answer(value: str) -> str:
    answer = ""
    for line in value.splitlines():
        # Убираем маркер списка или Markdown-заголовка в начале строки.
        list_item = re.match(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)", line)
        line = re.sub(r"^\s*(?:[-*+]\s+|\d+[.)]\s+|#{1,6}\s+|>\s*)", "", line)
        # Сохраняем содержимое выделения и inline-кода, убирая оформление.
        for pattern in (r"\*\*(.+?)\*\*", r"__(.+?)__", r"`([^`]+)`"):
            line = re.sub(pattern, r"\1", line)
        line = " ".join(line.split())
        if not line:
            continue
        separator = " "
        if answer and list_item and not answer.endswith((".", "!", "?", ":", ";")):
            separator = ". "
        answer = answer + separator + line if answer else line
    return answer
