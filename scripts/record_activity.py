from __future__ import annotations

import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path


BRT = timezone(timedelta(hours=-3))
AUTO_COMMIT_PREFIX = "chore(activity):"


def git_log_since(start_time: datetime) -> list[tuple[str, str]]:
    result = subprocess.run(
        [
            "git",
            "log",
            f"--since={start_time.astimezone(timezone.utc).isoformat()}",
            "--pretty=format:%H%x1f%s",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    commits: list[tuple[str, str]] = []
    for line in result.stdout.splitlines():
        if "\x1f" not in line:
            continue

        commit_hash, message = line.split("\x1f", 1)
        message = message.strip()

        if not message or message.startswith(AUTO_COMMIT_PREFIX):
            continue

        commits.append((commit_hash[:7], message))

    return commits


def main() -> None:
    now = datetime.now(BRT)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    commits = git_log_since(start_of_day)

    if not commits:
        print("Nenhuma atividade real encontrada hoje. Nenhum commit será criado.")
        return

    activity_dir = Path("journal/activity")
    activity_dir.mkdir(parents=True, exist_ok=True)

    file_path = activity_dir / f"{now:%Y-%m}.md"
    marker = f"<!-- activity:{now:%Y-%m-%d} -->"

    existing = file_path.read_text(encoding="utf-8") if file_path.exists() else ""
    if marker in existing:
        print("A atividade de hoje já foi registrada.")
        return

    if not existing:
        existing = f"# Atividade automática — {now:%m/%Y}\n\n"

    lines = [
        marker,
        f"## {now:%d/%m/%Y}",
        "",
        "Commits reais identificados no repositório:",
        "",
    ]
    lines.extend(f"- `{commit_hash}` — {message}" for commit_hash, message in reversed(commits))
    lines.extend(["", "---", ""])

    file_path.write_text(existing + "\n".join(lines), encoding="utf-8")
    print(f"Resumo automático salvo em {file_path}")


if __name__ == "__main__":
    main()
