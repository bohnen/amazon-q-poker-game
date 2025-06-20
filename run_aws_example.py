#!/usr/bin/env python
"""Entry point script to run the AWS integration example."""

from aws_poker.aws_game_example import AwsGameExample


def main():
    """Run the AWS integration example."""
    example = AwsGameExample(width=1024, height=768)
    example.run()


if __name__ == "__main__":
    main()
