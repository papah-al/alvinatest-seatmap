import streamlit as st
import pandas as pd
import os

# ======================
# STORAGE SETUP
# ======================
DATA_FILE = "bookings.xlsx"

def load_bookings():
    if os.path.exists(DATA_FILE):
        return pd.read_excel(DATA_FILE).to_dict("records")
    return []

def save_bookings(bookings):
    pd.DataFrame(bookings).to_excel(DATA_FILE, index=False)

# ======================
# SESSION STATE INIT
# ======================
if "selected_seats" not in st.session_state:
    st.session_state["selected_seats"] = []

if "bookings" not in st.session_state:
    st.session_state["bookings"] = load_bookings()

if "role" not in st.session_state:
    st.session_state["role"] = None

# ======================
# LOGIN PAGE
# ======================
if st.session_state["role"] is None:
    st.title("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        if username == "user" and password == "123":
            st.session_state["role"] = "User"
            st.rerun()

        elif username == "manager" and password == "admin":
            st.session_state["role"] = "Manager"
            st.rerun()

        else:
            st.error("Invalid credentials")

    st.stop()

# ======================
# LOGOUT BUTTON
# ======================
if st.sidebar.button("Logout"):
    st.session_state["role"] = None
    st.rerun()

# ======================
# SEAT MAP STRUCTURE
# ======================
rows = ["A", "B", "C", "D", "E"]
cols = list(range(1, 11))

# =========================
# USER BOOKING PAGE
# =========================
if st.session_state["role"] == "User":

    st.title("Seat Mapping Application")

    st.subheader("Booking Details")

    name = st.text_input("Your Name")
    project = st.text_input("Project")
    start_date = st.date_input("Start Date")
    end_date = st.date_input("End Date")

    if end_date < start_date:
        st.error("❌ End Date cannot be earlier than Start Date")
        st.stop()

    st.divider()
    st.subheader("Seat Map")

    for row in rows:
        col_ui = st.columns(len(cols))

        for i, col in enumerate(cols):
            seat_id = f"{row}{col}"
            label = f"🟢 {seat_id}"

            # Check booking conflicts
            for b in st.session_state["bookings"]:
                if b["Seat_ID"] == seat_id:

                    b_start = pd.to_datetime(b["Start"]).date()
                    b_end = pd.to_datetime(b["End"]).date()

                    overlap = not (end_date < b_start or start_date > b_end)

                    if overlap:
                        if b["Status"] == "Pending":
                            label = f"🟡 {seat_id}"
                        elif b["Status"] == "Approved":
                            label = f"🔴 {seat_id}"

            # Selected highlight
            if seat_id in st.session_state["selected_seats"]:
                label = f"🔵 {seat_id}"

            if col_ui[i].button(label, key=f"btn_{seat_id}"):

                if label.startswith("🔴"):
                    st.warning("Seat already booked")
                elif label.startswith("🟡"):
                    st.warning("Seat pending approval")
                else:
                    if seat_id in st.session_state["selected_seats"]:
                        st.session_state["selected_seats"].remove(seat_id)
                    else:
                        st.session_state["selected_seats"].append(seat_id)

                st.rerun()

    # Submit Booking
    if st.session_state["selected_seats"]:
        st.success(f"Selected Seats: {', '.join(st.session_state['selected_seats'])}")

        if st.button("Submit Booking"):
            for seat in st.session_state["selected_seats"]:
                st.session_state["bookings"].append({
                    "Seat_ID": seat,
                    "Name": name,
                    "Project": project,
                    "Start": start_date,
                    "End": end_date,
                    "Status": "Pending"
                })

            save_bookings(st.session_state["bookings"])
            st.session_state["selected_seats"] = []

            st.success("Booking submitted. Waiting manager approval.")
            st.rerun()
# =========================
# MANAGER APPROVAL PAGE
# =========================
if st.session_state["role"] == "Manager":

    st.title("Manager Approval Dashboard")

    if len(st.session_state["bookings"]) == 0:
        st.info("No booking requests yet.")
    else:
        for i, b in enumerate(st.session_state["bookings"]):
            st.divider()
            st.write(f"### Booking #{i+1}")

            # Editable fields
            seat = st.text_input("Seat", b["Seat_ID"], key=f"seat_{i}")
            name = st.text_input("Name", b["Name"], key=f"name_{i}")
            project = st.text_input("Project", b["Project"], key=f"project_{i}")
            start = st.date_input("Start Date", pd.to_datetime(b["Start"]).date(), key=f"start_{i}")
            end = st.date_input("End Date", pd.to_datetime(b["End"]).date(), key=f"end_{i}")

            status = b["Status"]
            st.write(f"**Status:** {status}")

            col1, col2, col3 = st.columns(3)

            # Approve button
            if status == "Pending":
                if col1.button("Approve", key=f"approve_{i}"):
                    st.session_state["bookings"][i]["Status"] = "Approved"
                    save_bookings(st.session_state["bookings"])
                    st.success("Approved")
                    st.rerun()

            # Save edits
            if col2.button("Save Changes", key=f"save_{i}"):
                if end < start:
                    st.error("End Date cannot be earlier than Start Date")
                else:
                    st.session_state["bookings"][i] = {
                        "Seat_ID": seat,
                        "Name": name,
                        "Project": project,
                        "Start": start,
                        "End": end,
                        "Status": status
                    }
                    save_bookings(st.session_state["bookings"])
                    st.success("Changes saved")
                    st.rerun()

            # Delete booking
            if col3.button("Delete", key=f"delete_{i}"):
                st.session_state["bookings"].pop(i)
                save_bookings(st.session_state["bookings"])
                st.warning("Booking deleted")
                st.rerun()
