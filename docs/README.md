# Design Notes

Background on why pytest-culprit works the way it does. If you're about to propose a change to the search strategy, start here.

## Why not binary search?

**Short answer:** it gives the wrong commit on any test that has broken more than once, and it can give a different wrong commit each time you run it.

This has been proposed several times ([#1](https://github.com/vashuteotia123/pytest-culprit/issues/1), [#9](https://github.com/vashuteotia123/pytest-culprit/issues/9)), and the reasoning for rejecting it is the same each time.

### The assumption bisection makes

Binary search — hand-rolled or via `git bisect run` — assumes the test has exactly **one** pass → fail transition in the range being searched:

```
older ───────────────────────────────────────────► newer
  pass  pass  pass  pass  FAIL  FAIL  FAIL  FAIL
                        ▲
                        the single boundary
```

Given that shape, halving the range is sound: probing any commit tells you which side the boundary is on.

### Why that assumption doesn't hold

Real tests break, get fixed, and break again:

```
older ───────────────────────────────────────────► newer
  pass  FAIL  FAIL  pass  pass  FAIL  FAIL  FAIL
      ▲               ▲       ▲
      break        fixed    broke again
```

There are now three transitions. Bisection has no way to know that — probing a commit tells it "pass" or "fail", never "how many boundaries are to my left." So it converges on *a* boundary, and **which one depends entirely on where the midpoints happen to land**. Change `n`, add a commit, and the same repository with the same test can report a different culprit.

That last property is the disqualifying one. A debugging tool that returns unstable answers is worse than a slow one, because you can't tell a wrong answer from a right one.

### Why the linear walk is correct

pytest-culprit walks backward from `HEAD` and stops at the first commit where the test passes. The commit immediately after it is, by construction, the **most recent** point at which the test broke:

```
older ───────────────────────────────────────────► newer
  pass  FAIL  FAIL  pass  pass  FAIL  FAIL  FAIL
                          ▲     ▲            │
                          │     │            │
                     stops here │     walks backward from HEAD
                                │
                          reports this one — the most recent break
```

This holds regardless of how many times the test broke earlier in history. "When did this most recently start failing" is the question the tool exists to answer, and the linear walk answers it exactly.

The cost is O(n) runs of your test suite instead of O(log n). That cost is what buys the correctness — it is a deliberate trade, not an optimization nobody got around to.

### What about `git bisect run`?

Same problem. `git bisect` carries the identical single-transition assumption; delegating to it moves the unsound assumption into git rather than removing it. It would bring useful machinery for free (worktree restore, `git bisect skip`), but not at the price of the tool's core guarantee.

### What would change this

Bisection becomes viable only if the tool's contract changes to "find *some* commit where the test broke" rather than "find the most recent one" — for example behind an explicit opt-in flag, documented as approximate, for users who know their test broke exactly once and have a long history to search. Nobody has asked for that yet.

## Related

- [#10](https://github.com/vashuteotia123/pytest-culprit/issues/10) — commits where the test *cannot run* (collection errors, missing dependencies) are currently counted as failures. This is a genuine gap in the linear walk and is unrelated to the search strategy.
