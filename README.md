# OSRS-GE-Trading-App-BE

## Project Overview

This project is a backend analysis tool for the Old School RuneScape Grand Exchange (GE). It processes historical price data for GE items and enriches it with a variety of technical indicators to support market analysis and backtesting of trading strategies.

### Current Features
- Loads and processes historical price data for GE items
- Calculates and exports the following technical indicators:
  - Moving Averages (various periods)
  - Bollinger Bands
  - Relative Strength Index (RSI)
  - Moving Average Convergence Divergence (MACD)
- Outputs enriched data in JSON format for further analysis or visualization
- Includes plotting functionality for price and moving averages

## Future Work: Volume-Based and Atypical Market Analysis

Once we have access to volume data, we plan to implement and analyze additional indicators and approaches, including:

### Volume-Based Indicators
- On-Balance Volume (OBV)
- Volume Weighted Average Price (VWAP)
- Other volume-driven metrics

### Atypical Market Analysis Approaches
- Techniques adapted from foreign exchange (forex) and always-on markets
- Rolling window statistics (means, medians, quantiles, volatility)
- Change point detection
- Event-based and player behavior analysis
- Custom statistical and machine learning features

These will help us better understand and model the unique dynamics of the Grand Exchange and similar 24/7 markets.