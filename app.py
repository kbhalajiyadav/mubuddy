import streamlit as st
import sqlite3
import datetime
import re
from db_operations  import create_tables
from db_operations import update_note, get_tags_string, get_linked_notes_string

def main():
    conn = sqlite3.connect('notes.db')
    create_tables(conn)
    conn.close()

    st.title('Networked Notes App')
    menu = ['Home', 'View Notes', 'Create Note', 'Edit Note']
    choice = st.sidebar.selectbox('Menu', menu)

    if choice == 'Home':
        st.write('Welcome to Networked Notes App!')

    elif choice == 'View Notes':
        view_notes()  # Define this function or remove the call if not needed

    elif choice == 'Create Note':
        create_note()

    elif choice == 'Edit Note':
        edit_note()

    conn.close()  # Close the database connection after all operations

def link_notes(content, conn):
    # Extracting linked note names from content
    linked_notes = [note.replace("[[", "").replace("]]", "") for note in content.split() if "[[" in note and "]]" in note]
    linked_notes_str = "','".join(linked_notes)

    # Querying relevant notes from the database
    c = conn.cursor()
    c.execute(f"SELECT title, content FROM notes WHERE title IN ('{linked_notes_str}')")
    linked_notes_data = c.fetchall()

    # Displaying relevant notes below the content
    if linked_notes_data:
        st.subheader("Relevant Linked Notes")
        for note_title, note_content in linked_notes_data:
            st.write(f"**{note_title}**:")
            st.write(note_content)
            st.write("---")

def create_note():
    conn = sqlite3.connect('notes.db')
    st.subheader('Create Note')
    title = st.text_input('Enter Title:')
    content = st.text_area('Enter Content:', height=200)
    tags_input = st.text_input('Enter Tags (comma-separated):')
    linked_notes_input = st.text_input('Enter Linked Notes IDs (comma-separated):')

    # Check if the content contains @date and replace it with the selected date
    if '@date' in content:
        selected_date = st.date_input("Select Date")
        content = content.replace('@date', str(selected_date))  # Replace @date with selected date

        # Display the 'Insert Date' button after selecting the date
        if st.button("Insert Date"):
            st.write(f"Date Inserted: {selected_date}")    


    # Parse content for special commands using regular expressions
    parse_special_commands(content)

    # Preview section
    st.subheader('Note Preview')
    st.write(f"**Title:** {title}")
    st.write(f"**Content:** {content}")
    st.write(f"**Tags:** {tags_input}")
    st.write(f"**Linked Notes IDs:** {linked_notes_input}")

    if st.button('Save Note'):
        update_note(None, title, content, tags_input, linked_notes_input, conn)
        st.success('Note saved successfully!')
    conn.close()

def parse_special_commands(content):
    # Regular expression to match special commands like @date, @table, @reminder
    pattern = r'@(\w+)'
    matches = re.findall(pattern, content)

    for match in matches:
        command = match.lower()
        if command == 'date':
            insert_date()
        elif command == 'table':
            insert_dynamic_table()
        elif command == 'reminder':
            add_reminder()

def insert_date():
    st.write("Insert Date")
    selected_date = st.date_input("Select Date")
    if st.button("Insert Date"):
        st.write(f"Date Inserted: {selected_date}")

def insert_dynamic_table():
    st.write("Insert Dynamic Table")
    # Insert dynamic table logic here

def add_reminder():
    st.write("Add Reminder")
    reminder_date = st.date_input("Reminder Date", datetime.date.today())
    reminder_time = st.time_input("Reminder Time", datetime.time(12, 0))
    reminder_description = st.text_input("Reminder Description")
    if st.button("Save Reminder"):
        # Save reminder logic here
        st.success("Reminder saved successfully!")

def edit_note():
    conn = sqlite3.connect('notes.db')
    st.subheader('Edit Note')
    note_id = st.number_input('Enter Note ID:')
    c = conn.cursor()  # Create cursor object
    note = c.execute('SELECT * FROM notes WHERE id=?', (note_id,)).fetchone()
    if note:
        st.write(f"**{note[1]}**")
        new_title = st.text_input('Edit Title:', value=note[1])
        new_content = st.text_area('Edit Content:', value=note[2], height=200)
        tags_input = st.text_input('Edit Tags (comma-separated):', value=get_tags_string(note_id, conn))
        linked_notes_input = st.text_input('Edit Linked Notes IDs (comma-separated):', value=get_linked_notes_string(note_id, conn))

        # Parse content for special commands using regular expressions
        parse_special_commands(new_content)

        if st.button('Update Note'):
            update_note(note_id, new_title, new_content, tags_input, linked_notes_input, conn)
            st.success('Note updated successfully!')
    conn.close()

def view_notes():
    conn = sqlite3.connect('notes.db')
    st.subheader('View Notes')
    c = conn.cursor()
    c.execute('SELECT * FROM notes')
    notes = c.fetchall()
    for note in notes:
        st.write(f"**ID:** {note[0]}")
        st.write(f"**Title:** {note[1]}")
        st.write(f"**Content:** {note[2]}")
        st.write(f"**Created At:** {note[3]}")
        st.write(f"**Last Edited At:** {note[4]}")
        st.write("---")

if __name__ == '__main__':
    main()
