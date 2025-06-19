#!/usr/bin/env python3
"""
ランキング表示スクリプト
"""

import json
import sys
from datetime import datetime

def show_rankings():
    """ランキングを表示"""
    rankings_file = "/Users/bohnen/Project/aws-game/aws-porker/rankings.json"
    
    try:
        with open(rankings_file, 'r') as f:
            rankings = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print("ランキングデータが見つかりません。")
        return
    
    if not rankings:
        print("まだランキングデータがありません。")
        return
    
    print("AWS Porker - ランキング")
    print("=" * 60)
    
    for i, entry in enumerate(rankings[:10], 1):  # トップ10を表示
        timestamp = datetime.fromisoformat(entry["timestamp"])
        loaded_mark = " [L]" if entry.get("loaded", False) else ""
        print(f"{i:2d}. {entry['total_score']:6d}点 | {entry['code']}{loaded_mark} | {timestamp.strftime('%Y-%m-%d %H:%M')}")
        
        # 詳細表示オプション
        if len(sys.argv) > 1 and sys.argv[1] == "--detail":
            if entry.get("loaded", False):
                print("    ※ ゲームコードからロードされたスコア")
            else:
                print("    ラウンド詳細:")
                for j, round_data in enumerate(entry["rounds"], 1):
                    print(f"      R{j}: {round_data['hand']} ({round_data['score']}点)")
            print()

def add_score_by_code():
    """ゲームコードでスコアを追加"""
    if len(sys.argv) < 3:
        print("使用方法: python show_rankings.py --add <ゲームコード>")
        return
    
    game_code = sys.argv[2]
    rankings_file = "/Users/bohnen/Project/aws-game/aws-porker/rankings.json"
    
    # 実際の実装では、ゲームコードから元のゲームデータを復元する必要があります
    # ここでは簡単な例として、コードを受け取ったことを表示
    print(f"ゲームコード '{game_code}' を受け取りました。")
    print("注意: 実際のスコア追加機能は、ゲームデータの暗号化/復号化が必要です。")

def main():
    """メイン関数"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--add":
            add_score_by_code()
        elif sys.argv[1] == "--detail":
            show_rankings()
        else:
            print("使用方法:")
            print("  python show_rankings.py           # ランキング表示")
            print("  python show_rankings.py --detail  # 詳細付きランキング表示")
            print("  python show_rankings.py --add <code>  # ゲームコードでスコア追加")
    else:
        show_rankings()

if __name__ == "__main__":
    main()
