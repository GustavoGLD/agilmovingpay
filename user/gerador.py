def eh_primo(numero):
    if numero <= 1:
        return False
    if numero <= 3:
        return True
    if numero % 2 == 0 or numero % 3 == 0:
        return False

    for i in range(5, numero):
        if numero % i == 0:
            return False

    return True


def primeiros_primos(N):
    contador = 0
    numero = 2
    while contador < N:
        if eh_primo(numero):
            print(numero)
            contador += 1
        numero += 1

# Lendo o valor de N
N = int(input("Digite o valor de N: "))

# Chamando a função para mostrar os N primeiros números primos
primeiros_primos(N)