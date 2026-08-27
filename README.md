# 📌 PrepTrack

**PrepTrack** is a personal placement preparation and interview tracking web application designed to help students organize and monitor their technical preparation in one place.

It allows you to track **DSA practice, SQL practice, company preparation, and overall progress** through a simple web dashboard.

## 🚀 Features

* 📊 **Dashboard** — View your overall preparation progress.
* 💻 **DSA Tracker** — Add and track DSA topics and practice progress.
* 🗄️ **SQL Tracker** — Manage SQL topics, difficulty levels, practice dates, and completion status.
* 🏢 **Company Preparation** — Maintain a list of target companies and preparation status.
* 📈 **Analytics** — Get an overview of your preparation progress.
* 🔐 **User Authentication** — Login and registration functionality.
* 📝 **Notes** — Add preparation notes for individual companies.
* 🔄 **Status Tracking** — Update preparation status as your progress changes.

## 🛠️ Tech Stack

* **Frontend:** HTML, CSS
* **Backend:** Python, Flask
* **Database:** SQLite
* **Templating:** Jinja2
* **Development Environment:** Visual Studio Code

## 📂 Project Structure

```text
PrepTrack/
│
├── app/
│   ├── templates/
│   │   ├── analytics.html
│   │   ├── base.html
│   │   ├── company.html
│   │   ├── dashboard.html
│   │   ├── dsa.html
│   │   ├── login.html
│   │   ├── mock.html
│   │   ├── register.html
│   │   └── sql.html
│   │
│   ├── __init__.py
│   ├── models.py
│   └── routes.py
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│
├── config.py
├── create_db.py
├── run.py
├── .gitignore
└── README.md
```

## ⚙️ Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/Kanishka-sketch/PrepTrack.git
cd PrepTrack
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

If a `requirements.txt` file is available:

```bash
pip install -r requirements.txt
```

Otherwise, install Flask:

```bash
pip install flask
```

### 4. Create the database

```bash
python create_db.py
```

### 5. Run the application

```bash
python run.py
```

Open the application in your browser at:

```text
http://127.0.0.1:5000
```

## 📋 How It Works

### DSA Preparation

Add DSA topics and keep track of which concepts you have completed or are currently practicing.

Examples:

* Arrays
* Strings
* Linked Lists
* Stack & Queue
* Trees
* Graphs
* Dynamic Programming

### SQL Preparation

Track SQL concepts based on difficulty and practice date.

Examples:

* SELECT Queries
* WHERE Clause
* GROUP BY
* JOINs
* Subqueries
* CTEs
* Window Functions

### Company Preparation

Add companies you are preparing for and maintain their preparation status.

Example:

| Company   | Status      |
| --------- | ----------- |
| TCS       | In Progress |
| Infosys   | In Progress |
| Accenture | In Progress |
| Deloitte  | Not Started |
| Amazon    | Not Started |

Notes can also be added for each company to specify the areas that need preparation.

## 🎯 Purpose

The main goal of **PrepTrack** is to make placement preparation more organized and consistent by keeping important preparation activities in one application.

Instead of maintaining separate notes or spreadsheets, users can track their:

**DSA → SQL → Companies → Interviews → Progress**

in one place.

## 🔮 Future Improvements

* [ ] Add more detailed analytics and progress charts
* [ ] Add coding problem tracking
* [ ] Add interview experience tracking
* [ ] Add reminders for pending topics
* [ ] Add difficulty-based filtering
* [ ] Add search and sorting functionality
* [ ] Add preparation deadlines
* [ ] Add more detailed company-wise preparation plans
* [ ] Deploy the application online

## 👩‍💻 Author

**Kanishka Joshi**

Built as a personal project to organize and improve placement preparation.

---

⭐ If you find this project useful, consider giving the repository a star!
