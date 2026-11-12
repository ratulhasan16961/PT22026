"""Remove '#' comments from Python files without touching strings or docstrings."""
import io
import sys
import tokenize
from pathlib import Path

SKIP_DIRS = {".venv", "__pycache__", ".git", "data", "models", "figures"}


def find_comments(source):
    tokens = tokenize.generate_tokens(io.StringIO(source).readline)
    return [(t.start[0], t.start[1], t.string) for t in tokens if t.type == tokenize.COMMENT]


def strip_comments(source):
    lines = source.splitlines(keepends=True)
    for row, col, _ in find_comments(source):
        line = lines[row - 1]
        ending = "\n" if line.endswith("\n") else ""
        kept = line[:col].rstrip()
        lines[row - 1] = kept + ending if kept else ""
    return "".join(lines)


def main():
    root = Path(sys.argv[1]).expanduser()
    apply = "--apply" in sys.argv
    total = 0
    for path in sorted(root.rglob("*.py")):
        if SKIP_DIRS & set(path.relative_to(root).parts):
            continue
        source = path.read_text(encoding="utf-8")
        comments = find_comments(source)
        if not comments:
            continue
        total += len(comments)
        print(f"\n{path.relative_to(root)}: {len(comments)} comment(s)")
        for row, _, text in comments:
            print(f"  line {row}: {text}")
        if apply:
            new_source = strip_comments(source)
            compile(new_source, str(path), "exec")
            path.write_text(new_source, encoding="utf-8")
    print(f"\nTotal comments {'removed' if apply else 'found'}: {total}")
    if not apply:
        print("Nothing changed. Run again with --apply to remove them.")


if __name__ == "__main__":
    main()
