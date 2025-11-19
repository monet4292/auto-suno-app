"""
Shared test utilities for queue + history suites.
"""
from src.utils.prompt_parser import SunoPrompt


def make_prompts(count: int) -> list[SunoPrompt]:
    return [
        SunoPrompt(
            title=f"Prompt #{i}",
            lyrics="Lyrics go here",
            style="Pop"
        )
        for i in range(count)
    ]
