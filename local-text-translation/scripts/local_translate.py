#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path

import argostranslate.package
import ctranslate2
import sentencepiece as spm

SUPPORTED = {".txt", ".md", ".markdown", ".jsonl"}
FENCE_RE = re.compile(r"(^```.*?^```\s*$|^~~~.*?^~~~\s*$)", re.M | re.S)
PROTECT_RE = re.compile(r"(`[^`\n]+`|https?://[^\s)>\]]+|\]\([^)]*\))")


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=path.name, suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


class OfflineTranslator:
    def __init__(self, source: str, target: str):
        packages = argostranslate.package.get_installed_packages()
        package = next((p for p in packages if p.from_code == source and p.to_code == target), None)
        if package is None:
            raise SystemExit(f"Model {source}->{target} is not installed. Run setup.ps1 or setup.sh first.")
        root = Path(package.package_path)
        self.processor = spm.SentencePieceProcessor(model_file=str(root / "sentencepiece.model"))
        self.engine = ctranslate2.Translator(str(root / "model"), device="cpu")

    def translate_sentences(self, text: str) -> str:
        sentences = [s for s in re.split(r"(?<=[.!?。！？])\s+|(?<=;)\s+", text) if s]
        if not sentences:
            return text
        tokenized = [self.processor.encode(s, out_type=str) for s in sentences]
        results = self.engine.translate_batch(tokenized, beam_size=4)
        translated = [self.processor.decode(item.hypotheses[0]).replace("▁", "").strip()
                      for item in results]
        joiner = "" if any("\u4e00" <= ch <= "\u9fff" for ch in "".join(translated)) else " "
        return joiner.join(translated)


def cache_key(source: str, target: str, text: str) -> str:
    return hashlib.sha256(f"{source}\0{target}\0{text}".encode("utf-8")).hexdigest()


def translate_segment(text, translator, cache, cache_path, source, target):
    if not text.strip() or not re.search(r"[A-Za-z\u4e00-\u9fff]", text):
        return text
    key = cache_key(source, target, text)
    if key in cache:
        return cache[key]
    pieces = PROTECT_RE.split(text)
    translated = "".join(
        piece if PROTECT_RE.fullmatch(piece) else translator.translate_sentences(piece)
        for piece in pieces
    )
    cache[key] = translated
    atomic_json(cache_path, cache)
    return translated


def translate_markdown(text, translator, cache, cache_path, source, target):
    output = []
    for piece in FENCE_RE.split(text):
        if not piece:
            continue
        if piece.startswith("```") or piece.startswith("~~~"):
            output.append(piece)
            continue
        paragraphs = re.split(r"(\n\s*\n)", piece)
        output.extend(p if re.fullmatch(r"\n\s*\n", p) else
                      translate_segment(p, translator, cache, cache_path, source, target)
                      for p in paragraphs)
    return "".join(output)


def translate_jsonl(text, translator, cache, cache_path, source, target):
    lines = []
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            lines.append(line)
            continue
        value = json.loads(line)
        if isinstance(value, str):
            value = translate_segment(value, translator, cache, cache_path, source, target)
        elif isinstance(value, dict):
            for key in ("text", "content", "body"):
                if isinstance(value.get(key), str):
                    value[key] = translate_segment(value[key], translator, cache, cache_path, source, target)
        else:
            raise ValueError(f"Line {number}: expected a JSON string or object")
        lines.append(json.dumps(value, ensure_ascii=False))
    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")


def source_language_warnings(text: str, source: str, target: str) -> list[str]:
    warnings = []
    if source == "en" and target.startswith("zh"):
        for index, paragraph in enumerate(re.split(r"\n\s*\n", text), 1):
            letters = len(re.findall(r"[A-Za-z]", paragraph))
            han = len(re.findall(r"[\u4e00-\u9fff]", paragraph))
            if len(paragraph) >= 120 and letters > 80 and han < 5:
                warnings.append(f"paragraph {index}: long English passage remains")
    return warnings


def translate_file(input_path, output_path, translator, cache, cache_path, source, target):
    text = input_path.read_text(encoding="utf-8-sig")
    if input_path.suffix.lower() == ".jsonl":
        result = translate_jsonl(text, translator, cache, cache_path, source, target)
    elif input_path.suffix.lower() in {".md", ".markdown"}:
        result = translate_markdown(text, translator, cache, cache_path, source, target)
    else:
        parts = re.split(r"(\n\s*\n)", text)
        result = "".join(p if re.fullmatch(r"\n\s*\n", p) else
                         translate_segment(p, translator, cache, cache_path, source, target)
                         for p in parts)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result, encoding="utf-8", newline="\n")
    return source_language_warnings(result, source, target)


def main() -> None:
    parser = argparse.ArgumentParser(description="Offline, cached text translation with an installed Argos model.")
    parser.add_argument("input", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    parser.add_argument("--from", dest="source", default="en")
    parser.add_argument("--to", dest="target", default="zh")
    parser.add_argument("--cache", type=Path, default=Path(".translation-cache.json"))
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()

    if args.check_only:
        text = args.input.read_text(encoding="utf-8-sig")
        warnings = source_language_warnings(text, args.source, args.target)
        print("\n".join(warnings) if warnings else "No long untranslated passages detected.")
        raise SystemExit(1 if warnings else 0)
    if args.output is None:
        raise SystemExit("Specify --output; inputs are never overwritten by default.")

    cache = json.loads(args.cache.read_text(encoding="utf-8")) if args.cache.exists() else {}
    translator = OfflineTranslator(args.source, args.target)
    if args.input.is_file():
        files = [(args.input, args.output)]
    else:
        if not args.recursive:
            raise SystemExit("Directory input requires --recursive.")
        files = [(path, args.output / path.relative_to(args.input))
                 for path in args.input.rglob("*")
                 if path.is_file() and path.suffix.lower() in SUPPORTED]

    warning_count = 0
    for index, (source_path, output_path) in enumerate(files, 1):
        warnings = translate_file(source_path, output_path, translator, cache, args.cache, args.source, args.target)
        warning_count += len(warnings)
        print(f"[{index}/{len(files)}] {source_path} -> {output_path}")
        for warning in warnings:
            print(f"  WARNING: {warning}")
    print(f"Done: {len(files)} file(s), {warning_count} warning(s), cache={args.cache}")


if __name__ == "__main__":
    main()
