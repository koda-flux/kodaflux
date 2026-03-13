import pathlib
import shutil
from pathspec import PathSpec


def setup_env_files():
    root = pathlib.Path.cwd()
    gitignore_file = root / ".gitignore"
    if gitignore_file.exists():
        with open(gitignore_file, "r") as f:
            spec = PathSpec.from_lines("gitwildmatch", f)
    else:
        spec = PathSpec.from_lines("gitwildmatch", [])

    print("🚀 Scanning for .env.example files...")

    for example_path in root.rglob(".env.example"):
        relative_path = example_path.relative_to(root)
        if spec.match_file(str(relative_path)):
            continue

        env_path = example_path.parent / ".env"

        if not env_path.exists():
            shutil.copy2(example_path, env_path)
            print(f"✅ Created: {env_path.relative_to(root)}")
        else:
            print(f"ℹ️  Skipped (exists): {env_path.relative_to(root)}")


if __name__ == "__main__":
    setup_env_files()
    print("✨ Done!")
