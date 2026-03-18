import time
import statistics
import sys
import os
from multiprocessing import Pool, cpu_count

# ─────────────────────────────────────────────
# Cores para terminal
# ─────────────────────────────────────────────
RESET   = "\033[0m"
BOLD    = "\033[1m"
CYAN    = "\033[96m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
MAGENTA = "\033[95m"
WHITE   = "\033[97m"
DIM     = "\033[2m"
RED     = "\033[91m"

# ─────────────────────────────────────────────
# Leitura do arquivo .txt
# ─────────────────────────────────────────────

def ler_arquivo(caminho_arquivo):
    if not os.path.exists(caminho_arquivo):
        print(f"\n{RED}❌  Arquivo não encontrado: '{caminho_arquivo}'{RESET}\n")
        sys.exit(1)

    lista = []
    erros = 0
    print(f"  {DIM}Carregando... (10 milhões de números, aguarde){RESET}")
    with open(caminho_arquivo, "r", encoding="utf-8") as f:
        for i, linha in enumerate(f, 1):
            linha = linha.strip()
            if not linha:
                continue
            try:
                lista.append(int(linha))
            except ValueError:
                erros += 1
                if erros <= 5:
                    print(f"  {DIM}⚠ Linha {i} ignorada (não é inteiro): '{linha}'{RESET}")

    if erros > 5:
        print(f"  {DIM}⚠ ... e mais {erros - 5} linha(s) ignorada(s){RESET}")

    return lista

# ─────────────────────────────────────────────
# Soma de chunk — função no nível do módulo
# (obrigatório para o multiprocessing serializar)
# ─────────────────────────────────────────────

def somar_chunk(chunk):
    return sum(chunk)

def dividir_em_chunks(lista, n):
    tamanho = len(lista) // n
    chunks = []
    for i in range(n):
        inicio = i * tamanho
        fim = inicio + tamanho if i < n - 1 else len(lista)
        chunks.append(lista[inicio:fim])
    return chunks

# ─────────────────────────────────────────────
# Execução com MULTIPROCESSING
# ─────────────────────────────────────────────

def executar_processos(lista, n_processos):
    chunks = dividir_em_chunks(lista, n_processos)
    inicio = time.perf_counter()
    with Pool(processes=n_processos) as pool:
        parciais = pool.map(somar_chunk, chunks)
    fim = time.perf_counter()
    return fim - inicio, sum(parciais)

# ──────────────────────────────
# Configurações do benchmark
# ──────────────────────────────

CONFIGURACOES = [2, 4, 8, 12]
N_REPETICOES  = 3

def barra_visual(tempo, tempo_max, largura=30):
    proporcao = tempo / tempo_max if tempo_max > 0 else 0
    preenchido = int(proporcao * largura)
    return "█" * preenchido + "░" * (largura - preenchido)

def main():
    if len(sys.argv) >= 2:
        caminho = sys.argv[1]
    else:
        print(f"\n{CYAN}Digite o caminho do arquivo .txt:{RESET} ", end="")
        caminho = input().strip().strip('"').strip("'")

    print(f"\n{BOLD}{CYAN}╔══════════════════════════════════════════════════════╗{RESET}")
    print(f"{BOLD}{CYAN}║       BENCHMARK MULTIPROCESSING — 10 MILHÕES         ║{RESET}")
    print(f"{BOLD}{CYAN}╚══════════════════════════════════════════════════════╝{RESET}")
    print(f"  CPUs disponíveis: {BOLD}{cpu_count()}{RESET}\n")

    print(f"{DIM}  Lendo arquivo: {caminho}{RESET}")
    lista = ler_arquivo(caminho)
    print(f"  {GREEN}✓ {len(lista):,} números carregados!{RESET}\n")

    tempos_medios = {}
    soma_final = None

    for n in CONFIGURACOES:
        print(f"  {YELLOW}▶ Testando com {n:>2} processos ({N_REPETICOES}x)...{RESET}", end="", flush=True)
        repeticoes = []
        for _ in range(N_REPETICOES):
            t, soma = executar_processos(lista, n)
            repeticoes.append(t)
            print(".", end="", flush=True)

        media  = statistics.mean(repeticoes)
        desvio = statistics.stdev(repeticoes) if len(repeticoes) > 1 else 0
        tempos_medios[n] = media
        soma_final = soma
        print(f"  {GREEN}{media:.4f}s{RESET} {DIM}(±{desvio:.4f}s){RESET}")

    # ─── Tabela de resultados ───
    tempo_max  = max(tempos_medios.values())
    tempo_base = tempos_medios[CONFIGURACOES[0]]
    melhor     = min(tempos_medios, key=tempos_medios.get)

    print(f"\n{BOLD}{WHITE}{'─'*54}{RESET}")
    print(f"{BOLD}{WHITE}  RESULTADOS FINAIS{RESET}")
    print(f"{BOLD}{WHITE}{'─'*54}{RESET}")
    print(f"  {'Processos':<12} {'Tempo Médio':>12}  {'Speedup':>8}  Gráfico")
    print(f"  {'─'*9:<12} {'─'*10:>12}  {'─'*7:>8}  {'─'*30}")

    for n, tempo in tempos_medios.items():
        speedup  = tempo_base / tempo
        barra    = barra_visual(tempo, tempo_max)
        destaque = f"{BOLD}{GREEN}" if n == melhor else WHITE
        print(f"  {destaque}{n:<12} {tempo:>11.4f}s  {speedup:>7.2f}x  {barra}{RESET}")

    print(f"{BOLD}{WHITE}{'─'*54}{RESET}")
    print(f"\n  {GREEN}✓ Melhor resultado: {melhor} processos ({tempos_medios[melhor]:.4f}s){RESET}")

    print(f"\n{BOLD}{CYAN}{'─'*54}{RESET}")
    print(f"{BOLD}{CYAN}  RESULTADO DO CÁLCULO{RESET}")
    print(f"{BOLD}{CYAN}{'─'*54}{RESET}")
    print(f"  Total de números : {len(lista):,}")
    print(f"  {BOLD}Soma total       : {soma_final:,}{RESET}")
    print(f"{BOLD}{CYAN}{'─'*54}{RESET}\n")

if __name__ == "__main__":
    main()
