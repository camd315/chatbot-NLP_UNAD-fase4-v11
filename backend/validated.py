"""Respuestas V11 permitidas SOLO con evidencia; lógica derivada de celdas 6-8 de Entrega."""
import re
import unicodedata

CASA_QUERY = "donde puedo recibir orientacion psicosocial y juridica en casa matria de cali"
LAW_QUERY = "que derechos reconoce la ley 1257 de 2008"
LAW_CONTEXT = "¿Cuáles son los derechos de las mujeres víctimas según el artículo 8 de la Ley 1257 de 2008?"
CASA_CONTEXT = "¿Dónde puedo recibir orientación psicosocial y jurídica en Casa Matria de Cali?"

def normalize(text):
    text=unicodedata.normalize('NFD',text.lower())
    text=''.join(c for c in text if unicodedata.category(c)!='Mn')
    return re.sub(r'\s+',' ',text).strip().strip('¿?¡! .')

def exact_route(question):
    q=normalize(question)
    return 'casa' if q==CASA_QUERY else ('ley' if q==LAW_QUERY else None)

def respond_casa(retriever):
    frags=retriever.retrieve(CASA_CONTEXT,k=4)
    docs=[f for f in frags if 'casa matria cumple 11' in normalize(f['documento'])]
    service=next((f for f in docs if 'psicosocial' in normalize(f['texto']) and 'juridic' in normalize(f['texto'])),None)
    phone=next((f for f in docs if re.search(r'311[\s.-]*612[\s.-]*00[\s.-]*00',normalize(f['texto']))),None)
    hours=next((f for f in docs if re.search(r'311[\s.-]*612[\s.-]*00[\s.-]*00',normalize(f['texto']))
                and re.search(r'24\s*(?:horas|/7)',normalize(f['texto']))),None)
    if not service or not phone:
        raise ValueError('Evidencia insuficiente: servicios o contacto ausentes')
    ref=lambda f: f"[documento institucional, página PDF {f['pagina_pdf']}]"
    lines=["Según el documento consultado, Casa Matria ofrece orientación psicosocial y jurídica. "+ref(service),
           "El número publicado es 311 612 0000. "+ref(phone)]
    if hours: lines.append("El documento describe atención telefónica 24 horas. "+ref(hours))
    lines.append("La disponibilidad actual del servicio no se ha verificado en tiempo real.")
    return '\n\n'.join(lines)

def respond_law(retriever):
    frags=retriever.retrieve(LAW_CONTEXT,article8=True)
    by_id={f['id']:f for f in frags}
    fragments=[]
    for i in range(1,5):
        f=by_id[f'Ley_1257_de_2008_p3_art8_f{i}']
        if f['documento'] != 'Ley_1257_de_2008.pdf' or int(f['pagina_pdf'])!=3:
            raise ValueError('Fuente jurídica inesperada')
        fragments.append(f['texto'].strip())
    joined=fragments[0]
    for next_chunk in fragments[1:]:
        overlap=0
        for n in range(min(len(joined),len(next_chunk)),29,-1):
            if joined.endswith(next_chunk[:n]):overlap=n;break
        if overlap<30:raise ValueError('Solapamiento no verificado')
        joined+=next_chunk[overlap:]
    joined=re.sub(r'\s+',' ',joined).strip()
    if re.search(r'CAP[IÍ]TULO\s+IV',joined,re.IGNORECASE):
        raise ValueError('Contenido posterior al artículo 8')
    matches=list(re.finditer(r'(?<![A-Za-zÀ-ÿ])([a-k])\)\s+',joined))
    if [m.group(1) for m in matches]!=list('abcdefghijk'):
        raise ValueError('No se identifican los once derechos')
    lines=['Según el artículo 8 de la Ley 1257 de 2008, el documento consultado reconoce:']
    for i,m in enumerate(matches):
        content=joined[m.end():matches[i+1].start() if i+1<len(matches) else len(joined)].strip()
        if len(content)<15:raise ValueError('Literal jurídico incompleto')
        lines.append(f'{m.group(1)}) {content}')
    lines.append('Fuente: Ley 1257 de 2008, página PDF 3, artículo 8. No se ha verificado la vigencia jurídica actual.')
    return '\n\n'.join(lines)
