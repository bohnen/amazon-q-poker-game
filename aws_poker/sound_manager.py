"""
AWSポーカーゲーム用サウンドマネージャー
"""

import os
import pygame
from pathlib import Path
from typing import Dict, Optional

class SoundManager:
    """サウンド管理クラス"""
    
    def __init__(self, sounds_dir: str = None):
        if sounds_dir is None:
            sounds_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sounds")
        self.sounds_dir = Path(sounds_dir)
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.bgm_playing = False
        self.volume_bgm = 0.3
        self.volume_sfx = 0.7
        self.enabled = True
        
        # pygame.mixerを初期化
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self.load_sounds()
        except pygame.error as e:
            print(f"サウンド初期化エラー: {e}")
            self.enabled = False
    
    def load_sounds(self):
        """サウンドファイルを読み込み"""
        if not self.enabled:
            return
        
        sound_files = {
            'bgm': 'aws_poker_bgm.wav',
            'card_draw': 'card_draw.wav',
            'hand_complete': 'hand_complete.wav',
            'game_end': 'game_end.wav'
        }
        
        for sound_name, filename in sound_files.items():
            sound_path = self.sounds_dir / filename
            try:
                if sound_path.exists():
                    if sound_name == 'bgm':
                        # BGMは pygame.mixer.music で管理
                        continue
                    else:
                        sound = pygame.mixer.Sound(str(sound_path))
                        self.sounds[sound_name] = sound
                        print(f"サウンド読み込み成功: {sound_name}")
                else:
                    print(f"サウンドファイルが見つかりません: {sound_path}")
            except pygame.error as e:
                print(f"サウンド読み込みエラー ({sound_name}): {e}")
    
    def play_bgm(self, loop: bool = True):
        """BGMを再生"""
        if not self.enabled or self.bgm_playing:
            return
        
        bgm_path = self.sounds_dir / 'aws_poker_bgm.wav'
        if bgm_path.exists():
            try:
                pygame.mixer.music.load(str(bgm_path))
                pygame.mixer.music.set_volume(self.volume_bgm)
                pygame.mixer.music.play(-1 if loop else 0)
                self.bgm_playing = True
                print("BGM再生開始")
            except pygame.error as e:
                print(f"BGM再生エラー: {e}")
    
    def stop_bgm(self):
        """BGMを停止"""
        if not self.enabled:
            return
        
        try:
            pygame.mixer.music.stop()
            self.bgm_playing = False
            print("BGM停止")
        except pygame.error as e:
            print(f"BGM停止エラー: {e}")
    
    def play_sound(self, sound_name: str):
        """効果音を再生"""
        if not self.enabled or sound_name not in self.sounds:
            return
        
        try:
            sound = self.sounds[sound_name]
            sound.set_volume(self.volume_sfx)
            sound.play()
        except pygame.error as e:
            print(f"効果音再生エラー ({sound_name}): {e}")
    
    def set_bgm_volume(self, volume: float):
        """BGM音量を設定（0.0-1.0）"""
        self.volume_bgm = max(0.0, min(1.0, volume))
        if self.enabled and self.bgm_playing:
            pygame.mixer.music.set_volume(self.volume_bgm)
    
    def set_sfx_volume(self, volume: float):
        """効果音音量を設定（0.0-1.0）"""
        self.volume_sfx = max(0.0, min(1.0, volume))
    
    def toggle_sound(self):
        """サウンドのオン/オフを切り替え"""
        self.enabled = not self.enabled
        if not self.enabled:
            self.stop_bgm()
        else:
            self.play_bgm()
        return self.enabled
    
    def is_bgm_playing(self) -> bool:
        """BGMが再生中かチェック"""
        if not self.enabled:
            return False
        return pygame.mixer.music.get_busy()
    
    def cleanup(self):
        """リソースをクリーンアップ"""
        if self.enabled:
            self.stop_bgm()
            pygame.mixer.quit()
