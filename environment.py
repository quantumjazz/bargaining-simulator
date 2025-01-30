import random
import numpy as np

class SellerEnvironment:
    def __init__(self):
        """
        A more realistic environment:
        - cost = 5000 (low quality) or 7000 (high quality).
        - signal costs: 1500 if low-quality tries to fake it, 500 if high-quality.
        - markup: random uniform between 2000..4000.
        - final price = cost + markup + (possible signal cost).
        """
        self.low_cost = 5000
        self.high_cost = 7000

        self.signal_cost_low = 1500
        self.signal_cost_high = 500

        self.min_markup = 2000
        self.max_markup = 4000

        self.max_rounds = 3
        self.round = 0

        self.reset()

    def reset(self):
        """Reset the environment for a new game or negotiation."""
        # Randomly assign low or high quality
        self.quality = random.choice(["low", "high"])
        if self.quality == "low":
            self.cost = self.low_cost
        else:
            self.cost = self.high_cost

        # Random markup
        self.markup = random.uniform(self.min_markup, self.max_markup)

        # Decide whether to signal (randomly or otherwise)
        if self.quality == "high":
            # High-quality more likely to signal
            self.signaling = (random.random() < 0.8)
        else:
            # Low-quality less likely to signal
            self.signaling = (random.random() < 0.2)

        # Compute the posted price
        base_price = self.cost + self.markup
        if self.signaling:
            if self.quality == "high":
                base_price += self.signal_cost_high
            else:
                base_price += self.signal_cost_low

        self.price = base_price

        self.round = 0
        return self.get_discrete_state()

    def get_discrete_state(self):
        """
        Convert the float price into a bin index for Q-learning.
        We'll map 5000..12000 in steps of 1000 → 8 bins (0..7).
        If price < 5000, bin=0; if price>12000, bin=7.
        """
        price_bin = int((self.price - 5000) // 1000)
        price_bin = max(0, min(price_bin, 7))

        return (price_bin, self.round, int(self.signaling))

    def step(self, action=None, player=False, counteroffer=None):
        """
        If player=True, interpret a human's counteroffer:
          - If counteroffer >= self.cost, success, reward = (counter - cost - signal_cost).
          - If counter < self.cost, reject → done, reward=-1.
        Otherwise, the environment can do AI actions (not shown).
        """
        self.round += 1
        reward = 0
        done = False

        if player:
            if counteroffer is not None:
                if counteroffer >= self.cost:
                    # Transaction successful
                    if self.signaling:
                        if self.quality == "high":
                            seller_profit = counteroffer - self.cost - self.signal_cost_high
                        else:
                            seller_profit = counteroffer - self.cost - self.signal_cost_low
                    else:
                        seller_profit = counteroffer - self.cost

                    reward = seller_profit
                    done = True
                else:
                    # Offer below cost -> reject
                    reward = -1
                    done = True
            else:
                # Buyer walks away (no counteroffer)
                done = True

        # If max rounds reached with no deal
        if not done and self.round >= self.max_rounds:
            done = True
            reward = -10

        next_state = self.get_discrete_state()
        return next_state, reward, done

