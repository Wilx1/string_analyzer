# 🧠 STRING ANALYZER API

## 📘 Project Overview
A RESTful API built with **Flask** that analyzes strings, stores their properties, and provides filtering options, including natural language queries.

---

## ⚙️ Features
- ✅ Create and analyze strings
- 🔍 Retrieve specific strings
- 🎯 Filter strings by parameters
- 💬 Filter strings using natural language queries
- ❌ Delete a string
- 🧾 Structured JSON responses

---

## 🧰 Tech Stack
| Component | Technology |
|------------|-------------|
| **Language** | Python |
| **Framework** | Flask |
| **Database** | SQLite (via SQLAlchemy ORM) |
| **ORM** | SQLAlchemy |
| **Server** | Gunicorn |
| **Hosting** | Railway |

---

## 📦 Dependencies
```
Flask
Flask-SQLAlchemy
SQLAlchemy
gunicorn
python-dotenv
requests
```
Install dependencies with:
```bash
pip install -r requirements.txt
```

---

## 🗂️ Folder Structure
```
STRING_ANALYZER/
│
├── app.py
├── models.py
├── routes/
│   ├── string_routes.py
├── database/
│   ├── __init__.py
│   ├── db_setup.py
├── requirements.txt
├── Procfile
├── .env
├── README.md
└── runtime.txt
```

---

## ⚙️ Environment Variables
Create a `.env` file in your project root with the following:
```
FLASK_ENV=production
DATABASE_URL=sqlite:///strings.db
PORT=8000
```

---

## 🚀 Running the Application Locally
1️⃣ Clone the repository  
```bash
git clone https://github.com/rilx1/string_analyzer.git
cd <your-repo>
```

2️⃣ Install dependencies  
```bash
pip install -r requirements.txt
```

3️⃣ Run the Flask app  
```bash
flask run
```
App runs on: `http://127.0.0.1:5000`

---

## 🌐 Deploying to Railway

### 1️⃣ Prepare your project
Ensure you have:
- `requirements.txt`
- `Procfile` (with: `web: gunicorn app:app`)
- Your app running locally

### 2️⃣ Push code to GitHub
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

### 3️⃣ Deploy on Railway
- Go to [https://railway.app](https://railway.app)
- Click **New Project → Deploy from GitHub**
- Connect your repository
- Add environment variables under **Settings → Variables**
- Railway auto-deploys your app

---

## 🔗 API Endpoints

| Method | Endpoint | Description |
|--------|-----------|-------------|
| **POST** | `/strings` | Create/analyze a string |
| **GET** | `/strings/<string_value>` | Retrieve a specific string |
| **GET** | `/strings` | Retrieve strings with query filtering |
| **GET** | `/strings/filter-by-natural-language` | Filter strings using natural language |
| **DELETE** | `/strings/<string_value>` | Delete a string |

**Base URL:**  
`https://your-railway-app-url.up.railway.app/`

---

## 🧪 Example Natural Language Queries
| Query | Interpreted Filters |
|--------|---------------------|
| `"all single word palindromic strings"` | `word_count=1`, `is_palindrome=true` |
| `"strings longer than 10 characters"` | `min_length=11` |
| `"palindromic strings that contain the first vowel"` | `is_palindrome=true`, `contains_character=a` |
| `"strings containing the letter z"` | `contains_character=z` |

---

## 📄 License
This project is released under the MIT License.
© 2025 String Analyzer API
