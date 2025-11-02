"""Comprehensive automation pipeline for vertical documentary shorts."""

from __future__ import annotations

import argparse
import json
import os
import re
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv


def _load_private_api_config() -> Dict[str, Any]:
    """Read optional API configuration from `private_settings.py`."""

    try:
        from private_settings import API_CONFIG  # type: ignore
    except ImportError:
        return {}

    if not isinstance(API_CONFIG, dict):  # pragma: no cover - defensive guard
        raise TypeError("API_CONFIG must be a dictionary in private_settings.py")

    return {key: value for key, value in API_CONFIG.items() if value not in (None, "")}

try:  # pragma: no cover - optional dependency
    from openai import OpenAI
except ImportError:  # pragma: no cover - runtime guard
    OpenAI = None  # type: ignore

PROMPT_TEMPLATE = textwrap.dedent(
    """
    You are a historian and documentary showrunner who blends the suspenseful narrative tones of
    Stephen King, Jordan Peele, Christopher Nolan, and Stanley Kubrick. Create a COMPLETE vertical
    short-film content package about {person_name}. All facts must be historically accurate.

    Return your answer as minified JSON with the following schema:
    {{
      "music_prompt": "single prompt string for an original soundtrack",
      "thumbnail_prompts": [
        {{
          "id": 1,
          "scene_focus": "brief Japanese description of what the frame captures",
          "prompt": "full English prompt meeting the art-direction rules"
        }},
        ... exactly 30 entries total ...
      ],
      "motion_prompts": [
        {{"id": 1, "scene_focus": "chapter or beat", "prompt": "cinematic motion prompt"}},
        ... at least 10 entries ...
      ],
      "script": {{
        "sections": [
          {{
            "title": "オープニング" or "第1章" etc,
            "time_range": "0:00-1:30" format,
            "emotion_level": 1-10 integer,
            "visual_directions": "具体的な映像指示 (Japanese)",
            "narration": "1100 Japanese characters per section, with line breaks, quotes for citations",
            "data_points": ["YYYY年MM月DD日", "金額", ... at least two concrete items],
            "lesson": "各章の教訓"
          }} (Opening + 10 chapters + Ending in chronological order)
        ]
      }},
      "supplement": {{
        "historical_background": "detailed Japanese summary",
        "references": ["primary or secondary sources with publication details"],
        "controversies": ["慎重な表現の論点"],
        "visual_assets": {{
          "chapter_recommendations": ["list describing suggested visuals"],
          "color_grading": "ディズニー風のカラーグレーディング指示"
        }}
      }},
      "seo": {{
        "titles": ["感情訴求型", "検索型", "クリックベイト"],
        "description": "500 Japanese characters structured with hook, overview, CTA",
        "tags": ["20 Japanese tags"],
        "chapters": [{{"label": "第1章", "timestamp": "01:30"}}],
        "thumbnail_advice": "視覚的多様性と選定理由"
      }},
      "quality_checklist": ["確認事項と達成状況を日本語で明記"]
    }}

    Thumbnail prompt requirements:
      * Must be vertical 9:16.
      * Include age, facial expression, historically accurate wardrobe and setting.
      * Include the keyword "Dynamic".
      * Include lighting directions (Rembrandt, golden hour, spotlight, etc.).
      * Add emotional or symbolic meaning.
      * Ensure copyright-safe Disney-inspired style.
      * Provide three prompts per chapter (including opening) for a total of 30.
      * Provide at least one motion prompt per chapter as cinematic camera guidance.

    Script requirements:
      * Opening 90s, Chapters 1-9 150s each, Chapter 10 180s, Ending 180s. Provide explicit time_range.
      * Narration speed: 300-400 Japanese characters per minute, target ~1100 characters per section.
      * Include concrete dates, figures, names, places, and cited quotes ("...").
      * Follow emotional curve: Chapter1=3-4, Chapter2=5-6, Chapter3=7-8, Chapter4=6-5, Chapter5=4-3,
        Chapter6=7-8, Chapter7=5-4, Chapter8=3-2, Chapter9=2-1, Chapter10=4-6, Ending close with hope.
      * Close each section with a lesson or insight.

    SEO requirements: include CTA for channel subscription, teaser for next figure, mention Disney style.
    References: cite sources in Japanese, specify if "伝えられている" when uncertain.

    Keep JSON valid. Do not wrap in markdown fences. Use escaped newlines (\n) inside narration strings.
    """
)


@dataclass
class GenerationResult:
    """Container for the generated package data."""

    person_name: str
    raw_text: str
    data: Dict[str, Any]
    package_dir: Path
    meta_path: Path
    response_path: Path


class TextModelClient:
    """Wrapper around the OpenAI Responses API with environment-based configuration."""

    def __init__(
        self,
        *,
        model: Optional[str] = None,
        temperature: float = 0.2,
    ) -> None:
        load_dotenv()
        private_config = _load_private_api_config()

        self.api_key = (
            private_config.get("openai_api_key")
            or os.getenv("OPENAI_API_KEY")
            or os.getenv("GENAI_API_KEY")
        )
        self.base_url = private_config.get(
            "openai_base_url", os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        )
        self.model = (
            model
            or private_config.get("openai_model")
            or os.getenv("OPENAI_MODEL")
            or "gpt-4.1"
        )

        private_temp = private_config.get("openai_temperature")
        self.temperature = float(private_temp) if private_temp is not None else temperature

        if OpenAI is None:
            raise RuntimeError("openai パッケージがインストールされていません。requirements.txt を確認してください。")
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY (または GENAI_API_KEY) が環境変数に設定されていません。")

        self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def generate_package(self, prompt: str) -> str:
        response = self._client.responses.create(
            model=self.model,
            temperature=self.temperature,
            input=prompt,
        )
        return response.output_text  # type: ignore[no-any-return]


class ShortsPackageGenerator:
    """Create story + image prompts + marketing assets for a vertical short."""

    def __init__(
        self,
        llm_client: TextModelClient,
        *,
        output_root: Path = Path("packages"),
    ) -> None:
        self.llm_client = llm_client
        self.output_root = output_root
        self.output_root.mkdir(exist_ok=True)

    def build_prompt(self, person_name: str) -> str:
        return PROMPT_TEMPLATE.format(person_name=person_name)

    def generate(self, person_name: str, *, auto_images: bool = False) -> GenerationResult:
        prompt = self.build_prompt(person_name)
        raw = self.llm_client.generate_package(prompt)
        data = self._parse_json(raw)

        package_dir = self._prepare_directory(person_name)
        response_path = package_dir / "raw_response.txt"
        response_path.write_text(raw, encoding="utf-8")

        json_path = package_dir / "shorts_package.json"
        json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

        meta_path = self._write_meta(package_dir, person_name, data)

        if auto_images:
            self._generate_images(data, meta_path)

        return GenerationResult(
            person_name=person_name,
            raw_text=raw,
            data=data,
            package_dir=package_dir,
            meta_path=meta_path,
            response_path=response_path,
        )

    def _parse_json(self, raw: str) -> Dict[str, Any]:
        raw = raw.strip()
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            json_candidate = self._extract_json_block(raw)
            if not json_candidate:
                raise
            return json.loads(json_candidate)

    @staticmethod
    def _extract_json_block(text: str) -> Optional[str]:
        match = re.search(r"\{.*\}\s*$", text, re.DOTALL)
        if match:
            return match.group(0)
        code_blocks = re.findall(r"```json\s*(\{.*?\})```", text, re.DOTALL)
        if code_blocks:
            return code_blocks[-1]
        return None

    def _prepare_directory(self, person_name: str) -> Path:
        slug = self._slugify(person_name)
        package_dir = self.output_root / slug
        package_dir.mkdir(parents=True, exist_ok=True)
        return package_dir

    @staticmethod
    def _slugify(value: str) -> str:
        value = value.strip().lower()
        value = re.sub(r"[^a-z0-9]+", "-", value)
        value = re.sub(r"-+", "-", value).strip("-")
        return value or "short"

    def _write_meta(self, package_dir: Path, person_name: str, data: Dict[str, Any]) -> Path:
        prompts = [entry.get("prompt", "") for entry in data.get("thumbnail_prompts", [])]
        prompts = [p for p in prompts if p]

        meta = {
            "title": f"{person_name} Documentary Thumbnails",
            "image_prompts": prompts,
            "descriptions": [entry.get("scene_focus", "") for entry in data.get("thumbnail_prompts", [])],
        }

        meta_path = package_dir / "meta.json"
        meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        return meta_path

    def _generate_images(self, data: Dict[str, Any], meta_path: Path) -> None:
        prompts = [entry.get("prompt", "") for entry in data.get("thumbnail_prompts", []) if entry.get("prompt")]
        if not prompts:
            return

        try:
            from config import OUTPUT_DIR as CONFIG_OUTPUT_DIR  # type: ignore
            from generate import generate_images_from_prompts
        except Exception as exc:  # pragma: no cover - runtime guard
            raise RuntimeError("画像生成モジュールを読み込めませんでした。config.py の設定を確認してください。") from exc

        output_dir = os.getenv("VERTICAL_IMAGE_OUTPUT", CONFIG_OUTPUT_DIR)
        title = data.get("seo", {}).get("titles", ["short"])[0]
        generate_images_from_prompts(prompts, title or "short", output_dir=output_dir)


def run_cli() -> None:
    parser = argparse.ArgumentParser(description="Generate a complete documentary shorts package.")
    parser.add_argument("person", help="著名人の名前")
    parser.add_argument(
        "--auto-images",
        action="store_true",
        help="Vertex AI を用いてサムネイル画像を自動生成",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="使用するテキスト生成モデル (環境変数が優先)",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.2,
        help="テキスト生成のtemperature",
    )

    args = parser.parse_args()

    client = TextModelClient(model=args.model, temperature=args.temperature)
    generator = ShortsPackageGenerator(client)
    result = generator.generate(args.person, auto_images=args.auto_images)

    print("\n=== 生成結果 ===")
    print(f"人物名: {result.person_name}")
    print(f"出力フォルダ: {result.package_dir}")
    print(f"meta.json: {result.meta_path}")
    print(f"生レスポンス: {result.response_path}")


if __name__ == "__main__":
    run_cli()
