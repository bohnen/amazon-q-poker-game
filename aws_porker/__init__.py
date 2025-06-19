"""
AWS Porker - AWSアイコンを使ったポーカーゲーム
"""

__version__ = "0.1.0"

from .card import Card, Deck
from .hand_evaluator import HandEvaluator
from .poker_game import PokerGame
from .sound_manager import SoundManager
from .clipboard_utils import ClipboardManager

def hello():
    """Simple hello function"""
    print("Hello from AWS Porker!")

def list_s3_buckets():
    """Example function to list S3 buckets"""
    print("This would list S3 buckets if AWS credentials were configured")

def run_poker():
    """ポーカーゲームを起動"""
    game = PokerGame()
    game.run()
