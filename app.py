import streamlit as st
from environment import SellerEnvironment
from q_learning_agent import QLearningAgent

env = SellerEnvironment()
agent = QLearningAgent(state_size=(6, 6), action_size=3)

def main():
    st.title("Bargaining Simulator (Akerlof ‘Lemons’ Model)")

    counteroffer = st.sidebar.number_input(
        "Your Counteroffer", min_value=0, max_value=200, value=60, step=1
    )
    negotiate_button = st.sidebar.button("Negotiate!")
    reset_button = st.sidebar.button("Reset Game")

    if "state" not in st.session_state:
        st.session_state.state = env.reset()
        st.session_state.done = False
        st.session_state.reward = 0

    # Handle reset
    if reset_button:
        st.session_state.state = env.reset()
        st.session_state.done = False
        st.session_state.reward = 0
        # No st.stop() - we let the code continue

    # Display environment state
    price_bin, round_number, signaling_flag = st.session_state.state
    asking_price = price_bin * 10 + 50

    st.subheader(f"Round {round_number + 1}")
    st.write(f"**Seller's asking price:** ${asking_price:.2f}")
    st.write(f"**Signal:** {'Yes' if signaling_flag else 'No'}")

    if st.session_state.done:
        if st.session_state.reward > 0:
            st.success(
                f"Transaction successful! Seller's profit was ${st.session_state.reward:.2f}."
            )
        else:
            st.warning("Transaction failed or ended without a deal.")
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
                        f"You paid ${counteroffer}, seller's profit: ${reward:.2f}."
                    )
                else:
                    st.warning("Seller rejected your offer!")

if __name__ == "__main__":
    main()





