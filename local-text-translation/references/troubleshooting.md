# Troubleshooting

## Model not installed

Run `setup.ps1` or `setup.sh`. Setup requires internet access; normal translation does not.

## Setup cannot find a model

Check the Argos package index for the exact language codes. Chinese is commonly `zh`, not `zh-CN`.

## Translation tries to access the network

Use the bundled `local_translate.py`. It loads CTranslate2 and SentencePiece files directly, avoiding runtime sentence-boundary downloads.

## Interrupted job

Run the same command with the same `--cache` path. Completed segments are reused.

## English remains in Chinese output

Run `--check-only`. Proper nouns, citations, and bibliography entries may be legitimate; long prose passages should be retranslated or reviewed.

## Poor segmentation

Insert blank lines between logical paragraphs. For structured documents, extract at heading/paragraph granularity rather than translating a whole book as one string.

