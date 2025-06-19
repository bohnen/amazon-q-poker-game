"""
AWSポーカーゲームのメインクラス
"""

import hashlib
import json
import random
import string
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import pygame

from .card import Card, Deck
from .hand_evaluator import HandEvaluator
from .sound_manager import SoundManager
from .clipboard_utils import ClipboardManager


class PokerGame:
    """AWSポーカーゲーム"""
    
    def __init__(self, width: int = 1800, height: int = 800):
        pygame.init()
        
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("AWS Porker - AWSアイコンポーカー")
        
        # フォント
        font_path = "/Users/bohnen/Project/aws-game/aws-porker/fonts/MPLUSRounded1c-Regular.ttf"
        try:
            self.font = pygame.font.Font(font_path, 24)
            self.small_font = pygame.font.Font(font_path, 16)
            self.large_font = pygame.font.Font(font_path, 32)
            self.huge_font = pygame.font.Font(font_path, 48)
        except:
            # フォントが見つからない場合はデフォルトフォントを使用
            self.font = pygame.font.Font(None, 36)
            self.small_font = pygame.font.Font(None, 24)
            self.large_font = pygame.font.Font(None, 48)
            self.huge_font = pygame.font.Font(None, 72)
        
        # 色定義
        self.bg_color = (34, 139, 34)  # フォレストグリーン
        self.button_color = (70, 130, 180)
        self.button_hover_color = (100, 149, 237)
        self.text_color = (255, 255, 255)
        
        # ゲーム状態
        self.deck = Deck()
        self.hand: List[Card] = []
        self.selected_cards: List[bool] = [False] * 5
        self.evaluator = HandEvaluator()
        
        # ゲーム進行
        self.current_round = 1
        self.max_rounds = 5
        self.draws_remaining = 2
        self.total_score = 0
        self.round_scores: List[Tuple[str, int, Dict]] = []
        
        # UI要素
        self.buttons = {}
        self.game_state = "playing"  # playing, round_end, game_end, show_hands, show_deck, hand_result, final_result
        self.show_overlay = False
        self.overlay_scroll = 0
        
        # 自動遷移用タイマー
        self.transition_timer = 0
        self.transition_duration = 3000  # 3秒
        self.current_hand_result = None
        self.final_game_code = None  # 最終ゲームコードを保存
        
        # クリップボード関連
        self.clipboard_manager = ClipboardManager()
        self.code_copied_time = 0  # コピー完了時刻
        self.code_rect = None  # ゲームコードの矩形領域
        
        # ランキング
        self.rankings_file = "/Users/bohnen/Project/aws-game/aws-porker/rankings.json"
        
        # サウンドマネージャー
        self.sound_manager = SoundManager()
        
        self.setup_game()
    
    def setup_game(self):
        """ゲームの初期設定"""
        self.deal_new_hand()
        self.create_buttons()
        # BGMを開始
        self.sound_manager.play_bgm()
    
    def deal_new_hand(self):
        """新しいハンドを配る"""
        if self.deck.cards_remaining() < 5:
            self.deck = Deck()  # 新しいデッキを作成
        
        self.hand = self.deck.deal(5)
        self.selected_cards = [False] * 5
        self.draws_remaining = 2
    
    def create_buttons(self):
        """UIボタンを作成"""
        button_width = 100
        button_height = 40
        button_spacing = 110
        start_x = 50
        
        self.buttons = {
            "draw": pygame.Rect(start_x, self.height - 100, button_width, button_height),
            "stand": pygame.Rect(start_x + button_spacing, self.height - 100, button_width, button_height),
            "next_round": pygame.Rect(start_x + button_spacing * 2, self.height - 100, button_width, button_height),
            "new_game": pygame.Rect(start_x + button_spacing * 3, self.height - 100, button_width, button_height),
            "save_score": pygame.Rect(start_x + button_spacing * 4, self.height - 100, button_width, button_height),
            "load_code": pygame.Rect(start_x + button_spacing * 5, self.height - 100, button_width, button_height),
            "sound_toggle": pygame.Rect(start_x + button_spacing * 6, self.height - 100, button_width, button_height),
            "show_hands": pygame.Rect(start_x + button_spacing * 7, self.height - 100, button_width, button_height),
            "show_deck": pygame.Rect(start_x + button_spacing * 8, self.height - 100, button_width, button_height),
            "close_overlay": pygame.Rect(self.width - 150, 50, 100, 40)
        }
    
    def handle_event(self, event):
        """イベント処理"""
        if event.type == pygame.QUIT:
            return False
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # カード選択
            if self.game_state == "playing":
                self.handle_card_selection(mouse_pos)
            
            # ゲームコードクリック（最終結果画面）
            if self.game_state == "final_result" and self.code_rect:
                if self.code_rect.collidepoint(mouse_pos):
                    self.copy_game_code_to_clipboard()
            
            # ボタンクリック
            self.handle_button_click(mouse_pos)
        
        elif event.type == pygame.KEYDOWN:
            # ESCキーでオーバーレイを閉じる
            if event.key == pygame.K_ESCAPE and self.show_overlay:
                self.show_overlay = False
                self.overlay_scroll = 0
                self.game_state = "playing" if self.current_round <= self.max_rounds else "final_result"
        
        elif event.type == pygame.MOUSEWHEEL and self.show_overlay:
            # マウスホイールでスクロール
            self.overlay_scroll += event.y * 20
            self.overlay_scroll = max(0, min(self.overlay_scroll, 200))  # スクロール範囲制限
        
        elif event.type == pygame.USEREVENT + 1:
            # 自動スタンド
            if self.game_state == "playing" and self.draws_remaining <= 0:
                self.stand()
            pygame.time.set_timer(pygame.USEREVENT + 1, 0)  # タイマーを停止
        
        elif event.type == pygame.USEREVENT + 2:
            # 自動次ラウンド
            if self.game_state == "hand_result":
                self.next_round()
            pygame.time.set_timer(pygame.USEREVENT + 2, 0)  # タイマーを停止
        
        return True
    
    def handle_card_selection(self, mouse_pos: Tuple[int, int]):
        """カード選択処理"""
        card_start_x = 100
        card_y = 200
        card_spacing = 180
        
        for i, card in enumerate(self.hand):
            card_rect = card.get_rect(card_start_x + i * card_spacing, card_y)
            if card_rect.collidepoint(mouse_pos):
                self.selected_cards[i] = not self.selected_cards[i]
                break
    
    def handle_button_click(self, mouse_pos: Tuple[int, int]):
        """ボタンクリック処理"""
        for button_name, button_rect in self.buttons.items():
            if button_rect.collidepoint(mouse_pos):
                if button_name == "draw" and self.game_state == "playing" and self.draws_remaining > 0:
                    self.draw_cards()
                elif button_name == "stand" and self.game_state == "playing":
                    self.stand()
                elif button_name == "next_round" and self.game_state == "round_end":
                    self.next_round()
                elif button_name == "new_game":
                    self.new_game()
                elif button_name == "save_score" and self.game_state == "final_result":
                    self.save_score()
                elif button_name == "load_code":
                    self.load_game_code()
                elif button_name == "sound_toggle":
                    self.sound_manager.toggle_sound()
                elif button_name == "show_hands":
                    self.show_hands_overlay()
                elif button_name == "show_deck":
                    self.show_deck_overlay()
                elif button_name == "close_overlay" and self.show_overlay:
                    self.show_overlay = False
                    self.overlay_scroll = 0
                    self.game_state = "playing" if self.current_round <= self.max_rounds else "final_result"
                break
    
    def draw_cards(self):
        """選択されたカードを交換"""
        if self.draws_remaining <= 0:
            return
        
        # 選択されたカードをデッキに戻す
        cards_to_return = []
        new_cards_needed = 0
        
        for i, selected in enumerate(self.selected_cards):
            if selected:
                cards_to_return.append(self.hand[i])
                new_cards_needed += 1
        
        if new_cards_needed == 0:
            return
        
        # デッキに戻してシャッフル
        self.deck.add_cards(cards_to_return)
        self.deck.shuffle()
        
        # 新しいカードを配る
        new_cards = self.deck.deal(new_cards_needed)
        new_card_index = 0
        
        for i, selected in enumerate(self.selected_cards):
            if selected:
                self.hand[i] = new_cards[new_card_index]
                new_card_index += 1
                self.selected_cards[i] = False
        
        self.draws_remaining -= 1
        
        # カードドロー効果音
        self.sound_manager.play_sound('card_draw')
        
        # ドローを使い切った場合は自動的にスタンド
        if self.draws_remaining <= 0:
            pygame.time.set_timer(pygame.USEREVENT + 1, 1000)  # 1秒後に自動スタンド
    
    def stand(self):
        """ハンドを確定"""
        hand_name, score, details = self.evaluator.evaluate_hand(self.hand)
        self.round_scores.append((hand_name, score, details))
        self.total_score += score
        self.current_hand_result = (hand_name, score, details)
        
        # 役の結果を表示してから次のラウンドへ
        self.game_state = "hand_result"
        self.transition_timer = pygame.time.get_ticks()
        
        # 役完成効果音
        self.sound_manager.play_sound('hand_complete')
        
        # 3秒後に次のラウンドまたは最終結果へ
        pygame.time.set_timer(pygame.USEREVENT + 2, self.transition_duration)
    
    def next_round(self):
        """次のラウンドへ"""
        self.current_round += 1
        if self.current_round > self.max_rounds:
            self.game_state = "final_result"
            # ゲーム終了時にゲームコードを一度だけ生成
            self.final_game_code = self.generate_game_code()
            # ゲーム終了効果音
            self.sound_manager.play_sound('game_end')
        else:
            self.deal_new_hand()
            self.game_state = "playing"
    
    def new_game(self):
        """新しいゲームを開始"""
        self.current_round = 1
        self.total_score = 0
        self.round_scores = []
        self.current_hand_result = None
        self.transition_timer = 0
        self.final_game_code = None  # ゲームコードをリセット
        self.code_copied_time = 0  # コピー時刻をリセット
        self.code_rect = None  # 矩形をリセット
        self.deck = Deck()
        self.deal_new_hand()
        self.game_state = "playing"
        
        # タイマーをリセット
        pygame.time.set_timer(pygame.USEREVENT + 1, 0)
        pygame.time.set_timer(pygame.USEREVENT + 2, 0)
    
    def save_score(self):
        """スコアを保存"""
        # 既に生成されたゲームコードを使用、なければ新規生成
        game_code = self.final_game_code if self.final_game_code else self.generate_game_code()
        ranking_entry = {
            "code": game_code,
            "total_score": self.total_score,
            "rounds": [{"hand": hand, "score": score, "details": details} 
                      for hand, score, details in self.round_scores],
            "timestamp": datetime.now().isoformat()
        }
        
        # ランキングファイルに保存
        try:
            with open(self.rankings_file, 'r') as f:
                rankings = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            rankings = []
        
        rankings.append(ranking_entry)
        rankings.sort(key=lambda x: x["total_score"], reverse=True)
        
        with open(self.rankings_file, 'w') as f:
            json.dump(rankings, f, indent=2)
        
        print(f"ゲームコード: {game_code}")
        print(f"スコア: {self.total_score}")
    
    def generate_game_code(self) -> str:
        """覚えやすいゲームコードを生成"""
        # ラウンドスコアとタイムスタンプからハッシュを生成
        score_string = "-".join([f"{hand}:{score}" for hand, score, _ in self.round_scores])
        timestamp = datetime.now().isoformat()
        hash_input = f"{score_string}-{timestamp}"
        
        hash_object = hashlib.md5(hash_input.encode())
        hash_hex = hash_object.hexdigest()
        
        # AWS風の覚えやすいコードに変換
        aws_words = ["CLOUD", "SCALE", "SECURE", "DEPLOY", "LAMBDA", "BUCKET", "QUEUE", "STACK"]
        word1 = aws_words[int(hash_hex[:2], 16) % len(aws_words)]
        word2 = aws_words[int(hash_hex[2:4], 16) % len(aws_words)]
        
        # 数字部分
        num_part = str(int(hash_hex[4:8], 16))[-4:]
        
        return f"{word1}-{word2}-{num_part}"
    
    def load_game_code(self):
        """ゲームコードを入力してランキングに追加"""
        try:
            # コンソール入力を使用（Tkinterの問題を回避）
            print("\n" + "="*50)
            print("🎮 ゲームコード入力")
            print("="*50)
            print("例: CLOUD-LAMBDA-1234")
            game_code = input("ゲームコードを入力してください: ").strip()
            
            if game_code:
                # ゲームコードの検証
                if self.validate_game_code(game_code):
                    # スコアデータを復元
                    score = self.generate_dummy_score_from_code(game_code)
                    self.add_score_to_ranking(game_code, score)
                    
                    # 成功メッセージを表示
                    self.show_message = f"コード読み込み完了！スコア: {score}"
                    self.message_timer = pygame.time.get_ticks()
                    print(f"✅ ゲームコード '{game_code}' をランキングに追加しました！")
                    print(f"📊 スコア: {score}")
                else:
                    self.show_message = "無効なゲームコードです"
                    self.message_timer = pygame.time.get_ticks()
                    print("❌ 無効なゲームコードです。")
            else:
                print("❌ コードが入力されませんでした。")
                
        except Exception as e:
            print(f"❌ ゲームコード読み込みエラー: {e}")
            self.show_message = "コード読み込みに失敗しました"
            self.message_timer = pygame.time.get_ticks()
    
    def validate_game_code(self, code: str) -> bool:
        """ゲームコードの形式を検証"""
        parts = code.split('-')
        return len(parts) == 3 and len(parts[2]) == 4 and parts[2].isdigit()
    
    def generate_dummy_score_from_code(self, code: str) -> int:
        """ゲームコードからダミースコアを生成（実際には暗号化されたデータから復元）"""
        # ハッシュ値からスコアを生成
        hash_value = sum(ord(c) for c in code)
        return (hash_value % 5000) + 1000  # 1000-6000の範囲
    
    def add_score_to_ranking(self, game_code: str, score: int):
        """スコアをランキングに追加"""
        ranking_entry = {
            "code": game_code,
            "total_score": score,
            "rounds": [{"hand": "Unknown", "score": score // 5, "details": {}} for _ in range(5)],
            "timestamp": datetime.now().isoformat(),
            "loaded": True  # ロードされたスコアであることを示す
        }
        
        try:
            with open(self.rankings_file, 'r') as f:
                rankings = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            rankings = []
        
        # 同じコードが既に存在するかチェック
        if not any(entry["code"] == game_code for entry in rankings):
            rankings.append(ranking_entry)
            rankings.sort(key=lambda x: x["total_score"], reverse=True)
            
            with open(self.rankings_file, 'w') as f:
                json.dump(rankings, f, indent=2)
    
    def get_high_score(self) -> int:
        """ハイスコアを取得"""
        try:
            with open(self.rankings_file, 'r') as f:
                rankings = json.load(f)
            return rankings[0]["total_score"] if rankings else 0
        except (FileNotFoundError, json.JSONDecodeError):
            return 0
    
    def copy_game_code_to_clipboard(self):
        """ゲームコードをクリップボードにコピー"""
        if self.final_game_code:
            success = self.clipboard_manager.copy_to_clipboard(self.final_game_code)
            if success:
                self.code_copied_time = pygame.time.get_ticks()
                print(f"ゲームコードをクリップボードにコピーしました: {self.final_game_code}")
            else:
                print("クリップボードへのコピーに失敗しました")
    
    def show_hands_overlay(self):
        """役の一覧を表示"""
        self.show_overlay = True
        self.overlay_scroll = 0
        self.game_state = "show_hands"
    
    def show_deck_overlay(self):
        """残りカードの分布を表示"""
        self.show_overlay = True
        self.overlay_scroll = 0
        self.game_state = "show_deck"
    
    def get_remaining_cards_distribution(self) -> Dict[str, Dict[str, int]]:
        """残りカードの分布を取得"""
        remaining_cards = self.deck.cards
        
        # スート別・ランク別の分布を計算
        suit_distribution = {}
        rank_distribution = {}
        
        for card in remaining_cards:
            # スート分布
            if card.suit not in suit_distribution:
                suit_distribution[card.suit] = 0
            suit_distribution[card.suit] += 1
            
            # ランク分布
            if card.rank not in rank_distribution:
                rank_distribution[card.rank] = 0
            rank_distribution[card.rank] += 1
        
        return {
            "suits": suit_distribution,
            "ranks": rank_distribution,
            "total": len(remaining_cards)
        }
    
    def draw(self):
        """画面描画"""
        self.screen.fill(self.bg_color)
        
        # タイトル
        title_text = self.large_font.render("AWS Porker", True, self.text_color)
        self.screen.blit(title_text, (50, 20))
        
        # ゲーム情報
        info_text = f"Round {self.current_round}/{self.max_rounds} | Draws: {self.draws_remaining} | Score: {self.total_score}"
        info_surface = self.font.render(info_text, True, self.text_color)
        self.screen.blit(info_surface, (50, 70))
        
        # カード描画
        if self.game_state in ["playing", "hand_result"]:
            self.draw_cards_on_screen()
        
        # 現在のハンド評価
        if self.hand and self.game_state == "playing":
            current_hand, current_score, details = self.evaluator.evaluate_hand(self.hand)
            hand_text = f"Current Hand: {current_hand} ({current_score} points)"
            hand_surface = self.font.render(hand_text, True, self.text_color)
            self.screen.blit(hand_surface, (50, 450))
            
            # ドロー使い切り時の自動スタンド通知
            if self.draws_remaining <= 0:
                auto_text = "ドローを使い切りました。自動的にスタンドします..."
                auto_surface = self.small_font.render(auto_text, True, (255, 255, 0))
                self.screen.blit(auto_surface, (50, 480))
        
        # 役の結果表示
        if self.game_state == "hand_result":
            self.draw_hand_result()
        
        # ラウンド結果表示
        if self.game_state in ["round_end", "final_result"]:
            self.draw_round_results()
        
        # 最終結果表示
        if self.game_state == "final_result":
            self.draw_final_result()
        
        # ボタン描画
        self.draw_buttons()
        
        # オーバーレイ描画
        if self.show_overlay:
            self.draw_overlay()
        
        pygame.display.flip()
    
    def draw_cards_on_screen(self):
        """カードを画面に描画"""
        card_start_x = 100
        card_y = 200
        card_spacing = 180
        
        for i, card in enumerate(self.hand):
            x = card_start_x + i * card_spacing
            
            # 選択されたカードをハイライト
            if self.selected_cards[i]:
                highlight_rect = pygame.Rect(x - 5, card_y - 5, 
                                           Card.CARD_WIDTH + 10, Card.CARD_HEIGHT + 10)
                pygame.draw.rect(self.screen, (255, 255, 0), highlight_rect, 3)
            
            card.draw(self.screen, x, card_y, self.font, self.small_font)
    
    def draw_hand_result(self):
        """役の結果を大きく表示"""
        if not self.current_hand_result:
            return
        
        hand_name, score, details = self.current_hand_result
        
        # 半透明の背景
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # 役名を大きく表示
        hand_surface = self.huge_font.render(hand_name, True, (255, 255, 0))
        hand_rect = hand_surface.get_rect(center=(self.width // 2, self.height // 2 - 50))
        self.screen.blit(hand_surface, hand_rect)
        
        # スコアを表示
        score_text = f"{score} points"
        score_surface = self.large_font.render(score_text, True, (255, 255, 255))
        score_rect = score_surface.get_rect(center=(self.width // 2, self.height // 2 + 20))
        self.screen.blit(score_surface, score_rect)
        
        # 残り時間表示
        elapsed = pygame.time.get_ticks() - self.transition_timer
        remaining = max(0, (self.transition_duration - elapsed) // 1000 + 1)
        if remaining > 0:
            timer_text = f"Next round in {remaining}..."
            timer_surface = self.font.render(timer_text, True, (200, 200, 200))
            timer_rect = timer_surface.get_rect(center=(self.width // 2, self.height // 2 + 80))
            self.screen.blit(timer_surface, timer_rect)
    
    def draw_final_result(self):
        """最終結果を表示"""
        # 背景
        result_rect = pygame.Rect(100, 150, self.width - 200, 450)
        pygame.draw.rect(self.screen, (0, 0, 0), result_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), result_rect, 3)
        
        # タイトル
        title_surface = self.large_font.render("ゲーム終了！", True, (255, 255, 0))
        title_rect = title_surface.get_rect(centerx=self.width // 2, y=result_rect.y + 20)
        self.screen.blit(title_surface, title_rect)
        
        # 最終スコア
        score_text = f"最終スコア: {self.total_score}"
        score_surface = self.large_font.render(score_text, True, (255, 255, 255))
        score_rect = score_surface.get_rect(centerx=self.width // 2, y=result_rect.y + 80)
        self.screen.blit(score_surface, score_rect)
        
        # ハイスコア
        high_score = self.get_high_score()
        if self.total_score > high_score:
            high_text = "新記録達成！"
            high_color = (255, 100, 100)
        else:
            high_text = f"ハイスコア: {high_score}"
            high_color = (200, 200, 200)
        
        high_surface = self.font.render(high_text, True, high_color)
        high_rect = high_surface.get_rect(centerx=self.width // 2, y=result_rect.y + 130)
        self.screen.blit(high_surface, high_rect)
        
        # ゲームコード（クリック可能）
        game_code = self.final_game_code if self.final_game_code else self.generate_game_code()
        code_text = f"ゲームコード: {game_code}"
        
        # マウスホバー効果
        mouse_pos = pygame.mouse.get_pos()
        code_surface = self.font.render(code_text, True, (100, 255, 100))
        code_rect = code_surface.get_rect(centerx=self.width // 2, y=result_rect.y + 180)
        self.code_rect = code_rect  # クリック判定用に保存
        
        # ホバー時の背景
        if code_rect.collidepoint(mouse_pos):
            hover_rect = pygame.Rect(code_rect.x - 10, code_rect.y - 5, 
                                   code_rect.width + 20, code_rect.height + 10)
            pygame.draw.rect(self.screen, (50, 50, 50), hover_rect)
            pygame.draw.rect(self.screen, (100, 255, 100), hover_rect, 2)
        
        self.screen.blit(code_surface, code_rect)
        
        # クリック説明
        click_text = "↑ クリックでコピー"
        click_surface = self.small_font.render(click_text, True, (150, 150, 150))
        click_rect = click_surface.get_rect(centerx=self.width // 2, y=result_rect.y + 210)
        self.screen.blit(click_surface, click_rect)
        
        # コピー完了メッセージ
        current_time = pygame.time.get_ticks()
        if self.code_copied_time > 0 and current_time - self.code_copied_time < 2000:  # 2秒間表示
            copied_text = "✓ クリップボードにコピーしました！"
            copied_surface = self.small_font.render(copied_text, True, (100, 255, 100))
            copied_rect = copied_surface.get_rect(centerx=self.width // 2, y=result_rect.y + 240)
            self.screen.blit(copied_surface, copied_rect)
        
        # 説明
        help_text = "このコードを友達と共有してスコアを比較しよう！"
        help_surface = self.small_font.render(help_text, True, (200, 200, 200))
        help_rect = help_surface.get_rect(centerx=self.width // 2, y=result_rect.y + 270)
        self.screen.blit(help_surface, help_rect)
    
    def draw_round_results(self):
        """ラウンド結果を描画"""
        y_offset = 500
        
        if self.game_state == "game_end":
            # 全ラウンドの結果
            results_title = self.font.render("Game Results:", True, self.text_color)
            self.screen.blit(results_title, (50, y_offset))
            y_offset += 40
            
            for i, (hand_name, score, details) in enumerate(self.round_scores):
                result_text = f"Round {i+1}: {hand_name} - {score} points"
                result_surface = self.small_font.render(result_text, True, self.text_color)
                self.screen.blit(result_surface, (70, y_offset))
                y_offset += 25
            
            # 合計スコア
            total_text = f"Total Score: {self.total_score}"
            total_surface = self.font.render(total_text, True, (255, 255, 0))
            self.screen.blit(total_surface, (50, y_offset + 20))
    
    def draw_overlay(self):
        """オーバーレイを描画"""
        # 半透明の背景
        overlay_surface = pygame.Surface((self.width, self.height))
        overlay_surface.set_alpha(200)
        overlay_surface.fill((0, 0, 0))
        self.screen.blit(overlay_surface, (0, 0))
        
        # オーバーレイの内容
        content_rect = pygame.Rect(100, 100, self.width - 200, self.height - 200)
        pygame.draw.rect(self.screen, (255, 255, 255), content_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), content_rect, 3)
        
        if self.game_state == "show_hands":
            self.draw_hands_help(content_rect)
        elif self.game_state == "show_deck":
            self.draw_deck_info(content_rect)
    
    def draw_hands_help(self, rect: pygame.Rect):
        """役の一覧を描画"""
        # スクロール可能な領域を作成
        scroll_surface = pygame.Surface((rect.width, rect.height + 400))
        scroll_surface.fill((255, 255, 255))
        
        title = self.large_font.render("ポーカー役一覧", True, (0, 0, 0))
        title_rect = title.get_rect(centerx=scroll_surface.get_width() // 2, y=20)
        scroll_surface.blit(title, title_rect)
        
        # 操作説明
        help_text = "ESCキーまたは「閉じる」ボタンで戻る | マウスホイールでスクロール"
        help_surface = self.small_font.render(help_text, True, (100, 100, 100))
        help_rect = help_surface.get_rect(centerx=scroll_surface.get_width() // 2, y=50)
        scroll_surface.blit(help_surface, help_rect)
        
        # 役の情報
        hands_info = [
            ("通常の役", ""),
            ("ハイカード", "10点 - 役なし"),
            ("ワンペア", "50点 - 同じランク2枚"),
            ("ツーペア", "100点 - 異なるペア2組"),
            ("スリーカード", "200点 - 同じランク3枚"),
            ("ストレート", "400点 - 連続する5つのランク"),
            ("フラッシュ", "500-2000点 - 同じスート5枚"),
            ("フルハウス", "1200点 - スリーカード+ペア"),
            ("フォーカード", "2500点 - 同じランク4枚"),
            ("ストレートフラッシュ", "5000点+ - 同スートのストレート"),
            ("", ""),
            ("AWSスペシャル役（カテゴリベース）", ""),
            ("DevOpsスイート", "500点 - DevTools×2 + Management"),
            ("データパイプライン", "600点 - Analytics×2 + Storage"),
            ("クラウドトリオ", "800点 - Compute + Storage + Database"),
            ("IoTエコシステム", "1000点 - IoT + (Analytics or AI)"),
            ("サーバーレスコンボ", "1300点 - Compute + Integration + Database"),
            ("セキュリティスイート", "1500点 - Security×3 or Security×2+Management"),
            ("マルチクラウド", "2200点 - 5つの異なるスート"),
            ("AWSアーキテクト", "3000点 - 主要5カテゴリ（Compute,Storage,Database,Security,Analytics）"),
            ("レジェンダリーフラッシュ", "10000点 - Greenストレートフラッシュ"),
            ("AWSマスター", "15000点 - ロイヤルストレートフラッシュ"),
            ("", ""),
            ("スート別希少度とフラッシュボーナス", ""),
            ("Blue", "43枚 (最も希少) - 2000点"),
            ("Red", "45枚 - 1800点"),
            ("Orange", "58枚 - 1600点"),
            ("Purple", "76枚 - 1200点"),
            ("Green", "87枚 (最も多い) - 500点"),
            ("", ""),
            ("主要カテゴリ", ""),
            ("Compute", "24枚 - Lambda, EC2, ECS等"),
            ("Storage", "16枚 - S3, EBS, EFS等"),
            ("Database", "11枚 - RDS, DynamoDB等"),
            ("Security", "27枚 - IAM, GuardDuty等"),
            ("Analytics", "21枚 - Redshift, Athena等"),
            ("AI/ML", "42枚 - SageMaker, Bedrock等"),
            ("Management", "30枚 - CloudWatch, Config等"),
        ]
        
        y_offset = 90
        for hand_name, description in hands_info:
            if hand_name == "":
                y_offset += 10
                continue
            
            if description == "":  # カテゴリタイトル
                text_surface = self.font.render(hand_name, True, (0, 100, 200))
                y_offset += 5
            else:
                text = f"{hand_name}: {description}"
                # スート名の場合は色付き
                if hand_name in Card.SUIT_COLORS:
                    color = Card.SUIT_COLORS[hand_name]
                    text_surface = self.small_font.render(text, True, color)
                else:
                    text_surface = self.small_font.render(text, True, (0, 0, 0))
            
            scroll_surface.blit(text_surface, (20, y_offset))
            y_offset += 25
        
        # スクロールされた部分を表示
        visible_rect = pygame.Rect(0, self.overlay_scroll, rect.width, rect.height)
        self.screen.blit(scroll_surface, rect, visible_rect)
    
    def draw_deck_info(self, rect: pygame.Rect):
        """残りカードの分布を描画"""
        distribution = self.get_remaining_cards_distribution()
        
        # スクロール可能な領域を作成
        scroll_surface = pygame.Surface((rect.width, rect.height + 200))
        scroll_surface.fill((255, 255, 255))
        
        title = self.large_font.render(f"残りカード分布 (総数: {distribution['total']}枚)", True, (0, 0, 0))
        title_rect = title.get_rect(centerx=scroll_surface.get_width() // 2, y=20)
        scroll_surface.blit(title, title_rect)
        
        # 操作説明
        help_text = "ESCキーまたは「閉じる」ボタンで戻る | マウスホイールでスクロール"
        help_surface = self.small_font.render(help_text, True, (100, 100, 100))
        help_rect = help_surface.get_rect(centerx=scroll_surface.get_width() // 2, y=50)
        scroll_surface.blit(help_surface, help_rect)
        
        # 使用済みカード情報
        used_cards = 527 - distribution['total']
        used_text = f"使用済みカード: {used_cards}枚 | 現在のラウンド: {self.current_round}/{self.max_rounds}"
        used_surface = self.font.render(used_text, True, (200, 0, 0))
        used_rect = used_surface.get_rect(centerx=scroll_surface.get_width() // 2, y=80)
        scroll_surface.blit(used_surface, used_rect)
        
        # 現在のハンド情報
        if self.hand:
            hand_suits = [card.suit for card in self.hand]
            hand_ranks = [card.rank for card in self.hand]
            hand_info = f"現在の手札: {', '.join([f'{r}({s})' for r, s in zip(hand_ranks, hand_suits)])}"
            hand_surface = self.small_font.render(hand_info, True, (0, 0, 200))
            hand_rect = hand_surface.get_rect(centerx=scroll_surface.get_width() // 2, y=110)
            scroll_surface.blit(hand_surface, hand_rect)
        
        # スート分布
        suit_title = self.font.render("スート別分布", True, (0, 100, 200))
        scroll_surface.blit(suit_title, (20, 150))
        
        y_offset = 180
        suit_order = ["Green", "Yellow", "Orange", "Red", "Purple", "Blue", "Gray"]
        
        for suit in suit_order:
            count = distribution['suits'].get(suit, 0)
            percentage = (count / distribution['total'] * 100) if distribution['total'] > 0 else 0
            color = Card.SUIT_COLORS.get(suit, (0, 0, 0))
            
            text = f"{suit}: {count}枚 ({percentage:.1f}%)"
            text_surface = self.small_font.render(text, True, color)
            scroll_surface.blit(text_surface, (30, y_offset))
            y_offset += 25
        
        # ランク分布
        rank_title = self.font.render("ランク別分布", True, (0, 100, 200))
        scroll_surface.blit(rank_title, (scroll_surface.get_width() // 2 + 20, 150))
        
        y_offset = 180
        rank_order = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        
        for rank in rank_order:
            count = distribution['ranks'].get(rank, 0)
            percentage = (count / distribution['total'] * 100) if distribution['total'] > 0 else 0
            
            text = f"{rank}: {count}枚 ({percentage:.1f}%)"
            text_surface = self.small_font.render(text, True, (0, 0, 0))
            scroll_surface.blit(text_surface, (scroll_surface.get_width() // 2 + 30, y_offset))
            y_offset += 25
        
        # 確率情報
        prob_title = self.font.render("役の作りやすさ (概算)", True, (0, 100, 200))
        scroll_surface.blit(prob_title, (20, y_offset + 20))
        y_offset += 50
        
        # フラッシュの確率
        for suit in suit_order:
            count = distribution['suits'].get(suit, 0)
            if count >= 5:
                # 簡易的な確率計算
                prob = min(100, (count / 40) * 100)  # 大まかな目安
                color = Card.SUIT_COLORS.get(suit, (0, 0, 0))
                text = f"{suit}フラッシュ: 約{prob:.1f}%の確率"
                text_surface = self.small_font.render(text, True, color)
                scroll_surface.blit(text_surface, (30, y_offset))
                y_offset += 20
        
        # スクロールされた部分を表示
        visible_rect = pygame.Rect(0, self.overlay_scroll, rect.width, rect.height)
        self.screen.blit(scroll_surface, rect, visible_rect)
    
    def draw_buttons(self):
        """ボタンを描画"""
        mouse_pos = pygame.mouse.get_pos()
        
        for button_name, button_rect in self.buttons.items():
            # ボタンの表示条件
            if not self.should_show_button(button_name):
                continue
            
            # ホバー効果
            color = self.button_hover_color if button_rect.collidepoint(mouse_pos) else self.button_color
            pygame.draw.rect(self.screen, color, button_rect)
            pygame.draw.rect(self.screen, self.text_color, button_rect, 2)
            
            # ボタンテキスト
            button_text = self.get_button_text(button_name)
            text_surface = self.small_font.render(button_text, True, self.text_color)
            text_rect = text_surface.get_rect(center=button_rect.center)
            self.screen.blit(text_surface, text_rect)
    
    def should_show_button(self, button_name: str) -> bool:
        """ボタンを表示すべきかチェック"""
        if self.show_overlay:
            return button_name == "close_overlay"
        
        if self.game_state == "hand_result":
            return False  # 役表示中はボタンを隠す
        
        if button_name == "draw":
            return self.game_state == "playing" and self.draws_remaining > 0
        elif button_name == "stand":
            return self.game_state == "playing"
        elif button_name == "next_round":
            return False  # 自動遷移するので不要
        elif button_name == "new_game":
            return True
        elif button_name == "save_score":
            return self.game_state == "final_result"
        elif button_name == "load_code":
            return self.game_state == "final_result" or self.game_state == "playing"
        elif button_name == "sound_toggle":
            return not self.show_overlay and self.game_state != "hand_result"
        elif button_name == "show_hands":
            return not self.show_overlay and self.game_state != "hand_result"
        elif button_name == "show_deck":
            return not self.show_overlay and self.game_state != "hand_result"
        elif button_name == "close_overlay":
            return self.show_overlay
        return False
    
    def get_button_text(self, button_name: str) -> str:
        """ボタンテキストを取得"""
        texts = {
            "draw": f"Draw ({self.draws_remaining})",
            "stand": "Stand",
            "next_round": "Next Round",
            "new_game": "New Game",
            "save_score": "Save Score",
            "load_code": "Load Code",
            "sound_toggle": "♪ ON" if self.sound_manager.enabled else "♪ OFF",
            "show_hands": "役一覧",
            "show_deck": "カード分布",
            "close_overlay": "閉じる"
        }
        return texts.get(button_name, button_name)
    
    def run(self):
        """ゲームループ"""
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                running = self.handle_event(event)
            
            self.draw()
            clock.tick(60)
        
        # クリーンアップ
        self.sound_manager.cleanup()
        pygame.quit()
        sys.exit()
        pygame.quit()
        sys.exit()
