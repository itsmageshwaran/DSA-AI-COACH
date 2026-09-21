"""Topic Learning Service providing deep educational content, language snippets, and practice mapping."""

from __future__ import annotations

import re
from typing import Any
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.domain.learning.models import Concept, Exercise, Lesson, Submission
from src.infrastructure.database.unit_of_work import UnitOfWork


TOPIC_CURRICULUM_DATA: dict[str, dict[str, Any]] = {
    "arrays": {
        "name": "Arrays & Dynamic Arrays",
        "tagline": "The foundational contiguous memory data structure.",
        "description": "Arrays store elements in contiguous memory locations, enabling instantaneous O(1) random access by index.",
        "why_it_matters": "Almost every high-performance system—from database page buffers to GPU tensor math—relies on arrays for cache locality and predictable memory bandwidth.",
        "prerequisites": ["Basic variable assignment", "Loops and conditions"],
        "estimated_minutes": 25,
        "icon": "Layers",
        "video": {
            "title": "Arrays & Dynamic Array Deep Dive",
            "duration": "14 mins",
            "embed_url": "https://www.youtube-nocookie.com/embed/n60Dn0UsbEk",
            "search_query": "Data Structures Arrays and Memory Allocation explained",
            "key_takeaways": [
                "Contiguous memory layout ensures maximum CPU cache line utilization.",
                "Index formula: Memory Address = Base Address + (Index * Element Size).",
                "Dynamic arrays double in size when full, maintaining amortized O(1) append time.",
                "Shifting elements during insertion or deletion causes worst-case O(n) overhead."
            ]
        },
        "complexity": {
            "access": "O(1)",
            "search": "O(n)",
            "insertion": "O(n) (O(1) amortized at end)",
            "deletion": "O(n) (O(1) at end)",
            "space": "O(n)"
        },
        "notes": [
            {
                "title": "1. What is an Array?",
                "content": "An array is a collection of items stored at contiguous memory locations. Because memory addresses are sequential, computing the physical location of any element `arr[i]` requires a single arithmetic operation: `base_address + i * size_of_type`."
            },
            {
                "title": "2. Fixed vs Dynamic Arrays",
                "content": "Fixed-size arrays require pre-allocating memory upfront. Dynamic arrays (such as Python `list`, C++ `std::vector`, Java `ArrayList`) automatically resize when capacity is exceeded by allocating a new buffer with double capacity and copying elements over."
            },
            {
                "title": "3. Core Operations Walkthrough",
                "content": "- **Traversal**: Linear scan through index `0` to `n-1` in `O(n)` time.\n- **Search**: Linear search checks each element `O(n)`; Binary search requires sorted order for `O(log n)`.\n- **Insertion**: Inserting at index `k` requires shifting `n - k` elements rightward `O(n)`.\n- **Deletion**: Removing index `k` requires shifting `n - k - 1` elements leftward `O(n)`."
            },
            {
                "title": "4. Common Algorithmic Patterns",
                "content": "- **Two Pointers**: Moving pointers from opposite ends (e.g. sorted Two Sum) or same direction (Dutch National Flag).\n- **Sliding Window**: Maintaining a contiguous subarray with variable or fixed size.\n- **Prefix Sum**: Precomputing running totals for instant `O(1)` subarray sum queries.\n- **Kadane's Algorithm**: Dynamic programming on arrays to find maximum subarray sum in single `O(n)` pass."
            },
            {
                "title": "5. Common Traps & Interview Tips",
                "content": "- **Off-by-One Errors**: Always check loop boundaries (`< n` vs `<= n - 1`).\n- **In-place Mutation vs Copies**: Clarify if modifying the input array in-place is allowed to save `O(1)` auxiliary space.\n- **Integer Overflow**: When summing large arrays in C++/Java, use 64-bit integer types (`long` / `long long`)."
            }
        ],
        "code_snippets": {
            "python": """# Python Array Operations & Two Pointer Technique
def two_sum_sorted(nums: list[int], target: int) -> list[int]:
    \"\"\"Find indices of two numbers that sum to target in a sorted array.\"\"\"
    left, right = 0, len(nums) - 1
    while left < right:
        current_sum = nums[left] + nums[right]
        if current_sum == target:
            return [left, right]
        elif current_sum < target:
            left += 1
        else:
            right -= 1
    return []

# Array Slicing & Running Prefix Sum
def running_sum(nums: list[int]) -> list[int]:
    for i in range(1, len(nums)):
        nums[i] += nums[i - 1]
    return nums
""",
            "javascript": """// JavaScript Array Operations & Two Pointers
function twoSumSorted(nums, target) {
  let left = 0, right = nums.length - 1;
  while (left < right) {
    const sum = nums[left] + nums[right];
    if (sum === target) return [left, right];
    if (sum < target) left++;
    else right--;
  }
  return [];
}
""",
            "cpp": """// C++ std::vector Operations
#include <vector>
using namespace std;

vector<int> twoSumSorted(const vector<int>& nums, int target) {
    int left = 0, right = nums.size() - 1;
    while (left < right) {
        int sum = nums[left] + nums[right];
        if (sum == target) return {left, right};
        if (sum < target) left++;
        else right--;
    }
    return {};
}
""",
            "java": """// Java Array Implementation
public class ArrayPatterns {
    public static int[] twoSumSorted(int[] nums, int target) {
        int left = 0, right = nums.length - 1;
        while (left < right) {
            int sum = nums[left] + nums[right];
            if (sum == target) return new int[]{left, right};
            if (sum < target) left++;
            else right--;
        }
        return new int[]{};
    }
}
""",
            "go": """// Go Slice Operations
package main

func twoSumSorted(nums []int, target int) []int {
    left, right := 0, len(nums)-1
    for left < right {
        sum := nums[left] + nums[right]
        if sum == target {
            return []int{left, right}
        }
        if sum < target {
            left++
        } else {
            right--
        }
    }
    return []int{}
}
"""
        }
    },
    "strings": {
        "name": "Strings & Pattern Matching",
        "tagline": "Character sequences, encoding, and string algorithms.",
        "description": "Strings represent sequential text data, commonly immutable or mutable depending on language design, requiring specialized manipulation techniques.",
        "why_it_matters": "Search engines, parsers, compilers, NLP pipelines, and web network protocols are all built upon robust string manipulation.",
        "prerequisites": ["Arrays", "Character ASCII/Unicode encoding"],
        "estimated_minutes": 20,
        "icon": "Type",
        "video": {
            "title": "String Manipulation & Two Pointers",
            "duration": "12 mins",
            "embed_url": "https://www.youtube-nocookie.com/embed/73r3KRhDeJM",
            "search_query": "String algorithms palindrome two pointers sliding window",
            "key_takeaways": [
                "Understand immutability: Concatenating strings in a loop creates O(n^2) allocations unless using StringBuilder / list joins.",
                "Two-pointer palindrome checks run in O(n) time and O(1) space.",
                "Character frequency maps using array of size 26 or 128 optimize hash lookups."
            ]
        },
        "complexity": {
            "access": "O(1)",
            "search": "O(n * m) naive / O(n) KMP",
            "insertion": "O(n) (immutable copy)",
            "deletion": "O(n)",
            "space": "O(n)"
        },
        "notes": [
            {
                "title": "1. String Representation & Immutability",
                "content": "In languages like Python, Java, and JavaScript, strings are immutable. Any modification creates a fresh string copy. For high-throughput building, use `StringBuilder` (Java), array `.join('')` (JS), or `''.join(list)` (Python)."
            },
            {
                "title": "2. Common String Patterns",
                "content": "- **Two Pointers**: Palindrome validation, in-place reversal.\n- **Sliding Window**: Longest Substring Without Repeating Characters, Minimum Window Substring.\n- **Frequency Array**: Counting occurrences using `int count[26]` for lowercase alphabet."
            }
        ],
        "code_snippets": {
            "python": """def is_palindrome(s: str) -> bool:
    left, right = 0, len(s) - 1
    while left < right:
        while left < right and not s[left].isalnum():
            left += 1
        while left < right and not s[right].isalnum():
            right -= 1
        if s[left].lower() != s[right].lower():
            return False
        left += 1
        right -= 1
    return True
""",
            "javascript": """function isPalindrome(s) {
  let left = 0, right = s.length - 1;
  const isAlphanumeric = c => /[a-z0-9]/i.test(c);
  while (left < right) {
    while (left < right && !isAlphanumeric(s[left])) left++;
    while (left < right && !isAlphanumeric(s[right])) right--;
    if (s[left].toLowerCase() !== s[right].toLowerCase()) return false;
    left++; right--;
  }
  return true;
}
""",
            "cpp": """#include <string>
#include <cctype>
using namespace std;

bool isPalindrome(string s) {
    int left = 0, right = s.length() - 1;
    while (left < right) {
        while (left < right && !isalnum(s[left])) left++;
        while (left < right && !isalnum(s[right])) right--;
        if (tolower(s[left]) != tolower(s[right])) return false;
        left++; right--;
    }
    return true;
}
""",
            "java": """public class StringPatterns {
    public static boolean isPalindrome(String s) {
        int left = 0, right = s.length() - 1;
        while (left < right) {
            while (left < right && !Character.isLetterOrDigit(s.charAt(left))) left++;
            while (left < right && !Character.isLetterOrDigit(s.charAt(right))) right--;
            if (Character.toLowerCase(s.charAt(left)) != Character.toLowerCase(s.charAt(right))) return false;
            left++; right--;
        }
        return true;
    }
}
""",
            "go": """package main
import "unicode"

func isPalindrome(s string) bool {
    runes := []rune(s)
    left, right := 0, len(runes)-1
    for left < right {
        for left < right && !unicode.IsLetter(runes[left]) && !unicode.IsDigit(runes[left]) { left++ }
        for left < right && !unicode.IsLetter(runes[right]) && !unicode.IsDigit(runes[right]) { right-- }
        if unicode.ToLower(runes[left]) != unicode.ToLower(runes[right]) { return false }
        left++; right--
    }
    return true
}
"""
        }
    },
    "linked-lists": {
        "name": "Linked Lists",
        "tagline": "Pointer-linked nodes for flexible O(1) dynamic re-linking.",
        "description": "A linear collection of nodes where each node contains data and references (pointers) to the next (and optionally previous) node.",
        "why_it_matters": "Linked lists power memory allocators, LRU cache eviction lists, and file system block chains due to O(1) node splicing without bulk memory copies.",
        "prerequisites": ["Pointers / Object References"],
        "estimated_minutes": 25,
        "icon": "GitCommit",
        "video": {
            "title": "Linked List Patterns & Fast/Slow Pointers",
            "duration": "15 mins",
            "embed_url": "https://www.youtube-nocookie.com/embed/F8AbOfQwl1c",
            "search_query": "Linked List reversal fast slow pointer cycle detection",
            "key_takeaways": [
                "Node insertion/deletion is O(1) once pointer to predecessor is known.",
                "Fast & Slow pointer (Floyd's Tortoise & Hare) detects cycles and finds middle in O(n) time and O(1) space.",
                "Sentinel (Dummy) nodes eliminate edge cases when inserting or deleting at head."
            ]
        },
        "complexity": {
            "access": "O(n)",
            "search": "O(n)",
            "insertion": "O(1) (at head/known pointer)",
            "deletion": "O(1) (at known pointer)",
            "space": "O(n)"
        },
        "notes": [
            {
                "title": "1. Singly vs Doubly Linked Lists",
                "content": "Singly linked lists store a single `next` pointer. Doubly linked lists store both `prev` and `next`, enabling bidirectional traversal and `O(1)` deletion given direct node reference."
            },
            {
                "title": "2. The Sentinel / Dummy Head Pattern",
                "content": "Creating a `dummy = ListNode(0, head)` avoids separate conditional branches for modifying the list's actual head pointer."
            },
            {
                "title": "3. Classic Patterns",
                "content": "- **In-place Reversal**: Iteratively swinging `curr.next` to `prev` with a `temp` pointer.\n- **Cycle Detection**: Slow pointer moves 1 step, fast pointer moves 2 steps.\n- **Merge Two Sorted Lists**: Compare head elements and weave references."
            }
        ],
        "code_snippets": {
            "python": """class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def reverse_list(head: ListNode | None) -> ListNode | None:
    prev = None
    curr = head
    while curr:
        nxt = curr.next
        curr.next = prev
        prev = curr
        curr = nxt
    return prev
""",
            "javascript": """function reverseList(head) {
  let prev = null, curr = head;
  while (curr) {
    const next = curr.next;
    curr.next = prev;
    prev = curr;
    curr = next;
  }
  return prev;
}
""",
            "cpp": """struct ListNode {
    int val;
    ListNode *next;
    ListNode(int x) : val(x), next(nullptr) {}
};

ListNode* reverseList(ListNode* head) {
    ListNode* prev = nullptr;
    ListNode* curr = head;
    while (curr) {
        ListNode* next = curr->next;
        curr->next = prev;
        prev = curr;
        curr = next;
    }
    return prev;
}
""",
            "java": """public class ListNode {
    int val;
    ListNode next;
    ListNode(int val) { this.val = val; }
    
    public static ListNode reverse(ListNode head) {
        ListNode prev = null, curr = head;
        while (curr != null) {
            ListNode next = curr.next;
            curr.next = prev;
            prev = curr;
            curr = next;
        }
        return prev;
    }
}
""",
            "go": """type ListNode struct {
    Val  int
    Next *ListNode
}

func reverseList(head *ListNode) *ListNode {
    var prev *ListNode
    curr := head
    for curr != nil {
        next := curr.Next
        curr.Next = prev
        prev = curr
        curr = next
    }
    return prev
}
"""
        }
    },
    "stack": {
        "name": "Stacks & Queues",
        "tagline": "LIFO & FIFO fundamental linear access data structures.",
        "description": "Stacks enforce Last-In First-Out (LIFO) order, while Queues enforce First-In First-Out (FIFO) access.",
        "why_it_matters": "Stacks power compiler call stacks, expression evaluation, and browser history. Queues power OS task scheduling, web server thread pools, and event streams.",
        "prerequisites": ["Arrays", "Linked Lists"],
        "estimated_minutes": 20,
        "icon": "Layers",
        "video": {
            "title": "Monotonic Stacks & Valid Parentheses",
            "duration": "14 mins",
            "embed_url": "https://www.youtube-nocookie.com/embed/WTzjTskDFMg",
            "search_query": "Stack data structure monotonic stack valid parentheses",
            "key_takeaways": [
                "LIFO operations (push/pop/peek) run in O(1) time.",
                "Monotonic stacks find Next Greater / Smaller Element in O(n) total time.",
                "Matching brackets/tokens is solved with a stack matching opposite symbols."
            ]
        },
        "complexity": {
            "access": "O(n)",
            "search": "O(n)",
            "insertion": "O(1) push",
            "deletion": "O(1) pop",
            "space": "O(n)"
        },
        "notes": [
            {
                "title": "1. Stack Basics & Valid Parentheses",
                "content": "A stack holds open tokens and pops them when matching closing tokens appear. Any mismatch or leftover tokens on the stack signals invalid syntax."
            },
            {
                "title": "2. Monotonic Stack Technique",
                "content": "Maintaining elements in strictly increasing or decreasing order allows solving range query problems (like Daily Temperatures or Largest Rectangle in Histogram) in linear `O(n)` time."
            }
        ],
        "code_snippets": {
            "python": """def is_valid_parentheses(s: str) -> bool:
    mapping = {')': '(', '}': '{', ']': '['}
    stack = []
    for char in s:
        if char in mapping:
            top = stack.pop() if stack else '#'
            if mapping[char] != top:
                return False
        else:
            stack.append(char)
    return not stack
""",
            "javascript": """function isValidParentheses(s) {
  const map = { ')': '(', '}': '{', ']': '[' };
  const stack = [];
  for (const char of s) {
    if (map[char]) {
      if (stack.pop() !== map[char]) return false;
    } else {
      stack.push(char);
    }
  }
  return stack.length === 0;
}
""",
            "cpp": """#include <string>
#include <stack>
#include <unordered_map>
using namespace std;

bool isValidParentheses(string s) {
    unordered_map<char, char> map = {{')', '('}, {'}', '{'}, {']', '['}};
    stack<char> st;
    for (char c : s) {
        if (map.count(c)) {
            if (st.empty() || st.top() != map[c]) return false;
            st.pop();
        } else {
            st.push(c);
        }
    }
    return st.empty();
}
""",
            "java": """import java.util.*;

public class StackPatterns {
    public static boolean isValidParentheses(String s) {
        Map<Character, Character> map = Map.of(')', '(', '}', '{', ']', '[');
        Deque<Character> stack = new ArrayDeque<>();
        for (char c : s.toCharArray()) {
            if (map.containsKey(c)) {
                if (stack.isEmpty() || stack.pop() != map.get(c)) return false;
            } else {
                stack.push(c);
            }
        }
        return stack.isEmpty();
    }
}
""",
            "go": """package main

func isValidParentheses(s string) bool {
    matching := map[rune]rune{')': '(', '}': '{', ']': '['}
    stack := []rune{}
    for _, r := range s {
        if opener, ok := matching[r]; ok {
            if len(stack) == 0 || stack[len(stack)-1] != opener {
                return false
            }
            stack = stack[:len(stack)-1]
        } else {
            stack = append(stack, r)
        }
    }
    return len(stack) == 0
}
"""
        }
    },
    "binary-search": {
        "name": "Binary Search",
        "tagline": "Logarithmic search over sorted collections and monotonic answer spaces.",
        "description": "Binary search halves the candidate search space on each iteration by comparing the middle element with the target value.",
        "why_it_matters": "B-Tree index scans in SQL databases and distributed partition range routing all rely on binary search to achieve O(log n) access across billions of records.",
        "prerequisites": ["Sorted Arrays", "Monotonic functions"],
        "estimated_minutes": 20,
        "icon": "Search",
        "video": {
            "title": "Binary Search & Monotonic Predicates",
            "duration": "16 mins",
            "embed_url": "https://www.youtube-nocookie.com/embed/W9QJ8HaRvSw",
            "search_query": "Binary search algorithm lower bound upper bound explanation",
            "key_takeaways": [
                "Halves search space on every comparison: O(log n) time complexity.",
                "Calculate mid safely: `mid = left + (right - left) // 2` prevents 32-bit integer overflow.",
                "Can be applied to search spaces of answers (Binary Search on Answer) whenever the predicate `f(x)` is monotonic: `[F, F, F, T, T, T]`."
            ]
        },
        "complexity": {
            "access": "N/A",
            "search": "O(log n)",
            "insertion": "N/A",
            "deletion": "N/A",
            "space": "O(1)"
        },
        "notes": [
            {
                "title": "1. Standard Binary Search Template",
                "content": "Initialize `left = 0`, `right = len(arr) - 1`. While `left <= right`, compute `mid` and adjust pointers based on comparison."
            },
            {
                "title": "2. Binary Search on Answer Space",
                "content": "When asked for the 'minimum capacity to ship within D days' or 'maximum speed to reach before deadline', define a boolean feasibility function `is_possible(x)` and binary search the range `[min_val, max_val]`."
            }
        ],
        "code_snippets": {
            "python": """def binary_search(nums: list[int], target: int) -> int:
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
""",
            "javascript": """function binarySearch(nums, target) {
  let left = 0, right = nums.length - 1;
  while (left <= right) {
    const mid = Math.floor(left + (right - left) / 2);
    if (nums[mid] === target) return mid;
    if (nums[mid] < target) left = mid + 1;
    else right = mid - 1;
  }
  return -1;
}
""",
            "cpp": """#include <vector>
using namespace std;

int binarySearch(const vector<int>& nums, int target) {
    int left = 0, right = nums.size() - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (nums[mid] == target) return mid;
        if (nums[mid] < target) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
""",
            "java": """public class BinarySearch {
    public static int search(int[] nums, int target) {
        int left = 0, right = nums.length - 1;
        while (left <= right) {
            int mid = left + (right - left) / 2;
            if (nums[mid] == target) return mid;
            if (nums[mid] < target) left = mid + 1;
            else right = mid - 1;
        }
        return -1;
    }
}
""",
            "go": """package main

func binarySearch(nums []int, target int) int {
    left, right := 0, len(nums)-1
    for left <= right {
        mid := left + (right-left)/2
        if nums[mid] == target {
            return mid
        }
        if nums[mid] < target {
            left = mid + 1
        } else {
            right = mid - 1
        }
    }
    return -1
}
"""
        }
    },
    "dynamic-programming": {
        "name": "Dynamic Programming",
        "tagline": "Breaking complex problems into overlapping subproblems with optimal substructure.",
        "description": "Dynamic Programming optimizes recursive solutions by storing intermediate subproblem results to prevent redundant recalculation.",
        "why_it_matters": "Powers shortest path routing, DNA sequence alignment in bioinformatics, financial portfolio optimization, and audio processing.",
        "prerequisites": ["Recursion", "Arrays / Hash Maps"],
        "estimated_minutes": 35,
        "icon": "Cpu",
        "video": {
            "title": "Dynamic Programming Patterns: Memoization to Tabulation",
            "duration": "22 mins",
            "embed_url": "https://www.youtube-nocookie.com/embed/oBt53YbR9Kk",
            "search_query": "Dynamic programming step by step memoization tabulation",
            "key_takeaways": [
                "Two core ingredients: Optimal Substructure + Overlapping Subproblems.",
                "Top-down (Memoization): Natural recursion + cache lookup.",
                "Bottom-up (Tabulation): Iterative DP table building from base cases.",
                "Space optimization: Keep only previous row/state values when transitions only look back K steps."
            ]
        },
        "complexity": {
            "access": "O(1)",
            "search": "O(1) state lookup",
            "insertion": "N/A",
            "deletion": "N/A",
            "space": "O(n) or O(1) optimized"
        },
        "notes": [
            {
                "title": "1. The 5-Step DP Recipe",
                "content": "1. **Define State**: `dp[i]` = answer for subproblem of size `i`.\n2. **Identify Base Cases**: `dp[0]`, `dp[1]`.\n3. **Formulate Transition Equation**: `dp[i] = max(dp[i-1], dp[i-2] + val)`.\n4. **Determine Evaluation Order**: Bottom-up or Top-down.\n5. **Identify Space Optimization**: Can we replace array with 2 variables?"
            },
            {
                "title": "2. Common DP Patterns",
                "content": "- **1D Sequence**: Climbing Stairs, House Robber, Coin Change.\n- **2D Grid / Matrix**: Unique Paths, Minimum Path Sum.\n- **String Matching**: Longest Common Subsequence, Edit Distance.\n- **0/1 Knapsack & Unbounded Knapsack**: Subsets with constraints."
            }
        ],
        "code_snippets": {
            "python": """def climb_stairs(n: int) -> int:
    \"\"\"Fibonacci-style DP with O(1) space optimization.\"\"\"
    if n <= 2:
        return n
    prev2, prev1 = 1, 2
    for _ in range(3, n + 1):
        curr = prev1 + prev2
        prev2 = prev1
        prev1 = curr
    return prev1

def coin_change(coins: list[int], amount: int) -> int:
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    for coin in coins:
        for x in range(coin, amount + 1):
            dp[x] = min(dp[x], dp[x - coin] + 1)
    return dp[amount] if dp[amount] != float('inf') else -1
""",
            "javascript": """function climbStairs(n) {
  if (n <= 2) return n;
  let prev2 = 1, prev1 = 2;
  for (let i = 3; i <= n; i++) {
    const curr = prev1 + prev2;
    prev2 = prev1;
    prev1 = curr;
  }
  return prev1;
}
""",
            "cpp": """#include <vector>
#include <algorithm>
using namespace std;

int climbStairs(int n) {
    if (n <= 2) return n;
    int prev2 = 1, prev1 = 2;
    for (int i = 3; i <= n; ++i) {
        int curr = prev1 + prev2;
        prev2 = prev1;
        prev1 = curr;
    }
    return prev1;
}
""",
            "java": """public class DPPatterns {
    public static int climbStairs(int n) {
        if (n <= 2) return n;
        int prev2 = 1, prev1 = 2;
        for (int i = 3; i <= n; i++) {
            int curr = prev1 + prev2;
            prev2 = prev1;
            prev1 = curr;
        }
        return prev1;
    }
}
""",
            "go": """package main

func climbStairs(n int) int {
    if n <= 2 {
        return n
    }
    prev2, prev1 := 1, 2
    for i := 3; i <= n; i++ {
        curr := prev1 + prev2
        prev2 = prev1
        prev1 = curr
    }
    return prev1
}
"""
        }
    }
}


class TopicService:
    """Service to assemble rich topic learning experiences connected to real DB exercises."""

    @staticmethod
    def _normalize_slug(name_or_slug: str) -> str:
        """Convert concept name or ID to normalized slug."""
        clean = re.sub(r"[^\w\s-]", "", name_or_slug.lower())
        return re.sub(r"[-\s]+", "-", clean).strip("-")

    @classmethod
    async def get_topic_learning_data(
        cls,
        uow: UnitOfWork,
        topic_identifier: str,
        user_id: str,
        preferred_language: str = "python"
    ) -> dict[str, Any]:
        """Fetch complete topic learning preview with curriculum data and DB exercises."""
        # 1. Find concept by UUID or slug/name
        concept: Concept | None = None
        
        # Try UUID first
        try:
            concept = await uow.session.get(Concept, topic_identifier)
        except Exception:
            pass

        # Try by name if not found
        if not concept:
            normalized_query = cls._normalize_slug(topic_identifier)
            stmt = select(Concept)
            all_concepts = (await uow.session.execute(stmt)).scalars().all()
            for c in all_concepts:
                if cls._normalize_slug(c.name) == normalized_query or c.name.lower() in normalized_query:
                    concept = c
                    break

        concept_name = concept.name if concept else topic_identifier.replace("-", " ").title()
        concept_slug = cls._normalize_slug(concept_name)
        
        # Fallback to arrays if unknown slug
        curriculum = TOPIC_CURRICULUM_DATA.get(concept_slug)
        if not curriculum:
            # Fallback to first matched or generic array structure
            for key, val in TOPIC_CURRICULUM_DATA.items():
                if key in concept_slug or concept_slug in key:
                    curriculum = val
                    break
            if not curriculum:
                curriculum = TOPIC_CURRICULUM_DATA["arrays"]

        # 2. Fetch live exercises for this concept from Database
        exercises: list[Exercise] = []
        if concept:
            ex_stmt = (
                select(Exercise)
                .join(Lesson, Exercise.lesson_id == Lesson.id)
                .where(Lesson.concept_id == concept.id)
                .order_by(Exercise.created_at)
            )
            exercises = list((await uow.session.execute(ex_stmt)).scalars().all())

        # If no concept-specific exercises found, load default foundational exercises
        if not exercises:
            fallback_stmt = select(Exercise).limit(6)
            exercises = list((await uow.session.execute(fallback_stmt)).scalars().all())

        # 3. Check user solved status from Submissions table
        sub_stmt = (
            select(Submission.exercise_id)
            .where(
                Submission.user_id == user_id,
                Submission.status == "accepted"
            )
        )
        solved_ids = set((await uow.session.execute(sub_stmt)).scalars().all())

        # 4. Map exercises with recommendation reasoning & progression
        practice_problems = []
        difficulty_order = {"easy": 1, "easy_plus": 2, "medium": 3, "medium_plus": 4, "hard": 5, "advanced": 6}

        for ex in exercises:
            is_done = ex.id in solved_ids
            diff = (ex.difficulty or "easy").lower()
            
            rationale = "Foundational problem to master basic traversal and memory indexing."
            if "plus" in diff:
                rationale = "Reinforces optimal two-pointer and sliding window space optimizations."
            elif "medium" in diff:
                rationale = "Standard tier-1 interview challenge testing edge cases and hash lookup trade-offs."
            elif "hard" in diff:
                rationale = "Advanced optimization problem testing deep algorithmic constraints."

            practice_problems.append({
                "id": ex.id,
                "title": ex.title,
                "difficulty": diff,
                "difficulty_rank": difficulty_order.get(diff, 1),
                "difficulty_tier": ex.difficulty_tier,
                "required_concept": ex.required_concept,
                "company_tags": ex.company_tags,
                "is_completed": is_done,
                "recommended_reason": rationale,
                "entrypoint": ex.entrypoint,
            })

        # Sort practice problems by progressive difficulty
        practice_problems.sort(key=lambda p: (p["is_completed"], p["difficulty_rank"]))

        # 5. Calculate real mastery
        total_count = len(practice_problems)
        solved_count = sum(1 for p in practice_problems if p["is_completed"])
        mastery_pct = int((solved_count / total_count * 100)) if total_count > 0 else 0

        # 6. Assemble complete response
        lang = preferred_language.lower() if preferred_language in curriculum.get("code_snippets", {}) else "python"

        return {
            "id": concept.id if concept else concept_slug,
            "slug": concept_slug,
            "name": curriculum.get("name", concept_name),
            "tagline": curriculum.get("tagline", "Master core data structures and algorithms."),
            "description": concept.description if concept and concept.description else curriculum.get("description", ""),
            "why_it_matters": curriculum.get("why_it_matters", ""),
            "prerequisites": curriculum.get("prerequisites", ["Basic programming"]),
            "estimated_minutes": curriculum.get("estimated_minutes", 20),
            "icon": curriculum.get("icon", "Layers"),
            "video": curriculum.get("video", {}),
            "complexity": curriculum.get("complexity", {}),
            "notes": curriculum.get("notes", []),
            "code_snippets": curriculum.get("code_snippets", {}),
            "preferred_language": lang,
            "practice_problems": practice_problems,
            "stats": {
                "total_problems": total_count,
                "solved_problems": solved_count,
                "mastery_percentage": mastery_pct,
                "status": "mastered" if mastery_pct == 100 else ("in_progress" if solved_count > 0 else "not_started")
            }
        }
