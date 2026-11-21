"""Chatbot documental V12, paso 28 (PILOTO PRIVADO, NO PUBLICAR).

Extrae oraciones completas verificables de resultados RAG. No sintetiza textos
con un LLM, no revisa vigencia de normas, y puede abstenerse cuando la
informacion es insuficiente. No cambia la coleccion ChromaDB.
"""
from dataclasses import dataclass
import re
import unicodedata
from .rag_v12 import Evidencia, RecuperadorV12


@dataclass(frozen=True)
class RespuestaV12:
    pregunta: str
    respuesta: str
    evidencias: list[Evidencia]
    estado: str


def _normalizar(texto: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFKD', texto.lower())
                   if not unicodedata.combining(c))


def _en_alcance(pregunta: str) -> bool:
    # Un filtro demostrativo, NO un clasificador robusto de intenciones.
    pistas = ('mujer', 'violencia', 'pareja', 'autonomi', 'emprend', 'cali',
              'genero', 'derecho', 'instituc', 'equidad', 'abuso', 'maltrato',
              'acoso', 'victima', 'comisaria', 'econom', 'empleo', 'trabajo',
              'psicolog', 'proteccion', 'discriminacion', 'igualdad',
              'amenaza', 'control', 'humillacion', 'aislamiento',
              'ruta de atencion')
    normal = _normalizar(pregunta)
    return any(p in normal for p in pistas)


def _intencion(pregunta: str) -> str:
    q = _normalizar(pregunta)
    if ('politic' in q or 'acuerdo' in q or 'normativ' in q or 'ordenanza' in q) and (
        'cali' in q or 'derecho' in q or 'mujer' in q
    ):
        return 'politicas'
    if ('violencia' in q or 'maltrato' in q or 'abuso' in q) and (
        'psicolog' in q or 'senal' in q or 'reconoc' in q
    ):
        return 'violencia_psicologica'
    if 'autonomi' in q and ('econom' in q or 'emple' in q or 'emprend' in q):
        return 'autonomia_economica'
    return 'general'


def _candidatos_textuales(texto: str) -> list[str]:
    """Candidatos con cierre gramatical; conservador frente a chunks cortados.

    Si el chunk empieza en minúscula, se descarta la primera sección hasta un
    cierre de oración. Evita inventar las partes ausentes.
    """
    limpio = re.sub(r'\s+', ' ', texto).strip()
    limpio = re.sub(r'(?i)^\s*(?:\d+\s+)?(?:contexto y justificaci[oó]n|resultados|conclusiones)\s+', '', limpio)
    # Corta en finales de oración o inicio de viñeta. Los grupos conservan
    # signos para impedir que fragmentos sin cierre se presenten completos.
    partes = re.findall(r'(?:^|(?<=[.!?])\s+|\s*[•]\s*)(.*?[.!?])(?=\s|$|\s*[•])', limpio)
    salida = []
    for parte in partes:
        frase = parte.strip(' \t\n-•')
        if not 65 <= len(frase) <= 650:
            continue
        if not re.match(r'^[¿¡«“"(]*[A-ZÁÉÍÓÚÜÑ]', frase):
            continue
        if re.search(r'(?i)(?:\s|:)\(?[a-z]\.|(?:\s+)(?:[a-z]|[0-9]+)\.$', frase):
            continue
        palabras = frase.split()
        if len(palabras) < 10:
            continue
        ratio_numeros = sum(any(c.isdigit() for c in p) for p in palabras) / len(palabras)
        if ratio_numeros > .20:
            continue
        salida.append(frase)
    return list(dict.fromkeys(salida))


def _filtrar_intencion(frase: str, intencion: str) -> bool:
    n = _normalizar(frase)
    if intencion == 'politicas':
        # Evitar recomendaciones sobre cómo administrar una política cuando
        # se pregunta cuáles políticas respaldan los derechos.
        instrumentos = ('politica publica para las mujeres', 'acuerdo 0',
                        'acuerdo municipal', 'ordenanza', 'subsecretaria de equidad',
                        'secretaria de bienestar social', 'consejo consultivo',
                        'observatorio de asuntos')
        return any(p in n for p in instrumentos)
    if intencion == 'violencia_psicologica':
        return ('psicolog' in n and any(p in n for p in (
            'control', 'aisla', 'humilla', 'insult', 'amenaz',
            'conducta', 'averg', 'emocion', 'acoso')))
    if intencion == 'autonomia_economica':
        return any(p in n for p in (
            'empleab', 'emprend', 'formacion', 'credito', 'laboral',
            'capacidad', 'ingreso', 'autonomia economica'))
    return True


def _prioridad(frase: str, intencion: str) -> float:
    n = _normalizar(frase)
    if intencion == 'politicas':
        # Nombres de normas concretas > descripcion general de gestión.
        return 0.045 * ('acuerdo 0539' in n or 'acuerdo 0313' in n) + \
               0.025 * ('politica publica para las mujeres' in n) + \
               0.015 * ('subsecretaria' in n or 'consejo consultivo' in n)
    if intencion == 'autonomia_economica':
        return 0.025 * ('formacion' in n or 'credito' in n or 'emprendimiento' in n)
    if intencion == 'violencia_psicologica':
        return 0.025 * ('amenaz' in n or 'aisla' in n or 'humilla' in n)
    return 0.0


class ChatbotDocumentalV12:
    def __init__(self, recuperador: RecuperadorV12):
        self.recuperador = recuperador

    def responder(self, pregunta: str, *, cantidad: int = 12) -> RespuestaV12:
        pregunta = pregunta.strip()
        if not pregunta:
            return RespuestaV12(pregunta, 'Escribe una pregunta para consultar los documentos.', [], 'consulta_vacia')
        if not _en_alcance(pregunta):
            return RespuestaV12(pregunta,
                'Esta consulta está fuera del alcance documental del prototipo '
                '(autonomía femenina, prevención de violencias y orientación institucional).',
                [], 'fuera_de_alcance')

        intencion = _intencion(pregunta)
        evidencias = self.recuperador.recuperar(pregunta, cantidad=cantidad)
        opciones = []
        for evidencia in evidencias:
            for frase in _candidatos_textuales(evidencia.texto):
                if _filtrar_intencion(frase, intencion):
                    opciones.append((frase, evidencia))
        if not opciones:
            return RespuestaV12(pregunta,
                'No encontré información documental suficientemente específica y completa '
                'para responder esta pregunta. Se requiere revisar las fuentes antes de '
                'proporcionar una orientación.', evidencias[:3], 'sin_evidencia_clara')

        vector_p = self.recuperador.modelo.encode(
            ['query: ' + pregunta], normalize_embeddings=True)[0]
        vectores_f = self.recuperador.modelo.encode(
            ['passage: ' + frase for frase, _ in opciones],
            normalize_embeddings=True, batch_size=16)
        puntuaciones = vectores_f @ vector_p
        orden = sorted(range(len(opciones)),
                       key=lambda i: float(puntuaciones[i]) + _prioridad(opciones[i][0], intencion),
                       reverse=True)

        seleccion = []
        ids = set()
        textos = set()
        for i in orden:
            frase, evidencia = opciones[i]
            clave = _normalizar(frase)
            if evidencia.id in ids or clave in textos:
                continue
            seleccion.append((frase, evidencia))
            ids.add(evidencia.id)
            textos.add(clave)
            if len(seleccion) == 2:
                break

        lineas = ['De acuerdo con los documentos consultados:']
        for frase, ev in seleccion:
            lineas.append(f'• {frase} (Fuente: {ev.cita}).')
        lineas.append('Nota: extractos documentales para evaluación privada; '
                      'no sustituyen orientación profesional ni confirman la vigencia '
                      'de políticas, normas o rutas institucionales.')
        return RespuestaV12(pregunta, '\n'.join(lineas),
                            [ev for _, ev in seleccion], 'extractiva_preliminar')
