import streamlit as st
from environment import SellerEnvironment
from q_learning_agent import QLearningAgent

env = SellerEnvironment()
agent = QLearningAgent(state_size=(6, 6), action_size=3)

def main():
    st.title("Bargaining Simulator (Akerlof ‘Lemons’ Model)")

    counteroffer = st.sidebar.number_input(
        "Your Counteroffer", min_value=0, max_value=20000, value=6000, step=100
    )
    negotiate_button = st.sidebar.button("Negotiate!")
    reset_button = st.sidebar.button("Reset Game")

    if "state" not in st.session_state:
        st.session_state.state = env.reset()
        st.session_state.done = False
        st.session_state.reward = 0

    # If user clicked "Reset Game"
    if reset_button:
        st.session_state.state = env.reset()
        st.session_state.done = False
        st.session_state.reward = 0

    # Extract state info
    price_bin, round_number, signaling_flag = st.session_state.state
    # We'll show the real float price from env.price
    asking_price = env.price  # <--- direct from environment

    st.subheader(f"Round {round_number + 1}")
    st.write(f"**Seller's asking price:** ${asking_price:,.2f}")
    st.write(f"**Signal:** {'Yes' if signaling_flag else 'No'}")

    # Check if negotiation ended
    if st.session_state.done:
        if st.session_state.reward > 0:
            st.success(
                f"Transaction successful! Seller's profit: ${st.session_state.reward:,.2f}."
            )
        else:
            st.warning("Transaction failed or ended without a deal.")
    else:
        # Ongoing negotiation
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
                        f"You paid ${counteroffer:,.2f}, seller's profit: ${reward:,.2f}."
                    )
                else:
                    st.warning("Seller rejected your offer!")

if __name__ == "__main__":
    main()





