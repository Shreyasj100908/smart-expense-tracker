# 💰 Smart Daily Expense Tracker

A personal finance management web application built using **Python, Streamlit, SQLite, Pandas and Plotly**.

The Smart Daily Expense Tracker helps users record income and expenses, monitor their monthly budget, analyse spending patterns and download financial reports through an interactive dashboard.

🔗 **Live Application:** https://smart-daily-expense-tracker.streamlit.app/

---

## 🚀 Features

- **Dashboard:** View total income, total expenses and remaining balance.
- **Transaction Management:** Add, view, edit and delete income and expense transactions.
- **Income and Expense Tracking:** Easily distinguish credited and debited amounts using green and red indicators.
- **Monthly Budget Management:** Set a monthly budget and monitor spending against it.
- **Expense Analytics:** Visualise category-wise expenses through interactive charts.
- **Monthly Financial Analysis:** Compare monthly income and expenses.
- **Search and Filtering:** Find transactions and filter them by type.
- **Financial Reports:** Export transaction records in CSV and Excel formats.
- **Dark Mode Interface:** A dark-themed dashboard for a comfortable viewing experience.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Streamlit | Web application interface |
| SQLite | Database management |
| Pandas | Data processing |
| Plotly | Interactive data visualisation |
| OpenPyXL | Excel report generation |
| GitHub | Source code management |
| Streamlit Community Cloud | Application deployment |

## 📸 Application Screenshots

Screenshots of the dashboard and its features will be added here.

Suggested screenshots:
- Main dashboard
- Add transaction section
- Monthly budget management
- Expense analytics
- Transaction management
- Export reports

## 📂 Project Structure

```text
smart-expense-tracker/
│
├── app.py
├── database.py
├── requirements.txt
├── .gitignore
└── README.md
```

The SQLite database (`expenses.db`) is created automatically when the application runs.

## ⚙️ Run the Project Locally

### 1. Clone the repository

```bash
git clone https://github.com/ShreyasJ100908/smart-expense-tracker.git
```

### 2. Open the project directory

```bash
cd smart-expense-tracker
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the environment

**Windows PowerShell:**

```powershell
.\venv\Scripts\Activate.ps1
```

### 5. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 6. Run the application

```bash
python -m streamlit run app.py
```

The application will open in your browser.

## 🌐 Live Deployment

The application is deployed using Streamlit Community Cloud.

**Visit:** https://smart-daily-expense-tracker.streamlit.app/

## 🔮 Future Improvements

- Persistent cloud database storage.
- Category-wise budget management.
- AI-powered spending insights.
- Monthly and yearly financial reports.
- Improved mobile responsiveness.

## ⚠️ Important Note

This project is intended for educational and demonstration purposes. The publicly deployed version should not be used for sensitive financial information until secure authentication and reliable persistent data storage are implemented.

## 👨‍💻 Developer

**Shreyas Joshi**

First-Year Computer Science Engineering Student  
Vishwakarma Institute of Technology, Pune

**Project:** Smart Daily Expense Tracker

---

⭐ If you find this project interesting, consider giving the repository a star!

**Built with Python and Streamlit.**
