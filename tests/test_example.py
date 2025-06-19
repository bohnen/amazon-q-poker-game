"""Tests for the example module."""

from aws_porker import example


def test_hello():
    """Test the hello function."""
    assert example.hello() == "Hello from AWS Porker!"
