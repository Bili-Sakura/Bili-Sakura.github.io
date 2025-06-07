#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, json, requests

# ── 配置 ──
UID = 3546681717033402  # Bilibili user ID
API_URL = (
    f"https://api.bilibili.com/x/space/arc/search?mid={UID}&pn=1&ps=20&order=pubdate"
)
LAST_FILE = "last_bvid.txt"
JSON_FILE = "videos.json"
MAX_VIDEOS = 5

if not UID:
    print("Error: Please set BILIBILI_UID in your GitHub Secrets.")
    sys.exit(1)

# 1) 读上次最新的视频 ID
last_bvid = None
if os.path.exists(LAST_FILE):
    with open(LAST_FILE, "r", encoding="utf-8") as f:
        last_bvid = f.read().strip()

# 2) 拉取最新投稿
resp = requests.get(API_URL)
resp.raise_for_status()
items = resp.json().get("data", {}).get("list", {}).get("vlist", [])
if not items:
    print("No videos found.")
    sys.exit(0)

# 3) 首次运行：初始化 videos.json 为最新 5 条，并写 last_bvid
if last_bvid is None or not os.path.exists(JSON_FILE):
    initial = items[:MAX_VIDEOS]
    initial_entries = [
        {
            "title": vid["title"].replace("\n", " "),
            "url": f"https://www.bilibili.com/video/{vid['bvid']}",
        }
        for vid in initial
    ]
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(initial_entries, f, ensure_ascii=False, indent=2)
    with open(LAST_FILE, "w", encoding="utf-8") as f:
        f.write(items[0]["bvid"])
    print(f"✅ First run: initialized {JSON_FILE} with {len(initial_entries)} videos.")
    sys.exit(0)

# 4) 抽取自上次以来的新视频
new_items = []
for vid in items:
    if vid["bvid"] == last_bvid:
        break
    new_items.append(vid)

if not new_items:
    print("No new videos.")
    sys.exit(0)

# 5) 构造 JSON 条目
entries = [
    {
        "title": vid["title"].replace("\n", " "),
        "url": f"https://www.bilibili.com/video/{vid['bvid']}",
    }
    for vid in new_items
]

# 6) 载入已有 videos.json（若存在）
old_list = []
if os.path.exists(JSON_FILE):
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        old_list = json.load(f)

# 7) 合并并截断到前 MAX_VIDEOS 条
updated = entries + old_list
updated = updated[:MAX_VIDEOS]

# 8) 写回 videos.json
with open(JSON_FILE, "w", encoding="utf-8") as f:
    json.dump(updated, f, ensure_ascii=False, indent=2)

# 9) 更新 last_bvid
with open(LAST_FILE, "w", encoding="utf-8") as f:
    f.write(items[0]["bvid"])

print(f"✅ Updated {JSON_FILE} with {len(entries)} new videos.")
