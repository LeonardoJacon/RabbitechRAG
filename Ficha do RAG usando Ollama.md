# Assistente de triagem de suporte técnico com Ollama e RAG

Teste técnico da RabbITech. Autor: Leonardo. Base: faq_interno.md (18 entradas). Repositório: README.md (fluxograma), docs/anexo_detalhado.md (resultados completos), src/ (Tentaiv_1.py e Teste_1.py) e tests/.

## 1. Contexto e restrições

O assistente decide entre responder automaticamente e escalar a um atendente, por busca de similaridade (RAG) sobre o FAQ. Restrições: modelo local via Ollama, nenhuma API externa, nenhum dado do cliente fora do ambiente (inclusive nos embeddings) e escalar quando a confiança for baixa. Medidas em notebook i5-13420H, 16 GB, sem GPU, com Ollama 0.40.16, llama3.1:8b (contexto de 4096, CPU) e nomic-embed-text. O FAQ (revisão de 12/2025, a reindexar a cada revisão) não cobre reembolso, preços, a URL da página de status, passos de webhook e de API, nem onde ver usuários e administrador; essas mensagens devem escalar.

## 2. Fluxo do pipeline

```
indexação (uma vez por revisão do FAQ):
  vetor[i] ← embed("search_document: " + pergunta + resposta)

por mensagem (independente, sem histórico):
  q ← embed("search_query: " + mensagem)
  melhores ← 2 entradas de maior cosseno com q        # k = 2
  se nota(melhores[0]) >= 0,70:                        # limiar provisório
      saída ← selecionador_LLM(mensagem, Trecho 1, Trecho 2)
      se saída inválida: escalar("saída inválida")     # falha segura
      se saída == NENHUM: escalar("nenhum trecho responde")
      responder(texto ao cliente das entradas escolhidas)
  senão se saudação/agradecimento/despedida e mensagem curta:
      responder(resposta_padrão)                       # sem LLM
  senão: escalar("fora do escopo")
escalar(motivo): envia ao atendente mensagem, motivo, nota e trechos
```

- **Dois caminhos:** resposta automática ou escalonamento. O selecionador responde só números de trechos ou NENHUM; a cobertura parcial escala (a regra de triagem prevê também a ressalva, que o protótipo não implementa).
- **Intenção pela própria busca:** é a entrada mais próxima; abaixo do limiar, “fora do escopo”, exceto conversa (frases de exemplo por embedding, resposta sem LLM). “Bom dia”: 0,5588; “bom dia, como cancelo o plano”: 0,7110, e segue pelo FAQ.

## 3. Justificativa técnica

**3.1 Ollama e RAG.** Local, pela política de dados. RAG porque, sem contexto, a mesma pergunta sobre o limite da API teve duas respostas, uma inventando que a RabbITech é uma empresa de cloud, contra o FAQ. No RAG os trechos entram no prompt e o modelo não é treinado de novo; “use só os trechos” é um pedido, não uma garantia.

**3.2 Embeddings.** nomic-embed-text (274 MB), um chunk por entrada (pergunta e resposta), prefixos search_document e search_query. k = 2: com k = 1 o modelo disse que não era possível exportar dados após cancelar (o FAQ dá 30 dias). Só a pergunta foi testado na mensagem 5 (0,7722 e 0,6903, contra 0,7812 e 0,7498); mantive pergunta e resposta.

**3.3 Limiar.** Método: 16 mensagens (9 com resposta total ou parcial, 7 sem), nota da melhor entrada e contagem de falsos positivos (aceitar o que devia escalar) e negativos (escalar o que tinha resposta). Notas de 0,6051 a 0,8829 com resposta e de 0,6213 a 0,7838 sem. Um falso positivo custa mais: entrega informação errada.

| Limiar | Falsos positivos | Falsos negativos |
|---|---|---|
| 0,78 | 1 | 5 |
| 0,70 | 1 | 2 |

Escolha provisória: **0,70** (qualquer valor de 0,6946 a 0,7220 dá o mesmo resultado). O falso positivo é a mensagem 6 (0,7838, contra a entrada de limites da API), que nenhum limiar abaixo de 0,78 barra; os negativos são a 13 e a 16. Limitações: 16 mensagens, limiar escolhido no mesmo conjunto em que é avaliado, a nota mede assunto, não resposta, e muda com o formato do texto embutido (mensagem 13: cerca de 0,70 numa versão anterior, 0,6051 na final). Refazer se a configuração mudar e recalibrar com mensagens reais.

**3.4 Geração e verificação.** Resposta extrativa: o sistema monta a resposta com o texto das entradas, revisado para o cliente (sem as instruções ao atendente do FAQ), e nenhuma frase do modelo chega ao cliente. Descartei comparar a resposta por código (um passo inventado como “criar uma nova integração” usa palavras do trecho) e pedir ao modelo que julgue a própria resposta (chamada extra, mesmo modelo). O llama3.1 é o selecionador. Testes (uma execução por caso; detalhes no anexo): com um prompt que pedia uma frase, o modelo errou a mensagem 9 e inventou como pedir reembolso na 15; com saída só por números, respondeu NENHUM nas quatro mensagens que deviam escalar (a 6 foi aceita em uma execução e barrada em outra), 3 de 7 execuções vieram fora do formato, que a falha segura escala, e na mensagem 5 omitiu o trecho de cancelamento (30 dias).

## 4. Riscos técnicos e mitigações

| Risco | Evidência medida | Mitigação | Limite |
|---|---|---|---|
| Alucinação | Sem contexto: cloud inventada. Com trechos e geração livre: passos inventados, “não é possível exportar” (k = 1). | Resposta extrativa; saída restrita; falha segura; k ≥ 2; escalar na dúvida. | O selecionador também erra (mensagens 5 e 6). |
| Latência | Geração de 7 a 8 tokens/s; prompt novo a cerca de 24 tokens/s. Selecionador de 5 tokens: 5,5 a 7,5 s com cache, cerca de 10 s sem; carga a frio, cerca de 15 s a mais. | Sem geração livre; saída curta; instrução fixa no início (cache); modelo mantido carregado (conferir o parâmetro na documentação). | CPU de notebook; embedding e concorrência não medidos. |
| Contexto | Janela de 4096; prompt com 2 trechos: 245 a 270 tokens. | Um chunk por entrada; k = 2. | Cresce com k e com a base. |
| Falsa semelhança e dois assuntos | Mensagem 6: 0,7838; 9: 0,6946; 10: 0,6921. Mensagem 16: melhor entrada foi a do aplicativo (0,6849). | Selecionador como segunda barreira; escalar sem trecho; dividir a mensagem (evolução). | Nenhum limiar abaixo de 0,78 barra a 6. |
| Mensagens sem pedido de suporte | “Bom dia”: 0,5588; mista: 0,7110. | Frases de exemplo, resposta sem LLM, só mensagens curtas. | Lista e limiar de conversa não definidos nem testados. |

## 5. Estimativa de esforço (implementação real)

| Etapa | Dias | Justificativa |
|---|---|---|
| Indexação e busca | 0,5 | O protótipo já faz embeddings e cosseno. |
| Texto do FAQ ao cliente | 0,5 | 18 entradas curtas, validadas com quem mantém o FAQ. |
| Selecionador | 1,5 | Prompt, validador e falha segura; o modelo variou. |
| Resposta e escalonamento | 1 | Montar o texto e definir o que vai ao atendente. |
| Integração com o canal | 1,5 | Depende de sistemas da empresa; a mais incerta. |
| Calibração e testes | 2 | Ampliar o conjunto, refazer o limiar, medir latência. |
| Documentação e execução local | 1 | README, serviço do Ollama e registros. |
| **Total** | **8** | Cerca de 10 dias úteis com 20% de margem (uma pessoa). |

## 6. Uso de IA

Usei o Claude (Anthropic) como mentor nos estudos, para revisar o meu raciocínio e organizar e redigir este documento a partir das minhas medidas, testes e decisões; scripts, prompts e medições são meus. Sugestões que ajustei:

- **Latência.** A IA estimou 8 a 10 s por chamada do selecionador; medi 5,5 a 7,5 s com saída curta e usei as minhas medidas.
- **Limiares.** A IA sugeriu 0,72, 0,70, 0,69 e 0,77 como pontos de teste; acrescentei outros da minha amostra. O 0,70 final coincide com um sugerido e foi mantido por dar o mesmo resultado que 0,72.
- **Formato.** A IA sugeriu pedir só números; o modelo ignorou o formato em 3 de 7 execuções, então adotei validação com falha segura.
