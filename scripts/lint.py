from subprocess import run


def main():
    """Lint all python files in the project"""
    ruff_check = run(["ruff", "check", "--fix", "."])
    ruff_format = run(["ruff", "format", "."])
    exit_code = (
        0 if ruff_check.returncode == 0 and ruff_format.returncode == 0 else 1
    )
    exit(exit_code)
