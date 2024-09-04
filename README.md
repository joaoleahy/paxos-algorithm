# Implementação do Protocolo Paxos

## Arquitetura
A implementação do protocolo Paxos está estruturada em um sistema distribuído de processos, onde cada processo pode desempenhar o papel de propositor ou aceitador. O sistema consiste nos seguintes componentes principais:
- **Processo**: Representa uma instância de um nó que pode propor valores para consenso ou aceitá-los. Cada processo tem um identificador único e é responsável por se comunicar com outros processos.
- **Comunicador**: Uma classe responsável pela comunicação entre processos utilizando sockets UDP. Cada processo cria um objeto Comunicador para enviar e receber mensagens de outros processos.
- **Mensagem**: Define os tipos de mensagens trocadas entre processos, como *PREPARE*, *PROMISE*, *ACCEPT*, *ACCEPTED*, e *DECIDE*. Cada mensagem contém um tipo, remetente, número da proposta, e valor proposto.

Dessa forma, basicamente temos que: **Processos** utilizam o **Comunicador** para enviar e receber **Mensagens** que definem o fluxo do protocolo Paxos.

## Workflow do Algoritmo
1. **Fase de Preparação (Prepare):** Um propositor escolhe um número de proposta maior do que qualquer número de proposta que ele usou anteriormente e envia uma mensagem *PREPARE* para a maioria dos aceitadores.
2. **Promessa (Promise):** Ao receber uma mensagem *PREPARE*, um aceitador responde com uma mensagem PROMISE, prometendo não aceitar nenhuma proposta com um número menor que o número da proposta recebida. Se o aceitador já aceitou uma proposta anteriormente, ele a retorna.
3. **Proposta de Aceitação (Accept):** Após receber promessas suficientes (maioria), o propositor envia uma mensagem *ACCEPT* com o valor proposto (ou o valor de uma proposta anterior mais alta que tenha sido prometida) para os aceitadores.
4. **Aceitação (Accepted):** Os aceitadores respondem com uma mensagem ACCEPTED ao receber uma mensagem ACCEPT com um número de proposta que seja maior ou igual ao maior número de proposta que eles já prometeram não aceitar. Isso indica que eles aceitam a proposta.
5. **Decisão (Decide):** Quando um propositor recebe confirmações suficientes (maioria) de que sua proposta foi aceita, ele envia uma mensagem DECIDE para todos os processos, indicando que o consenso foi alcançado.

## Decisões de Implementação
- **Sockets UDP:** Utilizamos sockets UDP devido à sua natureza não orientada a conexão. Isso significa que o UDP não estabelece uma conexão persistente entre o remetente e o destinatário antes de enviar dados, ao contrário do TCP, que exige um processo de handshake para estabelecer uma conexão confiável. A ausência de necessidade de conexão reduz a sobrecarga de comunicação e simplifica o envio de mensagens entre processos. Isso é vantajoso em sistemas distribuídos onde a baixa latência é crítica e as mensagens curtas e frequentes são comuns, como no protocolo Paxos. Além disso, UDP é naturalmente mais eficiente em termos de performance em cenários onde a perda de pacotes é tolerável, visto que Paxos é projetado para lidar com a perda de mensagens e falhas de comunicação.
- **Estruturas de Dados Simples:** Utilizamos estruturas de dados simples, como classes para mensagens e processos, para facilitar a manutenção e a extensão do código.
- **Multiprocessing:** Utilizamos a biblioteca de multiprocessing do Python permitindo a criação de processos em paralelo que, embora executem no mesmo ambiente físico, simulam a independência e o isolamento dos nós de um sistema distribuído. Esse isolamento em processos separados ajuda a imitar falhas de rede e atrasos, condições típicas em ambientes distribuídos. 

## Como Compilar e Executar o Projeto
1. Certifique-se de ter Python instalado em sua máquina.
2. Navegue até o diretório raíz do projeto.
3. Instale todas as dependências necessárias usando o comando: `pip install -r requirements.txt`
4. Crie um arquivo `.env` na raíz do projeto e preencha as variáveis de ambientes necessárias, conforme listado no arquivo `.env.example`
5. Execute o script principal usando o comando: `python main.py`.

*Obs: As ações e decisões dos processos serão registradas em tempo real no console, facilitando a análise do fluxo do algoritmo.*