from flask import Flask, request, render_template, jsonify, session
import random

app = Flask(__name__)
app.secret_key = 'kelompok8' 

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


def random_cipher(text):
    ciphers = [
        ('Caesar Cipher', lambda t: caesar_cipher(t, 3, encrypt=True)),
        ('Atbash Cipher', atbash_cipher),
        ('Rail Fence Cipher', lambda t: rail_fence_cipher_encrypt(t, 3)),
        ('Polybius Square Cipher', polybius_square_cipher_encrypt),
        ('Vigenère Cipher', lambda t: vigenere_cipher(t, 'KEY')),
        ('Transposition Cipher', lambda t: transposition_cipher(t, 3)),
        ('Affine Cipher', lambda t: affine_cipher(t, 5, 8)),
    ]
    cipher_name, cipher_func = random.choice(ciphers)
    encrypted_text, explanation = cipher_func(text)
    return cipher_name, encrypted_text, explanation


def vigenere_cipher(text, key, encrypt=True):
    result = ""
    explanation = []
    key_length = len(key)
    key_as_int = [ord(i) - 65 for i in key.upper()]
    text_as_int = [ord(i) - 65 for i in text.upper()]
    
    for i in range(len(text_as_int)):
        if text[i].isalpha():
            if encrypt:
                value = (text_as_int[i] + key_as_int[i % key_length]) % 26
                result += chr(value + 97)  # Changed from 65 to 97 for lowercase output
                explanation.append(f"'{text[i]}' -> '{chr(value + 97)}' (shifted by {key_as_int[i % key_length]})")
            else:
                value = (text_as_int[i] - key_as_int[i % key_length]) % 26
                result += chr(value + 97)  # Changed from 65 to 97 for lowercase output
                explanation.append(f"'{text[i]}' -> '{chr(value + 97)}' (shifted back by {key_as_int[i % key_length]})")
        else:
            result += text[i]
            explanation.append(f"'{text[i]}' remains unchanged (non-alphabetic)")
    
    return result, explanation


def transposition_cipher(text, key):
    # Create a list of empty strings for each column
    columns = [''] * key
    explanation = []

    # Fill the columns with characters from the text
    for index, char in enumerate(text):
        columns[index % key] += char
        explanation.append(f"Placing '{char}' in column {index % key}")

    # Join the columns to create the ciphertext
    result = ''.join(columns)
    return result, explanation


def affine_cipher(text, a, b, encrypt=True):
    result = ""
    explanation = []
    
    for char in text:
        if char.isalpha():
            shift_amount = 65 if char.isupper() else 97
            original_position = ord(char) - shift_amount
            
            if encrypt:
                new_position = (a * original_position + b) % 26
                new_char = chr(new_position + shift_amount)
                result += new_char
                explanation.append(f"'{char}' -> '{new_char}' (encrypted with a={a}, b={b})")
            else:
                # Decrypting
                a_inv = pow(a, -1, 26)  # Modular inverse of a
                new_position = a_inv * (original_position - b) % 26
                new_char = chr(new_position + shift_amount)
                result += new_char
                explanation.append(f"'{char}' -> '{new_char}' (decrypted with a={a}, b={b})")
        else:
            result += char
            explanation.append(f"'{char}' remains unchanged (non-alphabetic)")
    
    return result, explanation


@app.route('/game', methods=['GET', 'POST'])
def game():
    if request.method == 'GET':
        session['lives'] = 3  # Set initial lives
        session['correct_guesses'] = 0  # Initialize correct guesses
        session['current_question'] = 0  # Initialize current question index
        return render_template("game.html", lives=session['lives'], current_question_index=session['current_question'])

    if request.method == 'POST':
        if 'user_text' in request.form:
            user_text = request.form['user_text']
            questions = []
            lives = session.get('lives', 3)
            for _ in range(10):  # Generate 10 questions
                correct_cipher, encrypted_text, explanation = random_cipher(user_text)
                questions.append((correct_cipher, encrypted_text, explanation))
            session['questions'] = questions
            
            # Add options for guessing the cipher
            current_question = questions[0]
            correct_cipher = current_question[0]

            # Determine incorrect options
            all_ciphers = [
                'Caesar Cipher', 'Atbash Cipher', 'Rail Fence Cipher', 
                'Polybius Square Cipher', 'Vigenère Cipher', 
                'Transposition Cipher', 'Affine Cipher'
            ]
            available_incorrect_options = [cipher for cipher in all_ciphers if cipher != correct_cipher]
            num_incorrect_options = min(3, len(available_incorrect_options))  # Ensure we don't sample more than available
            
            # Select random incorrect options
            incorrect_options = random.sample(available_incorrect_options, num_incorrect_options)
            options = incorrect_options + [correct_cipher]  # Add the correct cipher
            random.shuffle(options)  # Shuffle the options to randomize their order
            
            return render_template('game.html', question=current_question, lives=lives, options=options, current_question_index=session['current_question'])
        
        elif 'guess' in request.form:
            guess = request.form['guess']
            correct_cipher = request.form['correct_cipher']
            current_question_index = session.get('current_question', 0)
            lives = session.get('lives', 3)

            if guess == correct_cipher:
                session['correct_guesses'] += 1  # Increment correct guesses
                message = "Correct! Here is the solution:"
                explanation = request.form['explanation'].split(';')
                session['current_question'] += 1  # Move to the next question
                current_question_index += 1  # Increment the question index
                
                # Check if the user has completed all questions
                if session['current_question'] >= len(session['questions']):
                    message = "Congratulations! You've completed the game!"
                    session.clear()  # Clear session for a new game
                    return jsonify({'message': message, 'redirect': '/', 'lives': lives, 'explanation': []})  # Send redirect info with empty explanation
                
                # Check if the user has won
                if session['correct_guesses'] >= 10:
                    message = "You've won the game! Redirecting to the main menu."
                    session.clear()  # Clear session for a new game
                    return jsonify({'message': message, 'redirect': '/', 'lives': lives, 'explanation': []})  # Send redirect info with empty explanation
            else:
                if lives > 0:
                    lives -= 1
                    session['lives'] = lives
                message = "Wrong! Try again."
                explanation = []
                if lives <= 0:
                    message = "Game Over! Redirecting to main menu."
                    session.clear()
                    explanation = []  # Ensure explanation is defined even when game is over

            return jsonify({'message': message, 'lives': lives, 'explanation': explanation, 'current_question_index': current_question_index})

    return render_template('game.html', encrypted_text=None, options=None, correct_cipher=None, explanation=None, current_question_index=session.get('current_question', 0))


@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template("home.html")


@app.route('/new_game', methods=['GET'])
def new_game():
    session.clear()  # Clear the session to reset lives and questions
    session['lives'] = 3  # Set initial lives for the new game
    return render_template("home.html")  # Redirect to home page


if __name__ == '__main__':
    app.run(debug=True)
