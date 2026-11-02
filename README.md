# Local Translation / 本地文本翻译

一个可供用户或 AI Agent 一键部署的离线文本翻译技能。模型安装完成后，正文不会发送到任何在线翻译服务。

主要特性：

- 基于 Argos Translate、CTranslate2 与 SentencePiece，本地 CPU 运行；
- 支持 TXT、Markdown、JSONL 与递归目录；
- 分段缓存、原子写入，可中断后继续；
- 保护 Markdown 代码块、行内代码、URL 和链接地址；
- 英译中漏译检测；
- 自带 Codex/Agent Skill，可复制到技能目录直接加载。

## 一键安装

Windows PowerShell：

```powershell
git clone https://github.com/lsgoodlionel/-Local-translation.git Local-translation
cd Local-translation
.\setup.ps1 -From en -To zh
```

macOS/Linux：

```bash
git clone https://github.com/lsgoodlionel/-Local-translation.git Local-translation
cd Local-translation
chmod +x setup.sh
./setup.sh en zh
```

安装阶段需要联网下载依赖和语言模型；完成后可断网翻译。

## 使用

Windows：

```powershell
.\.venv\Scripts\python.exe .\local-text-translation\scripts\local_translate.py input.md -o output.zh.md --from en --to zh --cache .translation-cache.json
```

macOS/Linux：

```bash
.venv/bin/python local-text-translation/scripts/local_translate.py input.md -o output.zh.md --from en --to zh --cache .translation-cache.json
```

翻译目录：

```bash
.venv/bin/python local-text-translation/scripts/local_translate.py ./input -o ./translated --recursive --from en --to zh
```

只检查是否存在大段漏译：

```bash
.venv/bin/python local-text-translation/scripts/local_translate.py output.zh.md --check-only --from en --to zh
```

## 加载为 Codex Skill

将 `local-text-translation` 文件夹复制到：

```text
~/.codex/skills/local-text-translation/
```

重新加载后使用 `$local-text-translation` 调用。其他支持 `SKILL.md` 的 Agent 也可直接读取该目录。

## 隐私说明

安装脚本会联网安装依赖和模型；翻译脚本只读取本地模型与文件，不调用网络翻译 API。源文件默认不会被覆盖。

## License

MIT。语言模型本身遵循其各自许可证。

