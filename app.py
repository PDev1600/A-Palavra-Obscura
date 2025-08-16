from flask import Flask, render_template, request, redirect, url_for, session
import random, json, os

app = Flask(__name__)
app.secret_key = "segredo"

# ficheiro onde guardamos os dados
USER_DATA_FILE = "user_data.json"

# listas de palavras
WORDS = {
    "pt": {
        4: ["amor", "casa", "gato", "bota", "rato", "loja", "rosa", "fato", "lago", "vida"],
        5: ["carta", "livro", "campo", "noite", "dente", "festa", "tempo", "chuva", "porco"],
        6: ["janela", "banana", "viagem", "carros", "amigos", "sonhar", "flores", "pratos", "lindos", "sapato"],
        7: ["amarelo", "jardins", "domingo", "estrela", "alegria", "viagens", "paredes", "tijolos", "cavalos", "corrida"],
    },
    "en": {
        4: ["love", "wall", "true", "fork", "slow", "fast", "call", "done", "show", "loop"],
        5: ["phone", "music", "badly", "great", "fishy", "glass", "lions", "lemon", "fruit", "death"],
        6: ["orange", "monday", "friday", "august", "melons", "paints", "boards", "python", "mirror", "dancer"],
        7: ["counter", "glasses", "payment", "smokers", "freedom", "journey", "mystery", "silence", "explore", "victory"],
    }
}

# EXP por vitória
EXP_REWARDS = {4: 200, 5: 250, 6: 350, 7: 500}

# carregar / guardar user_data
def load_data():
    if not os.path.exists(USER_DATA_FILE):
        return {"user": "Guest", "exp": 0, "level": 1}
    with open(USER_DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(data, f)

def exp_needed(level):
    return level * 100

# ================= Splash =================
@app.route("/")
def splash():
    return render_template("splash.html")

# ================= Menu =================
@app.route("/menu")
def menu():
    data = load_data()
    exp_percentage = (data["exp"] / exp_needed(data["level"])) * 100
    return render_template("menu.html", user=data["user"], level=data["level"], exp=exp_percentage)

# ================= Start Game =================
@app.route("/start_game", methods=["POST"])
def start_game():
    language = request.form["language"]
    letters = int(request.form["letters"])
    word = random.choice(WORDS[language][letters])
    session["word"] = word
    session["language"] = language
    session["letters"] = letters

    attempts = {4: 8, 5: 9, 6: 11, 7: 14}[letters]
    session["attempts"] = attempts
    session["guesses"] = []

    return redirect(url_for("game"))

# ================= Game =================
@app.route("/game")
def game():
    if "word" not in session:
        return redirect(url_for("menu"))
    return render_template("game.html",
                           letters=session["letters"],
                           attempts=session["attempts"],
                           guesses=session["guesses"])

# ================= Guess =================
@app.route("/guess", methods=["POST"])
def guess():
    guess_word = request.form["guess"].lower()
    word = session["word"]
    guesses = session["guesses"]
    letters = session["letters"]

    if len(guess_word) != letters:
        return redirect(url_for("game"))

    guesses.append(guess_word)
    session["attempts"] -= 1
    session["guesses"] = guesses

    if guess_word == word:
        reward = EXP_REWARDS[letters]
        data = load_data()
        data["exp"] += reward
        while data["exp"] >= exp_needed(data["level"]):
            data["exp"] -= exp_needed(data["level"])
            data["level"] += 1
        save_data(data)
        return render_template("result.html", win=True, word=word, exp=reward)

    if session["attempts"] <= 0:
        return render_template("result.html", win=False, word=word, exp=30)

    return redirect(url_for("game"))

# ================= Main =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
