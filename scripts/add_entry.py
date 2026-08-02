from __future__ import annotations

import os
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path


BRT = timezone(timedelta(hours=-3))


def required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"A variável {name} é obrigatória.")
    return value


def sanitize_single_line(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def main() -> None:
    topic = sanitize_single_line(required_env("TOPIC"))
    summary = required_env("SUMMARY")
    learning = required_env("LEARNING")
    next_step = os.getenv("NEXT_STEP", "").strip() or "Não definido."

    now = datetime.now(BRT)
    journal_dir = Path("journal")
    journal_dir.mkdir(parents=True, exist_ok=True)

    file_path = journal_dir / f"{now:%Y-%m}.md"
    if not file_path.exists():
        file_path.write_text(
            f"# Dev Journal — {now:%m/%Y}\n\n",
            encoding="utf-8",
        )

    entry = (
        f"## {now:%d/%m/%Y} — {topic}\n\n"
        f"**Resumo:** {summary.strip()}\n\n"
        f"**Aprendizado:** {learning.strip()}\n\n"
        f"**Próximo passo:** {next_step}\n\n"
        "---\n\n"
    )

    with file_path.open("a", encoding="utf-8") as journal_file:
        journal_file.write(entry)

    print(f"Entrada registrada em {file_path}")


if __name__ == "__main__":
    try:
        main()
    except ValueError as error:
        raise SystemExit(str(error)) from error
