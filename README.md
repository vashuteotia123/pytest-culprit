# pytest-culprit

A CLI tool to find the last Git commit where a specific pytest test started failing.

## 🚀 Installation

```bash
pip install pytest-culprit
```

## 🔍 Usage

```bash
pytest-culprit 15 pytest tests/test_rewards.py::test_logic
```

- `15`: Number of commits to check backward from HEAD
- `pytest ...`: The test command to run

## 🧠 What it does

- Walks backward through Git commits
- Runs your test command at each one
- Stops when the test passes
- Prints details of the last failing commit (the culprit)

## 📌 Example Output

```
📌 Starting from branch: main
▶️  Running test at commit 0a45b22 [3/15]
✅ Test started passing here.
❌ Last failing commit was:

commit f87d098
Author: Vishal Teotia <vishal@github.com>
Date:   2025-05-15

    break: tests

🧪 This commit broke: pytest tests/test_rewards.py::test_logic
```

---

## ⚖ License

MIT
