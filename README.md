# Trabalho Prático: O Labirinto dos Processos

## Integrantes do Grupo
1. João Victor Bertoldo
2. Giovana Aguiar
3. Matheus Diniz

##  Sobre o Projeto
Esta aplicação simula processos percorrendo um labirinto, demonstrando o funcionamento de conceitos centrais de Sistemas Operacionais[cite: 1]. A solução foi desenvolvida na linguagem Python, utilizando o módulo `multiprocessing`[cite: 1]. O sistema apresenta uma interface visual baseada no terminal, atualizada em tempo real[cite: 1].

## Arquitetura e Conceitos Aplicados

O sistema opera na arquitetura **Pai-Filho**, onde o Processo Principal gerencia a interface visual, e os Processos Filhos (exploradores) realizam o processamento e a navegação pelo labirinto.

* **Criação de Múltiplos Processos:** Foram instanciados múltiplos processos independentes (`multiprocessing.Process`), cada um responsável por explorar o labirinto usando uma lógica de Busca em Profundidade (DFS) e executar tarefas específicas[cite: 1].
* **Comunicação Interprocessos (IPC):** Como os processos possuem memória isolada, utilizamos Filas (`multiprocessing.Queue`) para a comunicação[cite: 1]. Os filhos enviam suas coordenadas pela fila, e o processo Pai as consome para renderizar a representação visual dos caminhos[cite: 1].
* **Sincronização:** Utilizamos Semáforos (`multiprocessing.Semaphore`) para proteger áreas críticas (pontos de Tarefa)[cite: 1]. Isso garante exclusão mútua, impedindo que dois processos realizem a mesma tarefa simultaneamente.
* **Condição de Saída:** O algoritmo garante que um processo só reconheça e utilize a saída do labirinto após ter cumprido todas as tarefas atribuídas durante o percurso[cite: 1].
* **Controle de Processos (Suspender/Retomar):** A aplicação permite criar, finalizar, suspender e retomar os processos durante a execução[cite: 1]. Para a pausa dinâmica, utilizamos `multiprocessing.Event` aliado a uma *Thread* em segundo plano que escuta os comandos do usuário.

---

## Como Executar

1. Certifique-se de ter o Python 3.x instalado em sua máquina.
2. Salve o código-fonte no arquivo `labirinto.py`.
3. Abra o terminal no diretório do arquivo e execute o comando:
   ```bash
   python labirinto.py
