import numpy as np
import ollama


def cosine_similarity(vec_a, vec_b):
    return np.dot(vec_a, vec_b) / (
        np.linalg.norm(vec_a) * np.linalg.norm(vec_b)
    )

query = "search_query: 	como fazer requisições na api?"
responses = [
    "search_document: Pergunta: Como faço para redefinir minha senha?",
    "search_document: Pergunta: O link de redefinição de senha expirou. E agora?",
    "search_document: Pergunta: Não consigo entrar mesmo com a senha certa. O que pode ser?",
    "search_document: Pergunta: Como adiciono um novo usuário à conta?",
    "search_document: Pergunta: Quantos usuários cada plano permite?",
    "search_document: Pergunta: Como faço upgrade ou downgrade de plano?",
    "search_document: Pergunta: Qual a diferença entre Suporte Premium e o suporte incluso?",
    "search_document: Pergunta: Qual o prazo de resposta do suporte?",
    "search_document: Pergunta: O sistema está fora do ar. Como confirmo?",
    "search_document: Pergunta: Como exporto meus dados?",
    "search_document: Pergunta: Consigo importar dados de outra ferramenta?",
    "search_document: Pergunta: A importação falhou com erro de codificação. O que fazer?",
    "search_document: Pergunta: Como integro o sistema a outras ferramentas?",
    "search_document: Pergunta: Qual o limite de requisições da API?",
    "search_document: Pergunta: Esqueci de configurar o webhook e perdi eventos. Dá para reenviar?",
    "search_document: Pergunta: Como cancelo minha assinatura?",
    "search_document: Pergunta: Vocês têm aplicativo para celular?",
    "search_document: Pergunta: Onde vejo minhas faturas?",
]


all_texts = [query] + responses
result = ollama.embed(model="nomic-embed-text", input=all_texts)

embeddings = result["embeddings"]
query_vec = embeddings[0]
response_vecs = embeddings[1:]

scored_responses = []
for text, vec in zip(responses, response_vecs):
    score = cosine_similarity(query_vec, vec)
    scored_responses.append((score, text))

for score, text in sorted(scored_responses, reverse=True):
    print(f"Score: {score:.4f} | {text}")