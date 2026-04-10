# StudyMatch

StudyMatch is a web application that helps students find study partners. Inspired by the swipe mechanic of dating apps, students can create a profile listing their courses, availability, and study preferences. They then browse other students' profiles and swipe right to connect or left to pass. When two students both swipe right on each other, they are matched and can plan to study together.

Built with Python and Flask, StudyMatch aims to make it easier for students to find the right study partner — whether they need help on a specific subject or just want someone to study alongside.

---

# Team & Task Division

**StudyMatch** — a Tinder-style swipe app that connects students who want to study together.

**Timeline:** 3–4 weeks | **Team size:** 3

---

## Roles

| Member | Role | Focus Area |
|--------|------|------------|
| Khoa | Back End | API, authentication, matching logic |
| Marko | Front End / UI | Templates, swipe interactions, styling |
| Emir | Database / DevOps | Schema design, deployment, infrastructure |

---

## Task Breakdown

### Member 1 — Back End (API & Logic)
- Set up Flask project structure
- Connect to MongoDB using **PyMongo**
- Build routes/endpoints (users, profiles, swipes, matches)
- Implement authentication (sign up, login, session handling)
- Develop the core matching algorithm (mutual swipe = match)
- Write API documentation

### Member 2 — Front End / UI
- Build Jinja2 HTML templates for all pages
- Style pages using **Tailwind CSS** + **DaisyUI** (via CDN)
- Create all screens: onboarding, profile setup, swipe deck, matches list
- Add swipe interactions (JS or DaisyUI components)
- Ensure consistent and responsive design across pages

### Member 3 — Database / DevOps
- Design MongoDB collections (users, profiles, swipes, matches, subjects)
- Manage and maintain the MongoDB database (via MongoDB Atlas)
- Handle file/image storage for profile photos
- Set up environment configs and .env files
- Deploy the Flask app (e.g. Render / Railway)
- Manage version control workflow (branching strategy, PRs, merges)

---

## Sprint Timeline

| Sprint | Member 1 (Back End) | Member 2 (Front End) | Member 3 (DB / DevOps) |
|--------|---------------------|----------------------|------------------------|
| **Sprint 1** *(Setup)* | User stories, repo setup, architecture diagrams | User stories, wireframes, UI mockups | User stories, DB schema diagram, backlog setup |
| **Sprint 2** *(Build)* | Flask project setup, auth routes | Base template, onboarding screens | MongoDB Atlas setup, collection schema |
| **Sprint 3** *(Core Features)* | Swipe & match logic (PyMongo) | Swipe card UI with DaisyUI | DB integration, image storage |
| **Sprint 4** *(Polish & Deploy)* | Route testing & bug fixes, final review | Connect templates to back end, UI polish | Deployment setup, final deploy, README polish |

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Back End** | Python + Flask |
| **Front End** | Jinja2 + Tailwind CSS + DaisyUI |
| **Database** | MongoDB (Atlas) |
| **Python–MongoDB Bridge** | PyMongo |
| **Auth** | Flask-Login / Flask session |
| **Deployment** | Render / Railway |
| **Version Control** | Git + GitHub |

---

## Backend Status

The backend logic is now implemented in the Flask app with MongoDB integration.

### Implemented features

- User registration with hashed passwords
- Login and logout using Flask session state
- MongoDB persistence for users, profiles, swipes, and matches
- Profile setup and profile editing flow
- Swipe submission through a JSON API endpoint
- Mutual-like matching logic with persisted match records
- Matches page populated from stored MongoDB data
- Public profile view route for matched users

### MongoDB collections used

- `users`: account credentials and primary email
- `profiles`: study profile data tied to each user
- `swipes`: like/pass decisions between users
- `matches`: stored mutual matches between two users

### Main routes

- `GET /`: landing page
- `GET, POST /register`: account creation
- `GET, POST /login`: account login
- `POST /logout`: account logout
- `GET /profile`: current user profile
- `GET, POST /profile-setup`: create or edit study profile
- `GET /swipe`: ranked study deck
- `POST /api/swipe/<target_user_id>`: save a like or pass
- `GET /matches`: list current matches
- `GET /profiles/<user_id>`: view another student's profile

---

## Local Setup

1. Install dependencies:

	`python -m pip install -r requirements.txt`

2. Create a `.env` file or update the existing one with:

	- `MONGODB_URI` or `MONGO_URI`
	- `MONGODB_DB`
	- `STUDYMATCH_SECRET_KEY`

3. Run the app:

	`python app.py`

4. Open the Flask server in your browser and use the sign-up flow before browsing the study deck.

5. Optional: seed realistic demo users for presentations or manual testing:

	`python seed_demo_data.py`

	Default seeded password: `Password123`

---

## Notes

- The app expects a valid MongoDB Atlas connection string.
- Passwords are stored as hashes, not plain text.
- Profiles must be completed before a user can swipe or view matches.

---

## Deploy To Render

This project is now set up to deploy cleanly to Render.

### Option 1: Use `render.yaml`

1. Push this repository to GitHub.
2. In Render, choose **New +** and then **Blueprint**.
3. Select this repository.
4. Render will detect [render.yaml](render.yaml).
5. Set the missing environment variable:
	- `MONGO_URI` = your MongoDB Atlas connection string
6. Deploy the service.

### Option 2: Create the web service manually

Use these settings in Render:

- **Environment**: `Python`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`

### Required environment variables

- `MONGO_URI`
- `MONGODB_DB`
- `STUDYMATCH_SECRET_KEY`

### Recommended values

- `MONGODB_DB=studymatch`
- `STUDYMATCH_SECRET_KEY=<long-random-secret>`

### After deploy

1. Open the deployed URL.
2. Register a user or seed demo data locally first if you want the database pre-populated.
3. Verify login, profile setup, swipe deck, and matches.
