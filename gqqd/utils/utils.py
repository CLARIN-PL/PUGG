import hashlib
import random
from datetime import datetime

from tinydb.table import Table


def get_current_time_str() -> str:
    return datetime.today().strftime("%Y-%m-%d %H:%M:%S")


def get_string_md5(string: str) -> str:
    return hashlib.md5(string.encode()).hexdigest()


def insert_to_table_and_clean_buffer(buffer: list[dict[str, str | int]], table: Table) -> None:
    table.insert_multiple(buffer)
    buffer.clear()


def split_list_with_weights(
    elements: list[str], weights: list[float], num_groups: int
) -> list[list[str]]:
    group_indices = random.choices(range(num_groups), weights=weights, k=len(elements))
    grouped_lists: list[list[str]] = [[] for _ in range(num_groups)]
    for element, group_index in zip(elements, group_indices):
        grouped_lists[group_index].append(element)
    return grouped_lists
