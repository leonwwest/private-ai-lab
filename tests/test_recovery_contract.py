from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_recovery_exercise_is_guarded_and_never_targets_the_primary_database() -> None:
    script = (ROOT / "scripts" / "postgres-recovery.sh").read_text()

    assert "CONFIRM_POSTGRES_RECOVERY_EXERCISE" in script
    assert 'restore_database="private_ai_restore_check"' in script
    assert '--dbname "${restore_database}"' in script
    primary_restore = (
        "pg_restore \\\n"
        '    --username "${postgres_user}" \\\n'
        '    --dbname "${primary_database}"'
    )
    assert primary_restore not in script
    assert "trap drop_restore_database EXIT" in script
    assert "Primary database modified: no" in script


def test_recovery_artifacts_are_ignored() -> None:
    gitignore = (ROOT / ".gitignore").read_text().splitlines()

    assert ".local/" in gitignore
