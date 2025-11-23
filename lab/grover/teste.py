from ket import *

def oracle(qubits, target):
    """Oráculo: inverte a amplitude do estado desejado."""
    X(
        qubits[i]
        for i, bit in enumerate(bin(target)[2:].zfill(len(qubits)))
        if bit == "0"
    )
    H(qubits[-1])
    ctrl(qubits[:-1], X, qubits[-1])  # Controle multi-qubit
    H(qubits[-1])
    X(
        qubits[i]
        for i, bit in enumerate(bin(target)[2:].zfill(len(qubits)))
        if bit == "0"
    )

def diffusion_operator(qubits):
    """Operador de difusão: amplifica as amplitudes dos estados marcados."""
    H(qubits)
    X(qubits)
    H(qubits[-1])
    ctrl(qubits[:-1], X, qubits[-1])  # Controle multi-qubit
    H(qubits[-1])
    X(qubits)
    H(qubits)
def grover(n, target):
    """Executa o algoritmo de Grover."""
    # Inicialização do processo
    process = Process()

    # Alocação de n qubits
    qubits = process.alloc(n)

    # Superposição inicial
    H(qubits)

    # Número ideal de iterações: sqrt(2^n)
    iterations = int((2**n) ** 0.5)

    # Iterações do algoritmo de Grover
    for _ in range(iterations):
        oracle(qubits, target)
        diffusion_operator(qubits)

    # Medição
    result = [measure(q).value for q in qubits]
    print("Estado encontrado:", result)


