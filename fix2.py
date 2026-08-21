import re
with open("src/modules/execution/service.py", "r") as f:
    content = f.read()

# I will find the function and remove it entirely until _update_lesson_progress
start_idx = content.find("def _extract_test_cases_from_exercise")
end_idx = content.find("async def _update_lesson_progress")

if start_idx != -1 and end_idx != -1:
    new_func = '''def _extract_test_cases_from_exercise(self, exercise: Exercise) -> list[TestCaseInput]:
        """Generate test cases from exercise specifications or default fallback."""
        if hasattr(exercise, 'test_cases_json') and exercise.test_cases_json:
            return [
                TestCaseInput(
                    input_data=tc.get("input"),
                    expected_output=tc.get("expected"),
                    is_hidden=tc.get("is_hidden", False)
                ) for tc in exercise.test_cases_json
            ]
        return [
            TestCaseInput(input_data=[1, 2], expected_output=3, is_hidden=False),
        ]

    '''
    content = content[:start_idx] + new_func + content[end_idx:]
    with open("src/modules/execution/service.py", "w") as f:
        f.write(content)
