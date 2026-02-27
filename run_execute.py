import numpy as np
import json
from datetime import datetime
from pathlib import Path

import alClifford as lm_clifford
import circuits as lm_circuits
import utils as lm_utils

from itertools import combinations

from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

def main(n:int):
    # ========================================================
    # PARÂMETROS GLOBAIS
    # ========================================================

    # n = 3
    shots = 4000
    output_dir = Path(f"./resultados_alg2_n{n}_26_02_2026")
    output_dir.mkdir(parents=True, exist_ok=True)


    # ========================================================
    # GERAÇÃO DOS CIRCUITOS
    # ========================================================

    gammas = lm_clifford.geradores_clifford(n)
    indices = list(combinations(range(len(gammas)), 2))

    circuits = []
    metadata = []

    print(f"> Criando os circuitos com {n} qubits...")

    for idx, (i, j) in enumerate(indices):

        qc, prob_ideal = lm_circuits.circuit_alg_2(
            n_qubits=n,
            gamma_i=gammas[i],
            gamma_j=gammas[j]
        )

        qc.metadata = {
            "gamma_i": i,
            "gamma_j": j,
            "idx": idx
        }

        circuits.append(qc)

        metadata.append({
            "i": i,
            "j": j,
            "prob_ideal": prob_ideal
        })

        print(f"\tΓ_{i}Γ_{j} construído.")


    # ========================================================
    # TRANSPILAÇÃO E EXECUÇÃO
    # ========================================================

    service = QiskitRuntimeService()
    backend = service.backend("ibm_torino")

    pm = generate_preset_pass_manager(
        backend=backend,
        optimization_level=3
    )

    t_qc = pm.run(circuits)

    print(f"> Backend: {backend.name}")
    print(f"> Jobs na fila: {backend.status().pending_jobs}")

    sampler = Sampler(mode=backend)
    job = sampler.run(t_qc, shots=shots)

    print(f"> JOB ID: {job.job_id()}")

    results = job.result()


    # ========================================================
    # ESTRUTURA DE ARMAZENAMENTO
    # ========================================================

    experiment_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "n_qubits": n,
        "shots": shots,
        "backend": backend.name,
        "job_id": job.job_id(),
        "optimization_level": 3,
        "circuits": []
    }


    # ========================================================
    # PÓS-PROCESSAMENTO
    # ========================================================

    basis_states = [
        format(k, f"0{n}b")
        for k in range(2**n)
    ]

    for idx, result in enumerate(results):

        counts = result.data.meas.get_counts()

        prob_ideal = metadata[idx]["prob_ideal"]
        i = metadata[idx]["i"]
        j = metadata[idx]["j"]

        total = sum(counts.values())

        prob_real = np.array([
            counts.get(bs, 0) / total
            for bs in basis_states
        ])

        fidelidade = float(
            np.sum(np.sqrt(prob_real * prob_ideal)) ** 2
        )

        depth_individual = t_qc[idx].depth()

        print("=" * 40)
        print(f">> Γ{i}Γ{j}")
        print(f"Fidelidade: {fidelidade}")
        print(f"Profundidade: {depth_individual}")

        # ----------------------------------------------------
        # Salva dados do circuito no JSON
        # ----------------------------------------------------

        experiment_data["circuits"].append({
            "gamma_i": i,
            "gamma_j": j,
            "depth": depth_individual,
            "counts": counts,
            "prob_ideal": prob_ideal.tolist(),
            "prob_real": prob_real.tolist(),
            "fidelity": fidelidade
        })

        # ----------------------------------------------------
        # Geração do histograma
        # ----------------------------------------------------

        info = {
            "fid": fidelidade,
            "algo": "ACE_Algoritmo2",
            "n": n,
            "job": job.job_id(),
            "title": rf"Algorithm 2 — Probability Distribution",
            "i": i,
            "j": j
        }

        lm_utils.gerar_histograma_artigo(
            counts,
            prob_ideal,
            basis_states,
            info,
            output_dir
        )


    # ========================================================
    # SALVAMENTO FINAL
    # ========================================================

    json_path = output_dir / "dados_experimento.json"

    with open(json_path, "w") as f:
        json.dump(experiment_data, f, indent=4)

    print(f"> Dados experimentais salvos em {json_path}")

if __name__ == "__main__":

    n_list = [3,4,5]
    for k in n_list:
        main(n = k)
