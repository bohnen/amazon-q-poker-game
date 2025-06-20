"""Tests for the example module."""

from aws_poker import example


def test_hello():
    """Test the hello function."""
    assert example.hello() == "Hello from AWS Porker!"
