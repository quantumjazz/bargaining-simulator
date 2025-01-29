import streamlit as st
import numpy as np
from environment import SellerEnvironment
from q_learning_agent import QLearningAgent

# Initialize environment and Q-learning agent
env = SellerEnvironment()
agent = QLearningAgent(state_size=(6, 6), action_size=3)

# Streamlit app layout
def main():
    st.title("Bargaining Simulator (Akerlof ‘Lemons’ Model)")

    # 1) Show some instructions or introduction
    st.write("""
    This is an interactive simulator demonstrating adverse selection 
    and signaling in a market with asymmetric information. 
    Use the sidebar to set your negotiation parameters, then see if you can 
    negotiate successfully with the seller!
    """)

    # 2) Sidebar for user inputs
    # e.g., user can choose a counteroffer
    counteroffer = st.sidebar.number_input("Your Counteroffer", min_value=0, max_value=200, value=60)
    play_round_button = st.sidebar.button("Negotiate!")

    # Keep track of environment state in Streamlit session_state
    if "state" not in st.session_state:
        # Reset environment at start
        st.session_state.state = env.reset()
        st.session_state.done = False
        st.session_state.reward = 0

    # If the user clicks "Negotiate!"
    if play_round_button and not st.session_state.done:
        next_state, reward, done = env.step(player=True, counteroffer=counteroffer)
        st.session_state.state = next_state
        st.session_state.reward = reward
        st.session_state.done = done

    # Display current status
    price_bin, round_number, signaling_flag = st.session_state.state
    st.write(f"**Round:** {round_number + 1}")
    st.write(f"**Seller's Price Bin:** {price_bin} (mapped to ~ {price_bin*10 + 50})")
    st.write(f"**Seller is Signaling:** {'Yes' if signaling_flag else 'No'}")

    if st.session_state.done:
        if st.session_state.reward > 0:
            st.success(f"Transaction successful! Seller's profit was {st.session_state.reward:.2f}.")
        else:
            st.warning("Transaction failed or ended.")
        # Offer a button to start a new game
        if st.button("Start New Game"):
            st.session_state.state = env.reset()
            st.session_state.done = False
            st.session_state.reward = 0

if __name__ == "__main__":
    main()


