"""Authored curriculum content, as data.

Content is versioned in the repository (not in a database dump) so that review, diffing and
licence checks are possible. The loader copies it into the database for the application to query.
"""

from app.curriculum.registry import (
    PATHS,
    all_items,
    all_lessons,
    all_objectives,
    get_path,
    item_index,
    lesson_index,
    list_path_summaries,
    objective_index,
)

__all__ = [
    "PATHS",
    "all_items",
    "all_lessons",
    "all_objectives",
    "get_path",
    "item_index",
    "lesson_index",
    "list_path_summaries",
    "objective_index",
]
