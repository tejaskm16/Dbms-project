import streamlit as st
import mysql.connector
import pandas as pd
from datetime import date

# MYSQL CONNECTION
conn = mysql.connector.connect(
    host="your-cloud-host",
    user="your-user",
    password="tejas",
    database="attedance_db1",
    port=3306
)
cursor = conn.cursor()

# PAGE TITLE
st.title("Student Attendance System")

# SIDEBAR MENU
menu = [
    "Add Student",
    "View Students",
    "Mark Attendance",
    "View Attendance",
    "Update Student",
    "Delete Student"
]

choice = st.sidebar.radio("Menu", menu)

# ADD STUDENT
# ADD STUDENT
if choice == "Add Student":

    st.subheader("Add Student")

    name = st.text_input("Enter Student Name")

    usn = st.text_input(
        "Enter Full USN",
        placeholder="Example: 1KG22CS001"
    )

    if st.button("Add Student"):

        if name and usn:

            # CHECK DUPLICATE NAME OR USN
            query = """
            SELECT * FROM students
            WHERE name = %s OR usn = %s
            """

            values = (name, usn)

            cursor.execute(query, values)

            existing_student = cursor.fetchone()

            if existing_student:

                st.error(
                    "Student already exists with same Name or USN"
                )

            else:

                query = """
                INSERT INTO students (name, usn)
                VALUES (%s, %s)
                """

                values = (name, usn)

                cursor.execute(query, values)
                conn.commit()

                st.success("Student Added Successfully")

        else:
            st.warning("Please Enter All Fields")

# VIEW STUDENTS
elif choice == "View Students":

    st.subheader("Student List")

    cursor.execute("SELECT * FROM students")
    data = cursor.fetchall()

    if data:

        df = pd.DataFrame(
            data,
            columns=["ID", "Name", "USN"]
        )

        st.dataframe(df)

    else:
        st.warning("No Students Found")

# MARK ATTENDANCE
elif choice == "Mark Attendance":

    st.subheader("Mark Attendance")

    cursor.execute("SELECT id, name, usn FROM students")
    students = cursor.fetchall()

    if students:

        attendance_data = {}

        st.write("### Student Attendance")

        for student in students:

            student_id = student[0]
            student_name = student[1]
            student_usn = student[2]

            col1, col2 = st.columns([5, 2])

            with col1:
                st.write(
                    f"Name: {student_name} | USN: {student_usn}"
                )

            with col2:
                status = st.radio(
                    "Status",
                    ["Present", "Absent"],
                    key=student_id
                )

            attendance_data[student_id] = status

        if st.button("Submit Attendance"):

            for student_id, status in attendance_data.items():

                query = """
                INSERT INTO attendance
                (student_id, date, status)
                VALUES (%s, %s, %s)
                """

                values = (
                    student_id,
                    date.today(),
                    status
                )

                cursor.execute(query, values)

            conn.commit()

            st.success("Attendance Submitted Successfully")

    else:
        st.warning("No Students Found")

# VIEW ATTENDANCE
# VIEW ATTENDANCE
elif choice == "View Attendance":

    st.subheader("Attendance Records")

    query = """
    SELECT
        attendance.id,
        students.name,
        students.usn,
        attendance.date,
        attendance.status
    FROM attendance
    JOIN students
    ON students.id = attendance.student_id
    ORDER BY attendance.date DESC
    """

    cursor.execute(query)
    data = cursor.fetchall()

    if data:

        df = pd.DataFrame(
            data,
            columns=[
                "Attendance ID",
                "Name",
                "USN",
                "Date",
                "Status"
            ]
        )

        st.dataframe(df)

        st.write("### Delete Attendance Record")

        attendance_ids = [
            row[0] for row in data
        ]

        selected_id = st.selectbox(
            "Select Attendance ID",
            attendance_ids
        )

        if st.button("Delete Attendance"):

            delete_query = """
            DELETE FROM attendance
            WHERE id = %s
            """

            cursor.execute(
                delete_query,
                (selected_id,)
            )

            conn.commit()

            st.success(
                "Attendance Record Deleted Successfully"
            )

    else:
        st.warning("No Attendance Records Found")

# UPDATE STUDENT
elif choice == "Update Student":

    st.subheader("Update Student")

    cursor.execute("SELECT id, name, usn FROM students")
    students = cursor.fetchall()

    if students:

        student_dict = {
            f"{sid} - {name}": sid
            for sid, name, usn in students
        }

        selected_student = st.selectbox(
            "Select Student",
            list(student_dict.keys())
        )

        student_id = student_dict[selected_student]

        cursor.execute(
            "SELECT name, usn FROM students WHERE id = %s",
            (student_id,)
        )

        current_data = cursor.fetchone()

        new_name = st.text_input(
            "Update Name",
            value=current_data[0]
        )

        new_usn = st.text_input(
            "Update USN",
            value=current_data[1]
        )

        if st.button("Update Student"):

            query = """
            UPDATE students
            SET name = %s, usn = %s
            WHERE id = %s
            """

            values = (
                new_name,
                new_usn,
                student_id
            )

            cursor.execute(query, values)
            conn.commit()

            st.success("Student Updated Successfully")

    else:
        st.warning("No Students Found")

# DELETE STUDENT
elif choice == "Delete Student":

    st.subheader("Delete Student")

    cursor.execute("SELECT id, name FROM students")
    students = cursor.fetchall()

    if students:

        student_dict = {
            f"{sid} - {name}": sid
            for sid, name in students
        }

        selected_student = st.selectbox(
            "Select Student To Delete",
            list(student_dict.keys())
        )

        if st.button("Delete Student"):

            student_id = student_dict[selected_student]

            # DELETE ATTENDANCE RECORDS
            cursor.execute(
                "DELETE FROM attendance WHERE student_id = %s",
                (student_id,)
            )

            # DELETE STUDENT
            cursor.execute(
                "DELETE FROM students WHERE id = %s",
                (student_id,)
            )

            conn.commit()

            st.success("Student Deleted Successfully")

    else:
        st.warning("No Students Found")