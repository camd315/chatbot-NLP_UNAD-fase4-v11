"""Recuperación extractiva V11 para uso académico privado.
No genera texto con LLM ni declara validados fragmentos por relevancia solamente.
"""


def retrieve_v11_answer(retriever, question, top_k=4):
    fragments = retriever.retrieve(question, k=top_k)
    if not fragments:
        return None
    blocks = []
    for n, fragment in enumerate(fragments, 1):
        doc = str(fragment.get("documento") or "Documento sin título")
        page = str(fragment.get("pagina_pdf") or "sin página")
        ident = str(fragment.get("id") or "sin identificador")
        body = " ".join(str(fragment.get("texto") or "").split())
        if not body:
            continue
        # Fragmentos breves para consulta privada de relevancia, no validación legal.
        snippet = body[:650].rstrip() + ("…" if len(body) > 650 else "")
        blocks.append(
            f"**Fuente {n}: {doc}** (página PDF: {page}; fragmento: `{ident}`)\n\n"
            + snippet
        )
    if not blocks:
        return None
    return (
        "Encontré estos **fragmentos potencialmente relacionados** en la base V11. "
        "Son extractos para revisión académica; no constituyen una respuesta "
        "jurídica validada ni verifican vigencia normativa.\n\n"
        + "\n\n---\n\n".join(blocks)
        + "\n\n**Verifica las fuentes originales y su vigencia antes de usar esta información.**"
    )
