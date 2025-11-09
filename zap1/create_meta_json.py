import json

# ========= テーマを設定 =========
TITLE = "レモン彗星とは"

# 日本語の説明から英語プロンプトに変換
SCENES = [
    {
        "description": "Scene 1: 宇宙の闇に浮かぶ青白く輝くレモン彗星",
        "prompt": (
            "A glowing blue-white comet with a bright tail streaking through deep space, "
            "surrounded by colorful nebula clouds and countless stars. "
            "The comet has a luminous pale blue core with a long flowing tail. "
            "Cinematic lighting, space photography, ultra realistic, 8K resolution, "
            "dramatic cosmic scene, vertical 9:16 composition"
        )
    },
    {
        "description": "Scene 2: 彗星の尾が太陽の光を受けて金色に輝く",
        "prompt": (
            "A magnificent comet with a golden glowing tail illuminated by sunlight, "
            "with Earth visible in the foreground as a blue sphere. "
            "The comet's tail shimmers in golden and amber hues. "
            "Deep contrast between the bright comet and dark space background. "
            "Cinematic space photography, photorealistic, dramatic lighting, "
            "ethereal atmosphere, vertical 9:16 format"
        )
    },
    {
        "description": "Scene 3: 彗星を見上げる観測者のシルエット",
        "prompt": (
            "Silhouette of a lone observer standing on a hilltop looking up at the night sky, "
            "watching a brilliant comet streak across the predawn sky. "
            "The comet leaves a glowing trail across the dark blue morning sky. "
            "Emotional and inspiring moment, cinematic composition, "
            "dramatic backlight, vertical 9:16 format, professional photography, "
            "sense of wonder and awe"
        )
    }
]

# meta.jsonを生成
meta_data = {
    "title": TITLE,
    "image_prompts": [scene["prompt"] for scene in SCENES],
    "descriptions": [scene["description"] for scene in SCENES]
}

# ファイルに保存
with open("meta.json", "w", encoding="utf-8") as f:
    json.dump(meta_data, f, indent=2, ensure_ascii=False)

print("✅ meta.json を作成しました！")
print(f"\n📋 タイトル: {TITLE}")
print(f"🎬 シーン数: {len(SCENES)}")
print("\n生成されるシーン:")
for i, scene in enumerate(SCENES, 1):
    print(f"\n{i}. {scene['description']}")
    print(f"   プロンプト: {scene['prompt'][:100]}...")

print("\n次のコマンドで画像を生成:")
print("python3 gcp_imagen_generator.py")
