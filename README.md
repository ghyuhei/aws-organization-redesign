# AWS Organization 再設計ガイド

新しい組織の OU・ポリシー設計と、既存のアカウントを止めずに移す手順（HTML）。

- `aws-organization-redesign.html`：本文（生成物）
- `diagrams/`：図（`.drawio` と `.drawio.svg`）
- `src/`：本文の元（`body.html`・`sources.json`）と、組み立て・検査のスクリプト

更新は `src/body.html` を編集してから、次を実行する。

```
python3 src/build.py && python3 src/check.py
```
