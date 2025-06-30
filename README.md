# NicePandora

Esta versão do Pandora, o NicePandora, introduz um sistema de Inteligência Artificial (IA), através da API Gemini (Google), que fornece feedback pedagógico contextualizado aos alunos sobre os erros no seu código.

## 🚀 Como Funciona a Integração com IA
Ao falhar um teste numa submissão de código, o aluno tem acesso a um botão "Help".

Este botão abre uma janela de chat interativa onde o aluno pode conversar com a IA.

## O Gemini analisa:

- A descrição do exercício.

O código correto de referência (sem nunca ser mostrado ao aluno).

O código submetido pelo aluno.

O input, o output esperado, o output obtido e a diferença entre ambos.

Com base nestes dados, a IA gera dicas ajustadas ao nível de dificuldade definido pelo professor, sem fornecer diretamente a solução.

## 🔒 Mecanismos de Controlo
O professor pode definir uma blacklist de palavras proibidas, impedindo que a IA utilize termos sensíveis, como partes da solução.

Caso a IA gere uma resposta contendo palavras proibidas, essa resposta não é apresentada ao aluno. O sistema automaticamente solicita ao Gemini uma nova resposta, livre dessas palavras.

Todo o histórico das interações com a IA é guardado:

Por Teste e Por Submissão.

Inclui data, hora, input do aluno, resposta da IA, e se a resposta violou ou não a blacklist.

O professor pode visualizar e exportar todas as interações, além de aceder a estatísticas sobre o número de interações e a percentagem de respostas bloqueadas.

## ⭐ Avaliação da IA
Após a primeira utilização da IA num exercício, o aluno é convidado a avaliar a qualidade da ajuda recebida:

Avaliação de 1 a 5 estrelas.

Comentário opcional.

As avaliações ficam visíveis na dashboard administrativa, permitindo monitorizar a qualidade percebida da IA.

## 🔑 Uso da API Gemini
Cada utilizador deve configurar a sua própria API Key do Gemini, diretamente no seu perfil na plataforma.

Isso garante sustentabilidade no uso dos recursos e controlo dos custos associados.

## ⚙️ Fluxo de Funcionamento
O aluno submete o código e verifica o resultado.

Se algum teste falhar, o botão "Help" aparece.

Ao clicar, abre-se uma janela de chat que comunica diretamente com o Gemini, passando um prompt estruturado com regras pedagógicas.

O aluno pode fazer perguntas adicionais durante a mesma sessão de chat.

Toda a conversa é armazenada para controlo docente e futura análise.

## 📊 Painel Administrativo
Visualização detalhada de todas as interações dos alunos com a IA.

Estatísticas por teste, incluindo:

Número de interações.

Respostas bloqueadas pela blacklist.

Opção de download de todos os dados em formato JSON.
