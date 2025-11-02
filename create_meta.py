import json

def create_meta_interactive():
    \"\"\"対話形式でmeta.jsonを作成\"\"\"
    
    print("\\n" + "="*70)
    print("🎬 meta.json 作成ツール")
    print("="*70)
    
    # タイトル入力
    print("\\n📝 プロジェクトタイトルを入力してください:")
    title = input(">>> ").strip()
    if not title:
        title = "Untitled Project"
    
    # シーン数入力
    while True:
        try:
            print("\\n🎞️  生成するシーン数を入力してください (1-10):")
            num_scenes = int(input(">>> "))
            if 1 <= num_scenes <= 10:
                break
            print("❌ 1〜10の数字を入力してください")
        except ValueError:
            print("❌ 数字を入力してください")
    
    # プロンプト入力
    prompts = []
    descriptions = []
    
    print("\\n" + "-"*70)
    print("各シーンのプロンプトを入力してください（英語推奨）")
    print("例: A beautiful sunset over mountains")
    print("-"*70)
    
    for i in range(num_scenes):
        print(f"\\n🎬 Scene {i+1}:")
        
        desc = input("  日本語説明 (オプション): ").strip()
        prompt = input("  英語プロンプト (必須): ").strip()
        
        if not prompt:
            print("  ⚠️  プロンプトが空です。スキップします")
            continue
        
        # プロンプトを自動拡張
        enhanced_prompt = (
            f"{prompt}, "
            f"cinematic lighting, ultra realistic, highly detailed, "
            f"professional photography, 8K resolution, dramatic composition, "
            f"vertical 9:16 format"
        )
        
        descriptions.append(desc if desc else prompt)
        prompts.append(enhanced_prompt)
    
    if not prompts:
        print("\\n❌ プロンプトが1つも入力されませんでした")
        return
    
    # meta.json生成
    meta = {
        "title": title,
        "image_prompts": prompts,
        "descriptions": descriptions
    }
    
    # 保存
    with open("meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    
    # 完了メッセージ
    print("\\n" + "="*70)
    print("✅ meta.json を作成しました！")
    print("="*70)
    print(f"\\n📋 タイトル: {title}")
    print(f"🎬 シーン数: {len(prompts)}")
    print("\\n生成されるシーン:")
    for i, (desc, prompt) in enumerate(zip(descriptions, prompts), 1):
        print(f"\\n  {i}. {desc}")
        print(f"     {prompt[:80]}...")
    
    print("\\n" + "="*70)
    print("次のコマンドで画像を生成:")
    print("  python3 generate.py")
    print("="*70 + "\\n")

if __name__ == "__main__":
    create_meta_interactive()