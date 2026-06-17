# Valuation

## Discounted Cash Flow (DCF)

A DCF values a company by projecting its future free cash flows and discounting them back to present value using the Weighted Average Cost of Capital (WACC).

**Steps:**
1. Project Free Cash Flow (FCF) for 5-10 years
2. Calculate Terminal Value (TV) using either the Gordon Growth Model or Exit Multiple method
3. Discount FCF and TV back to present using WACC
4. Sum to get Enterprise Value
5. Subtract Net Debt to get Equity Value
6. Divide by diluted shares outstanding for implied share price

**Free Cash Flow formula:**
FCF = EBIT × (1 - Tax Rate) + D&A - CapEx - Change in Net Working Capital

**Key assumptions to defend:** Revenue growth rate, EBIT margin trajectory, CapEx as % of revenue, terminal growth rate (typically 2-3%, should not exceed long-term GDP growth), WACC components.

**Common mistakes:** Using equity value when you should use enterprise value; inconsistent growth assumptions between the projection period and terminal value; forgetting to subtract stock-based compensation from FCF.

## Comparable Company Analysis (Trading Comps)

Trading comps value a company by comparing it to similar publicly traded companies using valuation multiples.

**Process:**
1. Select a peer group (same industry, size, growth profile, margin structure)
2. Calculate relevant multiples for each peer: EV/EBITDA, EV/Revenue, P/E, P/B
3. Determine the appropriate range (mean, median, or specific quartile)
4. Apply the selected multiple to the target company's metrics

**Most common multiples:**
- EV/EBITDA: Most widely used; capital-structure neutral, unaffected by D&A differences
- EV/Revenue: Used for high-growth or unprofitable companies
- P/E: Simple but distorted by capital structure and tax differences
- EV/EBIT: Better than P/E for comparing across capital structures

**Enterprise Value = Equity Value + Net Debt + Preferred Stock + Minority Interest - Cash & Equivalents**

**Why EV/EBITDA is preferred over P/E:** EV/EBITDA is capital-structure neutral (comparing enterprise-level metric to enterprise-level value), not distorted by depreciation policy differences, and works for companies with different tax jurisdictions.

## Precedent Transaction Analysis

Values a company by looking at prices paid in comparable M&A transactions.

**Process:**
1. Identify comparable transactions (same industry, similar size, recent timing)
2. Calculate transaction multiples (EV/EBITDA, EV/Revenue at time of deal)
3. Note control premiums paid (typically 20-40% over trading price)
4. Apply to target company's metrics

**Key considerations:**
- Precedent transactions typically yield higher valuations than trading comps due to control premiums
- Adjust for market conditions at time of each transaction
- More recent transactions are more relevant
- Strategic buyers typically pay higher premiums than financial buyers

## Leveraged Buyout (LBO) Analysis

An LBO values a company based on the returns a financial sponsor (PE firm) can generate using significant debt financing.

**Structure:**
- Typical leverage: 4-6x EBITDA
- Equity contribution: 30-50% of total purchase price
- Target IRR: 20-25% over a 3-7 year hold period
- Exit via sale or IPO

**Value creation levers:**
1. Revenue growth (organic and acquisitions)
2. Margin expansion (operational improvements, cost synergies)
3. Debt paydown (using free cash flow to reduce leverage)
4. Multiple expansion (buy low, sell at a higher multiple)

**LBO candidate characteristics:** Stable, predictable cash flows; low capital expenditure requirements; strong market position; opportunities for operational improvement; tangible assets for collateral.

## WACC (Weighted Average Cost of Capital)

WACC represents the blended required return across all sources of capital.

**Formula:**
WACC = (E/V) × Re + (D/V) × Rd × (1 - T)

Where:
- E/V = proportion of equity financing
- D/V = proportion of debt financing
- Re = cost of equity (from CAPM)
- Rd = cost of debt (yield on existing debt or comparable bonds)
- T = marginal tax rate

**CAPM (Cost of Equity):**
Re = Rf + β × (Rm - Rf)

Where:
- Rf = risk-free rate (10-year Treasury yield)
- β = beta (systematic risk relative to market)
- Rm - Rf = equity risk premium (typically 5-7%)

**For small companies:** Add a size premium (1-3%) to the CAPM cost of equity.

## Enterprise Value vs Equity Value

**Enterprise Value (EV):** The value of the entire business, independent of capital structure. Think of it as the price to buy the entire company, including assuming its debt.

**Equity Value:** The value attributable to shareholders only. Market cap = share price × diluted shares outstanding.

**Bridge:**
Enterprise Value = Equity Value + Net Debt + Preferred Stock + Minority Interest

**When to use which:**
- Enterprise Value metrics (EV/EBITDA, EV/Revenue): Use with unlevered metrics that are available to all capital providers
- Equity Value metrics (P/E, P/B): Use with levered metrics that are available only to equity holders

**Critical rule:** Never divide an enterprise-level metric by equity value, or vice versa. EV/Net Income is WRONG. P/EBITDA is WRONG.

## Terminal Value

Terminal Value captures the value of cash flows beyond the explicit projection period.

**Method 1: Gordon Growth Model (Perpetuity Growth)**
TV = FCF(n+1) / (WACC - g)

Where g = long-term sustainable growth rate (typically 2-3%)

**Method 2: Exit Multiple**
TV = EBITDA(n) × Exit EV/EBITDA Multiple

**Important:** Terminal value typically represents 60-80% of total DCF value. Small changes in terminal growth rate or exit multiple have enormous impact on valuation. Always run sensitivity analysis on these assumptions.
