import ollama
import numpy as np
def cossin(vec1, vec2):
    return np.dot(vec1, vec2)/(np.linalg.norm(vec1)*np.linalg.norm(vec2))

query = "search_query:como fazer requisições na api?"
resp = "respond"
responses = ["search_document: Como faço para redefinir minha senha?Na tela de login, clique em 'Esqueci minha senha' e informe o e-mail cadastrado. O link de redefinição chega em até 5 minutos e vale por 30 minutos. Se não chegar, peça ao cliente para conferir a caixa de spam antes de abrir chamado.",
'search_document: O link de redefinição de senha expirou. E agora? Basta solicitar um novo pelo mesmo caminho ("Esqueci minha senha"). Cada novo pedido invalida o link anterior. Não existe limite diário de solicitações.',
'search_document: Não consigo entrar mesmo com a senha certa. O que pode ser?Três causas cobrem quase todos os casos: (1) a conta está com acesso suspenso por falta de pagamento; (2) o usuário foi desativado por um administrador da empresa dele; (3) o e-mail digitado não é o cadastrado. Confirme os três antes de escalar.',
'search_document: Como adiciono um novo usuário à conta?Em Configurações → Usuários → Convidar. Só administradores da conta veem esse menu. O convite expira em 7 dias. O Plano Básico permite até 3 usuários, o Pro até 15, e o Enterprise não tem limite.',
'search_document: Quantos usuários cada plano permite?Plano Básico: 3 usuários. Plano Pro: 15 usuários. Plano Enterprise: ilimitado. Ao atingir o limite, o botão de convite fica desabilitado com aviso na tela.',
'search_document: Como faço upgrade ou downgrade de plano? Em Configurações → Assinatura → Alterar plano. O upgrade vale na hora e a cobrança é proporcional aos dias restantes. O downgrade só entra em vigor na renovação seguinte, e é bloqueado se a conta estiver acima do limite de usuários do plano de destino.',
'search_document: Qual a diferença entre Suporte Premium e o suporte incluso?O suporte incluso atende por e-mail em horário comercial, com resposta em até 24 horas úteis. O Suporte Premium é um adicional contratado à parte: atendimento por telefone e chat, 12h por dia, com primeira resposta em até 2 horas úteis.',
'search_document: Qual o prazo de resposta do suporte?Suporte incluso: até 24 horas úteis. Suporte Premium: até 2 horas úteis. Incidentes que derrubam o serviço para todos os usuários da conta são tratados como críticos e não seguem essa fila.',
'search_document: O sistema está fora do ar. Como confirmo?Consulte a página pública de status antes de qualquer coisa. Se houver incidente aberto lá, informe o cliente e não abra chamado duplicado. Se não houver, colete horário, mensagem de erro exata e navegador usado.',
'search_document: Como exporto meus dados?Em Configurações → Dados → Exportar. A exportação sai em CSV e chega por e-mail em até 15 minutos. Contas com mais de 500 mil registros podem levar algumas horas. A exportação está disponível em todos os planos.',
'search_document: Consigo importar dados de outra ferramenta?Sim, via CSV, em Configurações → Dados → Importar. O arquivo precisa estar em UTF-8 e ter no máximo 20 MB. Importações maiores são feitas pelo time de Consultoria.',
'search_document: A importação falhou com erro de codificação. O que fazer?O arquivo provavelmente está em ANSI/Latin-1. Peça ao cliente para salvar novamente como "CSV UTF-8" e tentar de novo. Se persistir, colete o arquivo (sem dados sensíveis) e escale para o segundo nível.',
'search_document: Como integro o sistema a outras ferramentas?Pelo webhook de eventos (Configurações → Integrações) ou pela API REST. A API está disponível no Plano Pro e no Enterprise; o Plano Básico não tem acesso. A chave é gerada pelo administrador da conta e pode ser revogada a qualquer momento.',
'search_document: Qual o limite de requisições da API?600 requisições por minuto por conta no Plano Pro e 3.000 no Enterprise. Ao estourar, a API responde 429 e o cliente deve espaçar as chamadas. Limites maiores são negociados comercialmente.',
'search_document: Esqueci de configurar o webhook e perdi eventos. Dá para reenviar?Sim, os eventos ficam disponíveis para reenvio por 7 dias em Integrações → Histórico de eventos → Reenviar. Passado esse prazo, não há como recuperar.',
'search_document: Como cancelo minha assinatura?Em Configurações → Assinatura → Cancelar. O acesso continua até o fim do período já pago, e os dados ficam disponíveis para exportação por mais 30 dias após o vencimento. Não há multa de cancelamento nos planos mensais.',
'search_document: Vocês têm aplicativo para celular?Não existe aplicativo nativo. A interface web é responsiva e funciona nos navegadores móveis atualizados. Não prometa data de lançamento de app ao cliente.',
'search_document: Onde vejo minhas faturas?Em Configurações → Assinatura → Faturas. Estão disponíveis as faturas dos últimos 24 meses, em PDF. Faturas anteriores a esse período são pedidas ao financeiro.'
]
allresp = [query] + responses
response = ollama.embed(model='nomic-embed-text',input=allresp)
results = response["embeddings"]
queryvect = results[0]
respvect = results[1:]

scored = []
bestres = []
"""
for vect,resp in zip(respvect,responses):
    score = cossin(queryvect,vect)
    scored.append((score,resp))
for score,text in sorted(scored, key=lambda x: x[0], reverse=True):
    print(f'Grade: {score:.4f} Mensagem: {text}')
"""
for vect,respo in zip(respvect,responses):
    score = cossin(queryvect,vect)
    scored.append(score)
    bestres.append((score,respo))
scored.sort(reverse=True)
bestres.sort(reverse=True)
if scored[0] >= 0.7 and resp == "responde":
    print("Responde")
elif scored[0] < 0.7 and resp == "responde":
    print("Falso negativo")
elif scored[0] < 0.7 and resp != "responde":
    print("Não Responde")
elif scored[0] >= 0.7 and resp != "responde":
    print("Falso positivo")
for i in range(2):
    print(f'Grade: {bestres[i][0]:.4f} Mensagem: {bestres[i][1]}')