from dataclasses import dataclass
from datetime import datetime, timedelta
import re

## sintaxis general input:
##      c[código tipo] t[código cuándo (opcional)] [...texto]

## tipo: tarea (T) - entrada (E) - recordatorio (A)
## cuando: 
##      - tarea/recordatorio: HH:MM/DD - HOYHH:MM (hoy a las HH:MM) - MANHH:MM (mañana a las HH:MM) - MAÑ -
##      MINMM (en MM minutos) - HHH (en HH horas) - vacio (default)
##      - entrada: ahora

# TIPOS
PREFIJOS_TIEMPO = {"MAÑANA": ["MAN", "MAÑ"], "HOY": ["HOY"], "MINUTOS": ["MIN", "M"], "HORAS": ["H"]}
CODIGOS_TIPO    = {"TAREA": ["T"], "ENTRADA": ["E", ""], "RECORDATORIO": ["R"]}

ALL_PREFIJOS = [ item for sublist in PREFIJOS_TIEMPO.values() for item in sublist ]
ALL_CODIGOS  = [ item for sublist in CODIGOS_TIPO.values()    for item in sublist ]

 
class InvalidEntryError(Exception):
    pass

class Entry:
    def __init__(self, texto_sucio: str):
        self.texto_sucio   = texto_sucio
        self.tipo          = ""
        self.tiempo_sucio  = ""
        self.tiempo: Tiempo | None = None
        self.texto_limpito = ""
        self.calendarId    = ""
    def to_dict(self):
        return {"texto": self.texto_limpito, "tipo": self.tipo, "horario": int(self.tiempo.tiempo.timestamp())}
    def __repr__(self):
        return f"""
                TEXTO  : {self.texto_limpito}
                TIPO   : {self.tipo}
                HORARIO: {self.tiempo}"""

class Tiempo:
    def __init__(self):
        self.HORA   = 0
        self.MINUTO = 0
        self.FECHA  = 0
        self.tiempo: datetime | None = None

    def __repr__(self):
        # return f"offset: {self.HORA}h {self.MINUTO}m {self.FECHA}d"
        return f'{self.tiempo.strftime("%d/%m %H:%M")}' 

@dataclass()
class Parser:
    def __init__(self):
#        self.tiempo_regex = "(w*)(d{2}*):*(d{2}*)//*(d{2}*)"
#        self.tiempo_regex = "([a-zA-Z]*)(\d*):*(\d*)\/*(\d*)"
        pass

    def pre_post(self, w):
        prefijo  = ""
        postfijo = ""
        
        for token in w:
            if not token.isalpha():
                break
            prefijo += token

        if prefijo[0] != "t":
            raise Exception(f"ERROR: Prefijo debe empezar con 't' (got: {prefijo})")
        prefijo = prefijo[1:] 
        prefijo = prefijo.upper()

        postfijo = w[len(prefijo) + 1:]
        postfijo_numerico = [t for t in postfijo if t.isnumeric()]
        
        if len(postfijo_numerico) % 2 == 1:
            postfijo = "0" + postfijo
        
        segmentos = []
        i = 0
        for index, token in enumerate(postfijo):
            if not token.isnumeric():
                continue
            if i % 2 == 0:
                segmentos.append(int(token + postfijo[index + 1]))
            i += 1
        return prefijo, segmentos

    def parse_tiempo(self, e: Entry):
        tiempo_final = Tiempo() 
        
        l_form = e.texto_sucio.split()
        header = l_form[:2]
        
        tiempo = header[1]
        
        prefijo, segmentos = self.pre_post(tiempo)    

        try:
            tiempo_final.HORA   = segmentos[0]
            tiempo_final.MINUTO = segmentos[1]
            tiempo_final.FECHA  = segmentos[2]
        except:
            pass
         

        if prefijo in PREFIJOS_TIEMPO["MAÑANA"]:
            tiempo_final.FECHA += 1
        elif prefijo in PREFIJOS_TIEMPO["MINUTOS"]:
            tiempo_final.HORA    = 0
            tiempo_final.MINUTO = segmentos[0]
        elif prefijo in PREFIJOS_TIEMPO["HORAS"]:
            tiempo_final.HORA = segmentos[0]
        elif not prefijo:
            if len(segmentos) == 1:
                tiempo_final.MINUTO = segmentos[0]
                tiempo_final.HORA   = 0
        # print(f"{e.texto_sucio=} {prefijo=} ")
        # print(f"{tiempo_final.FECHA=}, {tiempo_final.HORA=}, {tiempo_final.MINUTO=}") 

        now = datetime.now() 
        
        delta = now + timedelta(days=tiempo_final.FECHA)
        
        if tiempo_final.HORA and not tiempo_final.MINUTO:
            delta += timedelta(hours=tiempo_final.HORA)
        elif not tiempo_final.HORA and tiempo_final.MINUTO:
            delta += timedelta(minutes=tiempo_final.MINUTO)

        tiempo_final.tiempo = delta

        if tiempo_final.HORA and tiempo_final.MINUTO:
            tiempo_final.tiempo = tiempo_final.tiempo.replace(hour=tiempo_final.HORA, minute=tiempo_final.MINUTO)

        # print(f"{tiempo_final=}")
        # print("")
        return tiempo_final

    def parse_codigo(self, e: Entry):
         
        l_form = e.texto_sucio.split()
        header = l_form[:2]
        codigo = header[0]
        codigo_valid = len(codigo) > 1 and len(codigo) < 3 and codigo[0] == "c" and codigo[1] in ALL_CODIGOS
        if not codigo_valid:
            raise InvalidEntryError(f"ERROR: código {codigo} inválido.")
        
        return codigo[1]

    def parse_texto(self, e):
        splitted = e.texto_sucio.split(" ")
        texto_limpito = ""
        c_id = ""
        if e.tipo == "T" or e.tipo == "R":
            
            texto_limpito = " ".join(splitted[2:])
            c_id = splitted[2:][0]
            if c_id.startswith("CALENDAR_ID"):
                c_id = c_id.replace("CALENDAR_ID", "")
                texto_limpito.replace(c_id, "")
            else:
                c_id = ""
        else:
            texto_limpito = " ".join(splitted[1:])
        return texto_limpito, c_id 


    def check_rules(self, e):
        is_wrong = False
        splitted = e.texto_sucio.split(" ")
       
        
        if len(splitted) < 2:
            is_wrong = True

        if e.tipo == "T" or e.tipo == "R":
            if len(splitted[0]) < 2 \
                or len(splitted[1]) < 2 \
                or splitted[0][0] != "c" \
                or splitted[1][0] != "t" \
                :
                is_wrong = True
        if e.tipo == "E":
            pass
        if is_wrong:
            raise InvalidEntryError(f"ERROR: entrada {e.texto_sucio} inválida.")

    def parse(self, texto: str):
        e = Entry(texto)
        e.tipo         = self.parse_codigo(e)
        self.check_rules(e)
        e.tiempo = Tiempo()

        if e.tipo == "R" or e.tipo == "T":
            e.tiempo        = self.parse_tiempo(e)
        else:
            e.tiempo.tiempo = datetime.now()
        
        e.texto_limpito, e.calendarId = self.parse_texto(e)
        #print(e.calendarId) 
        return e


    pass

def main():

    p = Parser()

    frases = [  
                "cT tMAN10:20",
                "cR tHOY20:30", 
                "cT tMAN", 
                "cT t12:20/28", 
                "cT t10", 
                "cT t12:45", 
                "cT tMIN10", 
                "cT tH3",
                "cT t23:59", 
                "cT tMIN20", 
                "cT t30",
                "c t30",
                "cT",
                "cT "
              ]
    

    # for frase in frases:
        # entry = p.parse(frase) 
        # print(entry)
    while True:
        w = input("prompt: ")
        try:
            e = p.parse(w)
            print(e)
        except InvalidEntryError as error:
            print(error)

    return 1


if __name__ == "__main__":  
    main()
