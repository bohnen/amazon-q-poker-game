#!/usr/bin/env python3
"""
Architecture-Icons版のカード分析スクリプト
"""

import csv
from collections import defaultdict, Counter
from pathlib import Path

def analyze_cards(csv_path: str = "cards.csv"):
    """カードデータを分析"""
    
    print("Architecture-Icons カード分析")
    print("=" * 50)
    
    # データ読み込み
    cards = []
    with open(csv_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        cards = list(reader)
    
    print(f"総カード数: {len(cards)}枚")
    print()
    
    # スート別分析
    print("📊 スート別統計:")
    suit_counts = Counter(card['suit'] for card in cards)
    for suit, count in sorted(suit_counts.items()):
        percentage = (count / len(cards)) * 100
        print(f"  {suit:8s}: {count:3d}枚 ({percentage:5.1f}%)")
    print()
    
    # ランク別分析
    print("🎯 ランク別統計:")
    rank_counts = Counter(card['rank'] for card in cards)
    ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    for rank in ranks:
        count = rank_counts.get(rank, 0)
        percentage = (count / len(cards)) * 100 if count > 0 else 0
        print(f"  {rank:2s}: {count:3d}枚 ({percentage:5.1f}%)")
    print()
    
    # カテゴリ別分析
    print("🏗️  カテゴリ別統計:")
    category_counts = Counter(card['category'] for card in cards)
    for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(cards)) * 100
        print(f"  {category:30s}: {count:3d}枚 ({percentage:5.1f}%)")
    print()
    
    # スート×ランク分布
    print("🎴 スート×ランク分布:")
    suit_rank_dist = defaultdict(lambda: defaultdict(int))
    for card in cards:
        suit_rank_dist[card['suit']][card['rank']] += 1
    
    # ヘッダー
    print("     ", end="")
    for rank in ranks:
        print(f"{rank:>3s}", end="")
    print("  Total")
    
    # 各スートの分布
    for suit in sorted(suit_counts.keys()):
        print(f"{suit:8s}", end="")
        total = 0
        for rank in ranks:
            count = suit_rank_dist[suit][rank]
            print(f"{count:3d}", end="")
            total += count
        print(f"  {total:3d}")
    print()
    
    # ポーカー戦略分析
    print("♠️ ポーカー戦略分析:")
    
    # フラッシュの確率計算
    print("フラッシュ確率 (5枚中5枚同じスート):")
    for suit, count in sorted(suit_counts.items(), key=lambda x: x[1]):
        if count >= 5:
            # 組み合わせ計算 C(count, 5)
            from math import comb
            flush_combinations = comb(count, 5)
            total_combinations = comb(len(cards), 5)
            probability = (flush_combinations / total_combinations) * 100
            print(f"  {suit:8s}: {probability:6.3f}% ({flush_combinations:,} / {total_combinations:,})")
        else:
            print(f"  {suit:8s}: 不可能 (カード数: {count})")
    print()
    
    # ストレート分析
    print("ストレート分析:")
    rank_values = {'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13}
    
    # 各ランクの枚数
    print("各ランクの枚数:")
    for rank in ranks:
        count = rank_counts.get(rank, 0)
        print(f"  {rank:2s}: {count:2d}枚", end="")
        if count < 4:
            print(" ⚠️  (ストレート形成に不利)")
        else:
            print()
    print()
    
    # 希少度分析
    print("🌟 希少度分析:")
    
    # スート別希少度
    suit_rarity = sorted(suit_counts.items(), key=lambda x: x[1])
    print("スート希少度 (少ない順):")
    for i, (suit, count) in enumerate(suit_rarity, 1):
        rarity_level = "★" * (len(suit_rarity) - i + 1)
        print(f"  {i}. {suit:8s}: {count:3d}枚 {rarity_level}")
    print()
    
    # 推奨戦略
    print("🎯 推奨戦略:")
    rarest_suit = suit_rarity[0][0]
    most_common_suit = suit_rarity[-1][0]
    
    print(f"• 最も希少な{rarest_suit}フラッシュを狙うのは困難")
    print(f"• {most_common_suit}フラッシュが最も現実的")
    print("• ストレート狙いは全ランクが比較的均等に分布しているため有効")
    print("• ペア系の役が基本戦略として推奨")

def main():
    """メイン関数"""
    try:
        analyze_cards()
    except FileNotFoundError:
        print("エラー: cards.csv が見つかりません")
        print("先に create_architecture_cards.py を実行してください")
    except Exception as e:
        print(f"分析エラー: {e}")

if __name__ == "__main__":
    main()
