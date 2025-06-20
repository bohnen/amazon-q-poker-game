"""
ポーカーハンドの評価とスコア計算
"""

from typing import List, Tuple, Dict
from collections import Counter
from .card import Card

class HandEvaluator:
    """ポーカーハンドの評価クラス"""
    
    # ランクの順序
    RANK_ORDER = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    RANK_VALUES = {rank: i for i, rank in enumerate(RANK_ORDER)}
    
    # スートの希少度（少ない順）
    SUIT_RARITY = {
        'Green': 24,
        'Yellow': 27, 
        'Orange': 30,
        'Red': 75,
        'Purple': 82,
        'Blue': 114,
        'Gray': 175
    }
    
    def __init__(self):
        pass
    
    def evaluate_hand(self, cards: List[Card]) -> Tuple[str, int, Dict]:
        """
        ハンドを評価して役名、スコア、詳細情報を返す
        """
        if len(cards) != 5:
            return "Invalid Hand", 0, {}
        
        # 各種チェック
        ranks = [card.rank for card in cards]
        suits = [card.suit for card in cards]
        
        rank_counts = Counter(ranks)
        suit_counts = Counter(suits)
        
        # AWSスペシャル役をチェック
        special_result = self._check_special_hands(cards, ranks, suits)
        if special_result[1] > 0:
            return special_result
        
        # 通常の役をチェック
        return self._check_standard_hands(cards, ranks, suits, rank_counts, suit_counts)
    
    def _check_special_hands(self, cards: List[Card], ranks: List[str], suits: List[str]) -> Tuple[str, int, Dict]:
        """AWSスペシャル役をチェック（カテゴリベース）"""
        
        suit_counts = Counter(suits)
        rank_counts = Counter(ranks)
        
        # カテゴリ情報を取得
        categories = []
        for card in cards:
            if hasattr(card, 'category') and card.category:
                categories.append(card.category)
            else:
                categories.append('Unknown')
        
        category_counts = Counter(categories)
        
        # AWSマスター (ロイヤルストレートフラッシュ)
        if self._is_royal_straight_flush(ranks, suits):
            suit = suits[0]  # 全て同じスートなので
            base_score = 15000
            bonus = self._get_suit_bonus_multiplier(suit)
            final_score = int(base_score * bonus)
            return "AWS Master", final_score, {"suit": suit, "bonus_multiplier": bonus}
        
        # レジェンダリーフラッシュ (Greenストレートフラッシュ)
        if self._is_straight_flush(ranks, suits) and suits[0] == 'Green':
            return "Legendary Flush", 10000, {"suit": "Green"}
        
        # AWSアーキテクト (主要5カテゴリ)
        required_categories = {'Compute', 'Storage', 'Database', 'Security-Identity-Compliance', 'Analytics'}
        if len(set(categories)) >= 5 and required_categories.issubset(set(categories)):
            return "AWS Architect", 3000, {"categories": list(required_categories)}
        
        # マルチクラウド (5つの異なるスート)
        if len(set(suits)) == 5:
            return "Multi-Cloud", 2200, {"suits": list(set(suits))}
        
        # セキュリティスイート (Security中心)
        if (category_counts.get('Security-Identity-Compliance', 0) >= 3 or
            (category_counts.get('Security-Identity-Compliance', 0) >= 2 and 
             category_counts.get('Management-Governance', 0) >= 1)):
            return "Security Suite", 1500, {"security_focus": True}
        
        # サーバーレスコンボ (Compute + Integration + Database)
        if (category_counts.get('Compute', 0) >= 1 and
            category_counts.get('App-Integration', 0) >= 1 and
            category_counts.get('Database', 0) >= 1):
            return "Serverless Combo", 1300, {"combo": "Compute+Integration+Database"}
        
        # IoTエコシステム (IoT + Analytics + AI)
        if (category_counts.get('Internet-of-Things', 0) >= 1 and
            (category_counts.get('Analytics', 0) >= 1 or 
             category_counts.get('Artificial-Intelligence', 0) >= 1)):
            return "IoT Ecosystem", 1000, {"iot_focus": True}
        
        # クラウドトリオ (Compute + Storage + Database)
        if (category_counts.get('Compute', 0) >= 1 and
            category_counts.get('Storage', 0) >= 1 and
            category_counts.get('Database', 0) >= 1):
            return "Cloud Trio", 800, {"combo": "Compute+Storage+Database"}
        
        # データパイプライン (Analytics + Storage)
        if (category_counts.get('Analytics', 0) >= 2 and
            category_counts.get('Storage', 0) >= 1):
            return "Data Pipeline", 600, {"combo": "Analytics+Storage"}
        
        # DevOpsスイート (Developer-Tools + Management)
        if (category_counts.get('Developer-Tools', 0) >= 2 and
            category_counts.get('Management-Governance', 0) >= 1):
            return "DevOps Suite", 500, {"combo": "DevTools+Management"}
        
        return "", 0, {}
    
    def _check_standard_hands(self, cards: List[Card], ranks: List[str], suits: List[str], 
                            rank_counts: Counter, suit_counts: Counter) -> Tuple[str, int, Dict]:
        """通常のポーカー役をチェック"""
        
        # ストレートフラッシュ
        if self._is_straight_flush(ranks, suits):
            suit = suits[0]
            base_score = 5000
            suit_bonus = self._get_flush_bonus(suit)
            final_score = base_score + suit_bonus
            return "Straight Flush", final_score, {"suit": suit, "bonus": suit_bonus}
        
        # フォーカード
        if 4 in rank_counts.values():
            return "Four of a Kind", 2500, {"rank": self._get_most_common_rank(rank_counts, 4)}
        
        # フルハウス
        if 3 in rank_counts.values() and 2 in rank_counts.values():
            three_rank = self._get_most_common_rank(rank_counts, 3)
            pair_rank = self._get_most_common_rank(rank_counts, 2)
            return "Full House", 1200, {"three": three_rank, "pair": pair_rank}
        
        # フラッシュ
        if len(suit_counts) == 1:
            suit = list(suit_counts.keys())[0]
            score = self._get_flush_bonus(suit)
            return "Flush", score, {"suit": suit}
        
        # ストレート
        if self._is_straight(ranks):
            return "Straight", 400, {"high_card": max(ranks, key=lambda x: self.RANK_VALUES[x])}
        
        # スリーカード
        if 3 in rank_counts.values():
            rank = self._get_most_common_rank(rank_counts, 3)
            return "Three of a Kind", 200, {"rank": rank}
        
        # ツーペア
        pairs = [rank for rank, count in rank_counts.items() if count == 2]
        if len(pairs) == 2:
            return "Two Pair", 100, {"pairs": sorted(pairs, key=lambda x: self.RANK_VALUES[x], reverse=True)}
        
        # ワンペア
        if 2 in rank_counts.values():
            rank = self._get_most_common_rank(rank_counts, 2)
            return "One Pair", 50, {"rank": rank}
        
        # ハイカード
        high_card = max(ranks, key=lambda x: self.RANK_VALUES[x])
        return "High Card", 10, {"high_card": high_card}
    
    def _is_royal_straight_flush(self, ranks: List[str], suits: List[str]) -> bool:
        """ロイヤルストレートフラッシュかチェック"""
        royal_ranks = {'A', 'K', 'Q', 'J', '10'}
        return (len(set(suits)) == 1 and set(ranks) == royal_ranks)
    
    def _is_straight_flush(self, ranks: List[str], suits: List[str]) -> bool:
        """ストレートフラッシュかチェック"""
        return len(set(suits)) == 1 and self._is_straight(ranks)
    
    def _is_straight(self, ranks: List[str]) -> bool:
        """ストレートかチェック"""
        rank_values = sorted([self.RANK_VALUES[rank] for rank in ranks])
        
        # 通常のストレート
        for i in range(len(rank_values) - 1):
            if rank_values[i + 1] - rank_values[i] != 1:
                break
        else:
            return True
        
        # A-2-3-4-5 のストレート
        if set(ranks) == {'A', '2', '3', '4', '5'}:
            return True
        
        return False
    
    def _is_serverless_combo(self, cards: List[Card]) -> bool:
        """サーバーレスコンボかチェック"""
        filenames = [card.filename.lower() for card in cards]
        has_lambda = any('lambda' in name for name in filenames)
        has_api = any('api' in name for name in filenames)
        has_dynamo = any('dynamo' in name for name in filenames)
        return has_lambda and has_api and has_dynamo
    
    def _is_cloud_trio(self, suits: List[str], rank_counts: Counter) -> bool:
        """クラウドトリオかチェック"""
        suit_counts = Counter(suits)
        has_compute = suit_counts.get('Green', 0) >= 1
        has_storage = suit_counts.get('Blue', 0) >= 1
        has_database = suit_counts.get('Blue', 0) >= 2  # StorageとDatabaseは両方Blue
        
        # 3つの異なるランク + 他2枚の条件もチェック
        unique_ranks = len([rank for rank, count in rank_counts.items() if count >= 1])
        
        return has_compute and has_storage and unique_ranks >= 3
    
    def _get_flush_bonus(self, suit: str) -> int:
        """フラッシュのスート別ボーナス"""
        bonuses = {
            'Green': 2000,
            'Yellow': 1800,
            'Orange': 1600,
            'Red': 1000,
            'Purple': 800,
            'Blue': 600,
            'Gray': 500
        }
        return bonuses.get(suit, 500)
    
    def _get_suit_bonus_multiplier(self, suit: str) -> float:
        """スート別ボーナス倍率"""
        multipliers = {
            'Green': 3.0,
            'Yellow': 2.5,
            'Orange': 2.0,
            'Red': 1.5,
            'Purple': 1.3,
            'Blue': 1.2,
            'Gray': 1.0
        }
        return multipliers.get(suit, 1.0)
    
    def _get_most_common_rank(self, rank_counts: Counter, target_count: int) -> str:
        """指定された出現回数のランクを取得"""
        for rank, count in rank_counts.items():
            if count == target_count:
                return rank
        return ""
    
    def get_hand_strength(self, hand_name: str, score: int) -> int:
        """役の強さを数値で返す（比較用）"""
        strength_map = {
            "High Card": 1,
            "One Pair": 2,
            "Two Pair": 3,
            "Three of a Kind": 4,
            "Straight": 5,
            "Flush": 6,
            "Full House": 7,
            "Four of a Kind": 8,
            "Straight Flush": 9,
            "Royal Straight Flush": 10,
            "DevOps Suite": 11,
            "Data Pipeline": 12,
            "Cloud Trio": 13,
            "IoT Ecosystem": 14,
            "Serverless Combo": 15,
            "Security Suite": 16,
            "Multi-Cloud": 17,
            "AWS Architect": 18,
            "Legendary Flush": 19,
            "AWS Master": 20
        }
        return strength_map.get(hand_name, 0) * 1000 + score
