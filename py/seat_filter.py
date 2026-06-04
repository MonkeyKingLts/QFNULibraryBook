"""按座位号黑名单筛选可预约座位。"""

import json
import os


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
