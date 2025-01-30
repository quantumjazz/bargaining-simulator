import streamlit as st
import random

############################
# 1) Simple Akerlof Environment
############################
class SimpleLemonsEnv:
    def __init__(self):
        # Key parameters
        self.low_cost = 5000
        self.high_cost = 7000
        # Signaling costs (if relevant)
        self.signal_cost_low = 1500
        self.signal_cost_high = 500

        # Markup range
        self.min_markup = 2000
        self.max_markup = 4000

        # Internal state
        self.quality = None
        self.signaling = False
        self.cost = None
        self.price = None

        # Reset on init
        self.reset()

    def reset(self):
        """Randomly choose car quality, decide on signaling, and set a posted price."""
        self.quality = random.choice(["low", "high"])

        if self.quality == "low":
            self.cost = self.low_cost
            # Low-quality sellers less likely to signal
            self.signaling = random.random() < 0.2
        else:
            self.cost = self.high_cost
            # High-quality sellers more likely to signal
            self.signaling = random.random() < 0.8

        # Random markup
        markup = random.uniform(self.min_markup, self.max_markup)
        base_price = self.cost + markup

        # If signaling, add the appropriate signal cost
        if self.signaling:
            if self.quality == "high":
                base_price += self.signal_cost_high
            else:
                base_price += self.signal_cost_low

        self.price = round(base_price, 2)
        return self

    def attempt_purchase(self, offer):
        """
        If the buyer offers 'offer' and it is >= cost,
        a sale occurs. The seller's profit is offer - cost - (signal cost if any).
        Otherwise, no sale.
        """
        if offer >= self.cost:
            if self.signaling:
                if self.quality == "high":
                    profit = offer - self.cost - self.signal_cost_high
                else:
                    profit = offer - self.cost - self.signal_cost_low
            else:
                profit = offer - self.cost
            return True, profit
        else:
            return False, 0.0

############################
# 2) Streamlit UI
############################
def main():
    st.title("Akerlof 'Lemons' Model — Simple Bargaining Demo")

    # Initialize environment in session state if not already
    if "env" not in st.session_state:
        st.session_state.env = SimpleLemonsEnv()

    # Buttons to reset or proceed
    if st.button("Reset / New Car"):
        st.session_state.env.reset()

    # Show the environment's posted price and whether it signals
    posted_price = st.session_state.env.price
    quality_signal = st.session_state.env.signaling

    st.subheader("Seller's Posted Price")
    st.write(f"**Asking Price:** ${posted_price:,.2f}")

    st.subheader("Is the seller signaling high quality?")
    if quality_signal:
        st.write("Yes! The seller claims it's a *high-quality* car.")
    else:
        st.write("No obvious signals — could be *low* or *high* quality.")

    # Let the user decide how much they want to pay or if they just accept
    st.markdown("---")
    user_offer = st.number_input(
        "Enter your Offer (or match the asking price)",
        min_value=0,
        max_value=30000,
        value=int(posted_price),  # default to posted price
        step=100
    )
    purchase_button = st.button("Attempt Purchase")

    if purchase_button:
        success, seller_profit = st.session_state.env.attempt_purchase(user_offer)
        if success:
            st.success(
                f"Purchase successful at **${user_offer:,.2f}**! "
                f"Seller's profit = **${seller_profit:,.2f}**."
            )
        else:
            st.error(
                f"Your offer (${user_offer:,.2f}) was too low. The seller refuses to sell."
            )

    # (Optional) Show debug info: actual car quality & cost
    with st.expander("See Actual Car Info (spoilers!)"):
        st.write(f"Car quality: **{st.session_state.env.quality}**")
        st.write(f"Car cost: **${st.session_state.env.cost}**")

if __name__ == "__main__":
    main()






