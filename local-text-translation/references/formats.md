# Formats and routing

## Plain text

TXT is split on blank lines. Each non-empty paragraph is translated and cached independently.

## Markdown

Fenced code blocks, inline code, URLs, and Markdown link destinations are protected. Ordinary prose, headings, list text, and link labels are translated. Complex embedded HTML requires manual review.

## JSONL

Each line may be a JSON string or an object. For objects, string fields named `text`, `content`, or `body` are translated. Other fields remain unchanged.

## Directories

Use `--recursive`. The output mirrors the input tree and includes `.txt`, `.md`, `.markdown`, and `.jsonl` only.

## DOCX, EPUB, and PDF

Do not pass these binary formats directly. Extract structured text first, translate it, rebuild it with the appropriate document tool, and visually verify the rendered result. OCR scanned PDFs before translation.

