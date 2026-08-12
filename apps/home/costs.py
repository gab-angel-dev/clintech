import re

PRECOS = {
    "llama-3.3-70b": {"input": 0.85, "output": 1.20},
    "gpt-4.1": {"input": 2.00, "output": 8.00},
    "gpt-4.1-mini": {"input": 0.40, "output": 1.60},
}

_SUFIXO_DATA = re.compile(r"-\d{4}-\d{2}-\d{2}$")


def normalizar_model_name(model_name: str) -> str:
    if not model_name:
        return model_name
    return _SUFIXO_DATA.sub("", model_name)


def calcular_custo(input_tokens, output_tokens, model_name):
    nome_normalizado = normalizar_model_name(model_name)
    preco = PRECOS.get(nome_normalizado, {"input": 0, "output": 0})
    custo = (input_tokens * preco["input"] + output_tokens * preco["output"]) / 1_000_000
    return round(custo, 6)