from flask import Flask, request, render_template, jsonify
import random

app = Flask(__name__)


def caesar_cipher(text, shift, encrypt=True):
    result = ""
    explanation = []
    shift = shift if encrypt else -shift
    for char in text:
        if char.isalpha():
            shift_amount = 65 if char.isupper() else 97
            original_position = ord(char) - shift_amount
            new_position = (original_position + shift) % 26
            new_char = chr(new_position + shift_amount)
            result += new_char
            explanation.append(
                f"'{char}' -> '{new_char}' (shifted by {shift})")
        else:
            result += char
            explanation.append(f"'{char}' remains unchanged (non-alphabetic)")
    return result, explanation


def atbash_cipher(text):
    result = ""
    explanation = []
    for char in text:
        if char.isalpha():
            shift_amount = 65 if char.isupper() else 97
            original_position = ord(char) - shift_amount
            new_position = 25 - original_position
            new_char = chr(new_position + shift_amount)
            result += new_char
            explanation.append(
                f"'{char}' -> '{new_char}' (mirrored in alphabet)")
        else:
            result += char
            explanation.append(f"'{char}' remains unchanged (non-alphabetic)")
    return result, explanation


def rail_fence_cipher_encrypt(text, key):
    rail = [['\n' for _ in range(len(text))] for _ in range(key)]
    dir_down = False
    row, col = 0, 0
    explanation = []

    for i in range(len(text)):
        if row == 0 or row == key - 1:
            dir_down = not dir_down
        rail[row][col] = text[i]
        explanation.append(f"Placing '{text[i]}' at rail {row}, column {col}")
        col += 1
        row += 1 if dir_down else -1

    result = []
    for i in range(key):
        for j in range(len(text)):
            if rail[i][j] != '\n':
                result.append(rail[i][j])
    return ''.join(result), explanation


def rail_fence_cipher_decrypt(cipher, key):
    rail = [['\n' for _ in range(len(cipher))] for _ in range(key)]
    dir_down = None
    row, col = 0, 0
    explanation = []

    for i in range(len(cipher)):
        if row == 0:
            dir_down = True
        if row == key - 1:
            dir_down = False
        rail[row][col] = '*'
        col += 1
        row += 1 if dir_down else -1

    index = 0
    for i in range(key):
        for j in range(len(cipher)):
            if rail[i][j] == '*' and index < len(cipher):
                rail[i][j] = cipher[index]
                explanation.append(
                    f"Placing '{cipher[index]}' at rail {i}, column {j}")
                index += 1

    result = []
    row, col = 0, 0
    for i in range(len(cipher)):
        if row == 0:
            dir_down = True
        if row == key - 1:
            dir_down = False
        if rail[row][col] != '\n':
            result.append(rail[row][col])
            col += 1
        row += 1 if dir_down else -1

    return ''.join(result), explanation


def polybius_square_cipher_encrypt(text):
    square = {
        'A': '11', 'B': '12', 'C': '13', 'D': '14', 'E': '15',
        'F': '21', 'G': '22', 'H': '23', 'I': '24', 'J': '24',
        'K': '25', 'L': '31', 'M': '32', 'N': '33', 'O': '34',
        'P': '35', 'Q': '41', 'R': '42', 'S': '43', 'T': '44',
        'U': '45', 'V': '51', 'W': '52', 'X': '53', 'Y': '54',
        'Z': '55'
    }
    result = []
    explanation = []
    for char in text.upper():
        if char == ' ':
            result.append(' ')
            explanation.append("Space remains unchanged")
        elif char in square:
            result.append(square[char])
            explanation.append(f"'{char}' -> '{square[char]}'")
        else:
            result.append(char)
            explanation.append(f"'{char}' remains unchanged (non-alphabetic)")
    return ' '.join(result), explanation


def polybius_square_cipher_decrypt(cipher):
    square = {
        '11': 'A', '12': 'B', '13': 'C', '14': 'D', '15': 'E',
        '21': 'F', '22': 'G', '23': 'H', '24': 'I', '25': 'K',
        '31': 'L', '32': 'M', '33': 'N', '34': 'O', '35': 'P',
        '41': 'Q', '42': 'R', '43': 'S', '44': 'T', '45': 'U',
        '51': 'V', '52': 'W', '53': 'X', '54': 'Y', '55': 'Z'
    }
    result = []
    explanation = []
    pairs = cipher.split(' ')
    for pair in pairs:
        if pair == '':
            result.append(' ')
            explanation.append("Space remains unchanged")
        elif pair in square:
            result.append(square[pair])
            explanation.append(f"'{pair}' -> '{square[pair]}'")
        else:
            result.append(pair)
            explanation.append(f"'{pair}' remains unchanged (non-alphabetic)")
    return ''.join(result), explanation


def random_cipher(text):
    ciphers = [
        ('Caesar Cipher', lambda t: caesar_cipher(t, 3, encrypt=True)),
        ('Atbash Cipher', atbash_cipher),
        ('Rail Fence Cipher', lambda t: rail_fence_cipher_encrypt(t, 3)),
        ('Polybius Square Cipher', polybius_square_cipher_encrypt)
    ]
    cipher_name, cipher_func = random.choice(ciphers)
    encrypted_text, explanation = cipher_func(text)
    return cipher_name, encrypted_text, explanation


@app.route('/game', methods=['GET', 'POST'])
def game():
    if request.method == 'POST':
        if 'user_text' in request.form:
            user_text = request.form['user_text']
            correct_cipher, encrypted_text, explanation = random_cipher(
                user_text)

            # Shuffle options for multiple-choice
            options = ['Caesar Cipher', 'Atbash Cipher',
                       'Rail Fence Cipher', 'Polybius Square Cipher']
            random.shuffle(options)

            return render_template('game.html', encrypted_text=encrypted_text, options=options, correct_cipher=correct_cipher, explanation=explanation)
        elif 'guess' in request.form:
            guess = request.form['guess']
            correct_cipher = request.form.get('correct_cipher', '')
            explanation = request.form.get('explanation', '').split(';')

            if guess == correct_cipher:
                message = "Correct! Here is the solution:"
            else:
                message = f"Wrong! The correct algorithm was {correct_cipher}. Here is the solution:"

            return jsonify({'message': message, 'explanation': explanation})

    return render_template('game.html', encrypted_text=None, options=None, correct_cipher=None, explanation=None)


@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template("home.html")


if __name__ == '__main__':
    app.run(debug=True)
