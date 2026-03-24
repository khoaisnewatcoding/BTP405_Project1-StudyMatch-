# 📚 StudyMatch

StudyMatch is a web application that helps students find study partners. Inspired by the swipe mechanic of dating apps, students can create a profile listing their courses, availability, and study preferences. They then browse other students' profiles and swipe right to connect or left to pass. When two students both swipe right on each other, they are matched and can plan to study together.

Built with Python and Flask, StudyMatch aims to make it easier for students to find the right study partner — whether they need help on a specific subject or just want someone to study alongside.

---

# 👥 Team & Task Division

**StudyMatch** — a Tinder-style swipe app that connects students who want to study together.

**Timeline:** 3–4 weeks | **Team size:** 3

---

## 🧑‍💻 Roles

| Member | Role | Focus Area |
|--------|------|------------|
| Khoa | Back End | API, authentication, matching logic |
| Marko | Front End / UI | Templates, swipe interactions, styling |
| Emir | Database / DevOps | Schema design, deployment, infrastructure |

---

## 📋 Task Breakdown

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

## 🗓️ Sprint Timeline

| Sprint | Member 1 (Back End) | Member 2 (Front End) | Member 3 (DB / DevOps) |
|--------|---------------------|----------------------|------------------------|
| **Sprint 1** *(Setup)* | User stories, repo setup, architecture diagrams | User stories, wireframes, UI mockups | User stories, DB schema diagram, backlog setup |
| **Sprint 2** *(Build)* | Flask project setup, auth routes | Base template, onboarding screens | MongoDB Atlas setup, collection schema |
| **Sprint 3** *(Core Features)* | Swipe & match logic (PyMongo) | Swipe card UI with DaisyUI | DB integration, image storage |
| **Sprint 4** *(Polish & Deploy)* | Route testing & bug fixes, final review | Connect templates to back end, UI polish | Deployment setup, final deploy, README polish |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Back End** | Python + Flask |
| **Front End** | Jinja2 + Tailwind CSS + DaisyUI |
| **Database** | MongoDB (Atlas) |
| **Python–MongoDB Bridge** | PyMongo |
| **Auth** | Flask-Login / Flask session |
| **Deployment** | Render / Railway |
| **Version Control** | Git + GitHub |
