from datetime import datetime
import shlex
from typing import Dict, List
from collections import namedtuple
from util import Hiscore

from .mgmt_abc import INodeType

LeafValues = namedtuple("LeafValues", ["results", "query"])

def _convert_to_ordinal(date: datetime) -> int:
    """Convert datetime to ordinal time"""
    try:
        return date.toordinal()
    except ValueError as e:
        print(f"Error in convert to ordinal: {e}")
        return False
    
def _convert_str_date_to_ordinal(date_str: str, format="%Y-%m-%d") -> int:
    """Convert datetime string to ordinal time"""
    try:
        return datetime.strptime(date_str, format).toordinal()
    except ValueError as e:
        print(f"Error in convert string datetime to ordinal: {e}")
        return False

def _convert_from_ordinal(orddate: int, date_format: str="%Y-%m-%d") -> str:
    """Convert ordinal date to str date"""
    try:
        return datetime.fromordinal(orddate).strftime(date_format)
    except ValueError as e:
        print(f"Error converting to string date: {e}")
        return False
    
def print_hiscore_stats(name) -> Hiscore:
    try:
        hs_data = Hiscore(name).to_dict()
    except Exception as e:
        print("No stats found")
        return
    
    # print(f"Username: {hs_data['username']}")
    # print(f"Account Type: {hs_data['account_type']}")
    # print(f"Total Rank: {hs_data['total_rank']}")
    # print(f"Total Level: {hs_data['total_level']}")
    # print(f"Total XP: {hs_data['total_xp']:,}")
    # print("\n" + "="*50)

    # Print Skills Section
    print("\nSkills:")
    print("-" * 50)
    for skill in sorted(hs_data['skills'], key=lambda x: (x['level'], x['xp']), reverse=True):
        print(f"{skill['name'].title():<15} "
              f"Level: {skill['level']:<3} "
              f"XP: {skill['xp']:<10} ")

    # Print Activities Section
    print("\n" + "="*50)
    print("\nActivities:")
    print("-" * 50)
    for activity in hs_data['activities']:
        print(f"{activity['name']:<35} Score: {activity['score']}")

    # Print Bosses Section
    print("\n" + "="*50)
    print("\nBosses:")
    print("-" * 50)
    for boss in hs_data['bosses']:
        print(f"{boss['name']:<35} Score: {boss['score']}")

    print("\n" + "="*50)


def _refine_query(query: str, dtype: str) -> str:
    fields = shlex.split(query)
    if fields[1] == "=":
        fields[1] = "=="

    if dtype in ["string", "enum"]:
        fields[2] = f"\"{fields[2]}\""

    if dtype == "date":
        fields[2] = str(_convert_str_date_to_ordinal(fields[2]))

    return " ".join(fields[:3])

def get_leaf_values(leaf_names: List[str], 
                    leaf_blocks: Dict[str, INodeType],
                    build_query: bool = False) -> LeafValues:
    res = {}
    queries = []
    for name in leaf_names:
        if not (block := leaf_blocks.get(name)):
            continue
        if build_query:
            queries.append(_refine_query(block.expr_str(name), block.dtype))
        res[name] = block.value if not block.dtype == "date" else _convert_to_ordinal(block.value)
    return LeafValues(res, "&".join(queries) if queries else "")

