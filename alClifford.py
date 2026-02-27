import numpy as np
import scipy as sp 

from qiskit.quantum_info import Operator, SparsePauliOp

def geradores_clifford(n):
    """
        Gerar os 2n geradores da álgebra de CLifford seguindo o lema 1 do artigo.
    """

    gammas = []

    for j in range(1, n + 1):
        label_j = ['I'] * n 
        for k in range(j - 1): label_j[k] = 'X'
        label_j[j-1] = 'Y'
        gammas.append(SparsePauliOp("".join(label_j[::-1])))

    for j in range(1, n + 1):
        label_nj = ['I'] * n 
        for k in range(j - 1): label_nj[k] = 'X'
        label_nj[j-1] = 'Z'
        gammas.append(SparsePauliOp("".join(label_nj[::-1])))

    return gammas

def operator_rotate(theta, gamma_i, gamma_j):
    Rij = sp.linalg.expm(theta*(gamma_i@gamma_j))
    
    instrucao_R = Operator(Rij).to_instruction()
    instrucao_R.label = "R_ij"

    return instrucao_R

