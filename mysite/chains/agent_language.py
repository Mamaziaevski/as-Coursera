"""Язык запроса и точные ответы по полям профиля."""
import re


def get_answer_language(message: str) -> str:
    text = message.lower()
    explicit = re.findall(r"кыргызча|по-кыргызски|на кыргызском|на русском|по-русски", text)
    if explicit:
        return "ky" if explicit[-1] in ("кыргызча", "по-кыргызски", "на кыргызском") else "ru"
    ky_words = re.findall(r"\b(?:менин|мага|кандай|качан|канча|бер|көрсөт|аты[а-яңөү]*|профилим[а-яңөү]*)\b", text)
    ru_words = re.findall(r"\b(?:покажи|мой|моё|моя|мне|какой|какая|когда|измени|удали|зарегистрируй)\b", text)
    if ky_words and len(ky_words) > len(ru_words):
        return "ky"
    return "ky" if not ru_words and re.search(r"[ңөү]", text) else "ru"


def profile_answer(profile: dict, message: str, language: str) -> str | None:
    text = message.lower()
    # Для команды изменения нужен результат операции, а не подстановка профиля.
    if re.search(r"измени|обнови|удали|создай|зарегистрируй|өзгөрт|өчүр", text):
        return None
    patterns = {
        "full_name": r"фио|имя|фамил|атым|атыңыз|атың|full_name",
        "email": r"почт|email|e-mail",
        "role": r"роль|роли|ролум|ролу",
        "id": r"\bid\b|идентификатор",
        "created_at": r"дата|дату|регистрац|катталган|катталдым|created_at",
        "is_active": r"актуал|актив|is_active",
    }
    fields = [field for field, pattern in patterns.items() if re.search(pattern, text)]
    if not fields:
        if "профил" not in text:
            return None
        fields = list(patterns)
    if fields == ["id"]:
        return str(profile["id"])
    if fields == ["email"] and re.search(r"только|гана", text):
        return profile["email"]
    labels = {
        "ru": {"full_name": "ФИО", "email": "Почта", "role": "Роль", "id": "ID", "created_at": "Дата регистрации", "is_active": "Аккаунт активен"},
        "ky": {"full_name": "Атыңыз", "email": "Почтаңыз", "role": "Ролуңуз", "id": "ID", "created_at": "Катталган күнүңүз", "is_active": "Аккаунтуңуз активдүү"},
    }
    answers = []
    for field in fields:
        value = profile[field]
        if field == "is_active":
            value = ("ооба" if value else "жок") if language == "ky" else ("да" if value else "нет")
        answers.append(f"{labels[language][field]}: {value}")
    return ". ".join(answers) + "."


def action_answer(name: str, language: str) -> str:
    messages = {
        "ru": {"register_user": "Регистрация успешна", "update_my_profile": "Профиль обновлён", "delete_my_profile": "Свой аккаунт удалён"},
        "ky": {"register_user": "Каттоо ийгиликтүү аяктады", "update_my_profile": "Профилиңиз жаңыртылды", "delete_my_profile": "Аккаунтуңуз өчүрүлдү"},
    }
    return messages[language][name]
