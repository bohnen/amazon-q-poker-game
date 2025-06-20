#!/usr/bin/env python3
"""
AWSポーカーゲームの起動スクリプト
"""

import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from aws_poker.poker_game import PokerGame

def main():
    """メイン関数"""
    print("AWS Poker - AWSアイコンポーカーゲーム")
    print("=" * 50)
    print("ゲームルール:")
    print("- 5ラウンド制のポーカーゲーム")
    print("- 各ラウンドで5枚のカードが配られます")
    print("- カードをクリックして選択し、Drawで交換（2回まで）")
    print("- Standで役を確定し、次のラウンドへ")
    print("- 5ラウンドの合計スコアで競います")
    print()
    print("新機能:")
    print("- 「役一覧」ボタン: ポーカー役とスコアを確認")
    print("- 「カード分布」ボタン: 残りカードの分布を確認")
    print("- ESCキーまたは「閉じる」ボタンでオーバーレイを閉じる")
    print("- マウスホイールでスクロール可能")
    print("=" * 50)
    
    try:
        game = PokerGame()
        game.run()
    except Exception as e:
        print(f"ゲーム実行エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
