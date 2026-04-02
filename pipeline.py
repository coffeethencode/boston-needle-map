#!/usr/bin/env python3
"""Backward-compatibility wrapper. Use `uv run boston-needle-map run` instead."""
from boston_needle_map.cli import app

if __name__ == "__main__":
    app()
