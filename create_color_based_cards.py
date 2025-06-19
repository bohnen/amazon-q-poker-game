#!/usr/bin/env python3
"""
アイコンの実際の色を分析してスートを決定するカード生成スクリプト
"""

import os
import csv
import re
import colorsys
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
from collections import Counter

class ColorBasedCardGenerator:
    """アイコンの色分析に基づくカードジェネレーター"""
    
    def __init__(self, base_path: str = "/Users/bohnen/Project/aws-game/aws-porker/Architecture-Icons"):
        self.base_path = Path(base_path)
        self.cards = []
        
        # より細かい色からスートへのマッピング（実際のAWS色に基づく）
        self.color_to_suit = {
            'Red': {'hue_range': [(0, 25), (340, 360)], 'name': 'Red'},       # 赤系
            'Orange': {'hue_range': [(25, 45)], 'name': 'Orange'},            # オレンジ系
            'Yellow': {'hue_range': [(45, 75)], 'name': 'Yellow'},            # 黄系
            'Green': {'hue_range': [(75, 165)], 'name': 'Green'},             # 緑系（青緑含む）
            'Blue': {'hue_range': [(200, 270)], 'name': 'Blue'},              # 青系
            'Purple': {'hue_range': [(270, 340)], 'name': 'Purple'},          # 紫系（マゼンタ含む）
            'Gray': {'hue_range': [], 'name': 'Gray'}                         # グレー系
        }
        
        # ランクの順序
        self.ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        
        # 色分析結果のキャッシュ
        self.color_cache = {}
    
    def extract_dominant_colors(self, image_path: Path, n_colors: int = 8) -> List[Tuple[int, int, int]]:
        """画像から主要色を抽出（改良版）"""
        try:
            # 画像を開く
            with Image.open(image_path) as img:
                # RGBAの場合はRGBに変換
                if img.mode == 'RGBA':
                    # 透明部分を白背景に合成
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1])
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 画像をリサイズして処理を高速化
                img = img.resize((96, 96))  # より高解像度で分析
                
                # ピクセルデータを取得
                pixels = np.array(img).reshape(-1, 3)
                
                # 白に近い色（背景）をより厳密に除外
                non_white_pixels = []
                for pixel in pixels:
                    # 白、薄いグレーを除外
                    if not (pixel[0] > 230 and pixel[1] > 230 and pixel[2] > 230):
                        # 非常に暗い色も除外（影など）
                        if not (pixel[0] < 20 and pixel[1] < 20 and pixel[2] < 20):
                            non_white_pixels.append(pixel)
                
                if len(non_white_pixels) < 10:
                    # ほとんど白の場合はグレーとして扱う
                    return [(128, 128, 128)]
                
                non_white_pixels = np.array(non_white_pixels)
                
                # K-meansクラスタリングで主要色を抽出
                n_colors = min(n_colors, len(non_white_pixels))
                kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
                kmeans.fit(non_white_pixels)
                
                # クラスタの中心色を取得
                colors = kmeans.cluster_centers_.astype(int)
                
                # 各色の出現頻度を計算
                labels = kmeans.labels_
                color_counts = Counter(labels)
                
                # 頻度順にソート
                sorted_colors = []
                for label, count in color_counts.most_common():
                    color = tuple(colors[label])
                    # 極端に暗い色や明るい色を除外
                    r, g, b = color
                    if not (r < 30 and g < 30 and b < 30) and not (r > 240 and g > 240 and b > 240):
                        sorted_colors.append(color)
                
                return sorted_colors[:5]  # 上位5色を返す
                
        except Exception as e:
            print(f"色抽出エラー ({image_path}): {e}")
            return [(128, 128, 128)]  # デフォルトはグレー
    
    def rgb_to_hsv(self, r: int, g: int, b: int) -> Tuple[float, float, float]:
        """RGBをHSVに変換"""
        return colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
    
    def classify_color_to_suit(self, rgb_color: Tuple[int, int, int]) -> str:
        """RGB色をスートに分類（より正確な色判定）"""
        r, g, b = rgb_color
        h, s, v = self.rgb_to_hsv(r, g, b)
        
        # HSVのHue（色相）を0-360度に変換
        hue_degrees = h * 360
        
        # 彩度と明度の閾値を下げて、より多くの色を分類
        if s < 0.15 and v < 0.6:  # 非常に暗いグレー
            return 'Gray'
        elif s < 0.1:  # 彩度が非常に低い場合のみグレー
            return 'Gray'
        
        # 特定のAWS色の精密判定（RGB値での直接マッチング）
        aws_colors = {
            # オレンジ系（Compute）
            (237, 113, 0): 'Orange',
            (255, 153, 0): 'Orange',
            (255, 140, 0): 'Orange',
            
            # 紫系（Database, Management）
            (201, 37, 209): 'Purple',
            (200, 36, 208): 'Purple',
            (231, 21, 123): 'Purple',  # マゼンタ系も紫に
            (231, 20, 123): 'Purple',
            (146, 43, 156): 'Purple',
            
            # 青系（Analytics, Networking）
            (140, 79, 255): 'Blue',
            (83, 141, 213): 'Blue',
            (70, 130, 180): 'Blue',
            
            # 赤系（Security）
            (221, 52, 76): 'Red',
            (221, 51, 75): 'Red',
            (255, 69, 58): 'Red',
            (220, 53, 69): 'Red',
            
            # 緑系（Storage, IoT）
            (1, 168, 141): 'Green',   # ティール
            (0, 167, 141): 'Green',
            (122, 161, 22): 'Green',  # 黄緑も緑に
            (121, 161, 22): 'Green',
            (52, 199, 89): 'Green',
            
            # 黄色系
            (255, 204, 0): 'Yellow',
            (255, 193, 7): 'Yellow',
        }
        
        # 完全一致チェック
        if (r, g, b) in aws_colors:
            return aws_colors[(r, g, b)]
        
        # 近似色チェック（±10の範囲）
        for (ar, ag, ab), suit in aws_colors.items():
            if abs(r - ar) <= 10 and abs(g - ag) <= 10 and abs(b - ab) <= 10:
                return suit
        
        # HSV色相による分類（より広い範囲）
        if 340 <= hue_degrees <= 360 or 0 <= hue_degrees <= 25:
            return 'Red'
        elif 25 < hue_degrees <= 45:
            return 'Orange'
        elif 45 < hue_degrees <= 75:
            return 'Yellow'
        elif 75 < hue_degrees <= 165:
            return 'Green'
        elif 165 < hue_degrees <= 200:
            # 青緑系は緑に分類
            return 'Green'
        elif 200 < hue_degrees <= 270:
            return 'Blue'
        elif 270 < hue_degrees <= 340:
            return 'Purple'
        
        # 明度による最終判定
        if v < 0.3:
            return 'Gray'
        elif s < 0.2:
            return 'Gray'
        
        # デフォルトは最も近い色相に基づく
        if hue_degrees < 180:
            if hue_degrees < 90:
                return 'Orange' if hue_degrees < 45 else 'Yellow'
            else:
                return 'Green'
        else:
            if hue_degrees < 270:
                return 'Blue'
            else:
                return 'Purple'
    
    def analyze_icon_color(self, image_path: Path) -> str:
        """アイコンの色を分析してスートを決定（改良版）"""
        if str(image_path) in self.color_cache:
            return self.color_cache[str(image_path)]
        
        # 主要色を抽出
        dominant_colors = self.extract_dominant_colors(image_path)
        
        # 各色をスートに分類（重み付き投票）
        suit_votes = Counter()
        for i, color in enumerate(dominant_colors):
            suit = self.classify_color_to_suit(color)
            # 上位の色ほど重みを大きくする
            weight = len(dominant_colors) - i
            suit_votes[suit] += weight
        
        # 最も多く投票されたスートを選択
        if suit_votes:
            most_common_suit = suit_votes.most_common(1)[0][0]
        else:
            most_common_suit = 'Gray'
        
        # キャッシュに保存
        self.color_cache[str(image_path)] = most_common_suit
        
        # より詳細な色情報を表示
        color_info = ", ".join([f"RGB{color}" for color in dominant_colors[:3]])
        print(f"  {image_path.name}: [{color_info}] -> {most_common_suit}")
        
        return most_common_suit
    
    def extract_service_name(self, filename: str) -> str:
        """ファイル名からサービス名を抽出"""
        name = filename.replace("Arch_", "")
        name = re.sub(r"_48\.(png|svg)$", "", name)
        name = name.replace("-", " ").replace("_", " ")
        return name
    
    def scan_architecture_icons(self):
        """Architecture-Iconsフォルダをスキャンしてアイコンを収集"""
        print("Architecture-Iconsフォルダをスキャン中...")
        
        for category_dir in self.base_path.iterdir():
            if not category_dir.is_dir() or category_dir.name.startswith('.'):
                continue
            
            category_name = category_dir.name.replace("Arch_", "")
            
            # 48pixelフォルダを探す
            pixel_48_dir = category_dir / "48"
            if not pixel_48_dir.exists():
                print(f"警告: {category_name} に48pixelフォルダが見つかりません")
                continue
            
            # PNGファイルを収集
            png_files = list(pixel_48_dir.glob("*.png"))
            png_files = [f for f in png_files if not f.name.startswith('.')]
            
            print(f"\n{category_name}: {len(png_files)}個のPNGファイルを分析中...")
            
            for png_file in png_files:
                service_name = self.extract_service_name(png_file.name)
                
                # アイコンの色を分析してスートを決定
                suit = self.analyze_icon_color(png_file)
                
                card_data = {
                    'service_name': service_name,
                    'category': category_name,
                    'suit': suit,
                    'icon_path': str(png_file.relative_to(self.base_path.parent)),
                    'filename': png_file.name
                }
                
                self.cards.append(card_data)
    
    def assign_ranks(self):
        """カードにランクを割り当て"""
        print("\nランクを割り当て中...")
        
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
        print(f"\nCSVファイルを生成中: {output_file}")
        
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
        
        print("スート別枚数（色分析結果）:")
        for suit, count in sorted(suit_counts.items()):
            percentage = (count / len(self.cards)) * 100
            print(f"  {suit:8s}: {count:3d}枚 ({percentage:5.1f}%)")
        
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
        
        # 色分析の詳細統計
        print("\n=== 色分析統計 ===")
        category_suit_dist = {}
        for card in self.cards:
            category = card['category']
            suit = card['suit']
            if category not in category_suit_dist:
                category_suit_dist[category] = {}
            if suit not in category_suit_dist[category]:
                category_suit_dist[category][suit] = 0
            category_suit_dist[category][suit] += 1
        
        print("カテゴリ別スート分布:")
        for category, suit_dist in sorted(category_suit_dist.items()):
            print(f"  {category}:")
            for suit, count in sorted(suit_dist.items()):
                print(f"    {suit}: {count}枚")
    
    def run(self):
        """メイン処理を実行"""
        self.scan_architecture_icons()
        self.assign_ranks()
        self.generate_csv()
        self.print_statistics()

def main():
    """メイン関数"""
    print("色分析ベースAWSカードジェネレーター")
    print("=" * 50)
    print("アイコンの実際の色を分析してスートを決定します...")
    print("処理には時間がかかる場合があります。")
    print()
    
    generator = ColorBasedCardGenerator()
    generator.run()
    
    print("\n色分析ベースのカード生成完了！")
    print("新しいcards.csvファイルが作成されました。")
    print("実際のアイコンの色に基づいてスートが決定されています。")

if __name__ == "__main__":
    main()
