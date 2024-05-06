def create_tables(conn):
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS notes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT,
                  content TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  last_edited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS tags
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  note_id INTEGER,
                  FOREIGN KEY (note_id) REFERENCES notes(id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS links
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  from_note_id INTEGER,
                  to_note_id INTEGER,
                  FOREIGN KEY (from_note_id) REFERENCES notes(id),
                  FOREIGN KEY (to_note_id) REFERENCES notes(id))''')
    conn.commit()

def update_note(note_id, title, content, tags_input, linked_notes_input, conn):
    c = conn.cursor()

    # Update note
    if note_id is None:
        c.execute('''INSERT INTO notes (title, content) VALUES (?, ?)''', (title, content))
        note_id = c.lastrowid
    else:
        c.execute('UPDATE notes SET title=?, content=?, last_edited_at=CURRENT_TIMESTAMP WHERE id=?', (title, content, note_id))

    # Update tags
    c.execute('DELETE FROM tags WHERE note_id=?', (note_id,))
    tags = tags_input.split(',')
    for tag in tags:
        c.execute('INSERT INTO tags (name, note_id) VALUES (?, ?)', (tag.strip(), note_id))

    # Update linked notes
    c.execute('DELETE FROM links WHERE from_note_id=?', (note_id,))
    linked_notes = linked_notes_input.split(',')
    for linked_note_id in linked_notes:
        c.execute('INSERT INTO links (from_note_id, to_note_id) VALUES (?, ?)', (note_id, linked_note_id.strip()))

    conn.commit()

def get_tags_string(note_id, conn):
    c = conn.cursor()
    c.execute('SELECT name FROM tags WHERE note_id=?', (note_id,))
    tags = c.fetchall()
    tag_names = [tag[0] for tag in tags]
    return ', '.join(tag_names)

def get_linked_notes_string(note_id, conn):
    c = conn.cursor()
    c.execute('SELECT to_note_id FROM links WHERE from_note_id=?', (note_id,))
    linked_notes = c.fetchall()
    linked_note_ids = [str(note[0]) for note in linked_notes]
    return ', '.join(linked_note_ids)