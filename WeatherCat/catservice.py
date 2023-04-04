#----------------------------------------------------------------------
class CatDirectory():
    def __init__(self, conn):
        self.conn = conn
        c = self.conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS cats (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            name TEXT, 
            t TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""")
    def insert(self, name):
        c = self.conn.cursor()
        c.execute("INSERT INTO cats (name) VALUES (?)", (name))
        self.conn.commit()
        pass
    
    def random(self):
        cats = self.all()
        if len(cats)>0:
            return cats[0]
        else:
            raise Exception("No cats available")

    def all(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM cats")
        output = c.fetchall()
        return output
        pass
