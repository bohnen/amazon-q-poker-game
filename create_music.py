#!/usr/bin/env python3
"""
AWSポーカーゲーム用の音楽を生成するスクリプト
"""

import numpy as np
import wave
import math
from pathlib import Path

class MusicGenerator:
    """音楽生成クラス"""
    
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.duration = 0
        self.audio_data = []
    
    def note_frequency(self, note, octave=4):
        """音符から周波数を計算"""
        # A4 = 440Hz を基準とした12平均律
        notes = {
            'C': -9, 'C#': -8, 'D': -7, 'D#': -6, 'E': -5, 'F': -4,
            'F#': -3, 'G': -2, 'G#': -1, 'A': 0, 'A#': 1, 'B': 2
        }
        
        if note not in notes:
            return 0  # 休符
        
        # A4からの半音数を計算
        semitones = notes[note] + (octave - 4) * 12
        frequency = 440 * (2 ** (semitones / 12))
        return frequency
    
    def generate_tone(self, frequency, duration, volume=0.3, wave_type='sine'):
        """指定された周波数とデュレーションでトーンを生成"""
        frames = int(duration * self.sample_rate)
        
        if frequency == 0:  # 休符
            return np.zeros(frames)
        
        t = np.linspace(0, duration, frames, False)
        
        if wave_type == 'sine':
            wave_data = np.sin(2 * np.pi * frequency * t)
        elif wave_type == 'square':
            wave_data = np.sign(np.sin(2 * np.pi * frequency * t))
        elif wave_type == 'triangle':
            wave_data = 2 * np.arcsin(np.sin(2 * np.pi * frequency * t)) / np.pi
        else:
            wave_data = np.sin(2 * np.pi * frequency * t)
        
        # エンベロープ（フェードイン・フェードアウト）を適用
        envelope = np.ones(frames)
        fade_frames = int(0.05 * self.sample_rate)  # 50ms のフェード
        
        if frames > fade_frames * 2:
            # フェードイン
            envelope[:fade_frames] = np.linspace(0, 1, fade_frames)
            # フェードアウト
            envelope[-fade_frames:] = np.linspace(1, 0, fade_frames)
        
        return wave_data * envelope * volume
    
    def generate_chord(self, notes, octaves, duration, volume=0.2):
        """和音を生成"""
        chord_data = np.zeros(int(duration * self.sample_rate))
        
        for note, octave in zip(notes, octaves):
            freq = self.note_frequency(note, octave)
            tone = self.generate_tone(freq, duration, volume / len(notes))
            chord_data += tone
        
        return chord_data
    
    def create_aws_poker_music(self):
        """AWSポーカー用のループ音楽を作成"""
        # テンポとビート
        bpm = 120
        beat_duration = 60 / bpm  # 1拍の長さ（秒）
        
        # メロディーライン（Cメジャースケール基調）
        melody_sequence = [
            # 第1フレーズ（8拍）
            ('C', 5, 1), ('E', 5, 1), ('G', 5, 1), ('C', 6, 1),
            ('B', 5, 1), ('A', 5, 1), ('G', 5, 1), ('F', 5, 1),
            
            # 第2フレーズ（8拍）
            ('E', 5, 1), ('D', 5, 1), ('C', 5, 1), ('D', 5, 1),
            ('E', 5, 2), ('G', 5, 2),
            
            # 第3フレーズ（8拍）
            ('A', 5, 1), ('G', 5, 1), ('F', 5, 1), ('E', 5, 1),
            ('D', 5, 1), ('C', 5, 1), ('D', 5, 1), ('E', 5, 1),
            
            # 第4フレーズ（8拍）
            ('C', 5, 2), ('G', 4, 2), ('C', 5, 4),
        ]
        
        # ベースライン
        bass_sequence = [
            # 第1フレーズ
            ('C', 3, 2), ('F', 3, 2), ('G', 3, 2), ('C', 3, 2),
            
            # 第2フレーズ
            ('A', 3, 2), ('F', 3, 2), ('G', 3, 2), ('C', 3, 2),
            
            # 第3フレーズ
            ('F', 3, 2), ('C', 3, 2), ('G', 3, 2), ('C', 3, 2),
            
            # 第4フレーズ
            ('C', 3, 4), ('G', 3, 4),
        ]
        
        # 和音進行
        chord_sequence = [
            # 第1フレーズ
            (['C', 'E', 'G'], [4, 4, 4], 2),
            (['F', 'A', 'C'], [4, 4, 5], 2),
            (['G', 'B', 'D'], [4, 4, 5], 2),
            (['C', 'E', 'G'], [4, 4, 4], 2),
            
            # 第2フレーズ
            (['A', 'C', 'E'], [4, 5, 5], 2),
            (['F', 'A', 'C'], [4, 4, 5], 2),
            (['G', 'B', 'D'], [4, 4, 5], 2),
            (['C', 'E', 'G'], [4, 4, 4], 2),
            
            # 第3フレーズ
            (['F', 'A', 'C'], [4, 4, 5], 2),
            (['C', 'E', 'G'], [4, 4, 4], 2),
            (['G', 'B', 'D'], [4, 4, 5], 2),
            (['C', 'E', 'G'], [4, 4, 4], 2),
            
            # 第4フレーズ
            (['C', 'E', 'G'], [4, 4, 4], 4),
            (['G', 'B', 'D'], [4, 4, 5], 4),
        ]
        
        # 音楽データを生成
        total_duration = sum(beats * beat_duration for _, _, beats in melody_sequence)
        total_frames = int(total_duration * self.sample_rate)
        
        # 各パートを生成
        melody_data = np.zeros(total_frames)
        bass_data = np.zeros(total_frames)
        chord_data = np.zeros(total_frames)
        
        # メロディー生成
        current_time = 0
        for note, octave, beats in melody_sequence:
            duration = beats * beat_duration
            freq = self.note_frequency(note, octave)
            tone = self.generate_tone(freq, duration, volume=0.4, wave_type='sine')
            
            start_frame = int(current_time * self.sample_rate)
            end_frame = start_frame + len(tone)
            
            if end_frame <= len(melody_data):
                melody_data[start_frame:end_frame] += tone
            
            current_time += duration
        
        # ベース生成
        current_time = 0
        for note, octave, beats in bass_sequence:
            duration = beats * beat_duration
            freq = self.note_frequency(note, octave)
            tone = self.generate_tone(freq, duration, volume=0.3, wave_type='sine')
            
            start_frame = int(current_time * self.sample_rate)
            end_frame = start_frame + len(tone)
            
            if end_frame <= len(bass_data):
                bass_data[start_frame:end_frame] += tone
            
            current_time += duration
        
        # 和音生成
        current_time = 0
        for notes, octaves, beats in chord_sequence:
            duration = beats * beat_duration
            chord = self.generate_chord(notes, octaves, duration, volume=0.15)
            
            start_frame = int(current_time * self.sample_rate)
            end_frame = start_frame + len(chord)
            
            if end_frame <= len(chord_data):
                chord_data[start_frame:end_frame] += chord
            
            current_time += duration
        
        # 全パートをミックス
        mixed_audio = melody_data + bass_data + chord_data
        
        # 音量を正規化
        max_amplitude = np.max(np.abs(mixed_audio))
        if max_amplitude > 0:
            mixed_audio = mixed_audio / max_amplitude * 0.8
        
        return mixed_audio
    
    def create_sound_effects(self):
        """効果音を生成"""
        effects = {}
        
        # カードドロー音
        card_draw1 = self.generate_tone(800, 0.1, volume=0.3, wave_type='sine')
        card_draw2 = self.generate_tone(600, 0.1, volume=0.2, wave_type='sine')  # 同じ長さに統一
        card_draw = card_draw1 + card_draw2
        effects['card_draw'] = card_draw
        
        # 役完成音（成功音）
        success_notes = [('C', 5), ('E', 5), ('G', 5), ('C', 6)]
        success_sound = np.zeros(int(0.5 * self.sample_rate))
        current_pos = 0
        
        for note, octave in success_notes:
            freq = self.note_frequency(note, octave)
            tone = self.generate_tone(freq, 0.1, volume=0.4)
            end_pos = current_pos + len(tone)
            if end_pos <= len(success_sound):
                success_sound[current_pos:end_pos] += tone
            current_pos += int(0.05 * self.sample_rate)
        
        effects['hand_complete'] = success_sound
        
        # ゲーム終了音
        game_end_notes = [('C', 5), ('G', 5), ('E', 6), ('C', 6)]
        game_end_sound = np.zeros(int(1.0 * self.sample_rate))
        current_pos = 0
        
        for note, octave in game_end_notes:
            freq = self.note_frequency(note, octave)
            tone = self.generate_tone(freq, 0.2, volume=0.5)
            end_pos = current_pos + len(tone)
            if end_pos <= len(game_end_sound):
                game_end_sound[current_pos:end_pos] += tone
            current_pos += int(0.1 * self.sample_rate)
        
        effects['game_end'] = game_end_sound
        
        return effects
    
    def save_wav(self, audio_data, filename):
        """WAVファイルとして保存"""
        # 16ビット整数に変換
        audio_int16 = (audio_data * 32767).astype(np.int16)
        
        with wave.open(filename, 'w') as wav_file:
            wav_file.setnchannels(1)  # モノラル
            wav_file.setsampwidth(2)  # 16ビット
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(audio_int16.tobytes())

def main():
    """メイン関数"""
    print("AWSポーカー用音楽を生成中...")
    
    generator = MusicGenerator()
    sounds_dir = Path("/Users/bohnen/Project/aws-game/aws-porker/sounds")
    
    # BGM生成
    print("BGMを生成中...")
    bgm_data = generator.create_aws_poker_music()
    bgm_path = sounds_dir / "aws_poker_bgm.wav"
    generator.save_wav(bgm_data, str(bgm_path))
    print(f"BGMを保存しました: {bgm_path}")
    
    # 効果音生成
    print("効果音を生成中...")
    effects = generator.create_sound_effects()
    
    for effect_name, effect_data in effects.items():
        effect_path = sounds_dir / f"{effect_name}.wav"
        generator.save_wav(effect_data, str(effect_path))
        print(f"効果音を保存しました: {effect_path}")
    
    print("音楽生成完了！")
    print(f"生成されたファイル:")
    for file_path in sounds_dir.glob("*.wav"):
        print(f"  - {file_path.name}")

if __name__ == "__main__":
    main()
