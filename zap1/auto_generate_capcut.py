import os
import json
import glob

SCRIPT_DIR = "zap1/outputs/scripts"
OUTPUT_DIR = "zap1/outputs/capcut_projects"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_batches():
    return sorted(glob.glob(os.path.join(SCRIPT_DIR, "chapter_*.json")))

def make_capcut_project(chapter_json):
    """各章JSONからCapCutプロジェクトJSONを構築"""
    with open(chapter_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    cid = data["id"]
    title = data["title"]
    duration = data.get("duration_sec", 150)
    
    # Ensure image_dir exists and list files
    image_dir_path = data["output_paths"]["image_dir"]
    img_files = []
    if os.path.exists(image_dir_path):
        img_files = sorted([f for f in os.listdir(image_dir_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))])
    
    voice = data["output_paths"]["voice_path"]
    bgm = data["output_paths"].get("bgm_path")

    # 画像をタイムライン順に3枚配置
    image_clips = []
    # If no image files are found, create dummy clips to avoid division by zero or empty tracks
    if not img_files:
        # Create 3 dummy clips with a placeholder path
        segment = duration / 3
        for i in range(3):
            image_clips.append({
                "path": "placeholder_image.png", # Placeholder for missing images
                "start": i * segment,
                "duration": segment
            })
    else:
        segment = duration / len(img_files)
        for i, img in enumerate(img_files):
            image_clips.append({
                "path": os.path.join(image_dir_path, img).replace("\\\\", "/"), # Ensure forward slashes
                "start": i * segment,
                "duration": segment
            })

    # CapCut構造生成
    ccproj = {
        "version": "1.0.0",
        "tracks": [
            { "type": "video", "clips": image_clips },
            { "type": "audio", "clips": [
                { "path": voice.replace("\\\\", "/"), "start": 0 }, # Ensure forward slashes
                { "path": bgm.replace("\\\\", "/"), "start": 0 } # Ensure forward slashes
            ]},
            { "type": "text", "clips": [
                { "content": title, "start": 0.0, "duration": 3.0 }
            ]}
        ],
        "metadata": {
            "title": title,
            "chapter_id": cid,
            "resolution": "1920x1080",
            "fps": 30,
            "duration": duration
        }
    }

    return ccproj

def generate_all_capcut_projects():
    """全章分のCapCutプロジェクトを生成"""
    files = load_batches()
    for fpath in files:
        ccproj = make_capcut_project(fpath)
        out_name = os.path.basename(fpath).replace(".json", ".ccproj.json")
        out_path = os.path.join(OUTPUT_DIR, out_name)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(ccproj, f, ensure_ascii=False, indent=2)
        print(f"🎞 {out_name} 生成完了")

if __name__ == "__main__":
    generate_all_capcut_projects()
    print("\n✅ すべてのCapCutプロジェクト生成が完了しました！")
