import random
import numpy as np

class SellerEnvironment:
    def __init__(self):
        """
        In Akerlof's spirit:
        - cost = 50 (low quality) or 70 (high quality).
        - If the seller chooses to signal, we add a signal cost to the posted price.
          * For high-quality items, signal_cost might be small (e.g., 5).
          * For low-quality items, signal_cost might be larger (e.g., 15), so it's not worth faking.
        - The buyer only knows the final posted price and whether there's a 'signal' or not.
        """
        # Possible production costs
        self.low_cost = 50
        self.high_cost = 70

        # Signal costs
        self.signal_cost_low = 15   # More expensive for a low-quality seller to fake it
        self.signal_cost_high = 5   # Cheaper for a high-quality seller

        # Range for markup
        self.min_markup = 10
        self.max_markup = 30

        # Rounds
        self.max_rounds = 3
        self.round = 0

        # Initialize
        self.reset()

    def reset(self):
        """Reset the environment for a new game or negotiation."""
        # Randomly assign quality
        self.quality = random.choice(["low", "high"])
        if self.quality == "low":
            self.cost = self.low_cost
        else:
            self.cost = self.high_cost

        # Decide on a random markup
        self.markup = random.uniform(self.min_markup, self.max_markup)

        # Decide whether to signal or not
        # You can make it random or deterministic. For instance:
        #   - High-quality sellers frequently signal (80% chance).
        #   - Low-quality sellers rarely signal (20% chance).
        if self.quality == "high":
            self.signaling = (random.random() < 0.8)
        else:
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
        Return a discretized state (price_bin, round, signaling_flag).
        You can adapt bin sizes as needed.
        """
        # For example, let's bin the price from 50..120 in steps of 10 → indices 0..7
        price_bin = int(min(max((self.price - 50) // 10, 0), 7))
        return (price_bin, self.round, int(self.signaling))

    def step(self, action=None, player=False, counteroffer=None):
        """
        The main environment step:
        - If player=True, we interpret a human's counteroffer.
        - If the offer >= cost, the transaction succeeds, and the seller's reward is
          (counteroffer - cost - possible signal_cost).
        - If the offer < cost, it's rejected; negotiation ends (reward can be negative or zero).
        - If max_rounds are reached, negotiation ends with a penalty for unsold item.

        Returns: next_state, reward, done
        """
        self.round += 1
        reward = 0
        done = False

        if player:
            # The human buyer's behavior
            if counteroffer is not None:
                # Check acceptance from the SELLER's perspective:
                if counteroffer >= self.cost:
                    # Transaction successful
                    if self.signaling:
                        if self.quality == "high":
                            seller_profit = counteroffer - self.cost - self.signal_cost_high
                        else:
                            seller_profit = counteroffer - self.cost - self.signal_cost_low
                    else:
                        seller_profit = counteroffer - self.cost

                    # The environment returns the SELLER's profit as "reward"
                    reward = seller_profit
                    done = True
                else:
                    # Offer below cost → seller rejects
                    reward = -1
                    done = True
            else:
                # No counteroffer → buyer walks away, negotiation ends
                done = True

        else:
            # If you're letting an AI agent manipulate the price or do some action
            # (But for now, let's keep it minimal or adapt as needed)
            pass

        # Check if we exceeded the max number of rounds
        if not done and self.round >= self.max_rounds:
            done = True
            reward = -10  # penalty for no deal

        next_state = self.get_discrete_state()
        return next_state, reward, done

