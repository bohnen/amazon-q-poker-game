#!/usr/bin/env python3
"""
Architecture-Iconsフォルダから48pixelアイコンを使ってcards.csvを生成するスクリプト
"""

import os
import csv
import re
from pathlib import Path
from typing import List, Dict, Tuple

class ArchitectureCardGenerator:
    """Architecture-Iconsからカードデータを生成するクラス"""
    
    def __init__(self, base_path: str = None):
        if base_path is None:
            base_path = os.path.join(os.path.dirname(__file__), "Architecture-Icons")
        self.base_path = Path(base_path)
        self.cards = []
        
        # カテゴリとスート（色）のマッピング
        self.category_to_suit = {
            "Arch_Compute": "Blue",
            "Arch_Storage": "Green", 
            "Arch_Database": "Purple",
            "Arch_Networking-Content-Delivery": "Orange",
            "Arch_Security-Identity-Compliance": "Red",
            "Arch_Analytics": "Yellow",
            "Arch_Artificial-Intelligence": "Gray",
            "Arch_App-Integration": "Blue",
            "Arch_Business-Applications": "Purple",
            "Arch_Blockchain": "Gray",
            "Arch_Cloud-Financial-Management": "Green",
            "Arch_Containers": "Blue",
            "Arch_Customer-Enablement": "Orange",
            "Arch_Developer-Tools": "Yellow",
            "Arch_End-User-Computing": "Purple",
            "Arch_Front-End-Web-Mobile": "Orange",
            "Arch_Games": "Red",
            "Arch_General-Icons": "Gray",
            "Arch_Internet-of-Things": "Yellow",
            "Arch_Management-Governance": "Green",
            "Arch_Media-Services": "Red",
            "Arch_Migration-Modernization": "Orange",
            "Arch_Quantum-Technologies": "Gray",
            "Arch_Robotics": "Purple",
            "Arch_Satellite": "Blue"
        }
        
        # ランクの順序（A, 2-10, J, Q, K）
        self.ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    
    def extract_service_name(self, filename: str) -> str:
        """ファイル名からサービス名を抽出"""
        # "Arch_" プレフィックスを削除
        name = filename.replace("Arch_", "")
        # "_48.png" サフィックスを削除
        name = re.sub(r"_48\.(png|svg)$", "", name)
        # ハイフンをスペースに変換
        name = name.replace("-", " ")
        # アンダースコアをスペースに変換
        name = name.replace("_", " ")
        return name
    
    def scan_architecture_icons(self):
        """Architecture-Iconsフォルダをスキャンしてアイコンを収集"""
        print("Architecture-Iconsフォルダをスキャン中...")
        
        for category_dir in self.base_path.iterdir():
            if not category_dir.is_dir() or category_dir.name.startswith('.'):
                continue
            
            category_name = category_dir.name
            suit = self.category_to_suit.get(category_name, "Gray")
            
            # 48pixelフォルダを探す
            pixel_48_dir = category_dir / "48"
            if not pixel_48_dir.exists():
                print(f"警告: {category_name} に48pixelフォルダが見つかりません")
                continue
            
            # PNGファイルを収集
            png_files = list(pixel_48_dir.glob("*.png"))
            png_files = [f for f in png_files if not f.name.startswith('.')]
            
            print(f"{category_name}: {len(png_files)}個のPNGファイルを発見")
            
            for png_file in png_files:
                service_name = self.extract_service_name(png_file.name)
                
                card_data = {
                    'service_name': service_name,
                    'category': category_name.replace("Arch_", ""),
                    'suit': suit,
                    'icon_path': str(png_file.relative_to(self.base_path.parent)),
                    'filename': png_file.name
                }
                
                self.cards.append(card_data)
    
    def assign_ranks(self):
        """カードにランクを割り当て"""
        print("ランクを割り当て中...")
        
        # スート別にカードを分類
        suits = {}
        for card in self.cards:
            suit = card['suit']
            if suit not in suits:
                suits[suit] = []
            suits[suit].append(card)
        
        # 各スートにランクを割り当て
        for suit, suit_cards in suits.items():
            print(f"{suit}: {len(suit_cards)}枚")
            
            # サービス名でソート（一貫性のため）
            suit_cards.sort(key=lambda x: x['service_name'])
            
            # ランクを循環的に割り当て
            for i, card in enumerate(suit_cards):
                rank_index = i % len(self.ranks)
                card['rank'] = self.ranks[rank_index]
    
    def generate_csv(self, output_file: str = "cards.csv"):
        """CSVファイルを生成"""
        print(f"CSVファイルを生成中: {output_file}")
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['service_name', 'category', 'suit', 'rank', 'icon_path', 'filename']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for card in self.cards:
                writer.writerow(card)
        
        print(f"完了: {len(self.cards)}枚のカードを生成しました")
    
    def print_statistics(self):
        """統計情報を表示"""
        print("\n=== カード統計 ===")
        
        # スート別統計
        suit_counts = {}
        for card in self.cards:
            suit = card['suit']
            suit_counts[suit] = suit_counts.get(suit, 0) + 1
        
        print("スート別枚数:")
        for suit, count in sorted(suit_counts.items()):
            print(f"  {suit}: {count}枚")
        
        # ランク別統計
        rank_counts = {}
        for card in self.cards:
            rank = card['rank']
            rank_counts[rank] = rank_counts.get(rank, 0) + 1
        
        print("\nランク別枚数:")
        for rank in self.ranks:
            count = rank_counts.get(rank, 0)
            print(f"  {rank}: {count}枚")
        
        print(f"\n総カード数: {len(self.cards)}枚")
    
    def run(self):
        """メイン処理を実行"""
        self.scan_architecture_icons()
        self.assign_ranks()
        self.generate_csv()
        self.print_statistics()

def main():
    """メイン関数"""
    print("Architecture-Icons用カードジェネレーター")
    print("=" * 50)
    
    generator = ArchitectureCardGenerator()
    generator.run()
    
    print("\nカード生成完了！")
    print("新しいcards.csvファイルが作成されました。")

if __name__ == "__main__":
    main()
