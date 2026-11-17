# -*- coding: utf-8 -*-
"""批量修复 Python 源里中文行内的直引号（破坏字符串字面量）。"""
import re
import io

p = r"D:\projects\taomind-site\gen_tiktok_script_docx.py"
with io.open(p, "r", encoding="utf-8") as f:
    src = f.read()

# 把所有出现在中文字符之间的直双引号替换成中文弯引号
# 简单策略：双引号前面是中文（4e00-9fff / 3000-303f / ff00-ffef）或紧跟中文，转换成"
out_lines = []
fixed = 0
for line in src.split("\n"):
    if not re.search(r"[\u4e00-\u9fff]", line):
        out_lines.append(line)
        continue
    # 替换出现在中文旁的直引号为中文引号
    new = []
    chars = list(line)
    for i, ch in enumerate(chars):
        if ch == '"':
            prev = chars[i-1] if i > 0 else ""
            nxt = chars[i+1] if i+1 < len(chars) else ""
            prev_zh = bool(re.match(r"[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]", prev))
            nxt_zh = bool(re.match(r"[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]", nxt))
            # 出现在中文旁边的 → 弯引号
            if prev_zh and not nxt_zh:
                new.append("\u201d")  # 右引号
            elif nxt_zh and not prev_zh:
                new.append("\u201c")  # 左引号
            elif prev_zh and nxt_zh:
                new.append("\u201c")  # 文中用左
            else:
                new.append(ch)
            if prev_zh or nxt_zh:
                fixed += 1
        else:
            new.append(ch)
    out_lines.append("".join(new))

with io.open(p, "w", encoding="utf-8") as f:
    f.write("\n".join(out_lines))

print(f"Fixed {fixed} stray quotes in {p}")
