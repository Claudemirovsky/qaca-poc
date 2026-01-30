def rsa_encrypt(input: str, exp_hex: str, mod_hex: str) -> str:
    """
    Função para criptografia RSA, baseada na implementação que o
    QAcadêmico usa (https://www.ohdave.com/rsa/RSA.js), com padding OHDave.
    Padding "OHDave" é menos seguro que PKCS1, e nenhuma biblioteca de
    criptografia com devs mentalmente saudáveis tem uma implementação disso.
    """
    n = int(mod_hex, 16)
    e = int(exp_hex, 16)

    key_size = (n.bit_length() + 7) // 8

    encoded = input.encode("utf-8")

    padded = encoded + (b"\x00" * (key_size - len(encoded)))

    m = int.from_bytes(padded, byteorder="little")

    encrypted = pow(m, e, n)
    return hex(encrypted)[2:]
