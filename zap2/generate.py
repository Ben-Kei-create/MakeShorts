import os
import json
import base64
from typing import Iterable, List, Optional, Sequence, Tuple

import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

# config.py から設定を読み込み
try:
    from config import *  # noqa: F401,F403
except ImportError:
    print("❌ config.py が見つかりません")
    print("📝 セットアップ:")
    print("   1. cp config.example.py config.py")
    print("   2. config.py を編集してGCP情報を設定")
    exit(1)


def get_access_token() -> str:
    """GCPアクセストークンを取得"""
    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE,
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )
        credentials.refresh(Request())
        return credentials.token
    except FileNotFoundError:
        print(f"❌ {SERVICE_ACCOUNT_FILE} が見つかりません")
        print("📝 GCPサービスアカウントキーを配置してください")
        exit(1)
    except Exception as exc:  # pragma: no cover - runtime feedback only
        print(f"❌ 認証エラー: {exc}")
        exit(1)


def load_meta(meta_file: Optional[str] = None) -> Tuple[str, List[str]]:
    """meta.json からタイトルとプロンプト一覧を取得"""

    meta_file = meta_file or META_FILE

    if not os.path.exists(meta_file):
        raise FileNotFoundError(f"{meta_file} が見つかりません")

    with open(meta_file, "r", encoding="utf-8") as f:
        meta = json.load(f)

    title = meta.get("title", "untitled")
    prompts = meta.get("image_prompts", [])

    if not isinstance(prompts, Sequence) or not prompts:
        raise ValueError("image_prompts が含まれていません")

    return title, list(prompts)


def generate_images_from_prompts(
    prompts: Iterable[str],
    title: str,
    *,
    output_dir: str = OUTPUT_DIR,
    aspect_ratio: str = "9:16",
    sample_count: int = 1,
) -> int:
    """指定したプロンプト一覧から画像を生成して保存"""

    prompt_list = [prompt for prompt in prompts if prompt]
    if not prompt_list:
        raise ValueError("プロンプトが空です")

    os.makedirs(output_dir, exist_ok=True)

    print(f"\n{'=' * 70}")
    print(f"🎬 タイトル: {title}")
    print(f"🖼️  生成枚数: {len(prompt_list)} 枚")
    print(f"🧠 モデル: Imagen 3.0 (Vertex AI)")
    print(f"📍 プロジェクト: {PROJECT_ID}")
    print(f"{'=' * 70}\n")

    print("🔑 GCP認証中...")
    access_token = get_access_token()
    print("✅ 認証成功\n")

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    success_count = 0

    for index, prompt in enumerate(prompt_list, start=1):
        print(f"\n{'─' * 70}")
        print(f"🎨 Scene {index}/{len(prompt_list)} 生成中...")
        print(f"📝 プロンプト: {prompt[:100]}...")

        payload = {
            "instances": [{"prompt": prompt}],
            "parameters": {
                "sampleCount": sample_count,
                "aspectRatio": aspect_ratio,
            },
        }

        try:
            response = requests.post(ENDPOINT, headers=headers, json=payload, timeout=120)

            if response.status_code != 200:
                print(f"❌ エラー (Status {response.status_code}):")
                print(response.text[:200])
                continue

            data = response.json()
            image_data = data.get("predictions", [{}])[0].get("bytesBase64Encoded")

            if not image_data:
                print("⚠️  画像データが見つかりませんでした")
                continue

            filename = os.path.join(output_dir, f"{index:02d}_{title}.png")

            with open(filename, "wb") as file_obj:
                file_obj.write(base64.b64decode(image_data))

            print(f"✅ 保存完了: {filename}")
            success_count += 1

        except requests.exceptions.Timeout:
            print("⏱️  タイムアウト")
        except Exception as exc:  # pragma: no cover - runtime feedback only
            print(f"⚠️  エラー: {exc}")

    print(f"\n{'=' * 70}")
    print(f"🎉 完了！ {success_count}/{len(prompt_list)} 枚生成")
    print(f"📁 保存先: {os.path.abspath(output_dir)}")
    print(f"💰 概算コスト: ${success_count * 0.04:.2f} USD")
    print(f"{'=' * 70}\n")

    return success_count


def generate_images(meta_file: Optional[str] = None) -> int:
    """meta.json を読み込み、画像を生成"""

    meta_file = meta_file or META_FILE

    try:
        title, prompts = load_meta(meta_file)
    except FileNotFoundError:
        print(f"❌ {meta_file} が見つかりません")
        print("📝 create_meta.py を実行してプロンプトを作成してください")
        exit(1)
    except ValueError as exc:
        print(f"❌ {exc}")
        exit(1)

    return generate_images_from_prompts(prompts, title)


if __name__ == "__main__":
    generate_images()
