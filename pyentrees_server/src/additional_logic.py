from parser import Entry
from database import insert
from google_calendar import add_event

def additional_handler(e: Entry):
    
    if e.tipo == "R" or e.tipo == "T":
        add_event(e)

    insert(e) 

    return
