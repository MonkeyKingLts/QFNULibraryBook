"""按座位号黑名单筛选可预约座位。"""

import json
import os
import random


def build_exclude_set(ranges=None, singles=None):
    """合并区间与单个座位号，生成不抢座位集合。"""
    excluded = set()
    for lo, hi in ranges or []:
        excluded.update(range(int(lo), int(hi) + 1))
    for seat_no in singles or []:
        excluded.add(int(seat_no))
    return excluded


def filter_allowed_seats(seats, exclude_set):
    """从空闲座位列表中排除黑名单座位号。"""
    return [s for s in seats if int(s.get("no", 0)) not in exclude_set]


def resolve_preferred_seat_api_id(classroom_name, seat_no):
    """根据座位号从 seat_info 查询 API id。"""
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(repo_root, "json", "seat_info", f"{classroom_name}.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)["data"]
    target = int(seat_no)
    for s in data:
        if int(s["name"]) == target:
            return str(s["id"])
    return None


def pick_seat_with_preference(seats, preferred_no=None):
    """有空闲座时优先选 preferred_no，否则在列表中随机。"""
    if preferred_no is not None:
        target = int(preferred_no)
        for s in seats:
            if int(s.get("no", 0)) == target:
                return s["id"], str(s.get("no"))
    chosen = random.choice(seats)
    return chosen["id"], str(chosen.get("no"))


def load_allowed_seat_api_ids(classroom_name, exclude_set):
    """从 json/seat_info 加载可抢座位的 API id 列表（供模式 2 使用）。"""
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(repo_root, "json", "seat_info", f"{classroom_name}.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)["data"]
    return [
        int(s["id"])
        for s in data
        if int(s["name"]) not in exclude_set
    ]
