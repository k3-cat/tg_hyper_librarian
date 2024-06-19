if __name__ == "__main__":
    from pathlib import Path

    DIR = Path(__file__).parent / "rulesets"
    DIR.mkdir(exist_ok=True)

    from tg_hyper_librarian.profiles.default import generate_at

    generate_at(DIR)
