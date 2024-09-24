import streamlit as st
import StreamlitMain as sm
import StreamlitColumn as sc
import StreamlitFoundations as sf
import Home as h
import libraries


# Set the correct password
PASSWORD = "your_secure_password"

# Function to check password and set session state
def authenticate(password):
    if password == PASSWORD:
        st.session_state['authenticated'] = True
        st.success("Login successful!")
    else:
        st.session_state['authenticated'] = False
        st.error("Invalid password. Please try again.")

# Main function for the app
def main():
    # Initialize session state for authentication
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False

    # Check if the user is authenticated
    if not st.session_state['authenticated']:
        # Create login form
        st.title("Login")
        password = st.text_input("Enter your password", type='password')

        if st.button("Login"):
            authenticate(password)

    if st.session_state['authenticated']:
        # Access the stored inputs later in the app
        if "job_title" in st.session_state:
            st.write(f"Job Title: {st.session_state.job_title}")
            st.write(f"Initials: {st.session_state.initials}")
            st.write(f"Item: {st.session_state.item}")
            st.write(f"Revision: {st.session_state.rev}")
            st.write(f"Job Number: {st.session_state.job_number}")
            st.write(f"Date: {st.session_state.date}")
        else:
            st.write("Please enter the details on the home page.")

        # Dictionary to map page names to the corresponding module
        pages = {
            "Home": h,
            "Beams": sm,
            "Columns": sc,
            "Foundations": sf,
        }

        # Sidebar for navigation
        st.sidebar.title("Navigation")
        selection = st.sidebar.radio("Go to", list(pages.keys()))

        # Display the selected page
        page = pages[selection]
        page.app()  # Calls the `app` function from the selected page

# Run the app
if __name__ == "__main__":
    main()
