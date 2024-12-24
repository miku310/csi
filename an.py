import streamlit as st
from collections import Counter, defaultdict
import numpy as np
# ======== Fonctions générales ========

# Chiffrement Vigenère
def vigenere_encrypt(message, cle):
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    message = message.lower()
    cle = cle.lower()
    decalages = [alphabet.index(c) for c in cle]
    message_chiffre = ""
    index_cle = 0
    for lettre in message:
        if lettre in alphabet:
            decalage = decalages[index_cle % len(decalages)]
            indice_clair = alphabet.index(lettre)
            indice_chiffre = (indice_clair + decalage) % len(alphabet)
            message_chiffre += alphabet[indice_chiffre]
            index_cle += 1
        elif lettre in [",", ".","’"]:  # Vérifie si la lettre est une virgule ou un point
            message_chiffre += " "  # Remplace par un espace
        else:
            message_chiffre += lettre
    return message_chiffre

# Indice de coïncidence
def indice_de_coincidence(message):
    message = ''.join(filter(str.isalpha, message)).upper()
    n = len(message)
    if n < 2:
        return 0.0
    compteur = Counter(message)
    ic = sum(f * (f - 1) for f in compteur.values()) / (n * (n - 1))
    return ic

# Créer des sous-séquences
def create_subsequences(message, key_length):
    message = ''.join(filter(str.isalpha, message)).upper()
    subsequences = []
    for start in range(key_length):
        subsequence = ''.join([message[i] for i in range(start, len(message), key_length)])
        subsequences.append(subsequence)
    return subsequences

# Longueur de clé (Friedman)
def longueur_de_cle(message, ic_min=0.07, max_key_length=10):
    for key_length in range(1, max_key_length + 1):
        subsequences = create_subsequences(message, key_length)
        ic_values = [indice_de_coincidence(subsequence) for subsequence in subsequences]
        if any(ic >= ic_min for ic in ic_values):
            return key_length
    return None

# Extraire la clé
def extraire_cle(message, key_length):
    subsequences = create_subsequences(message, key_length)
    key = []
    for subsequence in subsequences:
        compteur = Counter(subsequence)
        most_common_letter = compteur.most_common(1)[0][0]
        shift = (ord(most_common_letter) - ord('E')) % 26
        key_letter = chr(ord('A') + shift)
        key.append(key_letter)
    return ''.join(key)

# Déchiffrement Vigenère
def vigenere_decrypt(message, key):
    message = ''.join(filter(str.isalpha, message)).upper()
    key = ''.join(filter(str.isalpha, key)).upper()
    decrypted_message = []
    key_index = 0
    for char in message:
        if char.isalpha():
            shift = ord(key[key_index % len(key)]) - ord('A')
            decrypted_char = chr(((ord(char) - ord('A') - shift) % 26) + ord('A'))
            decrypted_message.append(decrypted_char)
            key_index += 1
        else:
            decrypted_message.append(char)
    return ''.join(decrypted_message)

# Trouver les séquences répétées (Babbage)
def find_repeated_sequences(ciphertext, min_length=3):
    repeated = defaultdict(list)
    for length in range(min_length, len(ciphertext) // 2):
        for i in range(len(ciphertext) - length):
            seq = ciphertext[i:i + length]
            for j in range(i + length, len(ciphertext) - length + 1):
                if ciphertext[j:j + length] == seq:
                    repeated[seq].append(i)
    return repeated

# Trouver les périodes
def find_periods(repeated):
    periods = {}
    for seq, indices in repeated.items():
        if len(indices) > 1:
            seq_periods = [indices[i + 1] - indices[i] for i in range(len(indices) - 1)]
            periods[seq] = seq_periods
    return periods

# Facteurs communs
def factorize_number(number):
    """Decompose a number into its prime factors."""
    factors = []
    divisor = 2
    while number > 1:
        while number % divisor == 0:
            factors.append(divisor)
            number //= divisor
        divisor += 1
        if divisor * divisor > number and number > 1:
            factors.append(number)
            break
    return factors

def find_common_factor(periods):
    """Find the most common factor among the periods."""
    factor_count = Counter()
    for period_list in periods.values():
        for period in period_list:
            factors = factorize_number(period)
            factor_count.update(factors)
    if factor_count:
        return factor_count.most_common(1)[0][0]
    return None
def frequency_analysis(ciphertext, key_length, position):
    """Perform frequency analysis on characters in a specific modulo sequence."""
    filtered_chars = [ciphertext[i] for i in range(position, len(ciphertext), key_length)]
    freq_count = Counter(filtered_chars)
    most_frequent_char = freq_count.most_common(1)[0][0]
    return most_frequent_char

def compute_key(ciphertext, key_length):
    """Compute the key based on frequency analysis."""
    key = []
    for i in range(key_length):
        most_frequent_char = frequency_analysis(ciphertext, key_length, i)
        if most_frequent_char:
            # Align the most frequent ciphertext character with 'E'
            x = (ord(most_frequent_char) - ord('E')) % 26
            key_letter = chr(x + ord('A'))
            key.append(key_letter)
        else:
            key.append('?')  # Placeholder for missing key parts
    return ''.join(key)

# Déchiffrement final
def decrypt(ciphertext, key):
    key = [ord(char) - ord('A') for char in key]
    plaintext = []
    for i, char in enumerate(ciphertext):
        if char.isalpha():
            shift = key[i % len(key)]
            decrypted_char = chr(((ord(char) - ord('A') - shift) % 26) + ord('A'))
            plaintext.append(decrypted_char)
        else:
            plaintext.append(char)
    return ''.join(plaintext)

# ======== Interface Streamlit ========
st.markdown('<h1 style="color: #FFF455; font-size: 36px;">Chiffrement et Déchiffrement Vigenère</h1>', unsafe_allow_html=True)

# Choix de l'opération
operation = st.radio(
    "Choisissez une opération :",
    ["Chiffrement", "Déchiffrement (Friedman)", "Déchiffrement (Babbage)"],
    index=0,
    format_func=lambda x: f"🔹 {x}"  # Ajoute une icône devant chaque choix
)
if operation == "Chiffrement":
    st.markdown('<h2 style="color: #007F73;">Chiffrement Vigenère</h2>', unsafe_allow_html=True)
    #st.header("Chiffrement Vigenère")
    message = st.text_area("Entrez le message à chiffrer :", "")
    cle = st.text_input("Entrez la clé de chiffrement :", "")
    if st.button("Chiffrer"):
        if message and cle:
            encrypted_message = vigenere_encrypt(message, cle)
            st.subheader("Message Chiffré")
            st.write(encrypted_message)
        else:
            st.error("Veuillez entrer un message et une clé.")

elif operation == "Déchiffrement (Friedman)":
    st.markdown('<h2 style="color: #E4F1AC;">Déchiffrement avec la méthode de Friedman</h2>', unsafe_allow_html=True)
    #st.header("Déchiffrement avec la méthode de Friedman")
    message = st.text_area("Entrez le message chiffré :", "")
    if st.button("Déchiffrer"):
        if message:
            key_length = longueur_de_cle(message)
            if key_length:
                cle = extraire_cle(message, key_length)
                decrypted_message = vigenere_decrypt(message, cle)
                st.subheader("Message Déchiffré")
                st.write(decrypted_message)
                st.subheader("Détails de la Clé")
                st.write(f"Longueur de la clé : {key_length}")
                st.write(f"Clé trouvée : {cle}")
            else:
                st.error("Impossible de déterminer la longueur de la clé.")
        else:
            st.error("Veuillez entrer un message chiffré.")

elif operation == "Déchiffrement (Babbage)":
    st.markdown('<h2 style="color: #A7D477;">Déchiffrement avec la méthode de Babbage</h2>', unsafe_allow_html=True)
    #st.header("Déchiffrement avec la méthode de Babbage")
    ciphertext = st.text_area("Entrez le texte chiffré :", "").replace(" ", "").upper()
    if st.button("Déchiffrer"):
        if ciphertext:
            repeated = find_repeated_sequences(ciphertext)
            periods = find_periods(repeated)
            key_length = find_common_factor(periods)
            if key_length:
                key = compute_key(ciphertext, key_length)
                decrypted_message = decrypt(ciphertext, key)
                st.subheader("Message Déchiffré")
                st.write(decrypted_message)
                st.subheader("Détails de la Clé")
                st.write(f"Longueur de la clé : {key_length}")
                st.write(f"Clé trouvée : {key}")
            else:
                st.error("Impossible de déterminer la longueur de la clé.")
        else:
            st.error("Veuillez entrer un texte chiffré.")
