from secrets import choice, randbelow
ANIMALES = ("Zorro", "Búho", "Delfín", "Lince", "Colibrí", "Panda", "Tigre", "Koala", "Halcón", "Jaguar")
ADJETIVOS = ("Sonoro", "Rítmico", "Melódico", "Eléctrico", "Acústico", "Veloz", "Cósmico", "Nocturno", "Vibrante", "Sereno")

def generar_apodo() -> str:
    return f"{choice(ANIMALES)} {choice(ADJETIVOS)} {randbelow(90) + 10}"
