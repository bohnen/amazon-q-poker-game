#!/usr/bin/env python
"""Entry point script to run the game."""

from aws_porker.game import Game


def main():
    """Run the game."""
    game = Game(width=1024, height=768, title="AWS Porker")
    game.run()


if __name__ == "__main__":
    main()
