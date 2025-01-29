import numpy as np
import random
from environment import SellerEnvironment

class QLearningAgent:
    def __init__(
        self,
        state_size,
        action_size,
        learning_rate=0.1,
        gamma=0.95,
        epsilon=1.0,
        epsilon_decay=0.995
    ):
        """
        Q-Learning agent that interacts with the SellerEnvironment.
        :param state_size: A tuple defining the discrete state dimensions, e.g. (price_bins, round_bins, signaling_flag).
        :param action_size: Number of possible actions (e.g., 3 if only lower/keep/increase, 5 if adding signal, etc.).
        :param learning_rate: Q-learning update rate.
        :param gamma: Discount factor for future rewards.
        :param epsilon: Exploration rate for epsilon-greedy.
        :param epsilon_decay: Rate at which epsilon is decayed after each episode.
        """
        self.state_size = state_size
        self.action_size = action_size
        # The Q-table has shape: state_size + (action_size,)
        self.q_table = np.zeros(state_size + (action_size,))

        self.lr = learning_rate   # Learning rate
        self.gamma = gamma        # Discount factor
        self.epsilon = epsilon    # Exploration rate
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = 0.1

    def choose_action(self, state):
        """Epsilon-greedy action selection."""
        if np.random.rand() <= self.epsilon:
            return random.choice(range(self.action_size))  # Explore
        return np.argmax(self.q_table[state])  # Exploit

    def update_q_table(self, state, action, reward, next_state, done):
        """Update Q-value for a given state-action pair using the Q-Learning rule."""
        best_next_action = np.argmax(self.q_table[next_state])
        td_target = reward + (self.gamma * self.q_table[next_state][best_next_action] * (1 - done))
        td_error = td_target - self.q_table[state][action]
        self.q_table[state][action] += self.lr * td_error

        # If the episode ended, decay epsilon (exploration rate)
        if done:
            self.epsilon = max(self.epsilon * self.epsilon_decay, self.epsilon_min)

# ----------------------------------------------------------------
# Human interaction for testing/demo (unchanged from your original)
# ----------------------------------------------------------------
def human_interaction(env):
    state = env.reset()
    done = False
    player_bought = False
    player_price = None

    while not done:
        # The environment can store the "raw" price in env.price if you wish:
        posted_price = env.price  # A float, e.g., 84.37
        is_signaling = bool(state[2])

        print(f"\nRound {state[1]+1}")
        print(f"Seller's posted price: {posted_price:.2f}")
        if is_signaling:
            print(">>> The seller is SIGNALING (claims high quality).")
        else:
            print(">>> The seller is NOT signaling (might be low quality).")

        counteroffer_str = input("Enter your counteroffer (or press Enter to skip): ")
        if counteroffer_str.strip() == "":
            # Buyer walks away
            print("You chose to skip. Negotiation ends.")
            next_state, reward, done = env.step(action=None, player=True, counteroffer=None)
        else:
            counteroffer = float(counteroffer_str)
            # Evaluate step
            next_state, reward, done = env.step(action=None, player=True, counteroffer=counteroffer)
            if done and reward > 0:
                print(f"Transaction successful! You paid {counteroffer:.2f} and the seller's profit was {reward:.2f}.")
                player_bought = True
                player_price = counteroffer
            elif done:
                print("Transaction failed. Seller rejected your offer.")

        state = next_state  # Update state if continuing

    return player_bought, player_price



def simulate_buyers(env, num_buyers=5, player_bought=False, player_price=None):
    if player_bought:
        return False

    for i in range(num_buyers):
        # Suppose other buyers interpret the signal
        if env.signaling:
            # Higher willingness if they see a signal
            buyer_willingness = random.uniform(75, 100)
        else:
            # Lower willingness if no signal
            buyer_willingness = random.uniform(60, 85)

        # They only buy if posted price <= buyer_willingness
        price = env.price
        if price <= buyer_willingness:
            print(f"Another buyer purchased the item for {price:.2f}!")
            return True

    return False


# ----------------------------------------------------------------
# Main training/game loop (unchanged structure, minor annotation)
# ----------------------------------------------------------------
if __name__ == "__main__":
    # Initialize environment and Q-learning agent
    # NOTE: In your original code, state_size was (6,6) and action_size=3
    # If you keep 3 actions, you can leave it as-is. If you add signaling actions, adjust to e.g. 5.
    env = SellerEnvironment()
    agent = QLearningAgent(state_size=(6, 6), action_size=3)  # or action_size=5 if you add more actions

    print("Welcome to the Bargaining Simulator!")
    while True:
        print("\n--- New Game ---")
        env.reset()

        # 1) Human (player) interacts
        player_bought, player_price = human_interaction(env)

        # 2) If not purchased by the player, simulate other buyers
        if not player_bought and simulate_buyers(env, player_bought=player_bought, player_price=player_price):
            print("The product was purchased by another buyer!")

        # Option to continue or break
        play_again = input("Play again? (y/n): ")
        if play_again.lower() != "y":
            break
