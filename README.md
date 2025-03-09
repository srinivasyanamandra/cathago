# Document Scanning & Matching System

## Overview
This project is a **self-contained document scanning and matching system** with a built-in **credit system**. Each user has a **daily limit of 20 free scans**, and additional scans require requesting more credits from an admin.

### **Features:**
- **User Management & Authentication** (Regular Users & Admins)
- **Credit System** (Daily Free Scans & Admin Approval for Additional Credits)
- **Document Upload & Text Matching** (Basic text similarity matching)
- **Smart Analytics Dashboard** (Track scans, credits, and user activity)
- **Admin Panel** (Credit management, analytics, and user monitoring)
- **AI-powered document matching**
- **Automated Credit Reset** at midnight
- **User Activity Logs & Export Reports**
- **Multi-user Support** on a local server

---

## Tech Stack
### **Frontend:**
- HTML, CSS, JavaScript (No frameworks)

### **Backend:**
- Python Django (No external libraries or frameworks)

### **Database:**
- SQLite (Local Storage)

### **File Storage:**
- Store documents locally

### **Authentication:**
- Basic username-password authentication (Hashed passwords)

### **Text Matching Logic:**
- Custom algorithm using **Levenshtein distance, word frequency analysis**, etc.

### **Bonus (AI-powered Matching):**
- OpenAI API (GPT models), Google Gemini, DeepSeek AI, or self-hosted NLP models (spaCy, BERT, Llama2) for enhanced similarity detection.

---

## API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| **POST** | `/auth/register` | User registration |
| **POST** | `/auth/login` | User login (Session-based) |
| **GET** | `/user/profile` | Get user profile & credits |
| **POST** | `/scan` | Upload document for scanning (uses 1 credit) |
| **GET** | `/matches/:docId` | Get matching documents |
| **POST** | `/credits/request` | Request admin to add credits |
| **GET** | `/admin/analytics` | Get analytics for admins |

---

## Credit System Implementation

### **Daily Free Credits:**
- Each user receives **20 free credits daily** (auto-reset at midnight).
- If a user **runs out of credits**, they must wait until the next day or request additional credits from an admin.

### **Admin Credit Management:**
- Users can request additional credits.
- Admins can **approve/deny requests** or **manually adjust balances**.

### **Handling Credit Deductions:**
- Each document scan deducts **1 credit**.
- Users with **0 credits cannot scan** unless:
  - They wait for the next daily reset, OR
  - Admin manually adds credits.

---

## How to Run the Project

### **Step 1: Clone the Repository**
```bash
$ git clone https://github.com/srinivasyanamandra/cathago.git
$ cd cathago
```

### **Step 2: Set Up a Virtual Environment**
```bash
$ python -m venv venv
$ source venv/bin/activate  # For macOS/Linux
$ venv\Scripts\activate  # For Windows
```

### **Step 3: Install Dependencies**
```bash
$ pip install -r requirements.txt
```

### **Step 4: Run Migrations & Start the Server**
```bash
$ python manage.py migrate
$ python manage.py runserver
```

### **Step 5: Access the Application**
Open a web browser and go to:  
`http://127.0.0.1:8000/`

---

## Contributing
If you want to contribute to this project, follow these steps:
1. Fork the repository.
2. Create a new branch: `git checkout -b feature-branch`
3. Make your changes and commit them.
4. Push to your fork and submit a pull request.

---

## Contact
For any queries, feel free to reach out:  
👤 **Srinivas Yanamandra**  
📧 Email: *your-email@example.com*  
📌 GitHub: [srinivasyanamandra](https://github.com/srinivasyanamandra)

