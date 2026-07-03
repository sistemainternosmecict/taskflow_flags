#!/bin/bash
# Para o script imediatamente em caso de erro nos testes
set -e

echo "🟢 [1/3] Executando testes unitários rápidos..."
uv run pytest tests/unit/ -o pythonpath=. --cov=repository --cov=domain --cov-report=term-missing -v --disable-warnings

echo "🔵 [2/3] Executando testes de integração (Banco Real)..."
uv run pytest tests/integration/ -o pythonpath=. --cov=repository --cov=domain --cov-report=term-missing -v --disable-warnings

echo "🚀 [3/3] Todos os testes passaram!"
# Altere para o seu arquivo/comando principal de entrada da aplicação
#uv run uvicorn main:app --reload
