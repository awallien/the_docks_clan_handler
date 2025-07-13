from datetime import datetime
from typing import Dict, List
from collections import namedtuple

from .mgmt_abc import INodeType

def _convert_to_ordinal(date: datetime, date_format: str="%Y-%m-%d") -> datetime:
    """Convert date string to datetime object"""
    try:
        return date.toordinal()
    except ValueError as e:
        print(f"Error in convert to ordinal: {e}")
        return False


LeafValues = namedtuple("LeafValues", ["results", "query"])

def get_leaf_values(leaf_names: List[str], 
                    leaf_blocks: Dict[str, INodeType],
                    build_query: bool = False) -> LeafValues:
    res = {}
    queries = []
    for name in leaf_names:
        if not (block := leaf_blocks.get(name)):
            continue
        if build_query:
            queries.append(block.expr_str(name))
        res[name] = block.value if not block.dtype == "date" else _convert_to_ordinal(block.value)
    return LeafValues(res, "&".join(f"({queries})") if queries else "")

