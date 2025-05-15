import subprocess
import sys
import argparse
from typing import List


def run_cmd(cmd: List[str], capture_output=False) -> subprocess.CompletedProcess:
    try:
        result = subprocess.run(
            cmd,
            capture_output=capture_output,
            text=True,
            check=True
        )
        return result
    except subprocess.CalledProcessError as e:
        return e


def get_last_n_commits(n: int) -> List[str]:
    result = run_cmd(["git", "rev-list", "--max-count", str(n), "HEAD"], capture_output=True)
    return result.stdout.strip().split("\n")


def checkout_commit(commit: str):
    print(f"🔀 Checking out {commit}")
    run_cmd(["git", "checkout", commit], capture_output=True)


def test_passes(test_cmd: List[str]) -> bool:
    result = run_cmd(test_cmd, capture_output=True)
    return result.returncode == 0


def get_commit_full_info(commit: str) -> str:
    result = run_cmd(["git", "show", "--quiet", commit], capture_output=True)
    return result.stdout.strip()


def get_current_branch() -> str:
    result = run_cmd(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True)
    return result.stdout.strip()


def main():
    parser = argparse.ArgumentParser(description="Trace back until a test starts passing.")
    parser.add_argument("n", type=int, help="Number of commits to look back")
    parser.add_argument("test_cmd", nargs=argparse.REMAINDER, help="Test command to run (e.g. pytest tests/...)")
    args = parser.parse_args()

    original_branch = get_current_branch()
    print(f"📌 Starting from branch: {original_branch}")
    commits = get_last_n_commits(args.n)

    if not commits:
        print("❌ No commits found.")
        return

    last_failing_commit = None

    for idx, commit in enumerate(commits):
        checkout_commit(commit)
        print(f"▶️  Running test at commit {commit} [{idx+1}/{len(commits)}]")

        if test_passes(args.test_cmd):
            if last_failing_commit:
                print("\n🚨 Test started passing here.")
                print("❌ Last failing commit was:")
                print(get_commit_full_info(last_failing_commit))
                print(f"\n🧪 This commit broke: {' '.join(args.test_cmd)}")
            else:
                print("✅ Test passed for all checked commits.")
            break
        else:
            last_failing_commit = commit
    else:
        print(f"❌ Test failed for all {args.n} commits.")

    print(f"\n🔁 Resetting to original branch: {original_branch}")
    run_cmd(["git", "checkout", original_branch], capture_output=True)


if __name__ == "__main__":
    main()
