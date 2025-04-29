import sqlite3
import threading
import time
from envia_para_n8n import enviar_para_webhook

# Dicionário de timers ativos
timers = {}
lock = threading.Lock()  # Para evitar race conditions


# Inicializa o banco
def init_db():
    conn = sqlite3.connect('contatos.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contato (
            numero TEXT PRIMARY KEY,
            nome TEXT,
            mensagem TEXT
        )
    ''')
    conn.commit()
    conn.close()


# Salva ou atualiza mensagem no banco
def salvar_ou_atualizar_contato(numero, nome, mensagem):
    with lock:
        conn = sqlite3.connect('contatos.db')
        cursor = conn.cursor()

        # Verifica se já existe
        cursor.execute("SELECT mensagem FROM contato WHERE numero = ?",
                       (numero, ))
        row = cursor.fetchone()

        if row:
            nova_mensagem = row[0] + " , " + mensagem
            cursor.execute("UPDATE contato SET mensagem = ? WHERE numero = ?",
                           (nova_mensagem, numero))
        else:
            cursor.execute(
                "INSERT INTO contato (numero, nome, mensagem) VALUES (?, ?, ?)",
                (numero, nome, mensagem))

        conn.commit()
        conn.close()


# Função chamada quando o timer expira
def expirar_contato(numero):
    with lock:
        conn = sqlite3.connect('contatos.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM contato WHERE numero = ?", (numero, ))
        row = cursor.fetchone()

        if row:
            contato_finalizado = {
                "numero": row[0],
                "nome": row[1],
                "mensagem": row[2]
            }

            print("\n🚨 Tempo expirado! Contato finalizado:")
            print(contato_finalizado)
            # Envia o contato para o outro script
            enviar_para_webhook(contato_finalizado)

            # Remove do banco
            cursor.execute("DELETE FROM contato WHERE numero = ?", (numero, ))
            conn.commit()

        conn.close()
        timers.pop(numero, None)


# Reinicia o timer para o número
def reiniciar_timer(numero):
    with lock:
        if numero in timers:
            timers[numero].cancel()

        timer = threading.Timer(15.0, expirar_contato, args=[numero])
        timers[numero] = timer
        timer.start()


# Função externa que recebe nova mensagem
def receber_mensagem(dados):
    numero = dados.get("phone")
    nome = dados.get("senderName", "Desconhecido")
    mensagem = str(dados.get("message", ""))  # <- Corrigido aqui

    if not numero:
        print("⚠️ Número não informado. Ignorando...")
        return

    salvar_ou_atualizar_contato(numero, nome, mensagem)
    reiniciar_timer(numero)


# Inicializa banco ao importar
init_db()
