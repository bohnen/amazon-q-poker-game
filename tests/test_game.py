"""Tests for the game module."""

import pytest
from unittest.mock import patch, MagicMock
from aws_poker.game import Game


@pytest.fixture
def mock_pygame():
    """Mock pygame for testing."""
    with patch('aws_poker.game.pygame') as mock:
        # Mock display.set_mode to return a surface
        mock.display.set_mode.return_value = MagicMock()
        # Mock time.Clock to return a clock
        mock.time.Clock.return_value = MagicMock()
        yield mock


def test_game_initialization(mock_pygame):
    """Test game initialization."""
    game = Game(width=800, height=600, title="Test Game")
    
    # Check that pygame was initialized
    mock_pygame.init.assert_called_once()
    
    # Check that the display was set up correctly
    mock_pygame.display.set_mode.assert_called_once_with((800, 600))
    mock_pygame.display.set_caption.assert_called_once_with("Test Game")
    
    # Check that the clock was created
    mock_pygame.time.Clock.assert_called_once()
    
    # Check game attributes
    assert game.width == 800
    assert game.height == 600
    assert game.running is False
    assert game.fps == 60


def test_game_run(mock_pygame):
    """Test game run method."""
    game = Game()
    
    # Set up the mocks
    game.handle_events = MagicMock()
    game.update = MagicMock()
    game.render = MagicMock()
    mock_pygame.quit = MagicMock()
    
    # Make the game run for one iteration and then stop
    def run_once_side_effect(*args, **kwargs):
        if hasattr(run_once_side_effect, 'called'):
            game.running = False
        else:
            run_once_side_effect.called = True
    
    game.clock.tick = MagicMock(side_effect=run_once_side_effect)
    
    # Run the game
    game.run()
    
    # Check that methods were called
    assert game.handle_events.call_count >= 1
    assert game.update.call_count >= 1
    assert game.render.call_count >= 1
    mock_pygame.quit.assert_called_once()
