
import streamlit as st

def app():
    def get_inputs():
        st.header("Input Information")

        job_title = st.text_input("Job Title", value="")
        initials = st.text_input("Initials", value="MM").upper()  # Convert initials to uppercase
        item = st.text_input("Item", value="Structural Calculations")
        rev = st.text_input("Revision", value="")
        job_number = st.number_input("Job Number", value=24000)
        date = st.text_input("Date", value="")

        if st.button("Submit"):
            # Store inputs in session state
            st.session_state.job_title = job_title
            st.session_state.initials = initials
            st.session_state.item = item
            st.session_state.rev = rev
            st.session_state.job_number = job_number
            st.session_state.date = date
            st.success("Inputs saved! 😊")

    # Call the function to get inputs
    get_inputs()