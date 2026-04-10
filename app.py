import os
from datetime import datetime, timezone
from functools import wraps

from bson import ObjectId
from dotenv import load_dotenv
from flask import Flask, flash, g, jsonify, redirect, render_template, request, session, url_for
from pymongo import ASCENDING, MongoClient
from pymongo.errors import DuplicateKeyError, PyMongoError
from werkzeug.security import check_password_hash, generate_password_hash


load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("STUDYMATCH_SECRET_KEY", "dev-secret-change-me")
app.config["MONGODB_URI"] = os.getenv("MONGODB_URI") or os.getenv("MONGO_URI", "")
app.config["MONGODB_DB"] = os.getenv("MONGODB_DB", "studymatch")
app.config["MONGO_TIMEOUT_MS"] = 5000

mongo_client = None
mongo_db = None
indexes_ready = False


def utcnow():
    return datetime.now(timezone.utc)


def get_db():
    global mongo_client, mongo_db, indexes_ready

    if mongo_db is not None:
        return mongo_db

    mongo_uri = app.config["MONGODB_URI"]
    if not mongo_uri:
        raise RuntimeError("MONGODB_URI is not configured. Add it to your environment or .env file.")

    try:
        mongo_client = MongoClient(mongo_uri, serverSelectionTimeoutMS=app.config["MONGO_TIMEOUT_MS"])
        mongo_client.admin.command("ping")
        mongo_db = mongo_client[app.config["MONGODB_DB"]]
        if not indexes_ready:
            ensure_indexes(mongo_db)
            indexes_ready = True
        return mongo_db
    except PyMongoError as exc:
        raise RuntimeError(f"Could not connect to MongoDB: {exc}") from exc


def ensure_indexes(db):
    db.users.create_index([("email", ASCENDING)], unique=True)
    db.profiles.create_index([("user_id", ASCENDING)], unique=True)
    db.swipes.create_index([("swiper_id", ASCENDING), ("target_user_id", ASCENDING)], unique=True)
    db.matches.create_index([("pair_key", ASCENDING)], unique=True)


def parse_courses(raw_courses):
    if not raw_courses:
        return []
    return [course.strip().upper() for course in raw_courses.split(",") if course.strip()]


def serialize_profile(profile):
    if not profile:
        return None

    return {
        "id": str(profile["_id"]),
        "user_id": str(profile["user_id"]),
        "name": profile.get("name", ""),
        "email": profile.get("email", ""),
        "major": profile.get("major", ""),
        "study_style": profile.get("study_style", ""),
        "courses": profile.get("courses", []),
        "availability": profile.get("availability", ""),
        "bio": profile.get("bio", ""),
        "photo_url": profile.get("photo_url", ""),
        "completed": profile.get("completed", False),
    }


def get_pair_key(first_user_id, second_user_id):
    ordered_ids = sorted([str(first_user_id), str(second_user_id)])
    return "::".join(ordered_ids)


def is_profile_complete(profile):
    required_fields = [
        profile.get("name"),
        profile.get("email"),
        profile.get("major"),
        profile.get("availability"),
        profile.get("bio"),
    ]
    return all(required_fields) and bool(profile.get("courses"))


def calculate_match_score(current_profile, candidate_profile):
    current_courses = set(current_profile.get("courses", []))
    candidate_courses = set(candidate_profile.get("courses", []))
    shared_courses = len(current_courses & candidate_courses)
    same_study_style = int(current_profile.get("study_style") == candidate_profile.get("study_style"))
    same_major = int(current_profile.get("major") and current_profile.get("major") == candidate_profile.get("major"))
    return (shared_courses * 3) + same_study_style + same_major


def get_current_user_id():
    user_id = session.get("user_id")
    if not user_id:
        return None
    try:
        return ObjectId(user_id)
    except Exception:
        session.clear()
        return None


def login_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if not g.current_user:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)

    return wrapped_view


def profile_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if not g.current_user:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        if not g.current_profile or not g.current_profile.get("completed"):
            flash("Complete your profile before browsing other students.", "warning")
            return redirect(url_for("profile_setup"))
        return view_func(*args, **kwargs)

    return wrapped_view


@app.before_request
def load_session_user():
    g.current_user = None
    g.current_profile = None
    g.db_available = True

    user_id = get_current_user_id()
    if not user_id:
        return

    try:
        db = get_db()
        g.current_user = db.users.find_one({"_id": user_id})
        if g.current_user:
            g.current_profile = db.profiles.find_one({"user_id": user_id})
        else:
            session.clear()
    except RuntimeError:
        g.db_available = False


@app.context_processor
def inject_template_context():
    return {
        "current_user": g.get("current_user"),
        "current_profile": serialize_profile(g.get("current_profile")),
        "db_available": g.get("db_available", True),
    }


@app.route("/")
def home():
    match_count = 0
    if g.current_user and g.db_available:
        db = get_db()
        match_count = db.matches.count_documents({"user_ids": g.current_user["_id"]})
    return render_template("home.html", match_count=match_count)


@app.route("/register", methods=["GET", "POST"])
def register():
    if g.current_user:
        return redirect(url_for("profile_setup"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not name or not email or not password:
            flash("Name, email, and password are required.", "error")
            return render_template("register.html", form_data=request.form)

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("register.html", form_data=request.form)

        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "error")
            return render_template("register.html", form_data=request.form)

        db = get_db()
        user_document = {
            "name": name,
            "email": email,
            "password_hash": generate_password_hash(password),
            "created_at": utcnow(),
        }

        try:
            result = db.users.insert_one(user_document)
        except DuplicateKeyError:
            flash("An account with that email already exists.", "error")
            return render_template("register.html", form_data=request.form)

        db.profiles.insert_one(
            {
                "user_id": result.inserted_id,
                "name": name,
                "email": email,
                "major": "",
                "study_style": "Focused problem solving",
                "courses": [],
                "availability": "",
                "bio": "",
                "photo_url": "",
                "completed": False,
                "created_at": utcnow(),
                "updated_at": utcnow(),
            }
        )

        session["user_id"] = str(result.inserted_id)
        flash("Account created. Finish your profile to start matching.", "success")
        return redirect(url_for("profile_setup"))

    return render_template("register.html", form_data={})


@app.route("/login", methods=["GET", "POST"])
def login():
    if g.current_user:
        return redirect(url_for("home"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        db = get_db()
        user = db.users.find_one({"email": email})
        if not user or not check_password_hash(user["password_hash"], password):
            flash("Invalid email or password.", "error")
            return render_template("login.html", form_data=request.form)

        session["user_id"] = str(user["_id"])
        flash("You are now logged in.", "success")
        return redirect(url_for("match_deck"))

    return render_template("login.html", form_data={})


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))


@app.route("/profile")
@login_required
def my_profile():
    return render_template("profile_view.html", profile=serialize_profile(g.current_profile), is_owner=True)


@app.route("/profiles/<user_id>")
@login_required
def view_profile(user_id):
    try:
        target_id = ObjectId(user_id)
    except Exception:
        flash("That profile does not exist.", "error")
        return redirect(url_for("matches"))

    db = get_db()
    profile = db.profiles.find_one({"user_id": target_id, "completed": True})
    if not profile:
        flash("That profile does not exist.", "error")
        return redirect(url_for("matches"))

    return render_template(
        "profile_view.html",
        profile=serialize_profile(profile),
        is_owner=g.current_user and g.current_user["_id"] == target_id,
    )


@app.route("/profile-setup", methods=["GET", "POST"])
@login_required
def profile_setup():
    db = get_db()
    existing_profile = g.current_profile or db.profiles.find_one({"user_id": g.current_user["_id"]})

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        major = request.form.get("major", "").strip()
        study_style = request.form.get("study_style", "Focused problem solving").strip()
        courses = parse_courses(request.form.get("courses", ""))
        availability = request.form.get("availability", "").strip()
        bio = request.form.get("bio", "").strip()
        photo_url = request.form.get("photo_url", "").strip()

        profile_document = {
            "user_id": g.current_user["_id"],
            "name": name,
            "email": email,
            "major": major,
            "study_style": study_style,
            "courses": courses,
            "availability": availability,
            "bio": bio,
            "photo_url": photo_url,
            "updated_at": utcnow(),
        }
        profile_document["completed"] = is_profile_complete(profile_document)

        if not profile_document["completed"]:
            flash("Complete all profile fields and add at least one course.", "error")
            return render_template("profile_setup.html", profile=profile_document)

        existing_user = db.users.find_one({"email": email})
        if existing_user and existing_user["_id"] != g.current_user["_id"]:
            flash("Another account already uses that email address.", "error")
            return render_template("profile_setup.html", profile=profile_document)

        db.users.update_one({"_id": g.current_user["_id"]}, {"$set": {"email": email, "name": name}})
        db.profiles.update_one(
            {"user_id": g.current_user["_id"]},
            {
                "$set": profile_document,
                "$setOnInsert": {"created_at": utcnow()},
            },
            upsert=True,
        )

        flash("Profile saved successfully. You can now start swiping.", "success")
        return redirect(url_for("match_deck"))

    profile_data = serialize_profile(existing_profile) if existing_profile else {}
    return render_template("profile_setup.html", profile=profile_data)


@app.route("/swipe")
@profile_required
def match_deck():
    db = get_db()
    current_user_id = g.current_user["_id"]
    current_profile = g.current_profile

    swiped_user_ids = db.swipes.distinct("target_user_id", {"swiper_id": current_user_id})
    candidate_profiles = list(
        db.profiles.find(
            {
                "user_id": {"$nin": swiped_user_ids + [current_user_id]},
                "completed": True,
            }
        )
    )

    ranked_profiles = sorted(
        candidate_profiles,
        key=lambda profile: (
            calculate_match_score(current_profile, profile),
            profile.get("updated_at", datetime.min.replace(tzinfo=timezone.utc)),
        ),
        reverse=True,
    )
    cards = [serialize_profile(profile) for profile in ranked_profiles]
    return render_template("match_deck.html", cards=cards)


@app.route("/api/swipe/<target_user_id>", methods=["POST"])
@profile_required
def swipe_profile(target_user_id):
    try:
        target_object_id = ObjectId(target_user_id)
    except Exception:
        return jsonify({"message": "Invalid profile."}), 400

    if target_object_id == g.current_user["_id"]:
        return jsonify({"message": "You cannot swipe on your own profile."}), 400

    payload = request.get_json(silent=True) or {}
    action = payload.get("action", "").strip().lower()
    if action not in {"like", "pass"}:
        return jsonify({"message": "Action must be 'like' or 'pass'."}), 400

    db = get_db()
    target_profile = db.profiles.find_one({"user_id": target_object_id, "completed": True})
    if not target_profile:
        return jsonify({"message": "This profile is no longer available."}), 404

    liked = action == "like"
    db.swipes.update_one(
        {"swiper_id": g.current_user["_id"], "target_user_id": target_object_id},
        {
            "$set": {
                "liked": liked,
                "updated_at": utcnow(),
            },
            "$setOnInsert": {"created_at": utcnow()},
        },
        upsert=True,
    )

    matched = False
    if liked:
        reciprocal_swipe = db.swipes.find_one(
            {
                "swiper_id": target_object_id,
                "target_user_id": g.current_user["_id"],
                "liked": True,
            }
        )
        if reciprocal_swipe:
            matched = True
            pair_key = get_pair_key(g.current_user["_id"], target_object_id)
            db.matches.update_one(
                {"pair_key": pair_key},
                {
                    "$setOnInsert": {
                        "pair_key": pair_key,
                        "user_ids": [g.current_user["_id"], target_object_id],
                        "created_at": utcnow(),
                    }
                },
                upsert=True,
            )

    return jsonify(
        {
            "matched": matched,
            "message": "It is a match. You can now find this student in your matches list." if matched else "Swipe saved.",
        }
    )


@app.route("/matches")
@profile_required
def matches():
    db = get_db()
    current_user_id = g.current_user["_id"]
    match_documents = list(db.matches.find({"user_ids": current_user_id}).sort("created_at", -1))

    match_cards = []
    for match_document in match_documents:
        other_user_id = next(user_id for user_id in match_document["user_ids"] if user_id != current_user_id)
        profile = db.profiles.find_one({"user_id": other_user_id})
        if not profile:
            continue

        shared_courses = sorted(set(g.current_profile.get("courses", [])) & set(profile.get("courses", [])))
        message = (
            f"Shared course overlap: {', '.join(shared_courses)}."
            if shared_courses
            else "You both expressed interest in studying together."
        )
        serialized_profile = serialize_profile(profile)
        serialized_profile["message"] = message
        match_cards.append(serialized_profile)

    return render_template("matches.html", matches=match_cards)


@app.errorhandler(RuntimeError)
def handle_runtime_error(error):
    flash(str(error), "error")
    return render_template("home.html", match_count=0), 503


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "true").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
