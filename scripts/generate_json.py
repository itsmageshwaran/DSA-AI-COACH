import json
import os

problems = [
    {
        "title": "Two Sum",
        "concept": "Arrays",
        "skill": "Hashing",
        "difficulty": "Easy",
        "instructions": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
        "starter_code": "def twoSum(nums, target):\n    pass",
        "entrypoint": "twoSum",
        "test_cases": [
            {"input": {"nums": [2, 7, 11, 15], "target": 9}, "expected": [0, 1]},
            {"input": {"nums": [3, 2, 4], "target": 6}, "expected": [1, 2]},
            {"input": {"nums": [3, 3], "target": 6}, "expected": [0, 1]}
        ]
    },
    {
        "title": "Valid Anagram",
        "concept": "Strings",
        "skill": "Hashing",
        "difficulty": "Easy+",
        "instructions": "Given two strings s and t, return true if t is an anagram of s, and false otherwise.",
        "starter_code": "def isAnagram(s, t):\n    pass",
        "entrypoint": "isAnagram",
        "test_cases": [
            {"input": {"s": "anagram", "t": "nagaram"}, "expected": True},
            {"input": {"s": "rat", "t": "car"}, "expected": False}
        ]
    },
    {
        "title": "Valid Palindrome",
        "concept": "Strings",
        "skill": "Two Pointers",
        "difficulty": "Easy",
        "instructions": "A phrase is a palindrome if, after converting all uppercase letters into lowercase letters and removing all non-alphanumeric characters, it reads the same forward and backward. Given a string s, return true if it is a palindrome, or false otherwise.",
        "starter_code": "def isPalindrome(s):\n    pass",
        "entrypoint": "isPalindrome",
        "test_cases": [
            {"input": {"s": "A man, a plan, a canal: Panama"}, "expected": True},
            {"input": {"s": "race a car"}, "expected": False},
            {"input": {"s": " "}, "expected": True}
        ]
    },
    {
        "title": "Valid Parentheses",
        "concept": "Stack",
        "skill": "Simulation",
        "difficulty": "Easy",
        "instructions": "Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.",
        "starter_code": "def isValid(s):\n    pass",
        "entrypoint": "isValid",
        "test_cases": [
            {"input": {"s": "()"}, "expected": True},
            {"input": {"s": "()[]{}"}, "expected": True},
            {"input": {"s": "(]"}, "expected": False},
            {"input": {"s": "([)]"}, "expected": False}
        ]
    },
    {
        "title": "Binary Search",
        "concept": "Binary Search",
        "skill": "Divide and Conquer",
        "difficulty": "Easy",
        "instructions": "Given an array of integers nums which is sorted in ascending order, and an integer target, write a function to search target in nums. If target exists, then return its index. Otherwise, return -1.",
        "starter_code": "def search(nums, target):\n    pass",
        "entrypoint": "search",
        "test_cases": [
            {"input": {"nums": [-1, 0, 3, 5, 9, 12], "target": 9}, "expected": 4},
            {"input": {"nums": [-1, 0, 3, 5, 9, 12], "target": 2}, "expected": -1}
        ]
    },
    {
        "title": "Merge Two Sorted Lists",
        "concept": "Linked Lists",
        "skill": "Two Pointers",
        "difficulty": "Easy+",
        "instructions": "You are given the heads of two sorted linked lists list1 and list2. Merge the two lists into one sorted list. The list should be made by splicing together the nodes of the first two lists. Return the merged list as a plain python list for simplicity in this environment.",
        "starter_code": "def mergeTwoLists(list1, list2):\n    pass",
        "entrypoint": "mergeTwoLists",
        "test_cases": [
            {"input": {"list1": [1, 2, 4], "list2": [1, 3, 4]}, "expected": [1, 1, 2, 3, 4, 4]},
            {"input": {"list1": [], "list2": []}, "expected": []},
            {"input": {"list1": [], "list2": [0]}, "expected": [0]}
        ]
    },
    {
        "title": "Best Time to Buy and Sell Stock",
        "concept": "Arrays",
        "skill": "Sliding Window",
        "difficulty": "Easy+",
        "instructions": "You are given an array prices where prices[i] is the price of a given stock on the ith day. You want to maximize your profit by choosing a single day to buy one stock and choosing a different day in the future to sell that stock. Return the maximum profit you can achieve from this transaction. If you cannot achieve any profit, return 0.",
        "starter_code": "def maxProfit(prices):\n    pass",
        "entrypoint": "maxProfit",
        "test_cases": [
            {"input": {"prices": [7, 1, 5, 3, 6, 4]}, "expected": 5},
            {"input": {"prices": [7, 6, 4, 3, 1]}, "expected": 0}
        ]
    },
    {
        "title": "Maximum Subarray",
        "concept": "Arrays",
        "skill": "Dynamic Programming",
        "difficulty": "Medium",
        "instructions": "Given an integer array nums, find the subarray with the largest sum, and return its sum.",
        "starter_code": "def maxSubArray(nums):\n    pass",
        "entrypoint": "maxSubArray",
        "test_cases": [
            {"input": {"nums": [-2, 1, -3, 4, -1, 2, 1, -5, 4]}, "expected": 6},
            {"input": {"nums": [1]}, "expected": 1},
            {"input": {"nums": [5, 4, -1, 7, 8]}, "expected": 23}
        ]
    },
    {
        "title": "Climbing Stairs",
        "concept": "Dynamic Programming",
        "skill": "Math",
        "difficulty": "Easy",
        "instructions": "You are climbing a staircase. It takes n steps to reach the top. Each time you can either climb 1 or 2 steps. In how many distinct ways can you climb to the top?",
        "starter_code": "def climbStairs(n):\n    pass",
        "entrypoint": "climbStairs",
        "test_cases": [
            {"input": {"n": 2}, "expected": 2},
            {"input": {"n": 3}, "expected": 3},
            {"input": {"n": 4}, "expected": 5}
        ]
    },
    {
        "title": "3Sum",
        "concept": "Arrays",
        "skill": "Two Pointers",
        "difficulty": "Medium",
        "instructions": "Given an integer array nums, return all the triplets [nums[i], nums[j], nums[k]] such that i != j, i != k, and j != k, and nums[i] + nums[j] + nums[k] == 0. Notice that the solution set must not contain duplicate triplets.",
        "starter_code": "def threeSum(nums):\n    pass",
        "entrypoint": "threeSum",
        "test_cases": [
            {"input": {"nums": [-1, 0, 1, 2, -1, -4]}, "expected": [[-1, -1, 2], [-1, 0, 1]]},
            {"input": {"nums": [0, 1, 1]}, "expected": []},
            {"input": {"nums": [0, 0, 0]}, "expected": [[0, 0, 0]]}
        ]
    },
    {
        "title": "Container With Most Water",
        "concept": "Arrays",
        "skill": "Greedy",
        "difficulty": "Medium",
        "instructions": "You are given an integer array height of length n. There are n vertical lines drawn such that the two endpoints of the ith line are (i, 0) and (i, height[i]). Find two lines that together with the x-axis form a container, such that the container contains the most water.",
        "starter_code": "def maxArea(height):\n    pass",
        "entrypoint": "maxArea",
        "test_cases": [
            {"input": {"height": [1, 8, 6, 2, 5, 4, 8, 3, 7]}, "expected": 49},
            {"input": {"height": [1, 1]}, "expected": 1}
        ]
    },
    {
        "title": "Longest Substring Without Repeating Characters",
        "concept": "Strings",
        "skill": "Sliding Window",
        "difficulty": "Medium+",
        "instructions": "Given a string s, find the length of the longest substring without repeating characters.",
        "starter_code": "def lengthOfLongestSubstring(s):\n    pass",
        "entrypoint": "lengthOfLongestSubstring",
        "test_cases": [
            {"input": {"s": "abcabcbb"}, "expected": 3},
            {"input": {"s": "bbbbb"}, "expected": 1},
            {"input": {"s": "pwwkew"}, "expected": 3}
        ]
    },
    {
        "title": "Search in Rotated Sorted Array",
        "concept": "Binary Search",
        "skill": "Divide and Conquer",
        "difficulty": "Medium+",
        "instructions": "Given the array nums after the possible rotation and an integer target, return the index of target if it is in nums, or -1 if it is not in nums. You must write an algorithm with O(log n) runtime complexity.",
        "starter_code": "def search(nums, target):\n    pass",
        "entrypoint": "search",
        "test_cases": [
            {"input": {"nums": [4, 5, 6, 7, 0, 1, 2], "target": 0}, "expected": 4},
            {"input": {"nums": [4, 5, 6, 7, 0, 1, 2], "target": 3}, "expected": -1},
            {"input": {"nums": [1], "target": 0}, "expected": -1}
        ]
    },
    {
        "title": "Find Minimum in Rotated Sorted Array",
        "concept": "Binary Search",
        "skill": "Divide and Conquer",
        "difficulty": "Medium",
        "instructions": "Given the sorted rotated array nums of unique elements, return the minimum element of this array. You must write an algorithm that runs in O(log n) time.",
        "starter_code": "def findMin(nums):\n    pass",
        "entrypoint": "findMin",
        "test_cases": [
            {"input": {"nums": [3, 4, 5, 1, 2]}, "expected": 1},
            {"input": {"nums": [4, 5, 6, 7, 0, 1, 2]}, "expected": 0},
            {"input": {"nums": [11, 13, 15, 17]}, "expected": 11}
        ]
    },
    {
        "title": "Product of Array Except Self",
        "concept": "Arrays",
        "skill": "Prefix Sum",
        "difficulty": "Medium",
        "instructions": "Given an integer array nums, return an array answer such that answer[i] is equal to the product of all the elements of nums except nums[i]. The product of any prefix or suffix of nums is guaranteed to fit in a 32-bit integer. You must write an algorithm that runs in O(n) time and without using the division operation.",
        "starter_code": "def productExceptSelf(nums):\n    pass",
        "entrypoint": "productExceptSelf",
        "test_cases": [
            {"input": {"nums": [1, 2, 3, 4]}, "expected": [24, 12, 8, 6]},
            {"input": {"nums": [-1, 1, 0, -3, 3]}, "expected": [0, 0, 9, 0, 0]}
        ]
    },
    {
        "title": "Subsets",
        "concept": "Backtracking",
        "skill": "Recursion",
        "difficulty": "Medium",
        "instructions": "Given an integer array nums of unique elements, return all possible subsets (the power set). The solution set must not contain duplicate subsets. Return the solution in any order.",
        "starter_code": "def subsets(nums):\n    pass",
        "entrypoint": "subsets",
        "test_cases": [
            {"input": {"nums": [1, 2, 3]}, "expected": [[], [1], [2], [1, 2], [3], [1, 3], [2, 3], [1, 2, 3]]},
            {"input": {"nums": [0]}, "expected": [[], [0]]}
        ]
    },
    {
        "title": "Permutations",
        "concept": "Backtracking",
        "skill": "Recursion",
        "difficulty": "Medium+",
        "instructions": "Given an array nums of distinct integers, return all the possible permutations. You can return the answer in any order.",
        "starter_code": "def permute(nums):\n    pass",
        "entrypoint": "permute",
        "test_cases": [
            {"input": {"nums": [1, 2, 3]}, "expected": [[1,2,3], [1,3,2], [2,1,3], [2,3,1], [3,1,2], [3,2,1]]},
            {"input": {"nums": [0, 1]}, "expected": [[0,1], [1,0]]},
            {"input": {"nums": [1]}, "expected": [[1]]}
        ]
    },
    {
        "title": "Number of Islands",
        "concept": "Graph Traversal",
        "skill": "DFS",
        "difficulty": "Medium",
        "instructions": "Given an m x n 2D binary grid grid which represents a map of '1's (land) and '0's (water), return the number of islands. An island is surrounded by water and is formed by connecting adjacent lands horizontally or vertically.",
        "starter_code": "def numIslands(grid):\n    pass",
        "entrypoint": "numIslands",
        "test_cases": [
            {"input": {"grid": [["1","1","1","1","0"], ["1","1","0","1","0"], ["1","1","0","0","0"], ["0","0","0","0","0"]]}, "expected": 1},
            {"input": {"grid": [["1","1","0","0","0"], ["1","1","0","0","0"], ["0","0","1","0","0"], ["0","0","0","1","1"]]}, "expected": 3}
        ]
    },
    {
        "title": "Coin Change",
        "concept": "Dynamic Programming",
        "skill": "Knapsack",
        "difficulty": "Medium+",
        "instructions": "You are given an integer array coins representing coins of different denominations and an integer amount representing a total amount of money. Return the fewest number of coins that you need to make up that amount. If that amount of money cannot be made up by any combination of the coins, return -1.",
        "starter_code": "def coinChange(coins, amount):\n    pass",
        "entrypoint": "coinChange",
        "test_cases": [
            {"input": {"coins": [1, 2, 5], "amount": 11}, "expected": 3},
            {"input": {"coins": [2], "amount": 3}, "expected": -1},
            {"input": {"coins": [1], "amount": 0}, "expected": 0}
        ]
    },
    {
        "title": "Merge Intervals",
        "concept": "Sorting",
        "skill": "Arrays",
        "difficulty": "Medium",
        "instructions": "Given an array of intervals where intervals[i] = [starti, endi], merge all overlapping intervals, and return an array of the non-overlapping intervals that cover all the intervals in the input.",
        "starter_code": "def merge(intervals):\n    pass",
        "entrypoint": "merge",
        "test_cases": [
            {"input": {"intervals": [[1, 3], [2, 6], [8, 10], [15, 18]]}, "expected": [[1, 6], [8, 10], [15, 18]]},
            {"input": {"intervals": [[1, 4], [4, 5]]}, "expected": [[1, 5]]}
        ]
    },
    {
        "title": "Jump Game",
        "concept": "Greedy",
        "skill": "Arrays",
        "difficulty": "Medium+",
        "instructions": "You are given an integer array nums. You are initially positioned at the array's first index, and each element in the array represents your maximum jump length at that position. Return true if you can reach the last index, or false otherwise.",
        "starter_code": "def canJump(nums):\n    pass",
        "entrypoint": "canJump",
        "test_cases": [
            {"input": {"nums": [2, 3, 1, 1, 4]}, "expected": True},
            {"input": {"nums": [3, 2, 1, 0, 4]}, "expected": False}
        ]
    },
    {
        "title": "Course Schedule",
        "concept": "Graph Algorithms",
        "skill": "Topological Sort",
        "difficulty": "Hard",
        "instructions": "There are a total of numCourses courses you have to take, labeled from 0 to numCourses - 1. You are given an array prerequisites where prerequisites[i] = [ai, bi] indicates that you must take course bi first if you want to take course ai. Return true if you can finish all courses. Otherwise, return false.",
        "starter_code": "def canFinish(numCourses, prerequisites):\n    pass",
        "entrypoint": "canFinish",
        "test_cases": [
            {"input": {"numCourses": 2, "prerequisites": [[1, 0]]}, "expected": True},
            {"input": {"numCourses": 2, "prerequisites": [[1, 0], [0, 1]]}, "expected": False}
        ]
    },
    {
        "title": "Trapping Rain Water",
        "concept": "Two Pointers",
        "skill": "Arrays",
        "difficulty": "Hard",
        "instructions": "Given n non-negative integers representing an elevation map where the width of each bar is 1, compute how much water it can trap after raining.",
        "starter_code": "def trap(height):\n    pass",
        "entrypoint": "trap",
        "test_cases": [
            {"input": {"height": [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]}, "expected": 6},
            {"input": {"height": [4, 2, 0, 3, 2, 5]}, "expected": 9}
        ]
    },
    {
        "title": "Minimum Window Substring",
        "concept": "Sliding Window",
        "skill": "Strings",
        "difficulty": "Hard",
        "instructions": "Given two strings s and t of lengths m and n respectively, return the minimum window substring of s such that every character in t (including duplicates) is included in the window. If there is no such substring, return the empty string.",
        "starter_code": "def minWindow(s, t):\n    pass",
        "entrypoint": "minWindow",
        "test_cases": [
            {"input": {"s": "ADOBECODEBANC", "t": "ABC"}, "expected": "BANC"},
            {"input": {"s": "a", "t": "a"}, "expected": "a"},
            {"input": {"s": "a", "t": "aa"}, "expected": ""}
        ]
    },
    {
        "title": "Edit Distance",
        "concept": "Advanced DP",
        "skill": "Strings",
        "difficulty": "Advanced",
        "instructions": "Given two strings word1 and word2, return the minimum number of operations required to convert word1 to word2. You have the following three operations permitted on a word: Insert a character, Delete a character, Replace a character.",
        "starter_code": "def minDistance(word1, word2):\n    pass",
        "entrypoint": "minDistance",
        "test_cases": [
            {"input": {"word1": "horse", "word2": "ros"}, "expected": 3},
            {"input": {"word1": "intention", "word2": "execution"}, "expected": 5}
        ]
    }
]

with open('seed_data.json', 'w') as f:
    json.dump(problems, f, indent=4)
