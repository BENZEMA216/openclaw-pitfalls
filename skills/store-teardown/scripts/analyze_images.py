#!/usr/bin/env python3
"""Analyze store screenshots and extract a structured design brief.

This script processes a directory of store screenshots/product images,
extracts dominant colors via KMeans clustering, and optionally calls
the Gemini multimodal API for deeper visual analysis. The result is
a structured YAML design brief.

Usage:
    uv run scripts/analyze_images.py \
        --input /tmp/store-teardown/screenshots \
        --output /tmp/store-teardown/color_analysis.yaml

Dependencies (managed via inline script metadata for uv):
    pillow, scikit-learn, pyyaml, numpy, requests
"""
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pillow>=10.0",
#     "scikit-learn>=1.3",
#     "pyyaml>=6.0",
#     "numpy>=1.24",
#     "requests>=2.31",
# ]
# ///

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import yaml
from PIL import Image
from sklearn.cluster import KMeans


# ---------------------------------------------------------------------------
# Color utilities
# ---------------------------------------------------------------------------

def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB tuple to hex string."""
    return f"#{r:02X}{g:02X}{b:02X}"


def hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
    """Convert hex string to RGB tuple."""
    hex_str = hex_str.lstrip("#")
    return int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16)


def color_distance(c1: tuple[int, ...], c2: tuple[int, ...]) -> float:
    """Euclidean distance between two RGB colors."""
    return float(np.sqrt(sum((a - b) ** 2 for a, b in zip(c1, c2))))


def approximate_color_name(r: int, g: int, b: int) -> str:
    """Return a rough Chinese color name for a given RGB value."""
    named_colors: dict[str, tuple[int, int, int]] = {
        "纯白": (255, 255, 255),
        "纯黑": (0, 0, 0),
        "正红": (255, 0, 0),
        "深红": (139, 0, 0),
        "玫红": (255, 0, 127),
        "粉红": (255, 182, 193),
        "橙色": (255, 165, 0),
        "橙红": (255, 69, 0),
        "金色": (255, 215, 0),
        "黄色": (255, 255, 0),
        "柠檬黄": (255, 247, 0),
        "浅黄": (255, 255, 224),
        "草绿": (124, 252, 0),
        "深绿": (0, 100, 0),
        "翠绿": (0, 201, 87),
        "墨绿": (0, 64, 0),
        "天蓝": (135, 206, 235),
        "宝蓝": (0, 0, 205),
        "深蓝": (0, 0, 139),
        "藏蓝": (0, 0, 80),
        "浅蓝": (173, 216, 230),
        "紫色": (128, 0, 128),
        "薰衣草紫": (230, 230, 250),
        "深紫": (75, 0, 130),
        "灰白": (245, 245, 245),
        "浅灰": (211, 211, 211),
        "中灰": (169, 169, 169),
        "深灰": (105, 105, 105),
        "米白": (255, 248, 231),
        "米色": (245, 245, 220),
        "棕色": (139, 69, 19),
        "卡其": (195, 176, 145),
        "驼色": (193, 154, 107),
        "珊瑚": (255, 127, 80),
        "青色": (0, 255, 255),
        "藏青": (0, 47, 73),
    }
    min_dist = float("inf")
    closest = "未知"
    for name, (nr, ng, nb) in named_colors.items():
        d = color_distance((r, g, b), (nr, ng, nb))
        if d < min_dist:
            min_dist = d
            closest = name
    return closest


def classify_scheme(colors: list[dict[str, Any]]) -> str:
    """Classify the overall color scheme as warm / cool / neutral / contrast."""
    if not colors:
        return "中性"

    warm_score = 0
    cool_score = 0
    neutral_score = 0
    total_weight = 0

    for c in colors:
        r, g, b = hex_to_rgb(c["hex"])
        pct = c.get("percentage", 1)
        total_weight += pct

        # Hue-based classification
        h, s, v = _rgb_to_hsv(r, g, b)

        if s < 0.10:
            neutral_score += pct
        elif h < 60 or h > 300:
            warm_score += pct
        elif 60 <= h <= 180:
            cool_score += pct  # Note: 60-180 includes yellow-green to cyan
        else:
            cool_score += pct

    if total_weight == 0:
        return "中性"

    warm_ratio = warm_score / total_weight
    cool_ratio = cool_score / total_weight
    neutral_ratio = neutral_score / total_weight

    if neutral_ratio > 0.6:
        return "中性"
    if warm_ratio > 0.15 and cool_ratio > 0.15:
        return "撞色"
    if warm_ratio > cool_ratio:
        return "暖色调"
    return "冷色调"


def _rgb_to_hsv(r: int, g: int, b: int) -> tuple[float, float, float]:
    """Convert RGB (0-255) to HSV (H: 0-360, S: 0-1, V: 0-1)."""
    r_n, g_n, b_n = r / 255.0, g / 255.0, b / 255.0
    c_max = max(r_n, g_n, b_n)
    c_min = min(r_n, g_n, b_n)
    delta = c_max - c_min

    # Hue
    if delta == 0:
        h = 0.0
    elif c_max == r_n:
        h = 60.0 * (((g_n - b_n) / delta) % 6)
    elif c_max == g_n:
        h = 60.0 * (((b_n - r_n) / delta) + 2)
    else:
        h = 60.0 * (((r_n - g_n) / delta) + 4)

    # Saturation
    s = 0.0 if c_max == 0 else delta / c_max

    # Value
    v = c_max

    return h, s, v


# ---------------------------------------------------------------------------
# Image analysis
# ---------------------------------------------------------------------------

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"}


def load_images(input_dir: Path) -> list[Path]:
    """Find all supported image files in the input directory."""
    images: list[Path] = []
    for f in sorted(input_dir.iterdir()):
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS:
            images.append(f)
    return images


def extract_dominant_colors(
    image_paths: list[Path],
    n_colors: int = 8,
    sample_size: int = 50_000,
    merge_threshold: float = 25.0,
) -> list[dict[str, Any]]:
    """Extract dominant colors from a set of images using KMeans clustering.

    Args:
        image_paths: List of image file paths.
        n_colors: Number of color clusters for KMeans.
        sample_size: Max number of pixels to sample (for performance).
        merge_threshold: Euclidean distance below which clusters are merged.

    Returns:
        Sorted list of dicts with hex, name, percentage, rgb keys.
    """
    all_pixels: list[np.ndarray] = []

    for path in image_paths:
        try:
            img = Image.open(path).convert("RGB")
        except Exception as e:
            print(f"  [WARN] Cannot open {path.name}: {e}", file=sys.stderr)
            continue

        # Resize large images for speed
        max_dim = 600
        if max(img.size) > max_dim:
            img.thumbnail((max_dim, max_dim), Image.LANCZOS)

        pixels = np.array(img).reshape(-1, 3)
        all_pixels.append(pixels)

    if not all_pixels:
        return []

    combined = np.vstack(all_pixels)

    # Random sampling if too many pixels
    if len(combined) > sample_size:
        rng = np.random.default_rng(42)
        indices = rng.choice(len(combined), size=sample_size, replace=False)
        combined = combined[indices]

    # KMeans clustering
    kmeans = KMeans(n_clusters=min(n_colors, len(combined)), random_state=42, n_init=10)
    labels = kmeans.fit_predict(combined)
    centers = kmeans.cluster_centers_.astype(int)

    # Count pixels per cluster
    counts = Counter(labels)
    total = sum(counts.values())

    raw_colors = []
    for idx in range(len(centers)):
        r, g, b = int(centers[idx][0]), int(centers[idx][1]), int(centers[idx][2])
        pct = round(counts[idx] / total * 100, 1)
        raw_colors.append({
            "hex": rgb_to_hex(r, g, b),
            "rgb": [r, g, b],
            "name": approximate_color_name(r, g, b),
            "percentage": pct,
        })

    # Merge very similar colors
    merged: list[dict[str, Any]] = []
    used = set()
    raw_colors.sort(key=lambda c: c["percentage"], reverse=True)
    for i, c in enumerate(raw_colors):
        if i in used:
            continue
        group_pct = c["percentage"]
        for j in range(i + 1, len(raw_colors)):
            if j in used:
                continue
            dist = color_distance(tuple(c["rgb"]), tuple(raw_colors[j]["rgb"]))
            if dist < merge_threshold:
                group_pct += raw_colors[j]["percentage"]
                used.add(j)
        merged.append({
            "hex": c["hex"],
            "rgb": c["rgb"],
            "name": c["name"],
            "percentage": round(group_pct, 1),
        })

    merged.sort(key=lambda c: c["percentage"], reverse=True)
    return merged


def image_to_base64(path: Path, max_dim: int = 1024) -> str:
    """Encode an image as base64 JPEG for API calls."""
    img = Image.open(path).convert("RGB")
    if max(img.size) > max_dim:
        img.thumbnail((max_dim, max_dim), Image.LANCZOS)

    import io
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


# ---------------------------------------------------------------------------
# Gemini API integration (optional)
# ---------------------------------------------------------------------------

def call_gemini_vision(
    image_paths: list[Path],
    prompt: str,
    api_key: str,
    model: str = "gemini-3-pro-preview",
) -> str | None:
    """Call Gemini multimodal API with images and a text prompt.

    Returns the model's text response, or None on failure.
    """
    import requests

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    parts: list[dict[str, Any]] = []

    # Add images (up to 5 to stay within limits)
    for img_path in image_paths[:5]:
        try:
            b64 = image_to_base64(img_path)
            parts.append({
                "inline_data": {
                    "mime_type": "image/jpeg",
                    "data": b64,
                }
            })
        except Exception as e:
            print(f"  [WARN] Skipping {img_path.name} for Gemini: {e}", file=sys.stderr)

    # Add text prompt
    parts.append({"text": prompt})

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 4096,
        },
    }

    headers = {"Content-Type": "application/json"}

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        candidates = data.get("candidates", [])
        if candidates:
            content = candidates[0].get("content", {})
            text_parts = [p.get("text", "") for p in content.get("parts", [])]
            return "\n".join(text_parts)
    except Exception as e:
        print(f"  [WARN] Gemini API call failed: {e}", file=sys.stderr)

    return None


GEMINI_ANALYSIS_PROMPT = """\
你是一位资深的电商视觉设计分析师。请仔细分析这些电商店铺截图，提取以下设计要素。

请严格使用以下 YAML 格式输出（不要加 ```yaml 代码块标记，直接输出纯 YAML）：

color_impression:
  primary: "主色调描述及近似 HEX"
  secondary: "辅助色描述及近似 HEX"
  accent: "强调色描述及近似 HEX"
  scheme_type: "暖色调 | 冷色调 | 中性 | 撞色"
  mood: "奢华 | 清新 | 活泼 | 硬朗 | 甜美 | 专业"

typography:
  layout_pattern: "grid_3col | grid_2col | waterfall | list | mixed"
  spacing: "tight | normal | loose"
  card_style: "rounded_shadow | rounded_flat | square_shadow | square_flat"
  heading_style: "bold_gothic | thin_serif | handwritten | decorative"
  font_family_guess: "字体猜测"

image_style:
  photography: "studio | lifestyle | street | flatlay | mixed"
  background: "pure_white | light_gray | gradient | scene | cutout"
  lighting: "natural | soft_studio | hard | backlit | post_processed"
  post_processing: "high_saturation | low_saturation | vintage | japanese_fresh | raw"
  model_usage: "full_body | half_body | closeup | no_model"
  aspect_ratio: "1:1 | 3:4 | 16:9 | mixed"

overall:
  brand_positioning: "luxury | affordable_luxury | mass | fast_fashion | designer | guochao | value"
  target_audience: "年龄段和性别倾向"
  design_maturity: 7
  style_keywords:
    - "关键词1"
    - "关键词2"
    - "关键词3"
  top_strength: "最突出的设计优点"
  improvement_area: "最明显的改进空间"
"""


# ---------------------------------------------------------------------------
# Output builder
# ---------------------------------------------------------------------------

def build_design_brief(
    colors: list[dict[str, Any]],
    image_count: int,
    gemini_analysis: dict[str, Any] | None,
    input_dir: Path,
) -> dict[str, Any]:
    """Assemble the final design brief dictionary."""

    # Prepare quantized color list (top 8, without rgb arrays for cleaner YAML)
    quantized = []
    for c in colors[:8]:
        quantized.append({
            "hex": c["hex"],
            "name": c["name"],
            "percentage": c["percentage"],
        })

    scheme_type = classify_scheme(colors[:5])

    brief: dict[str, Any] = {
        "store_teardown": {
            "meta": {
                "analyzed_at": datetime.now(timezone.utc).isoformat(),
                "analyzed_by": "openclaw/store-teardown",
                "source_directory": str(input_dir.resolve()),
                "images_analyzed": image_count,
            },
            "color_palette": {
                "quantized_top_colors": quantized,
                "scheme_type": scheme_type,
            },
        }
    }

    # Merge Gemini analysis if available
    if gemini_analysis:
        teardown = brief["store_teardown"]

        if "color_impression" in gemini_analysis:
            teardown["color_palette"]["ai_impression"] = gemini_analysis["color_impression"]

        if "typography" in gemini_analysis:
            teardown["typography"] = gemini_analysis["typography"]

        if "image_style" in gemini_analysis:
            teardown["image_style"] = gemini_analysis["image_style"]

        if "overall" in gemini_analysis:
            teardown["overall_assessment"] = gemini_analysis["overall"]

    # Add screenshot file list
    brief["store_teardown"]["raw_data"] = {
        "source_directory": str(input_dir.resolve()),
        "images_analyzed": image_count,
    }

    return brief


def parse_gemini_yaml(text: str) -> dict[str, Any] | None:
    """Try to parse YAML from Gemini's response text."""
    # Strip markdown code fences if present
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        # Remove first and last lines (``` markers)
        lines = [l for l in lines if not l.strip().startswith("```")]
        cleaned = "\n".join(lines)

    try:
        return yaml.safe_load(cleaned)
    except yaml.YAMLError:
        # Try to find YAML block within the text
        for marker in ["color_impression:", "typography:", "image_style:", "overall:"]:
            idx = cleaned.find(marker)
            if idx >= 0:
                try:
                    return yaml.safe_load(cleaned[idx:])
                except yaml.YAMLError:
                    continue
    return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze store screenshots and extract a structured design brief."
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Directory containing screenshots/images to analyze.",
    )
    parser.add_argument(
        "--output", "-o",
        default="/tmp/store-teardown/color_analysis.yaml",
        help="Path for the output YAML design brief (default: /tmp/store-teardown/color_analysis.yaml).",
    )
    parser.add_argument(
        "--colors", "-c",
        type=int,
        default=8,
        help="Number of dominant colors to extract (default: 8).",
    )
    parser.add_argument(
        "--no-gemini",
        action="store_true",
        help="Skip Gemini API analysis (only do local color extraction).",
    )
    parser.add_argument(
        "--gemini-model",
        default="gemini-3-pro-preview",
        help="Gemini model to use for visual analysis (default: gemini-3-pro-preview).",
    )

    args = parser.parse_args()

    input_dir = Path(args.input)
    output_path = Path(args.output)

    if not input_dir.is_dir():
        print(f"[ERROR] Input directory does not exist: {input_dir}", file=sys.stderr)
        sys.exit(1)

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # --- Step 1: Find images ---
    print(f"[1/4] Scanning images in {input_dir} ...")
    image_paths = load_images(input_dir)
    if not image_paths:
        print(f"[ERROR] No supported images found in {input_dir}", file=sys.stderr)
        print(f"       Supported formats: {', '.join(sorted(SUPPORTED_EXTENSIONS))}")
        sys.exit(1)
    print(f"       Found {len(image_paths)} image(s):")
    for p in image_paths:
        print(f"         - {p.name}")

    # --- Step 2: Extract dominant colors ---
    print(f"\n[2/4] Extracting dominant colors (k={args.colors}) ...")
    colors = extract_dominant_colors(image_paths, n_colors=args.colors)
    print("       Top colors:")
    for c in colors[:6]:
        print(f"         {c['hex']}  {c['name']:6s}  {c['percentage']:5.1f}%")

    # --- Step 3: Gemini visual analysis (optional) ---
    gemini_result: dict[str, Any] | None = None

    if not args.no_gemini:
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if api_key:
            print(f"\n[3/4] Calling Gemini ({args.gemini_model}) for visual analysis ...")
            raw_response = call_gemini_vision(
                image_paths,
                GEMINI_ANALYSIS_PROMPT,
                api_key,
                model=args.gemini_model,
            )
            if raw_response:
                gemini_result = parse_gemini_yaml(raw_response)
                if gemini_result:
                    print("       Gemini analysis parsed successfully.")
                else:
                    print("  [WARN] Could not parse Gemini response as YAML.", file=sys.stderr)
                    print("         Raw response saved to output for reference.", file=sys.stderr)
                    # Store raw text as fallback
                    gemini_result = {"_raw_response": raw_response}
            else:
                print("  [WARN] No response from Gemini API.", file=sys.stderr)
        else:
            print(
                "\n[3/4] Skipping Gemini analysis (GEMINI_API_KEY not set).\n"
                "       Set GEMINI_API_KEY environment variable to enable AI visual analysis."
            )
    else:
        print("\n[3/4] Skipping Gemini analysis (--no-gemini flag).")

    # --- Step 4: Build and save design brief ---
    print(f"\n[4/4] Building design brief ...")
    brief = build_design_brief(
        colors=colors,
        image_count=len(image_paths),
        gemini_analysis=gemini_result,
        input_dir=input_dir,
    )

    # Custom YAML representer to avoid anchors/aliases and ensure clean output
    class CleanDumper(yaml.SafeDumper):
        pass

    def str_representer(dumper: yaml.Dumper, data: str) -> Any:
        if "\n" in data:
            return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
        return dumper.represent_scalar("tag:yaml.org,2002:str", data)

    CleanDumper.add_representer(str, str_representer)

    yaml_content = yaml.dump(
        brief,
        Dumper=CleanDumper,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
        width=120,
    )

    output_path.write_text(yaml_content, encoding="utf-8")
    print(f"\n       Design brief saved to: {output_path.resolve()}")
    print("       Done.")


if __name__ == "__main__":
    main()
