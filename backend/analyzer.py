import re

ALREADY_OPTIMAL_PATTERNS = {
    "Hashing", "Two Pointer", "Sliding Window", "Binary Search", "Single Pass",
    "Union-Find (Disjoint Set)", "Fast & Slow Pointers", "Trie",
    "Graph BFS", "Graph DFS", "Monotonic Stack", "Prefix Sum", "Bit Manipulation",
    "Kadane's Algorithm", "Matrix Traversal", "Interval Merging",
    "Topological Sort", "Segment Tree / Fenwick Tree", "Divide and Conquer",
}


def complexity_rank(time_complexity: str) -> int:
    """Converts a time-complexity string into a comparable rank (lower = faster). Used for comparing multiple solutions."""
    s = (time_complexity or "").lower()
    if "1)" in s:
        return 0
    if "log n)" in s and "n log n" not in s:
        return 1
    if "n log n" in s:
        return 3
    if "n^3" in s or "higher" in s:
        return 5
    if "n^2" in s or "n²" in s or "rows" in s:
        return 4
    if "exponential" in s:
        return 7
    if s.strip().startswith("o(n)") or s.strip() == "o(n)" or "v + e" in s:
        return 2
    return 6  # unknown / unverified


def generate_hint(pattern: str) -> dict:
    """Day 6 — Hint Mode. Returns {"is_optimal": bool, "message": str}."""
    if pattern in ALREADY_OPTIMAL_PATTERNS:
        return {
            "is_optimal": True,
            "message": "✅ Your code is already optimal for this approach — no further optimization needed based on the pattern used.",
        }

    hints = {
        "Recursion": "Think about what smaller subproblem this function solves, and what its base case is. Are any subproblems being solved more than once?",
        "Sorting": "Would sorting the data first make it easier to spot pairs, boundaries, or duplicates without extra nested checks?",
        "Brute Force": "You're comparing every possible pair. Is there information from earlier comparisons you could reuse instead of starting fresh each time?",
        "Dynamic Programming": "Are you recomputing the same subproblem multiple times? Storing results (memoization/tabulation) is likely already helping — check if a 1D array could replace a 2D one to save space.",
        "Backtracking": "Backtracking is often inherently exponential for this problem type — but check if you can 'prune' early (skip a branch as soon as you know it can't work) to avoid wasted exploration.",
        "Unclassified": "Try tracing through with a small example by hand — where exactly does the work get repeated?",
    }

    message = hints.get(
        pattern,
        "Look for the part of your code that repeats work unnecessarily — that's usually where the optimization hides.",
    )
    return {"is_optimal": False, "message": message}


def compute_code_quality(code: str, max_nesting: int) -> dict:
    """
    Day 17 — Code Quality Score.
    A simple rule-based readability/maintainability score out of 10.
    This is NOT about correctness or efficiency (that's covered by the
    complexity analysis) — purely about how readable/maintainable the
    code looks.
    """
    score = 10
    notes = []

    lines = [l for l in code.splitlines() if l.strip()]

    # Long lines hurt readability
    long_lines = [l for l in lines if len(l) > 100]
    if long_lines:
        score -= 1
        notes.append("Some lines are quite long — breaking them up could improve readability.")

    # No comments at all in a longer solution
    has_comment = bool(re.search(r"(//|#|/\*)", code))
    if not has_comment and len(lines) > 15:
        score -= 1
        notes.append("Consider adding a few comments to explain non-obvious steps.")

    # Single-letter variable names beyond common loop counters (i, j, k, n, m)
    single_letter_vars = re.findall(r"\b(?:int|long|string|auto|var|let)\s+([a-hlop-z])\b", code, re.IGNORECASE)
    if len(single_letter_vars) > 2:
        score -= 1
        notes.append("A few variable names are single letters — more descriptive names (beyond loop counters) can help readability.")

    # Repeated 'magic numbers' (same numeric literal, not 0/1/-1, appearing 3+ times)
    numbers = re.findall(r"(?<![\w.])(\d{2,})(?![\w.])", code)
    from collections import Counter
    number_counts = Counter(numbers)
    if any(count >= 3 for count in number_counts.values()):
        score -= 1
        notes.append("A repeated numeric literal appears — naming it as a constant would make intent clearer.")

    # Deep nesting hurts readability even if complexity is fine
    if max_nesting >= 3:
        score -= 1
        notes.append("Deep nesting (3+ levels) can hurt readability — consider extracting a helper function.")

    score = max(3, min(10, score))  # keep in a sane 3–10 range

    if not notes:
        notes.append("Clean and readable — no obvious style issues detected.")

    return {"score": score, "notes": notes}


def generate_edge_cases(pattern: str) -> list:
    """
    Day 18 — Edge Case Suggestions.
    Returns a short list of edge cases worth testing, tailored to the
    detected pattern. Always includes a couple of universal ones plus
    pattern-specific ones.
    """
    general = ["Empty input (array/string of length 0)", "Single-element input"]

    pattern_specific = {
        "Hashing": ["All elements are duplicates", "Target value not present in the input"],
        "Two Pointer": ["Array with all identical elements", "Target not achievable by any pair"],
        "Sliding Window": ["Window size larger than the array itself", "All elements identical"],
        "Binary Search": ["Array not actually sorted (breaks the binary search assumption)", "Target smaller than all elements / larger than all elements"],
        "Recursion": ["Very large input causing deep recursion (stack overflow risk)", "n = 0 or a negative input"],
        "Sorting": ["Already-sorted input", "Reverse-sorted input"],
        "Brute Force": ["All elements are duplicates", "No valid pair/answer exists"],
        "Dynamic Programming": ["n = 0 base case", "Very large n (watch for integer overflow in sums)"],
        "Backtracking": ["No valid solution exists at all", "All elements identical (many duplicate branches)"],
        "Graph BFS": ["Disconnected graph (unreachable nodes)", "Graph with a cycle", "A single isolated node with no edges"],
        "Graph DFS": ["Disconnected graph (unreachable nodes)", "Graph with a cycle", "A single isolated node with no edges"],
        "Topological Sort": ["A cycle exists (no valid topological order possible)"],
        "Fast & Slow Pointers": ["Empty linked list", "Linked list with a single node", "List that has no cycle at all"],
        "Matrix Traversal": ["Empty grid (0 rows or 0 columns)", "Grid with only 1 row or only 1 column"],
        "Interval Merging": ["No overlapping intervals at all", "All intervals overlap into a single merged one"],
        "Bit Manipulation": ["n = 0", "Negative numbers (sign-bit handling)"],
        "Trie": ["Inserting an empty string", "A prefix that matches no stored word"],
        "Union-Find (Disjoint Set)": ["Elements that are already in the same set", "Calling union on an element with itself"],
        "Kadane's Algorithm": ["All-negative numbers", "All-positive numbers"],
        "Heap / Priority Queue": ["Operating on an empty heap"],
        "Segment Tree / Fenwick Tree": ["Query range out of bounds", "Update exactly at a boundary index"],
    }

    specific = pattern_specific.get(pattern, ["Very large input (check performance holds up)", "Boundary values (0, negative numbers, maximum constraints)"])
    return general + specific


def analyze_code(problem: str, code: str, language: str) -> dict:
    """
    Rule-based static analysis. No AI here — just pattern matching on the
    code text. Covers a broad set of common DSA patterns.

    NOTE: 'Greedy' is intentionally NOT detected — it has no reliable
    syntactic signature (it's a strategy, not a code shape), so any
    keyword-based detection would produce too many false positives to
    be trustworthy. It's better to not classify it than to mislabel it.
    """
    code_lower = code.lower()

    # ---- 1. Loop nesting depth ----
    if language.lower() == "python":
        max_nesting = get_max_loop_nesting_python(code)
    else:
        max_nesting = get_max_loop_nesting(code)

    # ---- 2. Detect signals ----
    has_sort = bool(re.search(r"\bsort\s*\(", code_lower)) or "sorted(" in code_lower
    has_hashmap = any(kw in code_lower for kw in [
        "unordered_map", "unordered_set", "hashmap", "hashset",
        "dict(", "{}", "set()", " map<", "map<string", "map<integer"
    ])
    has_binary_search_hint = "binary_search" in code_lower or (
        "while" in code_lower and ("mid" in code_lower or ("low" in code_lower and "high" in code_lower))
    )
    has_recursion = is_recursive(code)
    has_two_pointer = is_two_pointer(code_lower)
    has_sliding_window = is_sliding_window(code_lower)

    has_dp = any(kw in code_lower for kw in ["dp[", "dp =", "memo[", "memo.", "cache[", "dp={", "dp = {"])
    has_dp_2d = bool(re.search(r"dp\[[^\]]+\]\[[^\]]+\]", code_lower))

    has_backtracking = has_recursion and any(kw in code_lower for kw in [
        "backtrack", "path.pop", "pop_back", ".remove(", "undo"
    ]) and any(kw in code_lower for kw in [".add(", "path.append", "push_back", ".append("])

    has_visited = "visited" in code_lower
    has_graph_structure = any(kw in code_lower for kw in ["adj", "graph", "neighbor", "edges"])
    has_queue = any(kw in code_lower for kw in ["queue<", "collections.deque", "deque(", "queue.queue"])
    has_graph_bfs = has_queue and has_visited
    has_graph_dfs = has_recursion and has_visited and has_graph_structure and not has_graph_bfs

    has_bit_manipulation = any(kw in code_lower for kw in [
        "<<", ">>", "__builtin_popcount", "bin(", "bitcount", "^=", "&=", "|="
    ])

    has_prefix_sum = any(kw in code_lower for kw in ["prefix[", "prefixsum", "prefix_sum", "cumsum"])

    has_stack_struct = "stack" in code_lower
    has_monotonic_stack = has_stack_struct and "while" in code_lower and (
        ".pop(" in code_lower or "pop_back(" in code_lower
    )

    has_heap = any(kw in code_lower for kw in ["priority_queue", "heapq", "priorityqueue", "heapify"])

    has_union_find = ("parent[" in code_lower or "parent =" in code_lower) and (
        "find(" in code_lower or "union(" in code_lower
    )

    has_fast_slow_pointer = "slow" in code_lower and "fast" in code_lower and (
        "->next" in code_lower or ".next" in code_lower
    )

    has_trie = "trienode" in code_lower or "trie" in code_lower

    has_kadane = any(kw in code_lower for kw in [
        "maxsofar", "max_so_far", "maxendinghere", "max_ending_here", "kadane"
    ])

    has_matrix = any(kw in code_lower for kw in ["grid[", "matrix[", "dx[", "dy["]) or bool(
        re.search(r"\b\w+\[[^\]]+\]\[[^\]]+\]", code_lower)
    ) and max_nesting >= 2

    has_interval_merge = "interval" in code_lower and has_sort and (
        "merged" in code_lower or ".back()" in code_lower or "result[-1]" in code_lower
    )

    has_topo_sort = any(kw in code_lower for kw in [
        "indegree", "in_degree", "topological", "topo_sort", "kahn"
    ])

    has_segment_tree = any(kw in code_lower for kw in [
        "segtree", "segment_tree", "segmenttree", "fenwick", "bit_tree"
    ])

    has_divide_conquer = has_recursion and "mid" in code_lower and any(kw in code_lower for kw in [
        "merge(", "mergesort", "merge_sort", "quicksort", "quick_sort", "partition"
    ]) and not has_binary_search_hint

    # ---- 3. Decide pattern + approach ----
    # Order matters: more specific/structural patterns are checked before
    # generic fallbacks like "nested loop = brute force".
    if has_trie:
        pattern = "Trie"
        approach = "Prefix-tree based lookup/insertion"
    elif has_segment_tree:
        pattern = "Segment Tree / Fenwick Tree"
        approach = "Tree/array structure built for fast range queries and updates"
    elif has_topo_sort:
        pattern = "Topological Sort"
        approach = "Orders nodes based on dependencies (in-degree tracking)"
    elif has_union_find:
        pattern = "Union-Find (Disjoint Set)"
        approach = "Disjoint Set Union for grouping/connectivity"
    elif has_heap:
        pattern = "Heap / Priority Queue"
        approach = "Priority queue used to repeatedly get the min/max element"
    elif has_fast_slow_pointer:
        pattern = "Fast & Slow Pointers"
        approach = "Two pointers moving at different speeds (commonly for cycle detection)"
    elif has_backtracking:
        pattern = "Backtracking"
        approach = "Explores choices recursively and undoes ('backtracks') when a path fails"
    elif has_graph_bfs:
        pattern = "Graph BFS"
        approach = "Breadth-first traversal using a queue and a visited set"
    elif has_graph_dfs:
        pattern = "Graph DFS"
        approach = "Depth-first traversal using recursion and a visited set"
    elif has_divide_conquer:
        pattern = "Divide and Conquer"
        approach = "Splits the problem in half, solves recursively, then combines results"
    elif has_dp:
        pattern = "Dynamic Programming"
        approach = "Stores results of subproblems to avoid recomputation (memoization/tabulation)"
    elif has_interval_merge:
        pattern = "Interval Merging"
        approach = "Sorts intervals, then merges overlapping ranges in one pass"
    elif has_kadane:
        pattern = "Kadane's Algorithm"
        approach = "Tracks the best running sum, resetting when it turns negative"
    elif has_monotonic_stack:
        pattern = "Monotonic Stack"
        approach = "Stack maintained in increasing/decreasing order to answer range queries efficiently"
    elif has_prefix_sum:
        pattern = "Prefix Sum"
        approach = "Precomputed cumulative sums for fast range-sum queries"
    elif has_recursion:
        pattern = "Recursion"
        approach = "Recursive approach"
    elif has_binary_search_hint:
        pattern = "Binary Search"
        approach = "Binary search on sorted/range data"
    elif has_two_pointer:
        pattern = "Two Pointer"
        approach = "Two indices moving toward/across each other"
    elif has_sliding_window:
        pattern = "Sliding Window"
        approach = "Expanding/shrinking window over a contiguous range"
    elif has_bit_manipulation:
        pattern = "Bit Manipulation"
        approach = "Uses bitwise operations for efficient computation"
    elif has_matrix:
        pattern = "Matrix Traversal"
        approach = "Traverses a 2D grid, typically visiting each cell once"
    elif max_nesting >= 2:
        pattern = "Brute Force"
        approach = "Nested loop / brute force comparison"
    elif has_hashmap:
        pattern = "Hashing"
        approach = "Hash map / hash set based lookup"
    elif has_sort:
        pattern = "Sorting"
        approach = "Sort-based approach"
    elif max_nesting == 1:
        pattern = "Single Pass"
        approach = "Single loop traversal"
    else:
        pattern = "Unclassified"
        approach = "Could not confidently detect a pattern from static rules"

    # ---- 4. Time complexity ----
    if pattern in ("Graph BFS", "Graph DFS", "Topological Sort"):
        time_complexity = "O(V + E)"
    elif pattern == "Backtracking":
        time_complexity = "Exponential (problem-dependent)"
    elif pattern == "Dynamic Programming":
        time_complexity = "O(n^2)" if has_dp_2d else "O(n)"
    elif pattern == "Union-Find (Disjoint Set)":
        time_complexity = "O(n) (near-constant per operation, amortized)"
    elif pattern == "Heap / Priority Queue":
        time_complexity = "O(n log n)"
    elif pattern in ("Monotonic Stack", "Prefix Sum", "Fast & Slow Pointers", "Two Pointer", "Sliding Window", "Kadane's Algorithm"):
        time_complexity = "O(n)"
    elif pattern == "Trie":
        time_complexity = "O(L) per word (L = word length)"
    elif pattern == "Matrix Traversal":
        time_complexity = "O(rows × cols)"
    elif pattern == "Interval Merging":
        time_complexity = "O(n log n)"
    elif pattern == "Segment Tree / Fenwick Tree":
        time_complexity = "O(log n) per query/update"
    elif pattern == "Divide and Conquer":
        time_complexity = "O(n log n)"
    elif has_two_pointer or has_sliding_window:
        time_complexity = "O(n)"
    elif max_nesting >= 3:
        time_complexity = "O(n^3) or higher"
    elif max_nesting == 2:
        time_complexity = "O(n^2)"
    elif has_sort and max_nesting <= 1:
        time_complexity = "O(n log n)"
    elif has_binary_search_hint:
        time_complexity = "O(log n)"
    elif max_nesting == 1:
        time_complexity = "O(n)"
    elif has_recursion:
        time_complexity = "Depends on recursion depth (needs manual check)"
    else:
        time_complexity = "O(1)"

    # ---- 5. Space complexity ----
    if pattern in ("Graph BFS", "Graph DFS", "Union-Find (Disjoint Set)", "Topological Sort"):
        space_complexity = "O(V)"
    elif pattern == "Dynamic Programming":
        space_complexity = "O(n^2)" if has_dp_2d else "O(n)"
    elif pattern == "Backtracking":
        space_complexity = "O(n) (recursion stack + current path)"
    elif pattern in ("Monotonic Stack", "Heap / Priority Queue", "Prefix Sum", "Trie", "Interval Merging", "Segment Tree / Fenwick Tree"):
        space_complexity = "O(n)"
    elif pattern in ("Fast & Slow Pointers", "Kadane's Algorithm"):
        space_complexity = "O(1)"
    elif pattern == "Matrix Traversal":
        space_complexity = "O(1) (unless a separate visited grid is used)"
    elif pattern == "Divide and Conquer":
        space_complexity = "O(n) (auxiliary arrays + recursion stack)"
    elif has_hashmap:
        space_complexity = "O(n)"
    elif has_recursion:
        space_complexity = "O(n) (recursion call stack)"
    else:
        space_complexity = "O(1)"

    # ---- 6. Optimization hint ----
    if pattern in ALREADY_OPTIMAL_PATTERNS or pattern in ("Dynamic Programming", "Backtracking", "Heap / Priority Queue"):
        if pattern == "Dynamic Programming" and has_dp_2d:
            optimization = "Consider whether a 1D array could replace the 2D dp table to reduce space complexity."
        elif pattern == "Backtracking":
            optimization = "Check if you can prune branches early (exit as soon as a partial solution can't possibly work)."
        else:
            optimization = "This is already an optimal or near-optimal pattern for this kind of problem."
    elif max_nesting >= 2 and not has_hashmap:
        optimization = "Consider using a hash map to avoid the nested loop and reduce time complexity."
    elif max_nesting >= 2 and has_hashmap:
        optimization = "You're using nested loops alongside a hash map — check if the nested loop is actually needed."
    else:
        optimization = "No obvious optimization detected by static rules."

    explanation = (
        f"Pattern detected: {pattern}. Static analysis found: max loop nesting = {max_nesting}, "
        f"sorting = {has_sort}, hash map/set = {has_hashmap}, recursion = {has_recursion}. "
        f"This is rule-based only — AI-generated explanations replace this when available."
    )

    return {
        "approach": approach,
        "pattern": pattern,
        "time_complexity": time_complexity,
        "space_complexity": space_complexity,
        "optimization": optimization,
        "explanation": explanation,
        "code_quality": compute_code_quality(code, max_nesting),
        "edge_cases": generate_edge_cases(pattern),
    }


def get_max_loop_nesting_python(code: str) -> int:
    """Python has no braces, so nesting is inferred from indentation."""
    lines = code.splitlines()
    open_loops = []
    max_depth = 0

    for line in lines:
        if not line.strip():
            continue

        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()

        while open_loops and indent <= open_loops[-1]:
            open_loops.pop()

        is_loop_line = bool(re.match(r"^(for|while)\b", stripped))
        if is_loop_line:
            open_loops.append(indent)
            max_depth = max(max_depth, len(open_loops))

    return max_depth


def get_max_loop_nesting(code: str) -> int:
    """Estimates max loop nesting depth using brace tracking (C++/Java style)."""
    lines = code.splitlines()
    loop_keywords = ("for", "while")

    max_depth = 0
    depth_stack = []
    brace_depth = 0

    for line in lines:
        stripped = line.strip()

        is_loop_line = any(
            re.match(rf"^\b{kw}\b", stripped) for kw in loop_keywords
        )

        if is_loop_line:
            depth_stack.append(brace_depth)
            current_depth = len(depth_stack)
            max_depth = max(max_depth, current_depth)

        brace_depth += stripped.count("{") - stripped.count("}")

        while depth_stack and brace_depth < depth_stack[-1]:
            depth_stack.pop()

    return max_depth


def is_two_pointer(code_lower: str) -> bool:
    """Requires real converging motion (increment AND decrement), not just variable names."""
    pair_patterns = [
        (r"\bleft\b", r"\bright\b"),
        (r"\blow\b", r"\bhigh\b"),
        (r"\bstart\b", r"\bend\b"),
    ]
    has_pair = any(
        re.search(a, code_lower) and re.search(b, code_lower)
        for a, b in pair_patterns
    )
    has_increment = bool(re.search(r"(left|low|start)\s*(\+\+|\+=)", code_lower))
    has_decrement = bool(re.search(r"(right|high|end)\s*(--|-=)", code_lower))
    return has_pair and has_increment and has_decrement


def is_sliding_window(code_lower: str) -> bool:
    """A window pointer that only ever moves forward (never resets)."""
    has_window_vars = (
        ("left" in code_lower and "right" in code_lower)
        or ("start" in code_lower and "end" in code_lower)
    )
    has_shrink_step = bool(re.search(r"(left|start)\s*(\+\+|\+=)", code_lower))
    return has_window_vars and has_shrink_step


def is_recursive(code: str) -> bool:
    """Very rough recursion check: does the function call itself by name?"""
    func_match = re.search(r"\b(?:def|void|int|long|string|bool|auto)\s+(\w+)\s*\(", code)
    if not func_match:
        return False
    func_name = func_match.group(1)
    occurrences = len(re.findall(rf"\b{re.escape(func_name)}\s*\(", code))
    return occurrences > 1