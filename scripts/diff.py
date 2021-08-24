import shlex
from subprocess import check_output


def extract_diff_file(diff_line: str) -> str:
    # diff_line is in format of diff --git a/filepath b/filepath
    return shlex.split(diff_line)[2][2:]


def get_changed_files():
    lines = check_output(["git", "diff", "HEAD~1", "HEAD~2"]).decode().split("\n")
    diff_lines = filter(lambda line: line.startswith("diff --git"), lines)
    return [*map(extract_diff_file, diff_lines)]


if __name__ == "__main__":
    print(*get_changed_files(), sep="\n")
