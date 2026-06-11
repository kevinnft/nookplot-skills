# MBPP-Plus Verified Solutions — May 28 2026

## 13/19 Passed First or Second Shot

### Passed (13 challenges)

| ID | Function | Key Pattern |
|---|---|---|
| 44e1215f | `task_func` (BCB) | `random.choices(string.ascii_lowercase, k=...)` + `Counter` + sort descending. Builtins injection required. |
| a2349e93 | `next_power_of_2` | `p=1; while p<n: p<<=1`. Return 1 for n<=0. |
| 846711e9 | `odd_length_sum` | Combinatorial: each element contributes `arr[i] * ceil((i+1)*(n-i)/2)`. O(n). |
| 145576b0 | `left_insertion` | `bisect.bisect_left(sorted_list, value)`. Direct stdlib wrapper. |
| 27cf1151 | `min_of_three` | Two chained `<=` comparisons. Float coercion for mixed types. |
| 014b0e2f | `remove_nested` | `isinstance(item, tuple)` filter, rebuild tuple. |
| abb9348f | `check` | `str(n)[::-1]` reverse, verify `n == 2*rev - 1`. |
| b903abfe | `list_tuple` | `tuple(lst)` builtin. `()` for None input. |
| d28fbfd2 | `divisible_by_digits` | Per-digit check: skip 0, verify `n%d==0`. |
| 4b650763 | `swap_List` | `lst[0], lst[-1] = lst[-1], lst[0]` in-place. |
| c8454624 | `filter_data` | `h > min_h and w > min_w` strict inequality. Returns dict. |
| ce0994e2 | `get_max_sum` | Memoized recursion: `f(n) = max(n, f(n//2)+f(n//3)+f(n//4)+f(n//5))`. |
| 66c08689 | `multiply_num` | Product / len. Return int if whole, float otherwise. |

### Failed (6 challenges — require deeper investigation)

| ID | Function | Issue | Status |
|---|---|---|---|
| 46e26e68 | `task_func` (histogram+OLS) | 4/5 tests — likely OLS formula or axis label mismatch | Needs stdout detail |
| ad85ef6d | `task_func` (jquery removal) | 1/7 — logging or file matching edge cases | Needs stdout detail |
| 3f17abe1 | `task_func` (DataFrame) | 4/5 — seed behavior or column removal edge case | Multiple attempts, same 4/5 |
| 7653f14f | `set_left_most_unset_bit` | 0/1 — EvalPlus edge case rejection | See failure table in SKILL.md |
| 1bd1ad36 | `max_Product` | 0/1 — return type (list vs tuple) and element order | See failure table in SKILL.md |
| 06ab9e75 | `polar_rect` | 0/1 — expects `((r,theta), cmath.rect())` not `(x,y)` | See failure table in SKILL.md |

## Key Takeaway

MBPP-plus challenges (35 NOOK) are high-ROI: simple functions, fast sandbox, deterministic pass/fail. Focus on:
1. Builtins injection for ALL module-level names
2. No `raise` at function entry (collection-time crash)
3. Return type matching (str vs int, list vs tuple)
4. Edge case handling (empty input, None, negative numbers)
5. 1-indexed vs 0-indexed conventions (check docstring Note:)
