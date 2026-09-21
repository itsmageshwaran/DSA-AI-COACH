"""
Seed hints, company_tags, required_concept, difficulty_tier into exercises.
Pure sqlite3 — no ORM needed. Idempotent.
"""
import sqlite3
import json
import os

PROBLEM_BANK = {
    "find the largest element": {
        "company_tags": "Beginner Practice",
        "required_concept": "Traversal + comparison",
        "difficulty_tier": "Basic",
        "hints": [
            "First ask: what value do you need to remember while scanning the array?",
            "Keep a variable containing the largest value seen so far.",
            "Start with the first element, then compare each next element with your current largest.",
            "If the current element is larger, update the stored value.",
            "You only need one pass: O(n) time and O(1) extra space.",
        ],
    },
    "reverse an array": {
        "company_tags": "Beginner Practice",
        "required_concept": "Two pointers",
        "difficulty_tier": "Basic",
        "hints": [
            "The first element belongs at the last position, and the last belongs at the first.",
            "Use one pointer at the left and one at the right.",
            "Swap the two values, then move both pointers toward the center.",
            "Stop when the pointers meet or cross.",
            "Because you modify the array directly, extra space can remain O(1).",
        ],
    },
    "two sum": {
        "company_tags": "Google, Amazon, Meta",
        "required_concept": "Hash Map + complement",
        "difficulty_tier": "Intermediate",
        "hints": [
            "First understand the brute-force idea: compare every pair.",
            "Why is comparing every pair expensive? We want to avoid repeatedly searching earlier elements.",
            "For the current number x, what other number would complete the target?",
            "Store previously seen values with their indices so the complement can be checked quickly.",
            "Check the complement before storing the current value. This gives expected O(n) time.",
        ],
    },
    "maximum subarray": {
        "company_tags": "Amazon, Microsoft",
        "required_concept": "Kadane's algorithm",
        "difficulty_tier": "Advanced",
        "hints": [
            "Move beyond checking every subarray. At each position, ask whether the previous running subarray helps.",
            "Define the best sum of a subarray that must end at the current position.",
            "Either start a new subarray at the current value or extend the previous one.",
            "Keep a separate global maximum because the best answer may occur before the final element.",
            "The resulting one-pass solution is O(n) time and O(1) extra space.",
        ],
    },
    "count vowels": {
        "company_tags": "Beginner Practice",
        "required_concept": "String traversal",
        "difficulty_tier": "Basic",
        "hints": [
            "You need to inspect each character once.",
            "Maintain a counter starting at zero.",
            "For each character, check whether it belongs to the set of vowels.",
            "If it is a vowel, increase the counter by one.",
            "This is a direct O(n) traversal with O(1) extra space.",
        ],
    },
    "valid anagram": {
        "company_tags": "Amazon, Google",
        "required_concept": "Frequency counting",
        "difficulty_tier": "Intermediate",
        "hints": [
            "Anagrams have the same number of each character.",
            "A first quick check: can strings with different lengths be anagrams?",
            "Use a frequency table to count characters.",
            "Increase counts from one string and decrease them for the other.",
            "After processing, every required count must balance to zero.",
        ],
    },
    "longest substring without repeating characters": {
        "company_tags": "Amazon, Meta, Google",
        "required_concept": "Sliding window",
        "difficulty_tier": "Advanced",
        "hints": [
            "A substring is contiguous, so think about maintaining a window.",
            "The window must always contain unique characters.",
            "When a duplicate enters, move the left side until the duplicate is no longer inside.",
            "A last-seen index map can let you move the left pointer directly.",
            "Track the largest valid window. The intended time is O(n).",
        ],
    },
    "factorial": {
        "company_tags": "Beginner Practice",
        "required_concept": "Base case + recursive call",
        "difficulty_tier": "Basic",
        "hints": [
            "What is the smallest input for which you already know the answer?",
            "Use n=0 as the base case with answer 1.",
            "For n>0, express factorial(n) using factorial(n-1).",
            "The recursive step multiplies n by the result of the smaller problem.",
            "Make sure every recursive call reduces n, so the base case is eventually reached.",
        ],
    },
    "climbing stairs": {
        "company_tags": "Apple, Google",
        "required_concept": "Recurrence + DP",
        "difficulty_tier": "Intermediate",
        "hints": [
            "Look at the final move: it must come from one or two steps below.",
            "Define ways(n) as the number of ways to reach step n.",
            "That gives a recurrence using ways(n-1) and ways(n-2).",
            "Write the smallest base cases before coding the general case.",
            "If plain recursion repeats the same states, store previous results or use two variables.",
        ],
    },
    "generate parentheses": {
        "company_tags": "Google, Amazon",
        "required_concept": "Backtracking",
        "difficulty_tier": "Advanced",
        "hints": [
            "Build the answer one parenthesis at a time.",
            "You may add '(' while you still have unused opening parentheses.",
            "You may add ')' only when there are more opening ones placed than closing ones.",
            "When a complete string has length 2n, record it.",
            "This is backtracking: choose, recurse, undo.",
        ],
    },
    "traverse a linked list": {
        "company_tags": "Beginner Practice",
        "required_concept": "Pointer traversal",
        "difficulty_tier": "Basic",
        "hints": [
            "Start at head and move through next references.",
            "Keep a running sum initialized to zero.",
            "While the current node exists, add its value and move to current.next.",
            "Stop when current becomes null.",
            "Each node is visited once: O(n) time and O(1) extra space.",
        ],
    },
    "reverse linked list": {
        "company_tags": "Amazon, Microsoft",
        "required_concept": "Prev / current / next",
        "difficulty_tier": "Intermediate",
        "hints": [
            "Before changing current.next, save the next node or you can lose the rest of the list.",
            "Use previous and current; a temporary next pointer protects the remaining nodes.",
            "Make current point to previous, then advance both pointers.",
            "When current becomes null, previous is the new head.",
            "Test empty, one-node and two-node lists before the full example.",
        ],
    },
    "linked list cycle": {
        "company_tags": "Amazon, Microsoft",
        "required_concept": "Slow and fast pointers",
        "difficulty_tier": "Advanced",
        "hints": [
            "If you keep moving one pointer, a cycle may make it loop forever.",
            "Use two pointers moving at different speeds.",
            "If a cycle exists, the faster pointer eventually catches the slower pointer.",
            "Always check that the fast pointer and fast.next exist before advancing them.",
            "This gives O(n) time and O(1) extra space.",
        ],
    },
    "implement a stack": {
        "company_tags": "Beginner Practice",
        "required_concept": "LIFO",
        "difficulty_tier": "Basic",
        "hints": [
            "A stack follows Last In, First Out.",
            "When a push occurs, add the value to the top.",
            "When a pop occurs, remove and return the most recently pushed value.",
            "A dynamic array/list can represent the stack top at its end.",
            "Trace a tiny sequence by hand before coding.",
        ],
    },
    "valid parentheses": {
        "company_tags": "Amazon, Google",
        "required_concept": "Stack + matching",
        "difficulty_tier": "Intermediate",
        "hints": [
            "The most recent opening bracket must be closed first, so think LIFO.",
            "Push opening brackets onto a stack.",
            "For a closing bracket, the top of the stack must be its matching opener.",
            "Reject an unmatched closing bracket immediately.",
            "After the scan, a valid string must leave the stack empty.",
        ],
    },
    "daily temperatures": {
        "company_tags": "Amazon, Google",
        "required_concept": "Monotonic stack",
        "difficulty_tier": "Advanced",
        "hints": [
            "For each day, you need the next index with a larger temperature.",
            "A brute-force scan forward for every day can be O(n^2).",
            "Keep unresolved indices in a stack while their temperatures are monotonic.",
            "When today's temperature is warmer than the stack top, today's day resolves that earlier index.",
            "Each index is pushed and popped at most once, giving O(n) time.",
        ],
    },
    "count tree nodes": {
        "company_tags": "Beginner Practice",
        "required_concept": "Tree traversal",
        "difficulty_tier": "Basic",
        "hints": [
            "An empty tree contains zero nodes.",
            "For a non-empty node, count the node itself plus nodes in its left and right subtrees.",
            "This directly suggests a recursive definition.",
            "Make sure the base case is returned before accessing children.",
            "Every node must be visited once: O(n) time.",
        ],
    },
    "maximum depth of binary tree": {
        "company_tags": "Amazon, Microsoft",
        "required_concept": "DFS recursion",
        "difficulty_tier": "Intermediate",
        "hints": [
            "Start with the empty-tree case.",
            "For a non-null node, the depth is one plus the larger depth of its children.",
            "Recursively ask the left and right subtrees for their depths.",
            "The answer is 1 + max(leftDepth, rightDepth).",
            "A traversal visits every node once: O(n) time and O(h) recursion space.",
        ],
    },
    "lowest common ancestor of a bst": {
        "company_tags": "Amazon, Meta",
        "required_concept": "BST ordering",
        "difficulty_tier": "Advanced",
        "hints": [
            "Use the BST ordering property instead of exploring every node.",
            "If both target values are smaller than root, where must their ancestor lie?",
            "If both are larger, move to the right subtree.",
            "When the values split around root, or one equals root, root is the LCA.",
            "Following one root-to-leaf path gives O(h) time.",
        ],
    },
    "bfs traversal": {
        "company_tags": "Beginner Practice",
        "required_concept": "Queue + visited",
        "difficulty_tier": "Basic",
        "hints": [
            "BFS explores nodes layer by layer, so use a queue.",
            "Mark a node visited when you add it to the queue to avoid duplicate entries.",
            "Remove the front node, record it, then add each unvisited neighbor.",
            "Continue until the queue is empty.",
            "With an adjacency list, traversal is O(V+E).",
        ],
    },
    "number of islands": {
        "company_tags": "Amazon, Google",
        "required_concept": "DFS/BFS + components",
        "difficulty_tier": "Intermediate",
        "hints": [
            "Treat each land cell as a node connected to its four neighbors.",
            "Every unvisited land cell that starts a traversal represents a new island.",
            "DFS or BFS should mark every connected land cell visited.",
            "Check row/column boundaries before visiting neighbors.",
            "Each cell is processed at most once: O(rows x cols).",
        ],
    },
    "course schedule": {
        "company_tags": "Amazon, Google",
        "required_concept": "Graph cycle detection / topological sort",
        "difficulty_tier": "Advanced",
        "hints": [
            "Prerequisites create directed edges. The question is whether those dependencies contain a cycle.",
            "If a course has no remaining prerequisites, it can be processed first.",
            "Track indegree, the number of prerequisites still required.",
            "Repeatedly remove zero-indegree courses and reduce indegree of their neighbors.",
            "If fewer than numCourses courses are processed, a cycle prevents completion.",
        ],
    },
    "fibonacci number": {
        "company_tags": "Beginner Practice",
        "required_concept": "Recurrence",
        "difficulty_tier": "Basic",
        "hints": [
            "Write the definition: F(n) depends on F(n-1) and F(n-2).",
            "Start with the two base cases F(0)=0 and F(1)=1.",
            "Notice that plain recursion repeats the same Fibonacci states.",
            "Store only the previous two values if you compute iteratively.",
            "This reduces time to O(n) and extra space to O(1).",
        ],
    },
    "house robber": {
        "company_tags": "Amazon, Google",
        "required_concept": "Choose/skip DP",
        "difficulty_tier": "Advanced",
        "hints": [
            "At each house, decide between skipping it and robbing it.",
            "If you rob the current house, which earlier house cannot be robbed?",
            "Define dp[i] as the best amount using the first i houses.",
            "Compare skip with current value plus the best compatible previous state.",
            "The final recurrence can be optimized to O(1) extra space.",
        ],
    },
    "contains duplicate": {
        "company_tags": "Beginner Practice",
        "required_concept": "Set membership",
        "difficulty_tier": "Basic",
        "hints": [
            "The key question is: have we seen this value before?",
            "A set stores unique values and supports fast membership checks.",
            "For each value, check the set before inserting it.",
            "If it is already present, you have found a duplicate.",
            "The expected complexity is O(n) time and O(n) extra space.",
        ],
    },
    "group anagrams": {
        "company_tags": "Amazon, Meta",
        "required_concept": "Canonical key + hashing",
        "difficulty_tier": "Intermediate",
        "hints": [
            "Two anagrams need to produce the same key.",
            "One simple key is the sorted version of the word.",
            "Use a map from that key to a list of original words.",
            "Process every word and append it to the matching group.",
            "If you sort each word, complexity is roughly O(n * k log k) for n words of length k.",
        ],
    },
    "longest consecutive sequence": {
        "company_tags": "Google, Amazon",
        "required_concept": "Set + sequence starts",
        "difficulty_tier": "Advanced",
        "hints": [
            "A sequence should be extended from its smallest element.",
            "Put all values into a set for O(1) membership checks.",
            "Only begin counting from x when x-1 is not present; then x is a sequence start.",
            "Keep checking x+1, x+2, and so on while they exist.",
            "This avoids sorting and achieves expected O(n) time.",
        ],
    },
    "linear search": {
        "company_tags": "Beginner Practice",
        "required_concept": "Sequential search",
        "difficulty_tier": "Basic",
        "hints": [
            "Start from index 0 and inspect values in order.",
            "If the current value equals target, return the current index.",
            "If you finish the scan, the target is absent.",
            "Do not skip values because the array is not assumed sorted.",
            "Worst-case time is O(n), with O(1) extra space.",
        ],
    },
    "binary search": {
        "company_tags": "Google, Microsoft",
        "required_concept": "Sorted search space",
        "difficulty_tier": "Intermediate",
        "hints": [
            "Sorted order lets you discard half of the remaining range.",
            "Maintain left and right boundaries.",
            "Compare target with the middle value.",
            "If target is smaller, move right; if larger, move left.",
            "The active range halves each iteration, giving O(log n) time.",
        ],
    },
    "search in rotated sorted array": {
        "company_tags": "Amazon, Meta, Google",
        "required_concept": "Modified binary search",
        "difficulty_tier": "Advanced",
        "hints": [
            "Even after rotation, at least one half around the middle is normally sorted.",
            "Check whether the left half is sorted by comparing nums[left] and nums[mid].",
            "If the target lies inside that sorted half's range, search there; otherwise discard it.",
            "If the left half is not sorted, reason similarly about the right half.",
            "Keep the binary-search invariant and shrink the interval every iteration.",
        ],
    },
}


def seed_db(path: str) -> None:
    if not os.path.exists(path):
        print(f"SKIP: {path} not found.")
        return

    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    # Verify columns exist
    cursor.execute("PRAGMA table_info(exercises)")
    cols = {row[1] for row in cursor.fetchall()}
    required = {"hints_json", "company_tags", "required_concept", "difficulty_tier"}
    missing = required - cols
    if missing:
        print(f"ERROR: {path} missing columns: {missing}. Run direct_migrate_exercises.py first.")
        conn.close()
        return

    cursor.execute("SELECT id, title, hints_json, company_tags FROM exercises")
    exercises = cursor.fetchall()

    updated = 0
    skipped_no_match = 0
    skipped_already_done = 0

    for ex_id, title, hints_json, company_tags in exercises:
        # Skip if already enriched
        if hints_json and company_tags:
            skipped_already_done += 1
            continue

        key = title.strip().lower()
        entry = PROBLEM_BANK.get(key)
        if not entry:
            for bank_key, bank_val in PROBLEM_BANK.items():
                if bank_key in key or key in bank_key:
                    entry = bank_val
                    break

        if not entry:
            skipped_no_match += 1
            continue

        cursor.execute(
            "UPDATE exercises SET hints_json=?, company_tags=?, required_concept=?, difficulty_tier=? WHERE id=?",
            (
                json.dumps(entry["hints"]),
                entry.get("company_tags"),
                entry.get("required_concept"),
                entry.get("difficulty_tier"),
                ex_id,
            ),
        )
        updated += 1

    conn.commit()
    conn.close()
    print(f"  {path}: {updated} enriched, {skipped_already_done} already done, {skipped_no_match} no match.")


if __name__ == "__main__":
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for db_name in ["app.db", "dsa_coach.db"]:
        db_path = os.path.join(base, db_name)
        print(f"Seeding {db_name}...")
        seed_db(db_path)
    print("Seed complete.")
