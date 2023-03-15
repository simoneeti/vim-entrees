from parser import Entry
import sqlite3

DATABASE = "../datos.db"

class Query:
    def __init__(self, texto="", timestamp=None):
        self.texto: str = texto
        self.timestamp: dict | None = timestamp

class QueryResult:
    def __init__(self):
        self.results: None | list = None
        self.error: bool          = False


def insert(e: Entry):
    conexion = sqlite3.connect(DATABASE)
    e_dict = e.to_dict()
    conexion.execute("""INSERT INTO entrees(texto, tipo, timestamp) VALUES (?, ?, ?)""", 
                     (e_dict.get("texto"), e_dict.get("tipo"), e_dict.get("horario")))
    conexion.commit()
    conexion.close()

def get_entries(q: Query): 
    ":return: (error, list[list])"
    result = QueryResult()
    try:
        conexion = sqlite3.connect(DATABASE)
        

        if q.texto and q.timestamp:
            cursor   = conexion.execute("SELECT * FROM ENTREES WHERE TEXTO MATCH ? AND timestamp BETWEEN ? AND ? ORDER BY RANK", 
                                        (q.texto, q.timestamp["start"], q.timestamp["end"])
                                    )        
        elif q.texto:
            cursor   = conexion.execute("SELECT * FROM ENTREES WHERE TEXTO MATCH ? ORDER BY RANK", 
                                        (q.texto,)
                                    )        
        elif q.timestamp:
            cursor   = conexion.execute("SELECT * FROM ENTREES WHERE TIMESTAMP BETWEEN ? AND ? ORDER BY RANK", 
                                        (q.timestamp["start"], q.timestamp["end"])
                                    )        
        else:
            conexion.close()
            result.error = True
            return result


        response = [list(r) for r in cursor]
        conexion.close()
        result.results = response
        return result

    except sqlite3.OperationalError as e:
        print(e)
        result.error = True
        return result 

def create_database():
    try:
        conexion = sqlite3.connect(DATABASE)
        conexion.execute("""
                        CREATE VIRTUAL TABLE IF NOT EXISTS entrees USING fts5(
                           texto,
                           tipo,
                           timestamp 
                            )
                         """)
        conexion.close()
    except sqlite3.OperationalError as e:
        print(e)




def query():
    q = Query(texto="hola", timestamp={"start": 0, "end": 99999999999})
    result = get_entries(q)
    return result

if __name__  == "__main__":
    print(query())
