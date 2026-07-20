"""中文脚本章节拆分器 — 纯规则，无LLM依赖"""

import re

# 句末标点
_SENTENCE_END = re.compile(r"[。！？!?\n]")
# 从句标点（用于二次拆分）
_CLAUSE_SEP = re.compile(r"[，,；;：:，]")


def split_script(script_text: str, max_chars_per_segment: int = 50, max_segments: int = 3) -> list[str]:
    """
    将中文脚本拆成大致等长的段落，用于多段视频生成。

    Args:
        script_text: 原始脚本文本
        max_chars_per_segment: 每段最大字符数（约）
        max_segments: 最多段数

    Returns:
        段落字符串列表（1 到 max_segments 个元素）
    """
    text = script_text.strip()
    if not text:
        return [""]

    # 1. 按句末标点拆
    raw_parts = [p.strip() for p in _SENTENCE_END.split(text) if p.strip()]

    if not raw_parts:
        return [text]

    # 2. 贪心合并短句，目标每段 20-60 字符
    merged = []
    buf = ""
    for part in raw_parts:
        tentative = (buf + "。" + part) if buf else part
        if len(tentative) <= max_chars_per_segment + 10:
            buf = tentative
        else:
            if buf:
                merged.append(buf)
            buf = part
    if buf:
        merged.append(buf)

    # 3. 如果段数 < max_segments 且段很长 → 二次拆最长的段
    while len(merged) < max_segments:
        longest_idx = max(range(len(merged)), key=lambda i: len(merged[i]))
        longest = merged[longest_idx]
        if len(longest) < 30:
            break
        sub = [s.strip() for s in _CLAUSE_SEP.split(longest) if s.strip()]
        if len(sub) >= 2:
            mid = len(sub) // 2
            merged[longest_idx:longest_idx + 1] = [
                "，".join(sub[:mid]),
                "，".join(sub[mid:]),
            ]
        else:
            break

    # 4. 如果段数 > max_segments → 合并最小的两段
    while len(merged) > max_segments:
        # 找到最短的相邻两段合并
        best_i, best_len = 0, float("inf")
        for i in range(len(merged) - 1):
            combined = len(merged[i]) + len(merged[i + 1])
            if combined < best_len:
                best_i, best_len = i, combined
        merged[best_i:best_i + 2] = [merged[best_i] + "。" + merged[best_i + 1]]

    return merged


def split_script_for_long_video(script_text: str) -> list[str]:
    """默认长视频拆分：目标 3 段，每段 30-50 字"""
    return split_script(script_text, max_chars_per_segment=50, max_segments=3)
