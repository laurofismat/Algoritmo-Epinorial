"""
Biblioteca com funções de padronização para a 
pesquisa em Computação Quântica
"""
from pathlib import Path 
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np

import json


def regenerar_histogramas_por_job(
    job_id: str,
    dir_root: str = ".",
    json_filename: str = "dados_experimento.json",
    output_subdir: str = "hist_reconstruidos"
):
    """
    Reconstroi todos os histogramas associados a um job_id
    a partir do JSON salvo.

    Não consulta a IBM. Utiliza apenas os dados persistidos.
    """

    root = Path(dir_root)
    json_path = root / json_filename

    if not json_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {json_path}")

    with open(json_path, "r") as f:
        data = json.load(f)

    if data.get("job_id") != job_id:
        raise ValueError(
            f"Job ID não corresponde ao JSON encontrado.\n"
            f"Esperado: {data.get('job_id')}\n"
            f"Recebido: {job_id}"
        )

    n = data["n_qubits"]

    basis_states = [
        format(k, f"0{n}b")
        for k in range(2**n)
    ]

    output_dir = root / output_subdir
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"> Regenerando histogramas para job {job_id}")

    for circuito in data["circuits"]:

        i = circuito["gamma_i"]
        j = circuito["gamma_j"]

        counts = circuito["counts"]
        prob_ideal = np.array(circuito["prob_ideal"])
        fidelidade = circuito["fidelity"]

        info = {
            "fid": fidelidade,
            "algo": "ACE_Algoritmo2",
            "n": n,
            "job": job_id,
            "title": rf"Algorithm 2 — Probability Distribution",
            "i": i,
            "j": j
        }

        gerar_histograma_artigo(
            counts,
            prob_ideal,
            basis_states,
            info,
            output_dir
        )

        print(f"\tΓ_{i}Γ_{j} reconstruído.")

    print("> Reconstrução finalizada.")

def gerar_histograma_artigo(counts, prob_ideal, basis_states, info, path_dir):
    """Função para gerar os Histogramas de Probabilidade (ACE)"""

    import re
    from pathlib import Path
    import numpy as np
    import matplotlib.pyplot as plt

    path_dir = Path(path_dir)
    path_dir.mkdir(parents=True, exist_ok=True)

    plt.rcParams.update({
        "font.family": "serif",
        "font.size": 10,
        "axes.linewidth": 0.8,
        "xtick.direction": "in",
        "ytick.direction": "in",
        "figure.dpi": 300
    })

    total = sum(counts.values())
    if total == 0:
        raise ValueError("Counts vazio — impossível normalizar.")

    prob_real = np.array(
        [counts.get(bs, 0) / total for bs in basis_states]
    )

    x = np.arange(len(basis_states))
    width = 0.38

    fig, ax = plt.subplots(figsize=(4.2, 3.2))

    # Experimental (barra sólida)
    ax.bar(
        x - width/2,
        prob_real,
        width,
        label="Experimental",
        edgecolor="black",
        linewidth=0.6,
        color="lightgray"
    )

    # Teórico (barra rachurada)
    ax.bar(
        x + width/2,
        prob_ideal,
        width,
        label="Theoretical",
        edgecolor="black",
        linewidth=0.6,
        fill=False,
        hatch="///"
    )

    ax.set_ylabel("Probability")
    ax.set_xlabel("Computational basis states")

    ax.set_xticks(x)
    ax.set_xticklabels(
        [f"$|{s}\\rangle$" for s in basis_states],
        rotation=90,
        ha='right',
        fontsize=8
    )

    # ---------- TÍTULO ----------
    ax.set_title(info["title"])

    # ---------- LEGENDA COM MÉTRICAS ----------
    fid_tex = f"{info['fid']:.4f}"
    # auto_tex = f"{info['auto_valor']}"

    i = info["i"]
    j = info["j"]
    gamma_tex = rf"$Bivetor: \Gamma_{{{i}}}\Gamma_{{{j}}}$"

    handles, labels = ax.get_legend_handles_labels()

    legenda_extra = (
        gamma_tex + "\n" +
        rf"$F_{{exp}} = {fid_tex}$"
    )

    props = dict(
        boxstyle="round",
        facecolor="white",
        edgecolor="black",
        alpha=0.85
    )

    ax.text(
        0.05,          # posição horizontal (0–1)
        0.85,          # posição vertical (0–1)
        legenda_extra,
        transform=ax.transAxes,
        fontsize=9,
        verticalalignment="top",
        bbox=props
    )
    
    ax.legend(
        handles,
        labels + [legenda_extra],
        frameon=False,
        loc="upper right"
    )

    ax.set_ylim(0, 1.05)
    ax.grid(axis="y", linestyle=":", linewidth=0.5, alpha=0.6)
    ax.set_axisbelow(True)

    plt.tight_layout()

    # ---------- NOME DO ARQUIVO ----------
    job_clean = re.sub(r"[^a-zA-Z0-9_-]", "_", info["job"])
    filename = (
        f"hist_ACE_{info['algo']}_"
        f"{info['n']}qb_"
        f"{job_clean}_Gamma_{i}{j}.pdf"
    )

    filepath = path_dir / filename
    plt.savefig(filepath, bbox_inches="tight")
    plt.close(fig)

    print(f"Gráfico salvo em: {filepath}")

