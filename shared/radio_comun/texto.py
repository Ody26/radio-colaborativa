import re
import unicodedata

_PATRON_ETIQUETA = re.compile(r"<[^>]*>")
_CARACTERES_BIDIRECCIONALES = set("‪‫‬‭‮⁦⁧⁨⁩")

def validar_texto_plano(
    valor: str,
    *,
    campo: str,
    minimo: int,
    maximo: int,
    colapsar_espacios: bool = True,
) -> str:
    valor = unicodedata.normalize("NFC", valor).strip()
    if colapsar_espacios:
        valor = " ".join(valor.split())
    if any(unicodedata.category(c) == "Cc" or c in _CARACTERES_BIDIRECCIONALES for c in valor if c != "\n"):
        raise ValueError(f"El {campo} contiene caracteres no permitidos")
    if _PATRON_ETIQUETA.search(valor):
        raise ValueError(f"El {campo} no puede contener etiquetas HTML")
    if not minimo <= len(valor) <= maximo:
        raise ValueError(f"El {campo} debe tener entre {minimo} y {maximo} caracteres")
    return valor
