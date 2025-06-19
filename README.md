# AWS Porker

AWSアーキテクチャアイコンを使ったポーカーゲーム！309枚のAWSサービスアイコンをトランプカードとして使用し、独自のスコアリングシステムでポーカーを楽しめます。

## 🎮 ゲームの特徴

- **309枚のAWSアーキテクチャアイコンカード**: 実際のAWSアーキテクチャアイコンを使用
- **5つのスート**: アイコンの実際の色に基づく分類（Green, Purple, Orange, Red, Blue）
- **色分析ベース**: 機械学習による色抽出でアイコンの主要色を自動判定
- **25のカテゴリ**: Compute、Storage、Database、AI、Securityなど幅広いAWSサービス
- **カテゴリ表示**: カードにはスート名ではなくAWSカテゴリ名を表示
- **AWSスペシャル役**: カテゴリベースの特別な役でAWSアーキテクチャを学習
- **5ラウンド制**: 各ラウンドで最大2回のドロー（カード交換）が可能
- **自動進行**: ドロー使い切り後やスタンド後は自動的に次のラウンドへ
- **美しい日本語表示**: M+ Rounded フォントで読みやすい表示
- **ランキング機能**: ゲームコードでスコア共有が可能
- **ヘルプ機能**: 役一覧とカード分布をリアルタイム確認
- **サウンド機能**: BGMと効果音でゲーム体験を向上

## 🚀 インストール

```bash
# リポジトリをクローン
git clone https://github.com/yourusername/aws-porker.git
cd aws-porker

# 仮想環境を作成・有効化
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 依存関係をインストール
uv pip install -e .
```

## 🎯 ゲームの遊び方

### 基本ルール
1. **5ラウンド制**: 各ラウンドで5枚のカードが配られます
2. **カード交換**: カードをクリックして選択し、「Draw」ボタンで交換（各ラウンド2回まで）
3. **役の確定**: 「Stand」ボタンで現在の手札を確定し、スコアを獲得
4. **自動進行**: ドロー使い切り後は自動的にスタンド、役表示後は自動的に次ラウンドへ
5. **合計スコア**: 5ラウンドの合計スコアで競います

### 新機能
- **役一覧表示**: 「役一覧」ボタンで全ての役とスコアを確認
- **カード分布表示**: 「カード分布」ボタンで残りカードの状況を確認
- **ゲームコード共有**: ゲーム終了時に生成されるコードで友達とスコア比較
- **コードロード機能**: 「Load Code」ボタンで他のプレイヤーのスコアをランキングに追加
- **ハイスコア表示**: 最終結果画面でハイスコアと比較表示
- **サウンド機能**: BGMと効果音（♪ボタンでオン/オフ切り替え可能）
- **クリップボードコピー**: ゲームコードをクリックして簡単コピー

### ゲーム起動
```bash
# ポーカーゲームを起動
python run_poker.py

# または
python -c "from aws_porker import run_poker; run_poker()"
```

### ランキング確認
```bash
# ランキング表示
python show_rankings.py

# 詳細付きランキング表示
python show_rankings.py --detail
```

## 🏆 スコアリングシステム

### 通常の役
- **ハイカード**: 10点
- **ワンペア**: 50点
- **ツーペア**: 100点
- **スリーカード**: 200点
- **ストレート**: 400点
- **フラッシュ**: 500-2000点（スート別）
- **フルハウス**: 1200点
- **フォーカード**: 2500点
- **ストレートフラッシュ**: 5000点+ボーナス

### AWSスペシャル役（カテゴリベース）
- **DevOpsスイート**: 500点（DevTools×2 + Management）
- **データパイプライン**: 600点（Analytics×2 + Storage）
- **クラウドトリオ**: 800点（Compute + Storage + Database）
- **IoTエコシステム**: 1000点（IoT + Analytics/AI）
- **サーバーレスコンボ**: 1300点（Compute + Integration + Database）
- **セキュリティスイート**: 1500点（Security×3 or Security×2+Management）
- **マルチクラウド**: 2200点（5つの異なるスート）
- **AWSアーキテクト**: 3000点（主要5カテゴリ：Compute,Storage,Database,Security,Analytics）
- **レジェンダリーフラッシュ**: 10000点（Greenストレートフラッシュ）
- **AWSマスター**: 15000点（ロイヤルストレートフラッシュ）

### スート別希少度
- **Blue**: 43枚（最も希少）
- **Red**: 45枚
- **Orange**: 58枚
- **Purple**: 76枚
- **Green**: 87枚（最も多い）

## 📊 ファイル構成

```
aws-porker/
├── cards.csv              # カード一覧データ
├── score.txt              # スコア表
├── rankings.json          # ランキングデータ
├── run_poker.py           # ゲーム起動スクリプト
├── show_rankings.py       # ランキング表示スクリプト
├── create_music.py        # 音楽生成スクリプト
├── create_color_based_cards.py # 色分析ベースカード生成
├── analyze_architecture_cards.py # Architecture-Icons用カード分析
├── fonts/                 # フォントファイル
│   └── MPLUSRounded1c-Regular.ttf
├── sounds/                # サウンドファイル
│   ├── aws_poker_bgm.wav  # BGM
│   ├── card_draw.wav      # カードドロー効果音
│   ├── hand_complete.wav  # 役完成効果音
│   └── game_end.wav       # ゲーム終了効果音
├── aws_porker/
│   ├── card.py           # カードクラス
│   ├── hand_evaluator.py # 役判定・スコア計算
│   ├── poker_game.py     # メインゲームクラス
│   ├── sound_manager.py  # サウンド管理
│   ├── clipboard_utils.py # クリップボード操作
│   └── __init__.py
└── Architecture-Icons/    # AWSアーキテクチャアイコンファイル
```

## 🎨 カードデザイン

各カードには以下が表示されます：
- **中央**: AWSサービスアイコン（80x80px）
- **対角**: ポーカーランク（A, 2-10, J, Q, K）
- **枠線**: スート色
- **下部**: サービス名とスート名

## 🔧 開発

```bash
# 開発用依存関係をインストール
uv pip install -e ".[dev]"

# テスト実行
pytest

# 新しいカード一覧作成（色分析ベース）
python create_color_based_cards.py

# カード分析
python analyze_architecture_cards.py
```

## 🌟 対戦機能

ネットワーク対戦ではありませんが、ゲームコード機能で間接的な対戦が可能：

1. ゲーム終了時に「Save Score」でゲームコードを生成
2. 生成されたコード（例：`CLOUD-LAMBDA-1234`）を友達と共有
3. ランキングで比較

## 🎓 学習効果

このゲームを通じて以下を学べます：
- AWSサービスの種類と分類
- サービス間の関連性
- AWSアーキテクチャの基本概念
- 確率とゲーム理論

## 📝 ライセンス

MIT License

## 🤝 コントリビューション

プルリクエストやイシューの報告を歓迎します！

---

**楽しいAWSポーカーライフを！** 🎰☁️
