"""
CNS ESE PRACTICE - BEGINNER-FRIENDLY ALGORITHM COLLECTION
Python 3 | No imports required for Experiments 1, 2 and 3.
For hashing, import hashlib only where indicated.

IMPORTANT:
- These are educational lab implementations, not production cryptography.
- RSA uses small classroom primes if generated from UID.
- Miller-Rabin uses a fixed base set; for arbitrary large numbers use a
  cryptographically sound randomized implementation / deterministic bounds.
- ECC example is a small-curve teaching implementation.
- ML-DSA and SLH-DSA are standardized schemes and are NOT practical to
  reimplement from scratch in a short beginner program. Your supplied
  Experiment 8 uses liboqs-python ("oqs") for them, and cryptography for
  RSA-PSS and ECDSA. See notes at the bottom.
"""


# ============================================================
# COMMON MATHEMATICAL FUNCTIONS
# ============================================================

def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return abs(a)


def mod_inverse(a, m):
    # Extended Euclidean Algorithm
    old_r, r = a, m
    old_s, s = 1, 0

    while r != 0:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s

    if old_r != 1:
        return None

    return old_s % m


# ============================================================
# EXPERIMENT 1 - PRIMALITY TESTING
# ============================================================

def fermat_test(n, bases=(2, 3, 5)):
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False

    for a in bases:
        a = a % n
        if a == 0:
            continue
        if gcd(a, n) != 1:
            return False
        if pow(a, n - 1, n) != 1:
            return False

    return True                 # probably prime, not proof


def euler_test(n, bases=(2, 3, 5)):
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False

    for a in bases:
        a = a % n
        if a == 0 or gcd(a, n) != 1:
            return False

        result = pow(a, (n - 1) // 2, n)
        if result != 1 and result != n - 1:
            return False

    return True                 # probably prime


def miller_rabin(n, bases=(2, 3, 5, 7, 11)):
    if n < 2:
        return False

    small_primes = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    for prime in small_primes:
        if n == prime:
            return True
        if n % prime == 0:
            return False

    # n - 1 = 2^s * d, with d odd
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1

    for a in bases:
        if a >= n:
            continue

        x = pow(a, d, n)

        if x == 1 or x == n - 1:
            continue

        for _ in range(s - 1):
            x = (x * x) % n
            if x == n - 1:
                break
        else:
            return False

    return True


def next_prime(start):
    n = max(2, start)
    if n > 2 and n % 2 == 0:
        n += 1
    while not miller_rabin(n):
        n += 1 if n == 2 else 2
    return n


# ============================================================
# EXPERIMENT 2 - CLASSICAL / SYMMETRIC CIPHERS
# ============================================================

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def caesar_encrypt(text, key):
    result = ""
    for ch in text.upper():
        if ch in ALPHABET:
            result += ALPHABET[(ALPHABET.index(ch) + key) % 26]
        else:
            result += ch
    return result


def caesar_decrypt(text, key):
    return caesar_encrypt(text, -key)


def monoalphabetic_encrypt(text, key_alphabet):
    # key_alphabet must be a permutation of A-Z
    key_alphabet = key_alphabet.upper()
    if len(key_alphabet) != 26 or set(key_alphabet) != set(ALPHABET):
        raise ValueError("Key must contain every A-Z letter exactly once")

    result = ""
    for ch in text.upper():
        if ch in ALPHABET:
            result += key_alphabet[ALPHABET.index(ch)]
        else:
            result += ch
    return result


def monoalphabetic_decrypt(text, key_alphabet):
    key_alphabet = key_alphabet.upper()
    if len(key_alphabet) != 26 or set(key_alphabet) != set(ALPHABET):
        raise ValueError("Key must contain every A-Z letter exactly once")

    result = ""
    for ch in text.upper():
        if ch in key_alphabet:
            result += ALPHABET[key_alphabet.index(ch)]
        else:
            result += ch
    return result


def vigenere_encrypt(text, key):
    key = "".join(ch for ch in key.upper() if ch in ALPHABET)
    if not key:
        raise ValueError("Key must contain letters")

    result = ""
    j = 0
    for ch in text.upper():
        if ch in ALPHABET:
            p = ALPHABET.index(ch)
            k = ALPHABET.index(key[j % len(key)])
            result += ALPHABET[(p + k) % 26]
            j += 1
        else:
            result += ch
    return result


def vigenere_decrypt(text, key):
    key = "".join(ch for ch in key.upper() if ch in ALPHABET)
    if not key:
        raise ValueError("Key must contain letters")

    result = ""
    j = 0
    for ch in text.upper():
        if ch in ALPHABET:
            c = ALPHABET.index(ch)
            k = ALPHABET.index(key[j % len(key)])
            result += ALPHABET[(c - k) % 26]
            j += 1
        else:
            result += ch
    return result


def playfair_matrix(key):
    # I and J share one cell
    key = key.upper().replace("J", "I")
    chars = ""
    for ch in key + "ABCDEFGHIKLMNOPQRSTUVWXYZ":
        if ch in "ABCDEFGHIKLMNOPQRSTUVWXYZ" and ch not in chars:
            chars += ch
    return [list(chars[i:i + 5]) for i in range(0, 25, 5)]


def playfair_prepare(text):
    text = "".join(ch for ch in text.upper() if ch in ALPHABET)
    text = text.replace("J", "I")

    pairs = []
    i = 0
    while i < len(text):
        a = text[i]
        if i + 1 >= len(text):
            b = "X"
            i += 1
        elif text[i + 1] == a:
            b = "X"
            i += 1
        else:
            b = text[i + 1]
            i += 2
        pairs.append(a + b)

    return pairs


def playfair_transform(text, key, decrypt=False):
    matrix = playfair_matrix(key)
    pairs = playfair_prepare(text) if not decrypt else [
        text.upper().replace("J", "I")[i:i + 2]
        for i in range(0, len("".join(ch for ch in text.upper()
                                     if ch in ALPHABET).replace("J", "I")), 2)
    ]

    positions = {}
    for r in range(5):
        for c in range(5):
            positions[matrix[r][c]] = (r, c)

    result = ""
    step = -1 if decrypt else 1

    for pair in pairs:
        if len(pair) != 2:
            continue
        a, b = pair[0], pair[1]
        r1, c1 = positions[a]
        r2, c2 = positions[b]

        if r1 == r2:
            result += matrix[r1][(c1 + step) % 5]
            result += matrix[r2][(c2 + step) % 5]
        elif c1 == c2:
            result += matrix[(r1 + step) % 5][c1]
            result += matrix[(r2 + step) % 5][c2]
        else:
            result += matrix[r1][c2]
            result += matrix[r2][c1]

    return result


def playfair_encrypt(text, key):
    return playfair_transform(text, key, False)


def playfair_decrypt(ciphertext, key):
    return playfair_transform(ciphertext, key, True)


def hill_encrypt(text, key):
    # 2x2 Hill cipher. Key is [[a,b],[c,d]].
    clean = "".join(ch for ch in text.upper() if ch in ALPHABET)
    if len(clean) % 2 == 1:
        clean += "X"

    a, b = key[0]
    c, d = key[1]
    determinant = (a * d - b * c) % 26

    if gcd(determinant, 26) != 1:
        raise ValueError("Invalid Hill key: determinant has no inverse mod 26")

    result = ""
    for i in range(0, len(clean), 2):
        x = ALPHABET.index(clean[i])
        y = ALPHABET.index(clean[i + 1])
        c1 = (a * x + b * y) % 26
        c2 = (c * x + d * y) % 26
        result += ALPHABET[c1] + ALPHABET[c2]

    return result


def hill_decrypt(ciphertext, key):
    a, b = key[0]
    c, d = key[1]
    determinant = (a * d - b * c) % 26
    inverse_det = mod_inverse(determinant, 26)

    if inverse_det is None:
        raise ValueError("Invalid Hill key")

    # Inverse matrix = det_inverse * [[d,-b],[-c,a]] mod 26
    ia = (inverse_det * d) % 26
    ib = (inverse_det * (-b)) % 26
    ic = (inverse_det * (-c)) % 26
    id_ = (inverse_det * a) % 26

    clean = "".join(ch for ch in ciphertext.upper() if ch in ALPHABET)
    if len(clean) % 2 != 0:
        raise ValueError("Ciphertext length must be even")

    result = ""
    for i in range(0, len(clean), 2):
        x = ALPHABET.index(clean[i])
        y = ALPHABET.index(clean[i + 1])
        p1 = (ia * x + ib * y) % 26
        p2 = (ic * x + id_ * y) % 26
        result += ALPHABET[p1] + ALPHABET[p2]

    return result


# ============================================================
# EXPERIMENT 3 - ASYMMETRIC CRYPTOGRAPHY
# ============================================================

def rsa_generate_keys(p, q):
    if not miller_rabin(p) or not miller_rabin(q) or p == q:
        raise ValueError("p and q must be distinct primes")

    n = p * q
    phi = (p - 1) * (q - 1)

    e = 65537
    if e >= phi or gcd(e, phi) != 1:
        e = 3
        while e < phi and gcd(e, phi) != 1:
            e += 2

    if e >= phi:
        raise ValueError("Could not find valid public exponent")

    d = mod_inverse(e, phi)
    return (e, n), (d, n), phi


def rsa_encrypt(message, public_key):
    e, n = public_key
    if message < 0 or message >= n:
        raise ValueError("Message must be between 0 and n-1")
    return pow(message, e, n)


def rsa_decrypt(ciphertext, private_key):
    d, n = private_key
    return pow(ciphertext, d, n)


def elgamal_generate_keys(p, g, x):
    # x is private key
    y = pow(g, x, p)
    return x, y


def elgamal_encrypt(message, p, g, y, k):
    # k must be fresh and in range 1..p-2
    c1 = pow(g, k, p)
    shared = pow(y, k, p)
    c2 = (message * shared) % p
    return c1, c2


def elgamal_decrypt(ciphertext, p, x):
    c1, c2 = ciphertext
    shared = pow(c1, x, p)
    inverse = mod_inverse(shared, p)
    if inverse is None:
        raise ValueError("Shared secret has no modular inverse")
    return (c2 * inverse) % p


def diffie_hellman(p, g, alice_private, bob_private):
    alice_public = pow(g, alice_private, p)
    bob_public = pow(g, bob_private, p)

    alice_secret = pow(bob_public, alice_private, p)
    bob_secret = pow(alice_public, bob_private, p)

    return alice_public, bob_public, alice_secret, bob_secret


# ---------------- ECC point arithmetic ----------------
# Curve: y^2 = x^3 + a*x + b (mod p)
# None represents the point at infinity.

def ecc_is_on_curve(P, a, b, p):
    if P is None:
        return True
    x, y = P
    return (y * y - (x * x * x + a * x + b)) % p == 0


def ecc_point_add(P, Q, a, p):
    if P is None:
        return Q
    if Q is None:
        return P

    x1, y1 = P
    x2, y2 = Q

    if x1 == x2 and (y1 + y2) % p == 0:
        return None

    if P != Q:
        denominator = mod_inverse((x2 - x1) % p, p)
        if denominator is None:
            raise ValueError("No modular inverse for point addition")
        slope = ((y2 - y1) * denominator) % p
    else:
        denominator = mod_inverse((2 * y1) % p, p)
        if denominator is None:
            return None
        slope = ((3 * x1 * x1 + a) * denominator) % p

    x3 = (slope * slope - x1 - x2) % p
    y3 = (slope * (x1 - x3) - y1) % p
    return x3, y3


def ecc_scalar_mult(k, P, a, p):
    result = None
    current = P

    while k > 0:
        if k % 2 == 1:
            result = ecc_point_add(result, current, a, p)
        current = ecc_point_add(current, current, a, p)
        k //= 2

    return result


def ecc_elgamal_encrypt(message, G, public_Q, a, p, k):
    C1 = ecc_scalar_mult(k, G, a, p)
    shared = ecc_scalar_mult(k, public_Q, a, p)
    if shared is None:
        raise ValueError("Invalid shared point")
    C2 = (message + shared[0]) % p
    return C1, C2


def ecc_elgamal_decrypt(ciphertext, private_d, a, p):
    C1, C2 = ciphertext
    shared = ecc_scalar_mult(private_d, C1, a, p)
    if shared is None:
        raise ValueError("Invalid shared point")
    return (C2 - shared[0]) % p


# ============================================================
# DIGITAL SIGNATURES - EDUCATIONAL NUMBER-THEORY METHODS
# ============================================================

def elgamal_sign(hash_value, p, g, private_x, k):
    # k must satisfy gcd(k, p-1) = 1 and must never be reused
    if gcd(k, p - 1) != 1:
        raise ValueError("k must be coprime to p-1")

    r = pow(g, k, p)
    k_inverse = mod_inverse(k, p - 1)
    s = (k_inverse * (hash_value - private_x * r)) % (p - 1)
    return r, s


def elgamal_verify(hash_value, signature, p, g, public_y):
    r, s = signature

    if not (1 <= r < p):
        return False
    if not (0 <= s < p - 1):
        return False

    left = pow(g, hash_value, p)
    right = (pow(public_y, r, p) * pow(r, s, p)) % p
    return left == right


# ============================================================
# QUICK EXAMPLE RUNS
# Uncomment the block you want to practise.
# ============================================================

if __name__ == "__main__":

    print("CNS ALGORITHM PRACTICE")
    print("1. Fermat, Euler, Miller-Rabin")
    print("2. Caesar")
    print("3. Monoalphabetic")
    print("4. Vigenere")
    print("5. Playfair")
    print("6. Hill")
    print("7. RSA")
    print("8. ElGamal Encryption")
    print("9. Diffie-Hellman")
    print("10. ECC / EC-ElGamal")
    print("11. ElGamal Digital Signature")

    choice = input("Choose algorithm number: ")

    if choice == "1":
        n = int(input("Enter number: "))
        print("Fermat:", fermat_test(n))
        print("Euler:", euler_test(n))
        print("Miller-Rabin:", miller_rabin(n))

    elif choice == "2":
        msg = input("Plaintext: ")
        key = int(input("Shift key: "))
        cipher = caesar_encrypt(msg, key)
        print("Ciphertext:", cipher)
        print("Decrypted:", caesar_decrypt(cipher, key))

    elif choice == "3":
        msg = input("Plaintext: ")
        key = input("26-letter substitution alphabet: ").upper()
        cipher = monoalphabetic_encrypt(msg, key)
        print("Ciphertext:", cipher)
        print("Decrypted:", monoalphabetic_decrypt(cipher, key))

    elif choice == "4":
        msg = input("Plaintext: ")
        key = input("Keyword: ")
        cipher = vigenere_encrypt(msg, key)
        print("Ciphertext:", cipher)
        print("Decrypted:", vigenere_decrypt(cipher, key))

    elif choice == "5":
        msg = input("Plaintext: ")
        key = input("Keyword: ")
        cipher = playfair_encrypt(msg, key)
        print("Ciphertext:", cipher)
        print("Decrypted (may contain filler X):", playfair_decrypt(cipher, key))

    elif choice == "6":
        msg = input("Plaintext: ")
        key = [[3, 3], [2, 5]]
        cipher = hill_encrypt(msg, key)
        print("Ciphertext:", cipher)
        print("Decrypted (may contain padding X):", hill_decrypt(cipher, key))

    elif choice == "7":
        p = int(input("Prime p: "))
        q = int(input("Prime q: "))
        public, private, phi = rsa_generate_keys(p, q)
        print("n =", public[1])
        print("phi =", phi)
        print("Public key =", public)
        print("Private key =", private)
        m = int(input("Numeric message (0 to n-1): "))
        c = rsa_encrypt(m, public)
        print("Ciphertext =", c)
        print("Decrypted =", rsa_decrypt(c, private))

    elif choice == "8":
        p = int(input("Prime p: "))
        g = int(input("Primitive root g: "))
        x = int(input("Private key x: "))
        k = int(input("Fresh random k: "))
        m = int(input("Numeric message: "))
        private, y = elgamal_generate_keys(p, g, x)
        cipher = elgamal_encrypt(m, p, g, y, k)
        print("Public key y =", y)
        print("Ciphertext =", cipher)
        print("Decrypted =", elgamal_decrypt(cipher, p, x))

    elif choice == "9":
        p = int(input("Public prime p: "))
        g = int(input("Public generator g: "))
        a = int(input("Alice private value: "))
        b = int(input("Bob private value: "))
        A, B, ka, kb = diffie_hellman(p, g, a, b)
        print("Alice public =", A)
        print("Bob public =", B)
        print("Alice secret =", ka)
        print("Bob secret =", kb)
        print("Match =", ka == kb)

    elif choice == "10":
        # Small teaching curve: y^2 = x^3 + 2x + 2 (mod 17)
        p, a, b = 17, 2, 2
        G = (5, 1)
        d = int(input("Private key d (example 7): "))
        k = int(input("Fresh temporary k (example 3): "))
        m = int(input("Message number (0 to p-1): "))
        Q = ecc_scalar_mult(d, G, a, p)
        cipher = ecc_elgamal_encrypt(m, G, Q, a, p, k)
        print("Public point Q =", Q)
        print("Ciphertext =", cipher)
        print("Decrypted =", ecc_elgamal_decrypt(cipher, d, a, p))

    elif choice == "11":
        p = int(input("Prime p: "))
        g = int(input("Primitive root g: "))
        x = int(input("Private key x: "))
        h = int(input("Integer hash value: "))
        k = int(input("Fresh k coprime to p-1: "))
        y = pow(g, x, p)
        sig = elgamal_sign(h, p, g, x, k)
        print("Public key y =", y)
        print("Signature (r,s) =", sig)
        print("Original verification =", elgamal_verify(h, sig, p, g, y))
        h2 = (h + 1) % (p - 1)
        print("Modified-hash verification =", elgamal_verify(h2, sig, p, g, y))

    else:
        print("Invalid choice")


# ============================================================
# EXPERIMENT 8 - IMPORTANT LIBRARY NOTE
# ============================================================
#
# Your supplied Experiment 8 does NOT implement these standards
# from scratch. It uses:
#
#   import oqs
#   from cryptography.hazmat.primitives import hashes, serialization
#   from cryptography.hazmat.primitives.asymmetric import ec, padding, rsa
#
# RSA-PSS:
#   cryptography RSA private_key.sign(message, PSS(...), SHA256())
#
# ECDSA:
#   cryptography EC private_key.sign(message, ec.ECDSA(SHA256()))
#
# ML-DSA and SLH-DSA:
#   oqs.Signature("ML-DSA-44") / oqs.Signature("SLH-DSA-SHA2-128s")
#
# ML-DSA and SLH-DSA are large standardized post-quantum schemes.
# A short beginner no-import implementation would not be a correct
# implementation. Use the supplied Docker/liboqs lab for these.
#
# SHA-256 in a basic custom ElGamal-signature exercise can be obtained
# with:
#   import hashlib
#   digest = hashlib.sha256(message.encode()).digest()
#   h = int.from_bytes(digest, "big")
#
# That import is only for hashing; the rest of the number theory above
# uses basic Python.
