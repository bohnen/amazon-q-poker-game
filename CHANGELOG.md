# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2025-06-20

### Fixed
- **綴りの修正**: プロジェクト全体で "porker" を "poker" に修正
  - ディレクトリ名: `aws_porker` → `aws_poker`
  - パッケージ名: `aws-porker` → `aws-poker`
  - すべてのファイル内の参照を修正
- **絶対パスの修正**: ハードコードされた絶対パスを相対パスに変更
  - フォントファイルパス
  - サウンドディレクトリパス
  - CSVファイルパス
  - ランキングファイルパス
  - アイコンディレクトリパス

### Changed
- パッケージ構造の改善
  - 相対パスを使用することでポータビリティを向上
  - `os.path.join()` と `os.path.dirname()` を使用した適切なパス処理
- 必要なモジュールのインポート追加
  - 各ファイルに `import os` を追加

### Technical Details
- 修正されたファイル:
  - `pyproject.toml`
  - `aws_poker/__init__.py`
  - `aws_poker/poker_game.py`
  - `aws_poker/card.py`
  - `aws_poker/sound_manager.py`
  - `run_poker.py`
  - `run_game.py`
  - `run_aws_example.py`
  - `show_rankings.py`
  - `create_music.py`
  - `create_cards.py`
  - `create_architecture_cards.py`
  - `create_color_based_cards.py`
  - `analyze_cards.py`
  - `tests/test_game.py`
  - `tests/test_example.py`
  - `README.md`

### Verified
- ✅ ゲームの正常起動を確認
- ✅ 全モジュールのインポート成功
- ✅ デッキ作成（309枚のカード）正常動作
- ✅ ランキング機能正常動作

## [0.1.0] - 2025-06-18

### Added
- 初回リリース
- AWSアーキテクチャアイコンを使用したポーカーゲーム
- 309枚のAWSサービスアイコンカード
- 5つのスート（Green, Purple, Orange, Red, Blue）
- 25のAWSカテゴリ
- AWSスペシャル役システム
- 5ラウンド制ゲームプレイ
- ランキング機能
- サウンド機能（BGM・効果音）
- ゲームコード共有機能
