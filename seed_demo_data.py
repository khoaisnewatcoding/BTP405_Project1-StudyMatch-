import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from pymongo import MongoClient
from werkzeug.security import generate_password_hash


load_dotenv()


def utcnow():
    return datetime.now(timezone.utc)


DEMO_PASSWORD = os.getenv("STUDYMATCH_DEMO_PASSWORD", "Password123")
MONGODB_URI = os.getenv("MONGODB_URI") or os.getenv("MONGO_URI", "")
MONGODB_DB = os.getenv("MONGODB_DB", "studymatch")


DEMO_USERS = [
    {
        "name": "Aisha Rahman",
        "email": "aisha.rahman@studymatch.demo",
        "major": "Computer Science",
        "study_style": "Focused problem solving",
        "courses": ["BTP405", "DBS301", "CPS510"],
        "availability": "Mon/Wed 6-8pm",
        "bio": "Looking for a backend project partner who enjoys debugging and whiteboarding database design.",
        "photo_url": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Noah Bennett",
        "email": "noah.bennett@studymatch.demo",
        "major": "Software Engineering",
        "study_style": "Exam prep",
        "courses": ["BTP405", "CPS406", "CPS530"],
        "availability": "Tue/Thu 5-7pm",
        "bio": "I like building review sheets, comparing architecture notes, and doing mock exam questions out loud.",
        "photo_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Mia Chen",
        "email": "mia.chen@studymatch.demo",
        "major": "Data Science",
        "study_style": "Flashcards / quizzes",
        "courses": ["BTP405", "MTH314", "CIND123"],
        "availability": "Weekends 1-4pm",
        "bio": "Best for fast review rounds, quiz sessions, and breaking large topics into smaller checkpoints.",
        "photo_url": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Jay Patel",
        "email": "jay.patel@studymatch.demo",
        "major": "Business Technology Management",
        "study_style": "Group discussion",
        "courses": ["BTP405", "ITM301", "CMN279"],
        "availability": "Fri 2-6pm",
        "bio": "Prefer collaborative sessions where we explain concepts, compare notes, and connect theory to case studies.",
        "photo_url": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Sofia Martinez",
        "email": "sofia.martinez@studymatch.demo",
        "major": "Computer Engineering",
        "study_style": "Focused problem solving",
        "courses": ["ELE404", "BTP405", "CPS412"],
        "availability": "Sun 10am-1pm",
        "bio": "Strong on system design and implementation details. Looking for someone consistent for weekly check-ins.",
        "photo_url": "https://images.unsplash.com/photo-1488426862026-3ee34a7d66df?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Ethan Walker",
        "email": "ethan.walker@studymatch.demo",
        "major": "Information Technology",
        "study_style": "Exam prep",
        "courses": ["BTP405", "CPS633", "CCPS109"],
        "availability": "Mon/Thu 7-9pm",
        "bio": "Looking for a dependable partner to prep for presentations, review implementation details, and stay on schedule.",
        "photo_url": "https://images.unsplash.com/photo-1504593811423-6dd665756598?auto=format&fit=crop&w=600&q=80",
    },
]


def ensure_indexes(db):
    db.users.create_index("email", unique=True)
    db.profiles.create_index("user_id", unique=True)


def seed_demo_users():
    if not MONGODB_URI:
        raise RuntimeError("Set MONGODB_URI or MONGO_URI before running the seed script.")

    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    db = client[MONGODB_DB]
    ensure_indexes(db)

    seeded_count = 0
    for demo_user in DEMO_USERS:
        user_document = {
            "name": demo_user["name"],
            "email": demo_user["email"],
            "password_hash": generate_password_hash(DEMO_PASSWORD),
            "created_at": utcnow(),
        }

        existing_user = db.users.find_one({"email": demo_user["email"]})
        if existing_user:
            user_id = existing_user["_id"]
            db.users.update_one(
                {"_id": user_id},
                {
                    "$set": {
                        "name": demo_user["name"],
                        "password_hash": generate_password_hash(DEMO_PASSWORD),
                    }
                },
            )
        else:
            user_id = db.users.insert_one(user_document).inserted_id
            seeded_count += 1

        profile_document = {
            "user_id": user_id,
            "name": demo_user["name"],
            "email": demo_user["email"],
            "major": demo_user["major"],
            "study_style": demo_user["study_style"],
            "courses": demo_user["courses"],
            "availability": demo_user["availability"],
            "bio": demo_user["bio"],
            "photo_url": demo_user["photo_url"],
            "completed": True,
            "updated_at": utcnow(),
        }

        db.profiles.update_one(
            {"user_id": user_id},
            {
                "$set": profile_document,
                "$setOnInsert": {"created_at": utcnow()},
            },
            upsert=True,
        )

    print(f"Seeded or refreshed {len(DEMO_USERS)} demo profiles in '{MONGODB_DB}'.")
    print(f"Newly created accounts: {seeded_count}")
    print("Demo login password:", DEMO_PASSWORD)


if __name__ == "__main__":
    seed_demo_users()