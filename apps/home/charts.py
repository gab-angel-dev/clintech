# apps/dashboard/charts.py

import base64
import io

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.style.use("seaborn-v0_8-whitegrid")

CORES = ["#4f63d2", "#16a34a", "#d97706", "#dc2626", "#0891b2", "#7c3aed", "#db2777"]


def _fig_to_base64(fig):
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", bbox_inches="tight", dpi=150, transparent=False)
    plt.close(fig)
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")


def _limpar_eixos(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def grafico_barras(labels, valores, titulo=""):
    fig, ax = plt.subplots(figsize=(6, 3.2))
    ax.bar(labels, valores, color=CORES[0], width=0.6, edgecolor="none")
    ax.set_title(titulo, fontsize=12, fontweight="bold", pad=12)
    ax.tick_params(axis="x", rotation=30, labelsize=9)
    ax.tick_params(axis="y", labelsize=9)
    _limpar_eixos(ax)
    fig.tight_layout()
    return _fig_to_base64(fig)


def grafico_linha(labels, series: dict, titulo=""):
    fig, ax = plt.subplots(figsize=(6, 3.2))
    for i, (nome, valores) in enumerate(series.items()):
        ax.plot(labels, valores, label=nome, color=CORES[i % len(CORES)],
                 linewidth=2, marker="o", markersize=3)
    ax.set_title(titulo, fontsize=12, fontweight="bold", pad=12)
    ax.tick_params(axis="x", rotation=30, labelsize=9)
    ax.tick_params(axis="y", labelsize=9)
    ax.legend(frameon=False, fontsize=9)
    _limpar_eixos(ax)
    fig.tight_layout()
    return _fig_to_base64(fig)


def grafico_pizza(labels, valores, titulo=""):
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie(
        valores,
        labels=labels,
        autopct="%1.0f%%",
        colors=CORES,
        textprops={"fontsize": 9},
        wedgeprops={"edgecolor": "white", "linewidth": 1.5},
    )
    ax.set_title(titulo, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    return _fig_to_base64(fig)