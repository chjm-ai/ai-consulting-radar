"""一次性脚本: 对抓到的原始标题做话题聚类(单次LLM调用), 给demo页用。"""
import json
import os
from pathlib import Path

from openai import OpenAI

client = OpenAI(
    api_key=os.environ["DASHSCOPE_API_KEY"],
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

REFERENCE_BLOGGERS = {
    "Simon Willison", "One Useful Thing", "Interconnects", "Chip Huyen",
    "Eugene Yan", "Lilian Weng", "Elad Gil", "Byrne Hobart (The Diff)",
    "swyx", "DHH", "levels.io", "Ahead of AI", "Import AI",
    "Don't Worry About the Vase", "Latent Space", "Jay Alammar",
}


def main():
    items = json.loads(Path("data/demo_raw_items.json").read_text())

    # 重点关注博主: 无论聚类结果如何,直接单独摘出他们最新的1条
    reference_items = [it for it in items if it["source_name"] in REFERENCE_BLOGGERS]
    reference_items.sort(key=lambda x: x["published_at"], reverse=True)
    seen_src = set()
    reference_latest = []
    for it in reference_items:
        if it["source_name"] in seen_src:
            continue
        seen_src.add(it["source_name"])
        reference_latest.append(it)

    lines = []
    for i, it in enumerate(items):
        lines.append(f"[{i}] ({it['source_name']}) {it['title']}")
    items_text = "\n".join(lines)

    system = (
        "你是一名AI行业信息编辑。下面是过去72小时从多个信息源抓到的标题列表(含来源名)。"
        "请找出被多个不同来源共同报道/讨论的同一事件或话题,把它们聚类。"
        "只聚类真正指向同一件事的条目(比如同一个模型发布、同一起收购、同一个热点讨论),"
        "不要仅因为都属于'AI'这种宽泛主题就归为一类。"
        "每个聚类至少包含2条不同来源的条目。"
        "返回JSON,格式:\n"
        '{"clusters": [{"topic": "话题标题(中文,简洁)", '
        '"summary": "1-2句话综述,这些来源主要在讲什么、有没有不同角度或分歧", '
        '"member_indices": [数字...]}]}\n'
        "summary里禁止出现任何数字编号或索引引用,包括但不限于'[0]'、'标题0'、'#44'、'帖子44'这类写法,"
        "只能用来源名称+具体内容自然表述,就像写给人看的新闻简报一样。"
        "按聚类内条目数量从多到少排序。最多返回15个聚类。"
    )
    user = f"标题列表:\n{items_text}"

    resp = client.chat.completions.create(
        model="qwen-plus",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.2,
        response_format={"type": "json_object"},
    )
    content = resp.choices[0].message.content
    result = json.loads(content)
    clusters = result.get("clusters", [])

    # 把indices换成完整条目
    for c in clusters:
        c["members"] = [items[i] for i in c.get("member_indices", []) if 0 <= i < len(items)]
        c.pop("member_indices", None)

    output = {
        "clusters": clusters,
        "reference_latest": reference_latest,
        "total_items": len(items),
    }
    Path("data/demo_clustered.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    usage = resp.usage
    print(f"聚类完成: {len(clusters)} 个话题簇, 覆盖 {sum(len(c['members']) for c in clusters)} 条")
    print(f"重点关注博主最新: {len(reference_latest)} 条")
    print(f"token用量: input={usage.prompt_tokens} output={usage.completion_tokens}")


if __name__ == "__main__":
    main()
