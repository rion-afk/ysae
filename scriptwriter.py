import random
from llm import llama_chat

def build_script(topic: str, outlier_desc: str, hook_template: str, seed: int) -> dict:
    rng = random.Random(seed)
    hook = llama_chat(
        f"Argomento: {topic}\nContesto outlier: {outlier_desc}",
        system=f"""Sei uno scrittore di YouTube Shorts in italiano. Genera SOLO la prima frase
(0-3 secondi, massimo 12 parole) dello script. Stile hook: {hook_template}.
VIETATO: presentazioni, 'in questo video', 'scopri', ciao, preamboli.
Inizia con una domanda spiazzante o un'affermazione controintuitiva.
Rispondi SOLO con la frase.""", temperature=1.0, max_tokens=60)

    escalation = llama_chat(
        f"Hook iniziale: {hook}",
        system="""Genera 4-6 frasi in italiano da 8-12 parole ciascuna, taglienti,
ritmo crescente, che escalano la tensione della tesi. Nessun riempitivo,
una frase per riga. Rispondi SOLO con le frasi.""", temperature=0.85)

    visual = llama_chat(
        f"Script finora:\n{hook}\n{escalation}",
        system="""Genera 6-8 righe in italiano. Ogni riga: 'SHOT: <descrizione visiva
concreta e filmabile>' — coerenti con lo script. Nessuna altra parola.""", temperature=0.8)

    loop = llama_chat(
        f"Hook iniziale: {hook}",
        system=f"""Genera UNA frase finale in italiano (max 15 parole) che si ricollega
SINTATTICAMENTE all'hook '{hook}': l'ultima parola deve permettere il loop seamless.
Rispondi SOLO con la frase.""", temperature=0.9)

    return {"hook": hook, "escalation": escalation, "visual_shots": visual,
            "loop": loop, "hook_template": hook_template, "seed": seed}
