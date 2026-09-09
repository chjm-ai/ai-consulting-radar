import json
import os
from pathlib import Path

from openai import OpenAI

client = OpenAI(
    api_key=os.environ["DASHSCOPE_API_KEY"],
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

items = json.loads(Path("data/demo_social_items.json").read_text())
lines = [f"[{i}] ({it['source_name']}) {it['title']}" for i, it in enumerate(items)]
items_text = "\n".join(lines)

system = (
    "你是一名AI行业信息编辑。下面是过去72小时从YouTube频道和Hacker News抓到的标题列表(含来源名,多为英文)。"
    "请找出被多个不同来源共同报道/讨论的同一事件或话题,把它们聚类。"
    "只聚类真正指向同一件事的条目,不要仅因为都属于'AI'这种宽泛主题就归为一类。"
    "每个聚类至少包含2条不同来源的条目。"
    "无论原始标题是什么语言,topic和summary字段必须用中文撰写,不要输出英文。"
    "summary里禁止出现任何数字编号或索引引用,包括但不限于'[0]'、'标题0'、'#44'、'帖子44'这类写法,"
    "只能用来源名称+具体内容自然表述,就像写给人看的新闻简报一样。"
    '返回JSON: {"clusters": [{"topic": "话题标题(中文)", "summary": "1-2句话综述(中文,不含编号引用)", "member_indices": [数字...]}]}'
    "按条目数从多到少排序,最多10个聚类。"
)
resp = client.chat.completions.create(
    model="qwen-plus",
    messages=[
        {"role": "system", "content": system},
        {"role": "user", "content": f"标题列表:\n{items_text}"},
    ],
    temperature=0.2,
    response_format={"type": "json_object"},
)
result = json.loads(resp.choices[0].message.content)
clusters = result.get("clusters", [])
for c in clusters:
    c["members"] = [items[i] for i in c.get("member_indices", []) if 0 <= i < len(items)]
    c.pop("member_indices", None)

clustered_ids = {id(m) for c in clusters for m in c["members"]}
singles = [it for it in items if id(it) not in clustered_ids]
singles.sort(key=lambda x: x["published_at"], reverse=True)

output = {"clusters": clusters, "singles": singles, "total_items": len(items)}
Path("data/demo_social_clustered.json").write_text(
    json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8"
)
print(f"聚类完成: {len(clusters)}个话题簇, 覆盖{sum(len(c['members']) for c in clusters)}条; 单条{len(singles)}条")
print("token:", resp.usage.prompt_tokens, resp.usage.completion_tokens)
