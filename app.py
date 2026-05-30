from flask import Flask, jsonify, request, render_template, redirect, url_for
import json
import os
from datetime import date

app = Flask(__name__)

# caminho absoluto — sempre aponta para a pasta do app.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARQUIVO  = os.path.join(BASE_DIR, "tarefas.json")

# cria o arquivo se não existir
def inicializar_json():
    if not os.path.exists(ARQUIVO):
        with open(ARQUIVO, "w", encoding="utf-8") as f:
            json.dump({"tarefas": []}, f, indent=2)

def ler_tarefas():
    inicializar_json()
    with open(ARQUIVO, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_tarefas(dados):
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)

# ─── PÁGINA PRINCIPAL ─────────────────────────────────────
@app.route("/")
def index():
    dados = ler_tarefas()
    filtro = request.args.get("filtro", "todas")

    if filtro == "pendentes":
        tarefas = [t for t in dados["tarefas"] if not t["concluida"]]
    elif filtro == "concluidas":
        tarefas = [t for t in dados["tarefas"] if t["concluida"]]
    else:
        tarefas = dados["tarefas"]

    return render_template("index.html", tarefas=tarefas, filtro_ativo=filtro)

# ─── CRIAR ────────────────────────────────────────────────
@app.route("/tarefas", methods=["POST"])
def criar_tarefa():
    dados = ler_tarefas()
    titulo = request.form.get("titulo", "").strip()

    if not titulo:
        return redirect(url_for("index"))

    ids_existentes = [t["id"] for t in dados["tarefas"]]
    novo_id = max(ids_existentes) + 1 if ids_existentes else 1

    dados["tarefas"].append({
        "id": novo_id,
        "titulo": titulo,
        "concluida": False,
        "data": str(date.today())
    })
    salvar_tarefas(dados)
    return redirect(url_for("index"))


# ─── CONCLUIR ─────────────────────────────────────────────
@app.route("/tarefas/<int:id>/concluir", methods=["POST"])
def concluir_tarefa(id):
    dados = ler_tarefas()
    for tarefa in dados["tarefas"]:
        if tarefa["id"] == id:
            tarefa["concluida"] = not tarefa["concluida"]  # alterna o status
            break
    salvar_tarefas(dados)
    return redirect(url_for("index"))


# ─── DELETAR ──────────────────────────────────────────────
@app.route("/tarefas/<int:id>/deletar", methods=["POST"])
def deletar_tarefa(id):
    dados = ler_tarefas()
    dados["tarefas"] = [t for t in dados["tarefas"] if t["id"] != id]
    salvar_tarefas(dados)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)