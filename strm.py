import streamlit as st

def rail_fence_encrypt(message, k):
    # Enlever les espaces du message pour le chiffrement
    message = message.replace(" ", "")

    # Initialiser les rails
    rails = ['' for _ in range(k)]
    direction_down = False
    row = 0

    # Remplissage des rails en va-et-vient
    for char in message:
        rails[row] += char
        # Changer de direction si on atteint un bord
        if row == 0 or row == k - 1:
            direction_down = not direction_down
        row += 1 if direction_down else -1

    # Combiner les rails pour obtenir le message chiffré
    encrypted_message = ''.join(rails)

    # Ajouter un espace toutes les 5 lettres
    spaced_message = ' '.join(
        [encrypted_message[i:i + 5] for i in range(0, len(encrypted_message), 5)]
    )
    return spaced_message

def decryptFence(cipher, rails, offset=0, debug=False):
    plain = ''

    # Ajouter l'offset
    if offset:
        t = rail_fence_encrypt('o' * offset + 'x' * len(cipher), rails)
        for i in range(len(t)):
            if t[i] == 'o':
                cipher = cipher[:i] + '#' + cipher[i:]

    length = len(cipher)
    fence = [['#'] * length for _ in range(rails)]

    # Construire la grille pour le déchiffrement
    i = 0
    for rail in range(rails):
        p = (rail != (rails - 1))
        x = rail
        while x < length and i < length:
            fence[rail][x] = cipher[i]
            if p:
                 x += 2 * (rails - rail - 1)
            else:
                 x += 2 * rail
            if rail != 0 and rail != (rails - 1):
                 p = not p
            i += 1

    # Lire la grille en suivant les lignes
    rail = 0
    dr = 1
    for x in range(length):
        if fence[rail][x] != '#':
            plain += fence[rail][x]
        if rail == 0:
            dr = 1
        elif rail == rails - 1:
            dr = -1
        rail += dr

    return plain

def main():
    st.title("Chiffrement et Déchiffrement Rail Fence")

    # Sélection de l'action
    action = st.radio("Choisissez une action", ("Chiffrement", "Déchiffrement"))

    # Entrée du texte
    message = st.text_area("Entrez le message :", "")

    # Entrée du nombre de rails
    k = st.number_input("Nombre de rails", min_value=2, max_value=10, value=3, step=1)

    # Offset pour le déchiffrement
    # offset = st.number_input("Offset (optionnel pour le déchiffrement)", min_value=0, max_value=10, value=0, step=1)

    # Bouton pour exécuter
    if st.button("Exécuter"):
        if action == "Chiffrement":
            if message:
                encrypted_message = rail_fence_encrypt(message, k)
                st.success(f"Message chiffré : {encrypted_message}")
            else:
                st.error("Veuillez entrer un message.")
        elif action == "Déchiffrement":
            if message:
                decrypted_message = decryptFence(message.replace(" ", ""), k)
                st.success(f"Message déchiffré : {decrypted_message}")
            else:
                st.error("Veuillez entrer un message.")

if __name__ == "__main__":
    main()
