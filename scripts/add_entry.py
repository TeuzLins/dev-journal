from __future__ import annotations

import os
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


BRASILIA = ZoneInfo("America/Sao_Paulo")


def required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"A variável {name} é obrigatória.")
    return value


def single_line(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def set_github_output(name: str, value: str) -> None:
    output_path = os.getenv("GITHUB_OUTPUT")
    if not output_path:
        return

    with Path(output_path).open("a", encoding="utf-8") as output_file:
        output_file.write(f"{name}={value}\n")


def main() -> None:
    activity_type = single_line(required_env("ACTIVITY_TYPE"))
    details = single_line(os.getenv("DETAILS", ""))
    class_study = single_line(os.getenv("CLASS_STUDY", ""))

    now = datetime.now(BRASILIA)
    journal_dir = Path("journal")
    journal_dir.mkdir(parents=True, exist_ok=True)

    file_path = journal_dir / f"{now:%Y-%m}.md"
    if not file_path.exists():
        file_path.write_text(
            f"# Dev Journal — {now:%m/%Y}\n\n",
            encoding="utf-8",
        )

    entry = [
        f"## {now:%d/%m/%Y} — Início às {now:%H:%M}",
        "",
        f"**Atividade:** {activity_type}",
        "",
    ]

    if details:
        entry.extend([f"**O que será feito:** {details}", ""])

    if class_study:
        entry.extend([
            f"**O que estudou na aula da faculdade:** {class_study}",
            "",
        ])

    entry.extend(["---", ""])

    with file_path.open("a", encoding="utf-8") as journal_file:
        journal_file.write("\n".join(entry) + "\n")

    commit_title = f"{now:%d/%m/%Y %H:%M} — {activity_type}"
    set_github_output("commit_title", commit_title)
    print(f"Atividade registrada em {file_path}: {commit_title}")


if __name__ == "__main__":
    try:
        main()
    except ValueError as error:
        raise SystemExit(str(error)) from error
