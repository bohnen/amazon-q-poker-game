"""
AWSポーカーのカードクラス
"""

import pygame
import csv
from pathlib import Path
from typing import List, Tuple, Optional
import random

class Card:
    """AWSアイコンを使ったポーカーカード"""
    
    # カードサイズ
    CARD_WIDTH = 150
    CARD_HEIGHT = 200
    
    # 色定義（スート別）
    SUIT_COLORS = {
        'Red': (220, 53, 69),
        'Blue': (13, 110, 253),
        'Green': (25, 135, 84),
        'Orange': (253, 126, 20),
        'Purple': (111, 66, 193),
        'Yellow': (255, 193, 7),
        'Gray': (108, 117, 125)
    }
    
    def __init__(self, path: str, filename: str, rank: str, suit: str):
        self.path = path
        self.filename = filename
        self.rank = rank
        self.suit = suit
        self.service_name = ""  # サービス名
        self.category = ""      # カテゴリ
        self.image = None
        self.card_surface = None
        self.back_surface = None
        self.is_face_up = True
        
    def load_image(self, base_path: str = "/Users/bohnen/Project/aws-game/aws-porker"):
        """アイコン画像を読み込む"""
        try:
            full_path = Path(base_path) / self.path
            self.image = pygame.image.load(str(full_path))
            # アイコンサイズを調整（48x48 -> 80x80）
            self.image = pygame.transform.scale(self.image, (80, 80))
        except pygame.error as e:
            print(f"画像読み込みエラー: {self.path} - {e}")
            # デフォルト画像を作成
            self.image = pygame.Surface((80, 80))
            self.image.fill((200, 200, 200))
    
    def get_service_name(self) -> str:
        """サービス名を取得"""
        # CSVから読み込んだサービス名があればそれを使用
        if hasattr(self, 'service_name') and self.service_name:
            return self.service_name
        
        # フォールバック: ファイル名からサービス名を抽出
        # Arch_Amazon-S3_48.png -> Amazon S3
        name = self.filename.replace('Arch_', '').replace('_48.png', '')
        name = name.replace('-', ' ').replace('_', ' ')
        return name
    
    def get_category_display_name(self) -> str:
        """カテゴリの表示名を取得"""
        if hasattr(self, 'category') and self.category:
            # カテゴリ名を短縮・日本語化
            category_mapping = {
                'Compute': 'Compute',
                'Storage': 'Storage', 
                'Database': 'Database',
                'Networking-Content-Delivery': 'Network',
                'Security-Identity-Compliance': 'Security',
                'Analytics': 'Analytics',
                'Artificial-Intelligence': 'AI/ML',
                'App-Integration': 'Integration',
                'Business-Applications': 'Business',
                'Management-Governance': 'Management',
                'Developer-Tools': 'DevTools',
                'Migration-Modernization': 'Migration',
                'Internet-of-Things': 'IoT',
                'Media-Services': 'Media',
                'Containers': 'Container',
                'Cloud-Financial-Management': 'Cost',
                'Customer-Enablement': 'Support',
                'End-User-Computing': 'EndUser',
                'Front-End-Web-Mobile': 'Frontend',
                'Games': 'Games',
                'General-Icons': 'General',
                'Blockchain': 'Blockchain',
                'Quantum-Technologies': 'Quantum',
                'Robotics': 'Robotics',
                'Satellite': 'Satellite'
            }
            return category_mapping.get(self.category, self.category)
        
        # フォールバック: スート名を返す
        return self.suit
    
    def create_card_surface(self, font: pygame.font.Font, small_font: pygame.font.Font) -> pygame.Surface:
        """カード表面を作成"""
        if self.card_surface is not None:
            return self.card_surface
            
        # カード背景
        surface = pygame.Surface((self.CARD_WIDTH, self.CARD_HEIGHT))
        surface.fill((255, 255, 255))
        
        # スート色の枠線
        border_color = self.SUIT_COLORS.get(self.suit, (0, 0, 0))
        pygame.draw.rect(surface, border_color, (0, 0, self.CARD_WIDTH, self.CARD_HEIGHT), 4)
        
        # ランクを左上と右下に表示
        rank_color = border_color
        rank_surface = font.render(self.rank, True, rank_color)
        
        # 左上
        surface.blit(rank_surface, (10, 10))
        
        # 右下（回転）
        rotated_rank = pygame.transform.rotate(rank_surface, 180)
        surface.blit(rotated_rank, (self.CARD_WIDTH - rank_surface.get_width() - 10, 
                                   self.CARD_HEIGHT - rank_surface.get_height() - 10))
        
        # 中央にアイコン
        if self.image:
            icon_x = (self.CARD_WIDTH - self.image.get_width()) // 2
            icon_y = 40
            surface.blit(self.image, (icon_x, icon_y))
        
        # サービス名とカテゴリを下部に表示
        service_name = self.get_service_name()
        category_name = self.get_category_display_name()
        
        # サービス名を複数行に分割
        words = service_name.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if small_font.size(test_line)[0] <= self.CARD_WIDTH - 20:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        
        # 最大2行まで（カテゴリ名のスペースを確保）
        lines = lines[:2]
        
        y_offset = 130
        for line in lines:
            text_surface = small_font.render(line, True, (0, 0, 0))
            text_x = (self.CARD_WIDTH - text_surface.get_width()) // 2
            surface.blit(text_surface, (text_x, y_offset))
            y_offset += 15
        
        # カテゴリ名を表示（スート名の代わり）
        category_surface = small_font.render(category_name, True, border_color)
        category_x = (self.CARD_WIDTH - category_surface.get_width()) // 2
        surface.blit(category_surface, (category_x, self.CARD_HEIGHT - 25))
        
        self.card_surface = surface
        return surface
        
        self.card_surface = surface
        return surface
    
    def create_back_surface(self) -> pygame.Surface:
        """カード裏面を作成"""
        if self.back_surface is not None:
            return self.back_surface
            
        surface = pygame.Surface((self.CARD_WIDTH, self.CARD_HEIGHT))
        surface.fill((255, 165, 0))  # AWS オレンジ
        
        # AWS ロゴ風のデザイン
        pygame.draw.rect(surface, (35, 47, 62), (10, 10, self.CARD_WIDTH-20, self.CARD_HEIGHT-20), 3)
        
        # 中央に "AWS" テキスト
        font = pygame.font.Font(None, 48)
        aws_text = font.render("AWS", True, (35, 47, 62))
        text_x = (self.CARD_WIDTH - aws_text.get_width()) // 2
        text_y = (self.CARD_HEIGHT - aws_text.get_height()) // 2
        surface.blit(aws_text, (text_x, text_y))
        
        self.back_surface = surface
        return surface
    
    def draw(self, screen: pygame.Surface, x: int, y: int, font: pygame.font.Font, small_font: pygame.font.Font):
        """カードを描画"""
        if self.is_face_up:
            surface = self.create_card_surface(font, small_font)
        else:
            surface = self.create_back_surface()
        
        screen.blit(surface, (x, y))
    
    def get_rect(self, x: int, y: int) -> pygame.Rect:
        """カードの矩形を取得"""
        return pygame.Rect(x, y, self.CARD_WIDTH, self.CARD_HEIGHT)
    
    def __str__(self):
        return f"{self.rank} of {self.suit} ({self.get_service_name()})"
    
    def __repr__(self):
        return self.__str__()


class Deck:
    """カードデッキ"""
    
    def __init__(self, csv_path: str = "/Users/bohnen/Project/aws-game/aws-porker/cards.csv"):
        self.cards: List[Card] = []
        self.load_cards(csv_path)
        self.shuffle()
    
    def load_cards(self, csv_path: str):
        """CSVファイルからカードを読み込み"""
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                card = Card(row['icon_path'], row['filename'], row['rank'], row['suit'])
                # サービス名も保存
                card.service_name = row['service_name']
                card.category = row['category']
                self.cards.append(card)
        
        # 画像を読み込み
        for card in self.cards:
            card.load_image()
    
    def shuffle(self):
        """デッキをシャッフル"""
        random.shuffle(self.cards)
    
    def deal(self, num_cards: int) -> List[Card]:
        """指定枚数のカードを配る"""
        if len(self.cards) < num_cards:
            raise ValueError("デッキに十分なカードがありません")
        
        dealt_cards = self.cards[:num_cards]
        self.cards = self.cards[num_cards:]
        return dealt_cards
    
    def add_cards(self, cards: List[Card]):
        """カードをデッキに戻す"""
        self.cards.extend(cards)
    
    def cards_remaining(self) -> int:
        """残りカード数"""
        return len(self.cards)
