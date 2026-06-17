# Technical & Brainteasers

## Mental Math Frameworks

Mental math in finance interviews tests your poise under pressure, not just your calculation ability. Always articulate your thought process out loud.

**Key techniques:**
1. **Factorization:** Break down difficult numbers. (e.g., 18 × 15 = 18 × 10 + 18 × 5 = 180 + 90 = 270)
2. **Estimation (Rule of 72):** To find how long it takes an investment to double, divide 72 by the annual return rate. (e.g., at 8% return, it takes 72/8 = 9 years to double)
3. **Fractions to Decimals:** Memorize 1/6 (16.7%), 1/7 (14.3%), 1/8 (12.5%), 1/9 (11.1%), 1/12 (8.3%), 1/16 (6.25%).
4. **Moving the Decimal:** For large numbers, drop the zeros, calculate, then add them back. (e.g., $1.5B / 300M = 15 / 3 = 5x)

**Common trick questions:**
- What is 17 squared? (289)
- What is the square root of 0.1? (~0.316, because 0.3 × 0.3 = 0.09)

## Expected Value & Probability

Expected Value (EV) is the probability-weighted average of all possible outcomes.

**Formula:**
EV = P(Outcome 1) × Value(Outcome 1) + P(Outcome 2) × Value(Outcome 2) + ...

**Common Scenario: Coin Flipping Games**
"I flip a coin. If it's heads, you win $2. If it's tails, you pay me $1. How much would you pay to play this game?"
*Answer:* EV = (0.5 × $2) + (0.5 × -$1) = $1.00 - $0.50 = $0.50. You should pay up to $0.49 to play and maintain a positive edge.

**Common Scenario: Russian Roulette Options**
Questions involving probability of default or contingent payouts rely on standard EV frameworks. Always state assumptions (e.g., independence of events).

## Market Sizing (Guesstimates)

Market sizing questions test your ability to structure ambiguous problems, make reasonable assumptions, and sanity-check your conclusions.

**The Framework:**
1. **Clarify:** Define the exact scope (e.g., "Number of gas stations in the US").
2. **Structure:** Choose top-down (population/demographics) or bottom-up (capacity/supply).
3. **Assume:** State your assumptions clearly. Use round numbers (US population = 300M or 330M).
4. **Calculate:** Walk through the math aloud.
5. **Sanity Check:** Does the final number make logical sense?

**Example: How many gas stations in the US?**
*Population Approach:*
- US Population: 330M
- Assume 3 people per household = 110M households.
- Assume 2 cars per household = 220M cars.
- Each car fills up once a week.
- A gas station has 8 pumps, each pump takes 5 mins per car = 12 cars per hour per pump = ~100 cars per hour per station.
- If open 15 hours a day, one station serves 1,500 cars a day, or ~10,000 a week.
- Total stations = 220M / 10,000 = 22,000 stations. (Actual is ~145,000, so we might have overestimated cars per station, but the logic is what matters).

## Logic Puzzles & Brainteasers

These test structured problem-solving.

**The Clock Angle Problem:**
"What is the angle between the hour and minute hands at 3:15?"
*Answer:* The minute hand is exactly at 3 (90 degrees). The hour hand moves 30 degrees per hour (360/12). In 15 minutes (1/4 of an hour), it has moved 1/4 of 30 degrees = 7.5 degrees past the 3. The angle is 7.5 degrees.

**The Heavy Ball Problem:**
"You have 8 balls. One is heavier. You have a balance scale and can only use it twice. How do you find the heavy ball?"
*Answer:* 
1. Weigh 3 vs 3. Leave 2 aside.
2. If the scale balances, the heavy ball is in the 2 aside. Weigh them 1 vs 1 to find it.
3. If the scale tips, the heavy ball is in the heavier group of 3. Weigh 1 vs 1 from that group. If it balances, it's the 3rd ball. If it tips, it's the heavier one on the scale.
