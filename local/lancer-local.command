#!/bin/bash
# Nephélé en local, modèle sur la machine (LM Studio) + proxy traducteur (LiteLLM).
#
# Prérequis (une seule fois) :
#   1. LM Studio installé, un modèle vision Qwen2.5-VL téléchargé et CHARGÉ,
#      serveur local démarré (onglet Developer → Start Server, port 1234).
#   2. LiteLLM installé :   pip install 'litellm[proxy]'
#   3. L'ID du modèle renseigné dans local/litellm.config.yaml.
#
# Ensuite : double-clic sur ce fichier. Ctrl-C arrête tout (proxy + serveur).

cd "$(dirname "$0")/.."                 # racine du dépôt
CONFIG="local/litellm.config.yaml"
PROXY_PORT=4000

# 1. Dépendances -------------------------------------------------------------
command -v litellm >/dev/null 2>&1 || {
  echo "✗ LiteLLM introuvable.  Installe-le :  pip install 'litellm[proxy]'"; exit 1; }
command -v python3 >/dev/null 2>&1 || {
  echo "✗ python3 introuvable (installe les Command Line Tools : xcode-select --install)"; exit 1; }

# LM Studio répond-il ?
if ! curl -s http://localhost:1234/v1/models >/dev/null 2>&1; then
  echo "⚠  LM Studio ne répond pas sur :1234."
  echo "   Ouvre LM Studio → charge Qwen2.5-VL → onglet Developer → Start Server, puis relance."
  exit 1
fi

# 2. Proxy traducteur Anthropic → LM Studio, en arrière-plan -----------------
litellm --config "$CONFIG" --port $PROXY_PORT >/tmp/nephele-litellm.log 2>&1 &
PROXY_PID=$!
cleanup(){ echo; echo "Arrêt du proxy…"; kill "$PROXY_PID" 2>/dev/null; }
trap cleanup EXIT INT TERM

printf "Démarrage du proxy LiteLLM"
for i in $(seq 1 40); do
  curl -s "http://localhost:$PROXY_PORT/health/liveliness" >/dev/null 2>&1 && break
  printf "."; sleep 0.5
done
echo "  ok   (logs : /tmp/nephele-litellm.log)"

# 3. Serveur statique pour l'app --------------------------------------------
PORT=8088
while lsof -i :$PORT >/dev/null 2>&1; do PORT=$((PORT+1)); done
echo
echo "Nephélé  →  http://localhost:$PORT      (Ctrl-C pour tout arrêter)"
echo "Dans le panneau de gauche :"
echo "   • Endpoint  →  http://localhost:$PROXY_PORT"
echo "   • Clé API   →  sk-local   (factice)"
echo "   • Modèle    →  nephele-vl"
echo
( sleep 1; open "http://localhost:$PORT" ) &
python3 -m http.server $PORT
