import streamlit as st
from collections import Counter, defaultdict
import numpy as np
from PIL import Image
from itertools import product
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
        elif lettre in [",", ".","’"]:  # Vérifie si la lettre est une virgule ou un point ou apostrophe
            message_chiffre += " "  # Remplace par un espace
        else:
            message_chiffre += lettre
    return message_chiffre

def ajuster_cle(cle, longueur_message):
    """
    Ajuste la clé à la longueur du message pour le chiffrement/déchiffrement.
    """
    cle = cle.upper()
    return (cle * (longueur_message // len(cle))) + cle[:longueur_message % len(cle)]

def indice_de_coincidence(message):
    """
    Calcule l'indice de coïncidence d'un message.
    """
    message = ''.join(filter(str.isalpha, message)).upper()
    n = len(message)
    if n < 2:
        return 0.0
    compteur = Counter(message)
    return sum(f * (f - 1) for f in compteur.values()) / (n * (n - 1))

def create_subsequences(message, key_length):
    """
    Divise le message en sous-séquences selon une longueur de clé donnée.
    """
    message = ''.join(filter(str.isalpha, message)).upper()
    return [
        ''.join(message[i] for i in range(j, len(message), key_length))
        for j in range(key_length)
    ]

def calculer_frequence(texte):
    """
    Trouve la ou les lettres les plus fréquentes dans un texte.
    """
    texte = ''.join(filter(str.isalpha, texte)).upper()
    if len(texte) < 3:
        return ['A']  # Retourne une valeur par défaut si la séquence est trop courte
    compteur = Counter(texte)
    max_freq = max(compteur.values())
    return [lettre for lettre, freq in compteur.items() if freq == max_freq]

def longueur_de_cle(message, ic_min=0.07):
    """
    Détermine la longueur de la clé basée sur l'indice de coïncidence.
    """
    message = ''.join(filter(str.isalpha, message)).upper()
    for key_length in range(1, len(message) + 1):
        subsequences = create_subsequences(message, key_length)
        ic = sum(indice_de_coincidence(subseq) for subseq in subsequences) / key_length
        # Retirer l'affichage de l'IC moyen
        if ic >= ic_min:
            return key_length
    return None

def extraire_cle(message, key_length):
    """
    Extrait toutes les clés possibles en analysant les sous-séquences.
    """
    messages_extraits = create_subsequences(message, key_length)
    all_keys = []

    # Trouver les lettres les plus fréquentes pour chaque sous-séquence
    possible_shifts = []
    for extrait in messages_extraits:
        most_common_letters = calculer_frequence(extrait)
        shifts = [(ord(letter) - ord('E')) % 26 for letter in most_common_letters]
        possible_shifts.append(shifts)

    # Si plusieurs options de décalage existent, afficher un message
    if any(len(shifts) > 1 for shifts in possible_shifts):
        print("\nIl y a plusieurs lettres avec la même fréquence dans certains messages extraits,")
        print("et donc plusieurs clés possibles peuvent être extraites.")

    # Générer toutes les combinaisons de clés possibles
    for combination in product(*possible_shifts):
        key = ''.join(chr(shift + ord('A')) for shift in combination)
        all_keys.append(key)

    return all_keys

def vigenere_decrypt(message, key):
    """
    Déchiffre un message en utilisant le chiffre de Vigenère.
    """
    message = ''.join(filter(str.isalpha, message)).upper()
    key = ajuster_cle(key, len(message))
    decrypted_message = []
    for i, char in enumerate(message):
        shift = ord(key[i]) - ord('A')
        decrypted_char = chr(((ord(char) - ord('A') - shift) % 26) + ord('A'))
        decrypted_message.append(decrypted_char)
    return ''.join(decrypted_message)

def add_spaces_to_message(decrypted_message, original_message):
    """
    Ajoute les espaces dans le message déchiffré en fonction de l'original.
    """
    decrypted_with_spaces = []
    decrypted_index = 0
    for char in original_message:
        if char.isalpha():
            decrypted_with_spaces.append(decrypted_message[decrypted_index])
            decrypted_index += 1
        else:
            decrypted_with_spaces.append(char)
    return ''.join(decrypted_with_spaces)

# # Demander à l'utilisateur de saisir un message chiffré
# message = input("Veuillez entrer le message chiffré : ")

# # Calculer la longueur de la clé à partir des sous-séquences
# longueur_cle = longueur_de_cle(message)
# print(f"La longueur de la clé est : {longueur_cle}")

# # Extraire la clé en utilisant la longueur déterminée
# cle = extraire_cle(message, longueur_cle)
# print(f"La clé extraite est : {cle}")

# # Déchiffrer le message en utilisant la clé
# message_dechiffre = vigenere_decrypt(message, cle)

# print(f"Le message déchiffré est : {message_dechiffre}")

def prime_factors(n):
    factors = []
    while n % 2 == 0:
        factors.append(2)
        n //= 2
    for i in range(3, int(n**0.5) + 1, 2):
        while n % i == 0:
            factors.append(i)
            n //= i
    if n > 2:
        factors.append(n)
    return factors

# Function to filter out shorter sequences contained within longer sequences
def filter_sequences_by_length(seq_periods):
    sorted_sequences = sorted(seq_periods.keys(), key=len, reverse=True)
    filtered_sequences = {}

    for seq in sorted_sequences:
        if not any(seq in longer_seq for longer_seq in filtered_sequences):
            filtered_sequences[seq] = seq_periods[seq]

    return filtered_sequences

def find_repeated_sequences_and_periods(ciphertext, min_length):
    repeated = defaultdict(list)

    # Find repeated sequences
    for length in range(min_length, len(ciphertext) + 1):
        for i in range(len(ciphertext) - length + 1):
            seq = ciphertext[i:i + length]
            repeated[seq].append(i)

    seq_periods = {}

    # Calculate periods (distances between repeated sequences)
    for seq, positions in repeated.items():
        if len(positions) > 1:  # Only consider sequences that repeat
            periods = [positions[i + 1] - positions[i] for i in range(len(positions) - 1)]
            seq_periods[seq] = periods

    filtered_seq_periods = filter_sequences_by_length(seq_periods)

    # Collect sequences with periods
    result = []
    for seq, period_list in filtered_seq_periods.items():
        result.append({"Sequence": seq, "Periods": period_list})

    # Calculate prime factorization for each period
    prime_factorizations = []
    for item in result:
        for period in item['Periods']:
            factors = prime_factors(period)
            unique_factors = set(factors)
            prime_factorizations.append({"Period": period, "Prime Factors": list(unique_factors)})

    # Count the frequency of each prime factor
    all_prime_factors = [factor for item in prime_factorizations for factor in item['Prime Factors']]
    prime_counter = Counter(all_prime_factors)

    # Sort by frequency (descending) and value (descending)
    sorted_factors = sorted(prime_counter.items(), key=lambda x: (x[1], x[0]), reverse=True)

    # Get the largest prime factor with the highest frequency
    most_common_prime_factor = sorted_factors[0] if sorted_factors else None
    return most_common_prime_factor[0] if most_common_prime_factor else None

def frequency_analysis(ciphertext, key_length, position):
    filtered_chars = [ciphertext[i] for i in range(position, len(ciphertext), key_length)]
    freq_count = Counter(filtered_chars)

    max_frequency = max(freq_count.values()) if freq_count else 0
    most_frequent_chars = [char for char, freq in freq_count.items() if freq == max_frequency]
    return most_frequent_chars

def compute_key(ciphertext, key_length):
    possible_keys = []

    for i in range(key_length):
        most_frequent_chars = frequency_analysis(ciphertext, key_length, i)
        
        # If multiple characters have the same frequency, display a warning
        if len(most_frequent_chars) > 1:
            st.warning(f"Pour la position {i + 1}, plusieurs caractères ont la même fréquence. Plusieurs clés possibles pour cette position.")

        # Align the most frequent ciphertext characters with 'E' and compute possible key letters
        key_letters_for_position = []
        for char in most_frequent_chars:
            x = (ord(char) - ord('E')) % 26
            key_letter = chr(x + ord('A'))
            key_letters_for_position.append(key_letter)

        possible_keys.append(key_letters_for_position)

    # Combine all possible keys from the positions
    all_combinations = [''.join(key) for key in product(*possible_keys)]

    print(f"\nAll Possible Keys: {all_combinations}")
    return all_combinations  # Return all possible keys

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





# Interface Streamlit
st.markdown('<h1 style="color: #740938; font-size: 36px; text-align: center;">Chiffrement et Déchiffrement Vigenère</h1>', unsafe_allow_html=True)

# Image centrée
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.image("images.jpg", caption="Principes de base de la cryptographie", use_container_width=True)

# Description de l'application
st.markdown(
    """
    <div style="text-align: justify; font-size: 18px; color: #4A4A4A; margin-bottom: 20px;">
        Cette application interactive permet de découvrir le fonctionnement du chiffre de Vigenère, un 
        algorithme classique de cryptographie. Vous pouvez explorer les techniques de chiffrement et de déchiffrement, 
        ainsi que la cryptanalyse à l'aide des méthodes de Babbage et Friedman. Une interface conviviale vous guide 
        à travers les étapes pour mieux comprendre la puissance et les limites de ce chiffrement historique.
    </div>
    """,
    unsafe_allow_html=True
)

# Choix de l'opération
operation = st.radio(
    "Choisissez une opération :",
    ["Chiffrement", "Déchiffrement (Friedman)", "Déchiffrement (Babbage)"],
    index=0,
    format_func=lambda x: f"🔹 {x}"  # Ajoute une icône devant chaque choix
)

# Partie Chiffrement
if operation == "Chiffrement":
    st.markdown('<h2 style="color: #AF1740;">Chiffrement Vigenère</h2>', unsafe_allow_html=True)
    message = st.text_area("Entrez le message à chiffrer :", "")
    cle = st.text_input("Entrez la clé de chiffrement :", "")
    
    if st.button("Chiffrer"):
        if message and cle:
            encrypted_message = vigenere_encrypt(message, cle)
            st.subheader("Message Chiffré")
            st.write(encrypted_message)
        else:
            st.error("Veuillez entrer un message et une clé.")

# Partie Déchiffrement (Friedman)
elif operation == "Déchiffrement (Friedman)":
    st.markdown('<h2 style="color: #CC2B52;">Déchiffrement avec la méthode de Friedman</h2>', unsafe_allow_html=True)
    message = st.text_area("Entrez le message chiffré :", "")
    
    if st.button("Déchiffrer"):
        if message:
            st.subheader("Étape 1 : Détection de la longueur de la clé")
            longueur_cle = longueur_de_cle(message, ic_min=0.07)
            if not longueur_cle:
                st.error("Impossible de déterminer la longueur de la clé.")
            else:
                st.success(f"Longueur probable de la clé : {longueur_cle}")

                st.subheader("Étape 2 : Extraction de toutes les clés possibles")
                cles_possibles = extraire_cle(message, longueur_cle)
                st.write(f"{len(cles_possibles)} clés possibles trouvées :")
                st.write(", ".join(cles_possibles))

                st.subheader("Étape 3 : Déchiffrement avec chaque clé")
                for cle in cles_possibles:
                    decrypted_message = vigenere_decrypt(message, cle)
                    final_message = add_spaces_to_message(decrypted_message, message)
                    st.write(f"**Clé : {cle}** -> Message déchiffré : {final_message}")
        else:
            st.error("Veuillez entrer un message chiffré.")

# Partie Déchiffrement (Babbage)
elif operation == "Déchiffrement (Babbage)":
    st.markdown('<h2 style="color: #C75B7A;">Déchiffrement avec la méthode de Babbage</h2>', unsafe_allow_html=True)
    ciphertext = st.text_area("Entrez le texte chiffré :").replace(" ", "").upper()

    # Longueur minimale des séquences
    min_length = st.number_input("Longueur minimale des séquences répétées :", min_value=2, value=3, step=1)

    if st.button("Déchiffrer"):
        if ciphertext:
        # Phase 1 : Détection des séquences répétées et calcul des périodes
            key_length = find_repeated_sequences_and_periods(ciphertext, min_length)
        
            if not key_length:
                st.error("Impossible de déterminer la longueur de la clé. Vérifiez le texte chiffré.")
            else:
                st.write(f"Longueur de la clé déterminée : {key_length}")

            # Phase 2 : Détermination de la clé
                decryption_keys = compute_key(ciphertext, key_length)
                st.write(f"Clés possibles : {decryption_keys}")

            # Phase 3 : Décryptage avec toutes les clés possibles
                st.subheader("Messages déchiffrés avec toutes les clés possibles :")
                for key in decryption_keys:
                    plaintext = decrypt(ciphertext, key)
                    st.write(f"Clé {key} : {plaintext}")
        else:
            st.error("Veuillez entrer un texte chiffré.")

