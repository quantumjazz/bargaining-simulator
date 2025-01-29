import streamlit as st
import numpy as np
import random
from environment import SellerEnvironment
from q_learning_agent import QLearningAgent

env = SellerEnvironment()
agent = QLearningAgent(state_size=(6, 6), action_size=3)

def main():
    st.title("Bargaining Simulator (Akerlof ‘Lemons’ Model)")

    st.write("""
    This interactive simulator demonstrates a simplified version of Akerlof's 'Market for Lemons.'
    As the buyer, you see the seller's asking price and whether they're signaling high quality.
    You must decide on a counteroffer each round until the negotiation ends.
    """)

    counteroffer = st.sidebar.number_input(
        "Your Counteroffer", min_value=0, max_value=200, value=60, step=1
    )
    negotiate_button = st.sidebar.button("Negotiate!")
    reset_button = st.sidebar.button("Reset Game")

    # Initialize session state if not present
    if "state" not in st.session_state:
        st.session_state.state = env.reset()
        st.session_state.done = False
        st.session_state.reward = 0

    # Handle "Reset Game" button without experimental_rerun
    if reset_button:
        st.session_state.state = env.reset()
        st.session_state.done = False
        st.session_state.reward = 0
        st.stop()  # Optional: stops further code, forcing a re-run/refresh

    price_bin, round_number, signaling_flag = st.session_state.state
    asking_price = price_bin * 10 + 50

    st.subheader(f"Round {round_number + 1}")
    st.write(f"**Seller's asking price:** ${asking_price:.2f}")
    st.write(f"**Signal:** {'Yes (claims high quality)' if signaling_flag else 'No'}")

    if st.session_state.done:
        if st.session_state.reward > 0:
            st.success(
                f"Transaction successful! The seller's final profit was ${st.session_state.reward:.2f}."
            )
        else:
            st.warning("Transaction failed or ended without a successful deal.")
    else:
        if negotiate_button:
            next_state, reward, done = env.step(
                action=None, player=True, counteroffer=counteroffer
            )
            st.session_state.state = next_state
            st.session_state.reward = reward
            st.session_state.done = done

            if done:
                if reward > 0:
                    st.success(
                        f"Transaction successful! You paid ${counteroffer} "
                        f"and the seller's profit was ${reward:.2f}."
                    )
                else:
                    st.warning("Transaction failed. The seller rejected your offer.")
            else:
                st.info("Negotiation continues...")

if __name__ == "__main__":
    main()




