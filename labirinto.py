import multiprocessing
import threading
import time
import os

labirinto = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 'T', 0, 0, 1],
    [1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 1, 0, 1, 'T', 1, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 'S', 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

CORES = {
    "reset": "\033[0m",
    "parede": "\033[94m███\033[0m",
    "tarefa": "\033[93m T \033[0m",
    "saida": "\033[92m S \033[0m",
    "p1": "\033[91m P1\033[0m",
    "p2": "\033[95m P2\033[0m"
}


def imprimir_mapa(mapa, posicoes, logs):
    os.system('cls' if os.name == 'nt' else 'clear')

    print("\033[1m=== O LABIRINTO DOS PROCESSOS ===\033[0m")
    print("Pressione [ENTER] a qualquer momento para PAUSAR / RETOMAR\n")

    # Desenha o labirinto
    for y, linha in enumerate(mapa):
        linha_visual = ""
        for x, celula in enumerate(linha):
            processo_aqui = None
            for pid, pos in posicoes.items():
                if pos == (x, y):
                    processo_aqui = pid
                    break

            if processo_aqui == 1:
                linha_visual += CORES["p1"]
            elif processo_aqui == 2:
                linha_visual += CORES["p2"]
            elif celula == 1:
                linha_visual += CORES["parede"]
            elif celula == 0:
                linha_visual += "   "
            elif celula == 'T':
                linha_visual += CORES["tarefa"]
            elif celula == 'S':
                linha_visual += CORES["saida"]

        print(linha_visual)

    print("\n\033[1m--- STATUS DOS PROCESSOS ---\033[0m")
    for log in logs.values():
        print(log)
    print("=================================")


def explorador(id_processo, x_inicial, y_inicial, mapa, fila_msg, semaforo, evento_pausa):
    visitados = set()
    pilha_de_caminhos = [(x_inicial, y_inicial)]
    tarefas_concluidas = 0

    while len(pilha_de_caminhos) > 0:
        evento_pausa.wait()

        x, y = pilha_de_caminhos.pop()

        if (x, y) in visitados:
            continue
        visitados.add((x, y))

        fila_msg.put({"id": id_processo, "x": x,
                     "y": y, "status": "explorando"})
        time.sleep(0.4)

        casa_atual = mapa[y][x]

        if casa_atual == 'T':
            semaforo.acquire()
            fila_msg.put({"id": id_processo, "x": x, "y": y,
                         "status": "executando tarefa (área crítica)"})
            time.sleep(2)
            tarefas_concluidas += 1
            semaforo.release()

        elif casa_atual == 'S' and tarefas_concluidas > 0:
            break

        movimentos = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for dx, dy in movimentos:
            novo_x = x + dx
            novo_y = y + dy
            if 0 <= novo_y < len(mapa) and 0 <= novo_x < len(mapa[0]):
                vizinho = mapa[novo_y][novo_x]
                if vizinho in [0, 'T', 'S'] and (novo_x, novo_y) not in visitados:
                    pilha_de_caminhos.append((novo_x, novo_y))

    fila_msg.put({"id": id_processo, "status": "fim"})


def escutar_teclado(evento_pausa):
    while True:
        input()
        if evento_pausa.is_set():
            evento_pausa.clear()
        else:
            evento_pausa.set()


if __name__ == '__main__':
    fila = multiprocessing.Queue()
    semaforo = multiprocessing.Semaphore(1)
    evento_pausa = multiprocessing.Event()
    evento_pausa.set()

    thread_teclado = threading.Thread(
        target=escutar_teclado, args=(evento_pausa,), daemon=True)
    thread_teclado.start()

    p1 = multiprocessing.Process(target=explorador, args=(
        1, 1, 1, labirinto, fila, semaforo, evento_pausa))
    p2 = multiprocessing.Process(target=explorador, args=(
        2, 1, 3, labirinto, fila, semaforo, evento_pausa))

    p1.start()
    p2.start()

    processos_ativos = 2
    posicoes_atuais = {1: (1, 1), 2: (1, 3)}
    logs_atuais = {1: "Processo 1 iniciando...", 2: "Processo 2 iniciando..."}

    while processos_ativos > 0:
        mensagem = fila.get()
        pid = mensagem["id"]

        if mensagem.get("status") == "fim":
            processos_ativos -= 1
            logs_atuais[pid] = f"Processo {pid} | \033[92mFINALIZADO (Saiu do labirinto)\033[0m"
            if pid in posicoes_atuais:
                del posicoes_atuais[pid]

            imprimir_mapa(labirinto, posicoes_atuais, logs_atuais)
            continue

        posicoes_atuais[pid] = (mensagem["x"], mensagem["y"])

        estado_geral = "MOVENDO" if evento_pausa.is_set(
        ) else "\033[91mPAUSADO\033[0m"
        logs_atuais[pid] = f"[{estado_geral}] Processo {pid} em ({mensagem['x']}, {mensagem['y']}) | Status: {mensagem['status']}"

        imprimir_mapa(labirinto, posicoes_atuais, logs_atuais)

    p1.join()
    p2.join()
    print("\nSimulação encerrada com sucesso!")
