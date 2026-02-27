import numpy as np 

import utils as lm_utils

from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator, Statevector
from qiskit.circuit.library import PauliEvolutionGate

def exec_alg_1():
    ...

def circuit_alg_2(
        n_qubits: int, 
        gamma_i: qiskit.quantum_info.operators.symplectic.sparse_pauli_op.SparsePauliOp,
        gamma_j: list,
        theta:float = np.pi / 6,
        shots:int = 4000,
    ) -> dict:
    """
    Script para execução nos servidores da IBM
    Algoritmo 2: Busca Espinorial
    """

    # Obter os autovalores e autovetores de gamma_j
    evals, evecs = np.linalg.eigh(gamma_j.to_matrix())
    
    # Estado inicial
    initial_state = evecs[:, np.argmax(evals)]

    qc = QuantumCircuit(n_qubits)
    qc.initialize(initial_state, range(n_qubits))

    hamiltonian = (1j * (gamma_i @ gamma_j)).simplify()
    R_gate = PauliEvolutionGate(hamiltonian, time=theta)
    qc.append(R_gate, range(n_qubits))

    state_rot = Statevector(qc)

    k = int(np.floor((np.pi / (4 * theta)) - 0.5))
    k = max(1, k)

    D_op = Operator(
        2 * np.outer(state_rot.data, np.conj(state_rot.data))
        - np.eye(2**n_qubits)
    )

    for _ in range(k):
        qc.append(Operator(gamma_j), range(n_qubits))
        qc.append(D_op, range(n_qubits))

    state_theo = Statevector(qc)
    prob_ideal = state_theo.probabilities()

    qc.measure_all()

    return qc, prob_ideal


# Testes

