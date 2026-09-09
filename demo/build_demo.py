import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent
news = json.loads((root / "data/demo_clustered.json").read_text())
social_items = json.loads((root / "data/demo_social_items.json").read_text())
sources = json.loads((root / "data/demo_sources.json").read_text())
channel_items = json.loads((root / "data/demo_channel_items.json").read_text())

DEFAULT_STARRED = [
    "Simon Willison", "Interconnects", "Don't Worry About the Vase",
    "levels.io", "Import AI", "Latent Space",
]

data = {
    "news": {"clusters": news["clusters"], "total_items": news["total_items"]},
    "social_items": social_items,
    "channel_items": channel_items,
    "sources": sources,
    "default_starred": DEFAULT_STARRED,
}

template = (root / "demo/cluster-demo.template.html").read_text()
out = template.replace("__DATA__", json.dumps(data, ensure_ascii=False))
(root / "demo/cluster-demo.html").write_text(out, encoding="utf-8")
print(
    f"built demo/cluster-demo.html: "
    f"news={len(news['clusters'])}clusters social_items={len(social_items)} "
    f"channel_items(sources)={len(channel_items)} sources={len(sources)}"
)
