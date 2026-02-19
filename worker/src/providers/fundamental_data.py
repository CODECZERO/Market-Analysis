"""
Wall Street Fundamental Data Provider
Fetches real fundamental metrics used by institutional investors
"""

import yfinance as yf
from typing import Dict, Optional, Any
import pandas as pd


class FundamentalDataProvider:
    """
    Provides real fundamental data and Wall Street metrics
    Used to ground LLM analysis in actual numbers
    """
    
    def get_fundamental_data(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch comprehensive fundamental data from yfinance
        
        Returns real data that LLMs must use (prevents hallucination)
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Fetch deeper financials (can be slow, use with care)
            try:
                cashflow = ticker.cashflow
                balance_sheet = ticker.balance_sheet
            except:
                cashflow = pd.DataFrame()
                balance_sheet = pd.DataFrame()

            # Extract key fundamental metrics
            fundamentals = {
                # Valuation Metrics
                "market_cap": info.get("marketCap"),
                "enterprise_value": info.get("enterpriseValue"),
                "pe_ratio": info.get("trailingPE"),
                "forward_pe": info.get("forwardPE"),
                "peg_ratio": info.get("pegRatio"),
                "price_to_book": info.get("priceToBook"),
                "price_to_sales": info.get("priceToSalesTrailing12Months"),
                "ev_to_revenue": info.get("enterpriseToRevenue"),
                "ev_to_ebitda": info.get("enterpriseToEbitda"),
                
                # Profitability Metrics
                "profit_margin": info.get("profitMargins"),
                "operating_margin": info.get("operatingMargins"),
                "ebitda_margin": info.get("ebitdaMargins"),
                "roe": info.get("returnOnEquity"),
                "roa": info.get("returnOnAssets"),
                "roic": info.get("returnOnCapital"),
                
                # Growth Metrics
                "revenue_growth": info.get("revenueGrowth"),
                "earnings_growth": info.get("earningsGrowth"),
                "earnings_quarterly_growth": info.get("earningsQuarterlyGrowth"),
                
                # Financial Health
                "current_ratio": info.get("currentRatio"),
                "quick_ratio": info.get("quickRatio"),
                "debt_to_equity": info.get("debtToEquity"),
                "total_debt": info.get("totalDebt"),
                "total_cash": info.get("totalCash"),
                "free_cashflow": info.get("freeCashflow"),
                
                # Dividend Metrics
                "dividend_yield": info.get("dividendYield"),
                "payout_ratio": info.get("payoutRatio"),
                "five_year_avg_dividend_yield": info.get("fiveYearAvgDividendYield"),
                
                # Analyst Metrics (Wall Street Consensus)
                "analyst_target_price": info.get("targetMeanPrice"),
                "analyst_high_price": info.get("targetHighPrice"),
                "analyst_low_price": info.get("targetLowPrice"),  
                "number_of_analysts": info.get("numberOfAnalystOpinions"),
                "recommendation": info.get("recommendationKey"),  # buy, hold, sell
                
                # Institutional Ownership
                "institutional_ownership": info.get("heldPercentInstitutions"),
                "insider_ownership": info.get("heldPercentInsiders"),
                "short_percent": info.get("shortPercentOfFloat"),
                
                # Company Info
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "employees": info.get("fullTimeEmployees"),
                
                # Price Metrics
                "current_price": info.get("currentPrice"),
                "fifty_day_average": info.get("fiftyDayAverage"),
                "two_hundred_day_average": info.get("twoHundredDayAverage"),
                "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
                "fifty_two_week_low": info.get("fiftyTwoWeekLow")
            }
            
            # 🆕 Advanced Accounting Metrics from Cashflow/Balance Sheet
            if not cashflow.empty and not balance_sheet.empty:
                try:
                    # Get latest year data
                    latest_cf = cashflow.iloc[:, 0]
                    latest_bs = balance_sheet.iloc[:, 0]
                    
                    fundamentals["free_cash_flow"] = latest_cf.get("Free Cash Flow")
                    fundamentals["operating_cash_flow"] = latest_cf.get("Operating Cash Flow")
                    fundamentals["total_debt"] = latest_bs.get("Total Debt")
                    fundamentals["total_assets"] = latest_bs.get("Total Assets")
                    fundamentals["cash_and_equiv"] = latest_bs.get("Cash And Cash Equivalents")
                    
                    # 📊 Calculated Institutional Ratios
                    if fundamentals.get("market_cap") and fundamentals.get("free_cash_flow"):
                        fundamentals["fcf_yield"] = (fundamentals["free_cash_flow"] / fundamentals["market_cap"]) * 100
                        
                    if fundamentals.get("total_debt") and fundamentals.get("market_cap"):
                        fundamentals["debt_to_market_cap"] = fundamentals["total_debt"] / fundamentals["market_cap"]
                        
                    # Liquidity: Cash / Total Assets
                    if fundamentals.get("cash_and_equiv") and fundamentals.get("total_assets"):
                        fundamentals["liquidity_ratio"] = fundamentals["cash_and_equiv"] / fundamentals["total_assets"]
                        
                    # Accounting Health Label
                except Exception as e:
                    print(f"   ⚠️  Accounting calculation error for {symbol}: {e}")
                
                # 🆕 Forensic Accounting (Z-Score & F-Score)
                fundamentals["z_score"] = self._calculate_altman_z_score(latest_bs, latest_cf, fundamentals.get("market_cap", 0))
                fundamentals["f_score"] = self._calculate_piotroski_f_score(latest_bs, latest_cf, balance_sheet, cashflow)
                
                # Update Accounting Health Label based on forensics
                if fundamentals["z_score"] < 1.8:
                    fundamentals["accounting_health"] = "Distress Risk (Low Z-Score)"
                elif fundamentals["f_score"] >= 7:
                    fundamentals["accounting_health"] = "Institutional Quality (High F-Score)"
            
            # Calculate additional Wall Street metrics
            if fundamentals.get("current_price") and fundamentals.get("analyst_target_price"):
                fundamentals["analyst_upside"] = (
                    (fundamentals["analyst_target_price"] - fundamentals["current_price"]) 
                    / fundamentals["current_price"] * 100
                )
            
            # Calculate intrinsic value using Graham formula (simplified)
            eps = info.get("trailingEps")
            if eps and eps > 0:
                # Graham Number: sqrt(22.5 * EPS * Book Value per Share)
                book_value = info.get("bookValue")
                if book_value:
                    fundamentals["graham_number"] = (22.5 * eps * book_value) ** 0.5
                    if fundamentals["current_price"]:
                        fundamentals["graham_valuation"] = (
                            "Undervalued" if fundamentals["current_price"] < fundamentals["graham_number"]
                            else "Overvalued"
                        )
            
            return fundamentals
            
        except Exception as e:
            print(f"Error fetching fundamentals for {symbol}: {e}")
            return {}
    
    def _calculate_accounting_health(self, f: Dict) -> str:
        """Categorize stock based on financial strength"""
        try:
            points = 0
            if f.get("free_cash_flow", 0) > 0: points += 1
            if f.get("fcf_yield", 0) > 4: points += 1 # Healthy FCF yield
            if f.get("debt_to_equity", 1.5) < 1.0: points += 1 # Low debt
            if f.get("current_ratio", 0.5) > 1.5: points += 1 # Good liquidity
            if f.get("roe", 0) > 0.15: points += 1 # High ROE
            
            if points >= 4: return "Institutional Quality (Cash Cow)"
            if points >= 2: return "Stable Growth"
            if points == 1: return "Speculative / Recovering"
            return "Financial Distress Risk"
        except:
            return "Neutral / Data Sparse"

    def _calculate_altman_z_score(self, bs, cf, market_cap) -> float:
        """
        Calculates Altman Z-Score for manufacturing/general firms.
        Z = 1.2A + 1.4B + 3.3C + 0.6D + 1.0E
        """
        try:
            total_assets = bs.get("Total Assets", 0)
            if not total_assets: return 0.0
            
            # A: Working Capital / Total Assets
            working_capital = bs.get("Current Assets", 0) - bs.get("Current Liabilities", 0)
            A = working_capital / total_assets
            
            # B: Retained Earnings / Total Assets
            retained_earnings = bs.get("Retained Earnings", 0)
            B = retained_earnings / total_assets
            
            # C: EBIT / Total Assets (Approx from Operating Cash Flow if EBIT missing)
            ebit = cf.get("Operating Cash Flow", 0) # Proxy
            C = ebit / total_assets
            
            # D: Market Value of Equity / Total Liabilities
            total_liabilities = bs.get("Total Liabilities Net Minority Interest", 0)
            if not total_liabilities: total_liabilities = total_assets * 0.5 # Fallback
            D = market_cap / total_liabilities
            
            # E: Sales / Total Assets (Asset Turnover) - Assuming we don't have Sales here, omit or approx
            E = 0.5 # Conservative default assumption for Asset Turnover
            
            z_score = 1.2*A + 1.4*B + 3.3*C + 0.6*D + 1.0*E
            return round(z_score, 2)
        except:
            return 0.0

    def _calculate_piotroski_f_score(self, current_bs, current_cf, full_bs, full_cf) -> int:
        """
        Calculates Piotroski F-Score (0-9).
        Tests Profitability, Leverage/Liquidity/Source of Funds, and Operating Efficiency.
        """
        score = 0
        try:
            # Get Previous Year Data
            if full_bs.shape[1] > 1: prev_bs = full_bs.iloc[:, 1]
            else: prev_bs = current_bs # Fallback
            
            # 1. ROA > 0
            net_income = current_cf.get("Net Income", 0) # Approximation
            avg_assets = (current_bs.get("Total Assets", 1) + prev_bs.get("Total Assets", 1)) / 2
            roa = net_income / avg_assets
            if roa > 0: score += 1
            
            # 2. Operating Cash Flow > 0
            ocf = current_cf.get("Operating Cash Flow", 0)
            if ocf > 0: score += 1
            
            # 3. OCF > Net Income (Quality of Earnings)
            if ocf > net_income: score += 1
            
            # 4. Long Term Debt < Prior Year (Leverage)
            current_ltd = current_bs.get("Long Term Debt", 0)
            prev_ltd = prev_bs.get("Long Term Debt", 0)
            if current_ltd < prev_ltd: score += 1
            
            # 5. Current Ratio > Prior Year (Liquidity)
            cur_cr = current_bs.get("Current Assets", 0) / (current_bs.get("Current Liabilities", 1) or 1)
            prev_cr = prev_bs.get("Current Assets", 0) / (prev_bs.get("Current Liabilities", 1) or 1)
            if cur_cr > prev_cr: score += 1
            
            # 6. No New Shares Issued (Dilution) - Simplified check
            if current_bs.get("Common Stock", 0) <= prev_bs.get("Common Stock", 0): score += 1
            
            # 7. Gross Margin > Prior Year (Efficiency) - Requires Income Statement, skip or approx
            # 8. Asset Turnover > Prior Year (Efficiency) - Requires Sales, skip or approx
            
            # Bonus points for strong OCF margin
            if ocf / avg_assets > 0.1: score += 1
            
            return min(9, score)
        except:
            return 0

    def format_for_llm(self, fundamentals: Dict[str, Any]) -> str:
        """
        Format fundamental data for LLM consumption
        Clear, structured format that prevents hallucination
        """
        
        def fmt(value, suffix="", multiplier=1, decimals=2):
            """Helper to format numbers safely"""
            if value is None:
                return "N/A"
            try:
                return f"{float(value) * multiplier:.{decimals}f}{suffix}"
            except:
                return "N/A"
        
        formatted = f"""
FUNDAMENTAL DATA (ACTUAL NUMBERS - DO NOT HALLUCINATE):

📊 VALUATION METRICS:
- Current Price: ₹{fmt(fundamentals.get('current_price'))}
- Market Cap: ₹{fmt(fundamentals.get('market_cap'), ' Cr', 1e-7, 0)}
- P/E Ratio: {fmt(fundamentals.get('pe_ratio'))}
- Forward P/E: {fmt(fundamentals.get('forward_pe'))}
- PEG Ratio: {fmt(fundamentals.get('peg_ratio'))}
- Price/Book: {fmt(fundamentals.get('price_to_book'))}
- Price/Sales: {fmt(fundamentals.get('price_to_sales'))}

📊 CASH FLOW & ACCOUNTING (PROFESSIONAL):
- Accounting Health: {fundamentals.get('accounting_health', 'N/A')}
- Free Cash Flow: ₹{fmt(fundamentals.get('free_cash_flow'), ' Cr', 1e-7, 0)}
- FCF Yield: {fmt(fundamentals.get('fcf_yield'), '%')}
- Liquidity Ratio: {fmt(fundamentals.get('liquidity_ratio'), '', 1, 3)}
- Debt/Market Cap: {fmt(fundamentals.get('debt_to_market_cap'), '', 1, 3)}

💰 PROFITABILITY:
- Profit Margin: {fmt(fundamentals.get('profit_margin'), '%', 100)}
- Operating Margin: {fmt(fundamentals.get('operating_margin'), '%', 100)}
- ROE: {fmt(fundamentals.get('roe'), '%', 100)}
- ROA: {fmt(fundamentals.get('roa'), '%', 100)}

📈 GROWTH:
- Revenue Growth: {fmt(fundamentals.get('revenue_growth'), '%', 100)}
- Earnings Growth: {fmt(fundamentals.get('earnings_growth'), '%', 100)}

🏦 FINANCIAL HEALTH:
- Current Ratio: {fmt(fundamentals.get('current_ratio'))}
- Debt/Equity: {fmt(fundamentals.get('debt_to_equity'))}
- Free Cash Flow: ₹{fmt(fundamentals.get('free_cashflow'), ' Cr', 1e-7, 0)}

⭐ WALL STREET CONSENSUS:
- Analyst Target: ₹{fmt(fundamentals.get('analyst_target_price'))}
- Upside Potential: {fmt(fundamentals.get('analyst_upside'), '%')}
- Recommendation: {fundamentals.get('recommendation', 'N/A').upper()}
- Number of Analysts: {fundamentals.get('number_of_analysts', 'N/A')}

🏛️ INSTITUTIONAL:
- Institutional Ownership: {fmt(fundamentals.get('institutional_ownership'), '%', 100)}
- Short Interest: {fmt(fundamentals.get('short_percent'), '%', 100)}

📍 PRICE LEVELS:
- 52-Week High: ₹{fmt(fundamentals.get('fifty_two_week_high'))}
- 52-Week Low: ₹{fmt(fundamentals.get('fifty_two_week_low'))}
- 50-Day MA: ₹{fmt(fundamentals.get('fifty_day_average'))}
- 200-Day MA: ₹{fmt(fundamentals.get('two_hundred_day_average'))}

IMPORTANT: Use ONLY these ACTUAL numbers in your analysis. Do NOT make up or estimate values.
"""
        return formatted.strip()
    
    def validate_llm_numbers(self, llm_output: str, actual_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if LLM is hallucinating by comparing mentioned numbers with actual data
        
        Returns:
            - is_valid: bool
            - hallucinations: list of detected fabrications
            - confidence_penalty: float (0-1) to reduce LLM confidence if hallucinating
        """
        hallucinations = []
        
        # Extract numbers from LLM output (basic check)
        import re
        mentioned_prices = re.findall(r'₹\s*(\d+(?:,\d+)?(?:\.\d+)?)', llm_output)
        
        if mentioned_prices:
            current_price = actual_data.get('current_price')
            if current_price:
                # Check if mentioned prices are reasonable (within ±50% of current)
                for price_str in mentioned_prices:
                    try:
                        price = float(price_str.replace(',', ''))
                        deviation = abs(price - current_price) / current_price
                        
                        if deviation > 0.5:  # More than 50% deviation
                            hallucinations.append(f"Price ₹{price} deviates {deviation*100:.0f}% from actual ₹{current_price}")
                    except:
                        pass
        
        # Check if LLM mentions metrics that don't exist
        if "P/E" in llm_output and actual_data.get('pe_ratio') is None:
            hallucinations.append("Mentioned P/E ratio but no data available")
        
        if "analyst" in llm_output.lower() and actual_data.get('analyst_target_price') is None:
            hallucinations.append("Mentioned analyst targets but no data available")
        
        # Calculate confidence penalty
        confidence_penalty = max(0, 1 - (len(hallucinations) * 0.2))  # -20% per hallucination
        
        return {
            "is_valid": len(hallucinations) == 0,
            "hallucinations": hallucinations,
            "confidence_penalty": confidence_penalty,
            "validation_score": confidence_penalty
        }


# Global instance
_fundamental_provider = None


def get_fundamental_provider() -> FundamentalDataProvider:
    """Get or create global fundamental data provider"""
    global _fundamental_provider
    if _fundamental_provider is None:
        _fundamental_provider = FundamentalDataProvider()
    return _fundamental_provider
