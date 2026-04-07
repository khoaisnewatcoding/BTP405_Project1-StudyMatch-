from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "replace-with-secure-secret"

sample_cards = [
    {
        "name": "Aisha",
        "major": "Computer Science",
        "courses": ["CS101", "CS204"],
        "availability": "Mon/Wed 6-8pm",
        "bio": "Looking for a focused partner to study algorithms and database concepts.",
    },
    {
        "name": "Jayden",
        "major": "Business Analytics",
        "courses": ["STAT210", "ECON102"],
        "availability": "Tue/Thu 4-6pm",
        "bio": "Easygoing study buddy who loves group sessions and review quizzes.",
    },
    {
        "name": "Mia",
        "major": "Mathematics",
        "courses": ["MATH231", "PHYS148"],
        "availability": "Weekends",
        "bio": "Happy to help with proofs, problem sets, and exam prep.",
    },
]

sample_matches = [
    {
        "name": "Ethan",
        "major": "Software Engineering",
        "courses": ["CS201", "CS271"],
        "message": "Matched on data structures and project work!",
    },
    {
        "name": "Sana",
        "major": "Psychology",
        "courses": ["PSY100", "SOC140"],
        "message": "Ready to study for the next midterm together.",
    },
]

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/profile-setup", methods=["GET", "POST"])
def profile_setup():
    if request.method == "POST":
        flash("Profile saved successfully. You can now start swiping!", "success")
        return redirect(url_for("match_deck"))
    return render_template("profile_setup.html")

@app.route("/swipe")
def match_deck():
    return render_template("match_deck.html", cards=sample_cards)

@app.route("/matches")
def matches():
    return render_template("matches.html", matches=sample_matches)

@app.route("/login")
def login():
    return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=True)
