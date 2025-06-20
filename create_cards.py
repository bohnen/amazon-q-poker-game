#!/usr/bin/env python3
"""
AWSアイコンを使ったポーカーカードの一覧を作成するスクリプト
"""

import os
import csv
from pathlib import Path
import re

def extract_color_from_filename(filename):
    """
    ファイル名から色を推測する
    AWSアイコンの命名規則に基づいて色を判定
    """
    filename_lower = filename.lower()
    
    # AWSアイコンの一般的な色パターン
    if 'red' in filename_lower or 'alarm' in filename_lower or 'error' in filename_lower:
        return 'Red'
    elif 'blue' in filename_lower or 'database' in filename_lower or 'storage' in filename_lower:
        return 'Blue'
    elif 'green' in filename_lower or 'success' in filename_lower or 'compute' in filename_lower:
        return 'Green'
    elif 'orange' in filename_lower or 'analytics' in filename_lower or 'lambda' in filename_lower:
        return 'Orange'
    elif 'purple' in filename_lower or 'ai' in filename_lower or 'ml' in filename_lower:
        return 'Purple'
    elif 'yellow' in filename_lower or 'security' in filename_lower:
        return 'Yellow'
    else:
        # カテゴリ別に色を割り当て
        if 'res_database' in filename_lower:
            return 'Blue'
        elif 'res_compute' in filename_lower:
            return 'Green'
        elif 'res_storage' in filename_lower:
            return 'Blue'
        elif 'res_analytics' in filename_lower:
            return 'Orange'
        elif 'res_security' in filename_lower:
            return 'Yellow'
        elif 'res_networking' in filename_lower:
            return 'Purple'
        elif 'res_iot' in filename_lower:
            return 'Red'
        elif 'res_artificial-intelligence' in filename_lower:
            return 'Purple'
        elif 'res_management' in filename_lower:
            return 'Gray'
        else:
            return 'Gray'

def get_rank_name(index):
    """
    インデックスからポーカーのランク名を取得
    """
    ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    return ranks[index % len(ranks)]

def create_cards_csv():
    """
    Resource-Iconsディレクトリ内のPNGファイルを読み取り、
    cards.csvファイルを作成する
    """
    base_dir = Path(os.path.join(os.path.dirname(__file__), 'Resource-Icons'))
    png_files = []
    
    # すべてのPNGファイルを再帰的に検索
    for png_file in base_dir.rglob('*.png'):
        png_files.append(png_file)
    
    # ファイル名でソート（一貫性のため）
    png_files.sort(key=lambda x: str(x))
    
    # CSVファイルを作成
    csv_path = Path(os.path.join(os.path.dirname(__file__), 'cards.csv'))
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['path', 'filename', 'rank', 'suit']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # ヘッダーを書き込み
        writer.writeheader()
        
        # 各PNGファイルの情報を書き込み
        for index, png_file in enumerate(png_files):
            relative_path = png_file.relative_to(Path(os.path.dirname(__file__)))
            filename = png_file.name
            rank = get_rank_name(index)
            suit = extract_color_from_filename(str(png_file))
            
            writer.writerow({
                'path': str(relative_path),
                'filename': filename,
                'rank': rank,
                'suit': suit
            })
    
    print(f"カード一覧を作成しました: {csv_path}")
    print(f"総カード数: {len(png_files)}")
    
    # スート別の統計を表示
    suit_counts = {}
    for png_file in png_files:
        suit = extract_color_from_filename(str(png_file))
        suit_counts[suit] = suit_counts.get(suit, 0) + 1
    
    print("\nスート別カード数:")
    for suit, count in sorted(suit_counts.items()):
        print(f"  {suit}: {count}枚")

if __name__ == "__main__":
    create_cards_csv()
