# 🎬 偉人シリーズ自動映像生成パイプライン

このプロジェクトは、テキスト入力からナレーション・画像・字幕を自動生成し、CapCutプロジェクト（.ccproj）として出力するフルオート映像制作システムです。YouTubeやショート動画向けに最適化されています。

✅ 特徴

✍️ Geminiで人物伝を自動生成

🖼 章ごとに静止画プロンプトを生成し、背景画像に適用

🗣 VOICEVOXでナレーション音声を自動生成

🎞 CapCut形式（.ccproj）でタイムライン構築済みプロジェクトを出力

🎧 BGM自動配置・クロスフェード・デュッキング処理

💬 字幕自動生成（スタイル付き）＋フェードイン/アウト演出

🎨 Ken Burns演出（感情レベルに応じて動作）

☀️ グレーディング効果（warm, cool など）

🖥 CapCut Pro のローカルプロジェクトフォルダに自動コピー

🚀 GUI自動操作によるMP4書き出し（PyAutoGUI）

📂 ディレクトリ構成（概要）
zap1/
├── images/                 # 生成画像
├── voice/                  # VOICEVOX音声
├── bgm/                    # BGMファイル群
├── outputs/
│   ├── subtitles/          # SRT字幕ファイル
│   ├── shotlist.csv        # CapCut用ショットリスト
│   ├── [person]_capcut.ccproj  # CapCutプロジェクトファイル
├── packages/
│   └── [person]/master.json    # Gemini生成の入力パッケージ

🚀 使い方（CLI）
1️⃣ 全自動生成コマンド
python3 make_all.py --package packages/tesla/master.json --export


--package：Gemini出力のmaster.json

--export：CapCutのGUI書き出しも自動で実行（任意）

2️⃣ 単章テスト生成（開発用）
python3 test_single_chapter.py --package packages/tesla/master.json --chapter 0 --grade warm --fade 0.6


特定章だけを生成し、効果の確認ができます

🎨 ビジュアル演出オプション
機能内容
Ken Burns動作emotion_levelに応じて自動決定（例：zoom-in, pan-leftなど）
字幕フェードfade=0.6 などで字幕のフェードイン/アウト時間指定
グレーディングgrade=warm, cool, bw, sunset などを指定して雰囲気演出
自動画像補完空スロットがある章はプレースホルダー画像で補完
🧠 拡張構想（今後）

 多言語展開（英語音声・字幕）

 モバイル表示向けのショート動画比率対応（9:16構成）

 SFX（効果音）の自動割り当て

 登場人物や時代背景のイラスト生成強化

 Geminiの連続会話による脚本構成支援

💡 CapCutで開く方法

出力された .ccproj は自動で下記フォルダにコピーされます：

~/Movies/CapCut/User Data/projects/


CapCutを開くと、ホーム画面に自動的にプロジェクトが表示されます。クリックして即編集開始可能。

🛠 前提・依存ライブラリ

Python 3.8+

pyautogui（自動操作用）

VOICEVOX（インストール＆ローカルAPI使用）

ffmpeg（音声整形）

CapCut（Pro版推奨、Mac/Windows）

🤝 コントリビュート歓迎

新しい偉人シリーズのmaster.json作成、新機能の追加、スタイル調整など、拡張のアイディアはいつでも大歓迎です！