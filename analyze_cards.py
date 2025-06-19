#!/usr/bin/env python3
"""
カードの分布を分析してスコア設定の参考にする
"""

import csv
from collections import Counter, defaultdict
import math

def analyze_cards():
    """
    cards.csvを分析してカード分布を調べる
    """
    suits = []
    ranks = []
    suit_rank_combinations = []
    
    with open('/Users/bohnen/Project/aws-game/aws-porker/cards.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            suits.append(row['suit'])
            ranks.append(row['rank'])
            suit_rank_combinations.append((row['suit'], row['rank']))
    
    total_cards = len(suits)
    suit_counts = Counter(suits)
    rank_counts = Counter(ranks)
    
    print(f"総カード数: {total_cards}")
    print("\n=== スート分布 ===")
    for suit, count in sorted(suit_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_cards) * 100
        print(f"{suit}: {count}枚 ({percentage:.1f}%)")
    
    print("\n=== ランク分布 ===")
    for rank in ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']:
        count = rank_counts[rank]
        percentage = (count / total_cards) * 100
        print(f"{rank}: {count}枚 ({percentage:.1f}%)")
    
    # 各スートでの各ランクの分布
    print("\n=== スート別ランク分布 ===")
    suit_rank_matrix = defaultdict(lambda: defaultdict(int))
    for suit, rank in suit_rank_combinations:
        suit_rank_matrix[suit][rank] += 1
    
    for suit in sorted(suit_counts.keys()):
        print(f"\n{suit} ({suit_counts[suit]}枚):")
        for rank in ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']:
            count = suit_rank_matrix[suit][rank]
            if count > 0:
                print(f"  {rank}: {count}枚")
    
    # 確率計算のための情報
    print("\n=== 役の作りやすさ分析 ===")
    
    # フラッシュ（同じスートの5枚）の確率
    print("フラッシュの作りやすさ:")
    for suit, count in sorted(suit_counts.items(), key=lambda x: x[1], reverse=True):
        if count >= 5:
            # C(count, 5) / C(total, 5)
            flush_combinations = math.comb(count, 5)
            total_combinations = math.comb(total_cards, 5)
            probability = flush_combinations / total_combinations
            print(f"  {suit}フラッシュ: {probability:.6f} ({flush_combinations}/{total_combinations})")
    
    # ストレート（連続する5つのランク）
    print(f"\nストレートの作りやすさ:")
    rank_order = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    for i in range(len(rank_order) - 4):
        straight_ranks = rank_order[i:i+5]
        min_count = min(rank_counts[rank] for rank in straight_ranks)
        print(f"  {'-'.join(straight_ranks)}: 最小{min_count}枚")
    
    return suit_counts, rank_counts, total_cards

if __name__ == "__main__":
    analyze_cards()
