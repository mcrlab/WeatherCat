
class ImageDirectory():
    def __init__(self, conn):
        self.conn = conn
        c = self.conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            name TEXT, 
            path TEXT, 
            t TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""")
    def insert(self, name, path):
        c = self.conn.cursor()
        c.execute("INSERT INTO images (name, path) VALUES (?,?)", (name, path))
        self.conn.commit()
        pass
    
    def find(self, description):
        c = self.conn.cursor()
        c.execute("SELECT * FROM images WHERE name = ?", (description,))
        output = c.fetchall()
        return output
    
    def all(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM images")
        output = c.fetchall()
        return output
        pass
