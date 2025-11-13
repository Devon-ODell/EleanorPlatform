"""
AI-Powered Arbitrage Decision Engine
Analyzes scraped DEX data and makes trading decisions

Integrates with:
- Selenium DEX scraper
- Existing arbitrage detection
- Risk management
- Execution engine
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import logging
import json

# ML imports
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
import joblib


@dataclass
class ArbitrageSignal:
    """AI-generated arbitrage signal"""
    timestamp: datetime
    pair: str
    buy_dex: str
    sell_dex: str
    buy_price: float
    sell_price: float
    gross_spread_pct: float
    net_profit_pct: float
    expected_profit_usd: float
    confidence_score: float  # 0-1, AI confidence
    risk_score: float  # 0-1, higher = riskier
    recommended_size_usd: float
    execution_priority: str  # 'high', 'medium', 'low'
    reasoning: str  # AI explanation


class FeatureEngineer:
    """
    Extract features from DEX price data for ML models
    """

    def __init__(self):
        self.scaler = StandardScaler()

    def extract_features(self, prices: List[dict], historical_data: Optional[pd.DataFrame] = None) -> np.ndarray:
        """
        Extract ML features from price data

        Features:
        - Spread between DEXs
        - Liquidity metrics
        - Volume metrics
        - Historical volatility
        - Time-based features
        - Network congestion indicators
        """
        features = []

        for price in prices:
            feature_vector = []

            # Price spread features
            if len(prices) >= 2:
                prices_sorted = sorted([p['price'] for p in prices])
                spread = (prices_sorted[-1] - prices_sorted[0]) / prices_sorted[0]
                feature_vector.append(spread * 100)  # Spread %

                # Price variance across DEXs
                price_variance = np.var([p['price'] for p in prices])
                feature_vector.append(price_variance)
            else:
                feature_vector.extend([0, 0])

            # Liquidity features
            total_liquidity = sum([p.get('liquidity', 0) for p in prices])
            avg_liquidity = total_liquidity / len(prices) if prices else 0
            feature_vector.extend([
                total_liquidity / 1_000_000,  # Normalize
                avg_liquidity / 1_000_000,
                np.std([p.get('liquidity', 0) for p in prices]) / 1_000_000
            ])

            # Volume features
            total_volume = sum([p.get('volume_24h', 0) for p in prices])
            feature_vector.extend([
                total_volume / 1_000_000,
                total_volume / total_liquidity if total_liquidity > 0 else 0  # Turnover ratio
            ])

            # Time-based features
            hour = datetime.now().hour
            day_of_week = datetime.now().weekday()
            feature_vector.extend([
                hour / 24,  # Normalize
                day_of_week / 7,
                1 if 9 <= hour <= 17 else 0,  # Trading hours
                1 if day_of_week < 5 else 0   # Weekday
            ])

            # DEX diversity (more DEXs = better)
            num_dexs = len(prices)
            feature_vector.append(num_dexs)

            # Fee tier features (if available)
            avg_fee = np.mean([self._parse_fee(p.get('fee_tier', '0.3%')) for p in prices])
            feature_vector.append(avg_fee)

            # Historical features (if available)
            if historical_data is not None:
                # TODO: Add historical volatility, trend, etc.
                pass

            features.append(feature_vector)

        return np.array(features)

    def _parse_fee(self, fee_str: str) -> float:
        """Parse fee string like '0.3%' to 0.003"""
        try:
            return float(fee_str.replace('%', '')) / 100
        except:
            return 0.003


class OpportunityClassifier:
    """
    ML model to classify arbitrage opportunities as profitable or not
    """

    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_trained = False

    def train(self, features: np.ndarray, labels: np.ndarray):
        """
        Train the classifier

        Args:
            features: Feature matrix
            labels: Binary labels (1 = profitable, 0 = not profitable)
        """
        features_scaled = self.scaler.fit_transform(features)
        self.model.fit(features_scaled, labels)
        self.is_trained = True

        # Feature importance
        importance = self.model.feature_importances_
        logging.info(f"Feature importances: {importance}")

    def predict_probability(self, features: np.ndarray) -> np.ndarray:
        """
        Predict probability of profitability

        Returns:
            Array of probabilities [0-1]
        """
        if not self.is_trained:
            logging.warning("Model not trained, returning default probabilities")
            return np.ones(len(features)) * 0.5

        features_scaled = self.scaler.transform(features)
        probabilities = self.model.predict_proba(features_scaled)[:, 1]
        return probabilities

    def save(self, path: str):
        """Save model to disk"""
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'is_trained': self.is_trained
        }, path)

    def load(self, path: str):
        """Load model from disk"""
        data = joblib.load(path)
        self.model = data['model']
        self.scaler = data['scaler']
        self.is_trained = data['is_trained']


class ProfitPredictor:
    """
    Regression model to predict actual profit amount
    """

    def __init__(self):
        self.model = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_trained = False

    def train(self, features: np.ndarray, profits: np.ndarray):
        """Train profit predictor"""
        features_scaled = self.scaler.fit_transform(features)
        self.model.fit(features_scaled, profits)
        self.is_trained = True

    def predict(self, features: np.ndarray) -> np.ndarray:
        """Predict profit amounts"""
        if not self.is_trained:
            return np.zeros(len(features))

        features_scaled = self.scaler.transform(features)
        predictions = self.model.predict(features_scaled)
        return predictions


class RiskAssessment:
    """
    Assess risk of arbitrage opportunities
    """

    def __init__(self):
        pass

    def calculate_risk_score(self,
                            spread: float,
                            liquidity: float,
                            volume_24h: float,
                            num_dexs: int,
                            historical_volatility: float = None) -> float:
        """
        Calculate risk score [0-1]

        Risk factors:
        - Low liquidity = high risk
        - High spread = potentially high risk (too good to be true)
        - Low volume = high risk
        - Few DEXs = higher risk
        - High volatility = higher risk
        """
        risk = 0.0

        # Liquidity risk (low liquidity = high risk)
        if liquidity < 100_000:
            risk += 0.3
        elif liquidity < 500_000:
            risk += 0.2
        elif liquidity < 1_000_000:
            risk += 0.1

        # Spread risk (abnormally high spread = suspicious)
        if spread > 5:  # > 5% spread
            risk += 0.3
        elif spread > 3:
            risk += 0.2
        elif spread > 2:
            risk += 0.1

        # Volume risk
        if volume_24h < 50_000:
            risk += 0.2
        elif volume_24h < 200_000:
            risk += 0.1

        # DEX diversity (fewer DEXs = higher risk)
        if num_dexs < 3:
            risk += 0.2
        elif num_dexs < 5:
            risk += 0.1

        # Cap at 1.0
        return min(risk, 1.0)


class ArbitrageDecisionEngine:
    """
    Main AI decision engine for arbitrage
    Integrates all components
    """

    def __init__(self,
                 min_confidence: float = 0.6,
                 min_profit_pct: float = 0.5,
                 max_risk_score: float = 0.6):
        self.min_confidence = min_confidence
        self.min_profit_pct = min_profit_pct
        self.max_risk_score = max_risk_score

        # Initialize components
        self.feature_engineer = FeatureEngineer()
        self.opportunity_classifier = OpportunityClassifier()
        self.profit_predictor = ProfitPredictor()
        self.risk_assessor = RiskAssessment()

        # Historical data for learning
        self.trade_history = []

    def analyze_scraped_data(self, scraped_data: Dict[str, List[dict]]) -> List[ArbitrageSignal]:
        """
        Analyze scraped DEX data and generate arbitrage signals

        Args:
            scraped_data: Dictionary mapping pairs to list of price data
                         Format: {'ETH/USDC': [{'dex': 'uniswap_v3', 'price': 3500, ...}, ...]}

        Returns:
            List of ArbitrageSignal objects
        """
        signals = []

        for pair, prices in scraped_data.items():
            if len(prices) < 2:
                continue  # Need at least 2 DEXs to arbitrage

            # Find best buy and sell opportunities
            prices_sorted = sorted(prices, key=lambda x: x['price'])
            buy_candidate = prices_sorted[0]  # Lowest price
            sell_candidate = prices_sorted[-1]  # Highest price

            # Calculate gross spread
            gross_spread_pct = ((sell_candidate['price'] - buy_candidate['price']) /
                               buy_candidate['price']) * 100

            if gross_spread_pct <= 0:
                continue  # No arbitrage opportunity

            # Extract features for ML
            features = self.feature_engineer.extract_features(prices)

            # Get AI confidence (probability of profitability)
            confidence = self.opportunity_classifier.predict_probability(features)[0]

            # Predict expected profit
            predicted_profit_pct = self.profit_predictor.predict(features)[0]

            # Calculate risk score
            total_liquidity = sum([p.get('liquidity', 0) for p in prices])
            total_volume = sum([p.get('volume_24h', 0) for p in prices])
            risk_score = self.risk_assessor.calculate_risk_score(
                spread=gross_spread_pct,
                liquidity=total_liquidity,
                volume_24h=total_volume,
                num_dexs=len(prices)
            )

            # Calculate net profit (estimate)
            # Account for fees, slippage, gas
            estimated_fees = self._estimate_total_fees(buy_candidate, sell_candidate)
            estimated_slippage = self._estimate_slippage(total_liquidity)
            net_profit_pct = gross_spread_pct - estimated_fees - estimated_slippage

            if net_profit_pct < self.min_profit_pct:
                continue

            # Calculate recommended size
            recommended_size = self._calculate_optimal_size(
                liquidity=total_liquidity,
                risk_score=risk_score,
                confidence=confidence
            )

            expected_profit_usd = (net_profit_pct / 100) * recommended_size

            # Determine execution priority
            priority = self._determine_priority(
                net_profit_pct=net_profit_pct,
                confidence=confidence,
                risk_score=risk_score
            )

            # Generate reasoning
            reasoning = self._generate_reasoning(
                gross_spread_pct=gross_spread_pct,
                net_profit_pct=net_profit_pct,
                confidence=confidence,
                risk_score=risk_score,
                liquidity=total_liquidity
            )

            # Create signal if passes filters
            if confidence >= self.min_confidence and risk_score <= self.max_risk_score:
                signal = ArbitrageSignal(
                    timestamp=datetime.now(),
                    pair=pair,
                    buy_dex=buy_candidate['dex'],
                    sell_dex=sell_candidate['dex'],
                    buy_price=buy_candidate['price'],
                    sell_price=sell_candidate['price'],
                    gross_spread_pct=gross_spread_pct,
                    net_profit_pct=net_profit_pct,
                    expected_profit_usd=expected_profit_usd,
                    confidence_score=confidence,
                    risk_score=risk_score,
                    recommended_size_usd=recommended_size,
                    execution_priority=priority,
                    reasoning=reasoning
                )
                signals.append(signal)

        # Sort by expected profit (highest first)
        signals.sort(key=lambda x: x.expected_profit_usd, reverse=True)

        return signals

    def _estimate_total_fees(self, buy_data: dict, sell_data: dict) -> float:
        """Estimate total fees in percentage"""
        # Trading fees
        buy_fee = self.feature_engineer._parse_fee(buy_data.get('fee_tier', '0.3%'))
        sell_fee = self.feature_engineer._parse_fee(sell_data.get('fee_tier', '0.3%'))

        # Gas fees (estimate based on DEX)
        gas_fee_usd = self._estimate_gas_cost(buy_data['dex']) + self._estimate_gas_cost(sell_data['dex'])

        # Convert gas fee to percentage (assume $1000 trade size)
        gas_fee_pct = (gas_fee_usd / 1000) * 100

        return (buy_fee + sell_fee) * 100 + gas_fee_pct

    def _estimate_gas_cost(self, dex: str) -> float:
        """Estimate gas cost for a DEX"""
        gas_costs = {
            'uniswap_v2': 15.0,
            'uniswap_v3': 12.0,
            'pancakeswap_v3': 0.5,  # BSC is cheaper
            'aerodrome': 2.0,  # Base is cheaper
            'fluid': 10.0,
            'orca': 0.01,  # Solana is very cheap
        }
        return gas_costs.get(dex, 10.0)

    def _estimate_slippage(self, liquidity: float, trade_size: float = 1000) -> float:
        """Estimate slippage percentage"""
        if liquidity <= 0:
            return 5.0  # High slippage

        impact = trade_size / liquidity
        if impact < 0.01:
            return 0.1
        elif impact < 0.05:
            return 0.5
        elif impact < 0.1:
            return 1.0
        else:
            return 2.0

    def _calculate_optimal_size(self,
                               liquidity: float,
                               risk_score: float,
                               confidence: float,
                               max_size: float = 10000) -> float:
        """Calculate optimal trade size"""
        # Base size on liquidity (use 1-2% of total liquidity)
        size_from_liquidity = liquidity * 0.015

        # Adjust for risk (lower risk = larger size)
        risk_multiplier = 1 - risk_score

        # Adjust for confidence (higher confidence = larger size)
        confidence_multiplier = confidence

        optimal_size = size_from_liquidity * risk_multiplier * confidence_multiplier

        # Ensure within bounds
        optimal_size = max(100, min(optimal_size, max_size))

        return optimal_size

    def _determine_priority(self,
                           net_profit_pct: float,
                           confidence: float,
                           risk_score: float) -> str:
        """Determine execution priority"""
        score = net_profit_pct * confidence * (1 - risk_score)

        if score > 2.0:
            return 'high'
        elif score > 1.0:
            return 'medium'
        else:
            return 'low'

    def _generate_reasoning(self,
                           gross_spread_pct: float,
                           net_profit_pct: float,
                           confidence: float,
                           risk_score: float,
                           liquidity: float) -> str:
        """Generate human-readable reasoning for the signal"""
        reasoning_parts = []

        # Spread analysis
        if gross_spread_pct > 3:
            reasoning_parts.append(f"Large spread ({gross_spread_pct:.2f}%) detected.")
        elif gross_spread_pct > 1:
            reasoning_parts.append(f"Moderate spread ({gross_spread_pct:.2f}%).")
        else:
            reasoning_parts.append(f"Small spread ({gross_spread_pct:.2f}%).")

        # Profitability
        if net_profit_pct > 2:
            reasoning_parts.append(f"High net profit potential ({net_profit_pct:.2f}%).")
        elif net_profit_pct > 0.5:
            reasoning_parts.append(f"Moderate net profit ({net_profit_pct:.2f}%).")
        else:
            reasoning_parts.append(f"Low net profit ({net_profit_pct:.2f}%).")

        # Confidence
        if confidence > 0.8:
            reasoning_parts.append(f"AI high confidence ({confidence:.2%}).")
        elif confidence > 0.6:
            reasoning_parts.append(f"AI moderate confidence ({confidence:.2%}).")
        else:
            reasoning_parts.append(f"AI low confidence ({confidence:.2%}).")

        # Risk
        if risk_score < 0.3:
            reasoning_parts.append("Low risk.")
        elif risk_score < 0.6:
            reasoning_parts.append("Moderate risk.")
        else:
            reasoning_parts.append("High risk.")

        # Liquidity
        if liquidity > 1_000_000:
            reasoning_parts.append(f"Strong liquidity (${liquidity/1e6:.1f}M).")
        elif liquidity > 100_000:
            reasoning_parts.append(f"Adequate liquidity (${liquidity/1e3:.0f}K).")
        else:
            reasoning_parts.append(f"Low liquidity (${liquidity/1e3:.0f}K).")

        return " ".join(reasoning_parts)

    def record_trade_outcome(self,
                            signal: ArbitrageSignal,
                            actual_profit_usd: float,
                            success: bool):
        """
        Record trade outcome for model improvement

        This data can be used to retrain the ML models
        """
        self.trade_history.append({
            'timestamp': datetime.now(),
            'pair': signal.pair,
            'predicted_profit': signal.expected_profit_usd,
            'actual_profit': actual_profit_usd,
            'predicted_confidence': signal.confidence_score,
            'predicted_risk': signal.risk_score,
            'success': success,
            'gross_spread': signal.gross_spread_pct,
            'net_profit_pct': signal.net_profit_pct,
        })

    def retrain_models(self):
        """
        Retrain ML models using historical trade data
        Called periodically to improve AI performance
        """
        if len(self.trade_history) < 100:
            logging.info("Not enough historical data to retrain (need 100+ trades)")
            return

        logging.info(f"Retraining models with {len(self.trade_history)} historical trades...")

        # Prepare training data
        # TODO: Extract features from trade history and retrain models

        logging.info("Models retrained successfully")


def main():
    """Example usage"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Load scraped data (from Selenium scraper)
    with open('dex_prices.json', 'r') as f:
        scraped_data = json.load(f)

    # Initialize decision engine
    engine = ArbitrageDecisionEngine(
        min_confidence=0.6,
        min_profit_pct=0.5,
        max_risk_score=0.6
    )

    # Analyze data and get signals
    signals = engine.analyze_scraped_data(scraped_data)

    # Display signals
    print("\n" + "="*80)
    print("AI ARBITRAGE SIGNALS")
    print("="*80)

    if not signals:
        print("No arbitrage opportunities found.")
    else:
        for i, signal in enumerate(signals, 1):
            print(f"\n#{i} - {signal.pair}")
            print(f"  Priority: {signal.execution_priority.upper()}")
            print(f"  Buy:  {signal.buy_dex} @ ${signal.buy_price:.4f}")
            print(f"  Sell: {signal.sell_dex} @ ${signal.sell_price:.4f}")
            print(f"  Spread: {signal.gross_spread_pct:.2f}% → Net: {signal.net_profit_pct:.2f}%")
            print(f"  Expected Profit: ${signal.expected_profit_usd:.2f}")
            print(f"  Recommended Size: ${signal.recommended_size_usd:.0f}")
            print(f"  AI Confidence: {signal.confidence_score:.1%}")
            print(f"  Risk Score: {signal.risk_score:.2f}/1.0")
            print(f"  Reasoning: {signal.reasoning}")

    # Save signals
    signals_data = [
        {
            'pair': s.pair,
            'buy_dex': s.buy_dex,
            'sell_dex': s.sell_dex,
            'net_profit_pct': s.net_profit_pct,
            'expected_profit_usd': s.expected_profit_usd,
            'confidence': s.confidence_score,
            'risk': s.risk_score,
            'priority': s.execution_priority,
            'reasoning': s.reasoning
        }
        for s in signals
    ]

    with open('arbitrage_signals.json', 'w') as f:
        json.dump(signals_data, f, indent=2)

    print(f"\n✅ Saved {len(signals)} signals to arbitrage_signals.json")


if __name__ == "__main__":
    main()
