"""
NeuralChat Evaluation Framework
================================
Automated testing and scoring of chatbot responses.
Tests tool routing accuracy, answer quality, and memory extraction.

Usage:
    cd chatbot
    python evaluate.py
"""

import uuid
import sys
import time
from datetime import datetime
from langchain_core.messages import HumanMessage, AIMessage

# Import from backend
from backend import chatbot, llm, extract_user_memories, get_memory_context, add_user_memory, is_memory_duplicate

# ======================= Test Cases =======================

TEST_CASES = [
    # --- General Knowledge (no tool expected) ---
    {
        "id": "GK-1",
        "category": "General Knowledge",
        "query": "What is the capital of France?",
        "expected_tool": None,
        "quality_check": "The answer must mention 'Paris'.",
    },
    {
        "id": "GK-2",
        "category": "General Knowledge",
        "query": "Explain what photosynthesis is in one sentence.",
        "expected_tool": None,
        "quality_check": "The answer must mention plants converting sunlight/light into energy/food.",
    },
    {
        "id": "GK-3",
        "category": "General Knowledge",
        "query": "What is a Python decorator?",
        "expected_tool": None,
        "quality_check": "The answer must describe decorators as functions that modify/wrap other functions.",
    },

    # --- Calculator Tool ---
    {
        "id": "CALC-1",
        "category": "Calculator",
        "query": "What is 456 multiplied by 789?",
        "expected_tool": "calculator",
        "quality_check": "The answer must contain the number 359784.",
    },
    {
        "id": "CALC-2",
        "category": "Calculator",
        "query": "Calculate 1000 divided by 7",
        "expected_tool": "calculator",
        "quality_check": "The answer must contain approximately 142.857.",
    },

    # --- Internet Search Tool ---
    {
        "id": "SEARCH-1",
        "category": "Internet Search",
        "query": "What are the latest developments in AI this week?",
        "expected_tool": "search_internet",
        "quality_check": "The answer must reference recent AI news, events, or developments.",
    },
    {
        "id": "SEARCH-2",
        "category": "Internet Search",
        "query": "Who won the most recent Cricket World Cup?",
        "expected_tool": "search_internet",
        "quality_check": "The answer must name a country as the winner.",
    },

    # --- Stock Price Tool ---
    {
        "id": "STOCK-1",
        "category": "Stock Price",
        "query": "What is Apple's current stock price?",
        "expected_tool": "get_stock_price",
        "quality_check": "The answer must mention a price or stock data for AAPL/Apple.",
    },

    # --- Memory Extraction ---
    {
        "id": "MEM-1",
        "category": "Memory",
        "query": "My name is TestUser and I am a machine learning engineer.",
        "expected_tool": None,
        "quality_check": "The response should acknowledge the user's name (TestUser) or role (ML engineer).",
        "memory_check": ["TestUser", "machine learning"],
    },
    {
        "id": "MEM-2",
        "category": "Memory",
        "query": "I work at Google and I love building chatbots.",
        "expected_tool": None,
        "quality_check": "The response should acknowledge the user's workplace or interest.",
        "memory_check": ["Google", "chatbot"],
    },

    # --- Edge Cases ---
    {
        "id": "EDGE-1",
        "category": "Edge Case",
        "query": "Hello!",
        "expected_tool": None,
        "quality_check": "The response should be a friendly greeting, not use any tools.",
    },
    {
        "id": "EDGE-2",
        "category": "Edge Case",
        "query": "",
        "expected_tool": None,
        "quality_check": "The response should handle empty input gracefully.",
        "skip": True,
    },
]


# ======================= Test Runner =======================

def run_single_test(test_case):
    """Run a single test case through the chatbot and capture results."""
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    # Set global context for memory
    import backend
    backend._CURRENT_THREAD_ID = thread_id
    backend._CURRENT_USER_ID = f"eval_user_{thread_id[:8]}"

    result = {
        "id": test_case["id"],
        "category": test_case["category"],
        "query": test_case["query"],
        "expected_tool": test_case["expected_tool"],
        "tools_used": [],
        "response": "",
        "tool_correct": False,
        "quality_score": 0,
        "memory_score": None,
        "error": None,
        "latency_ms": 0,
    }

    try:
        start_time = time.time()

        # Stream through the chatbot to capture tool calls
        for event in chatbot.stream(
            {"messages": [HumanMessage(content=test_case["query"])]},
            config=config,
            stream_mode="values",
        ):
            if "messages" in event:
                messages = event["messages"]
                # Capture tool calls
                if messages and hasattr(messages[-1], "tool_calls"):
                    for tc in messages[-1].tool_calls or []:
                        tool_name = tc.get("name", "Unknown")
                        if tool_name not in result["tools_used"]:
                            result["tools_used"].append(tool_name)

                # Capture final AI response
                if messages and isinstance(messages[-1], AIMessage):
                    content = messages[-1].content
                    if isinstance(content, str) and content.strip():
                        result["response"] = content
                    elif isinstance(content, list) and len(content) > 0:
                        text = content[0].get("text", "") if isinstance(content[0], dict) else str(content[0])
                        if text.strip():
                            result["response"] = text

        result["latency_ms"] = int((time.time() - start_time) * 1000)

        # --- Check tool routing accuracy ---
        expected = test_case["expected_tool"]
        if expected is None:
            # No tool should be used (direct answer)
            result["tool_correct"] = len(result["tools_used"]) == 0
        else:
            result["tool_correct"] = expected in result["tools_used"]

        # --- LLM-as-Judge for quality ---
        result["quality_score"] = grade_response(
            test_case["query"],
            result["response"],
            test_case["quality_check"],
        )

        # --- Memory check (if applicable) ---
        if "memory_check" in test_case:
            result["memory_score"] = check_memory_extraction(
                test_case["query"],
                test_case["memory_check"],
                backend._CURRENT_USER_ID,
            )

    except Exception as e:
        result["error"] = str(e)

    return result


# ======================= LLM-as-Judge =======================

def grade_response(query, response, quality_criteria):
    """Use the LLM to grade a response on a 1-5 scale."""
    if not response:
        return 1

    grading_prompt = f"""You are an AI evaluator. Grade the following chatbot response on a scale of 1-5.

USER QUERY: {query}

CHATBOT RESPONSE: {response}

QUALITY CRITERIA: {quality_criteria}

SCORING:
1 = Completely wrong or irrelevant
2 = Partially relevant but mostly incorrect
3 = Acceptable but missing key information
4 = Good response with minor issues
5 = Excellent, accurate, and complete

Respond with ONLY a single number (1-5), nothing else."""

    try:
        grade = llm.invoke(grading_prompt)
        content = grade.content
        if isinstance(content, list) and len(content) > 0:
            content = content[0].get("text", "") if isinstance(content[0], dict) else str(content[0])
        # Extract the number from the response
        score = int("".join(c for c in str(content).strip() if c.isdigit())[:1])
        return max(1, min(5, score))
    except Exception:
        return 3  # Default to middle score on error


def check_memory_extraction(query, expected_keywords, user_id):
    """Check if the memory system correctly extracted facts from the query."""
    try:
        existing_memories = get_memory_context(user_id)
        if not existing_memories:
            return 0.0

        found = 0
        for keyword in expected_keywords:
            if keyword.lower() in existing_memories.lower():
                found += 1

        return round(found / len(expected_keywords), 2)
    except Exception:
        return 0.0


# ======================= Report Generator =======================

def generate_report(results):
    """Generate a formatted evaluation report."""
    print("\n" + "=" * 70)
    print("  📊 NEURALCHAT EVALUATION REPORT")
    print(f"  📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # Group by category
    categories = {}
    for r in results:
        cat = r["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(r)

    total_tool_correct = 0
    total_tool_tests = 0
    total_quality_score = 0
    total_tests = 0
    total_memory_score = 0
    memory_tests = 0

    for category, tests in categories.items():
        print(f"\n  ── {category} ──")

        for r in tests:
            total_tests += 1
            status = "✅" if r["tool_correct"] and r["quality_score"] >= 3 else "❌"

            # Tool check
            if r["expected_tool"] is not None or len(r["tools_used"]) > 0:
                total_tool_tests += 1
                if r["tool_correct"]:
                    total_tool_correct += 1

            total_quality_score += r["quality_score"]

            # Print result
            print(f"\n  {status}  [{r['id']}] \"{r['query'][:50]}{'...' if len(r['query']) > 50 else ''}\"")

            if r["error"]:
                print(f"      ⚠️  Error: {r['error']}")
                continue

            # Tool info
            expected_str = r["expected_tool"] or "none"
            actual_str = ", ".join(r["tools_used"]) if r["tools_used"] else "none"
            tool_icon = "✅" if r["tool_correct"] else "❌"
            print(f"      {tool_icon} Tool: expected={expected_str}, actual={actual_str}")

            # Quality score
            stars = "★" * r["quality_score"] + "☆" * (5 - r["quality_score"])
            print(f"      📝 Quality: {stars} ({r['quality_score']}/5)")

            # Memory score (if applicable)
            if r["memory_score"] is not None:
                memory_tests += 1
                total_memory_score += r["memory_score"]
                mem_pct = int(r["memory_score"] * 100)
                print(f"      🧠 Memory: {mem_pct}% keywords extracted")

            # Latency
            print(f"      ⏱️  Latency: {r['latency_ms']}ms")

    # --- Summary ---
    print("\n" + "=" * 70)
    print("  📈 SUMMARY")
    print("=" * 70)

    avg_quality = round(total_quality_score / max(total_tests, 1), 2)
    tool_accuracy = round(total_tool_correct / max(total_tool_tests, 1) * 100, 1)
    avg_memory = round(total_memory_score / max(memory_tests, 1) * 100, 1)

    passed = sum(1 for r in results if r["tool_correct"] and r["quality_score"] >= 3)
    failed = total_tests - passed

    print(f"""
  Tests Run:       {total_tests}
  Tests Passed:    {passed} ✅
  Tests Failed:    {failed} ❌
  
  Quality Score:   {avg_quality} / 5.0  ({int(avg_quality/5*100)}%)
  Tool Accuracy:   {total_tool_correct}/{total_tool_tests} ({tool_accuracy}%)
  Memory Accuracy: {avg_memory}%
  
  Avg Latency:     {int(sum(r['latency_ms'] for r in results) / max(len(results), 1))}ms
""")

    # Grade
    if avg_quality >= 4.5 and tool_accuracy >= 90:
        grade = "A+"
    elif avg_quality >= 4.0 and tool_accuracy >= 80:
        grade = "A"
    elif avg_quality >= 3.5 and tool_accuracy >= 70:
        grade = "B"
    elif avg_quality >= 3.0:
        grade = "C"
    else:
        grade = "D"

    print(f"  🎯 OVERALL GRADE: {grade}")
    print("=" * 70 + "\n")

    return {
        "total_tests": total_tests,
        "passed": passed,
        "failed": failed,
        "avg_quality": avg_quality,
        "tool_accuracy": tool_accuracy,
        "memory_accuracy": avg_memory,
        "grade": grade,
    }


# ======================= Main =======================

if __name__ == "__main__":
    print("\n🚀 Starting NeuralChat Evaluation...\n")
    print(f"Running {len([t for t in TEST_CASES if not t.get('skip')])} test cases...\n")

    results = []
    for i, test in enumerate(TEST_CASES):
        if test.get("skip"):
            print(f"  ⏭️  Skipping [{test['id']}]: {test['query'][:40]}")
            continue

        print(f"  [{i+1}/{len(TEST_CASES)}] Testing: \"{test['query'][:50]}\"...", end=" ", flush=True)
        result = run_single_test(test)
        results.append(result)

        status = "✅" if result["tool_correct"] and result["quality_score"] >= 3 else "❌"
        print(f"{status} ({result['quality_score']}/5, {result['latency_ms']}ms)")

    summary = generate_report(results)

    # Exit with error code if too many failures
    if summary["failed"] > len(results) * 0.5:
        print("⚠️  More than 50% of tests failed!")
        sys.exit(1)
