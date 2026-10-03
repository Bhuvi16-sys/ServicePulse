# ⚡ ServicePulse

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![SQLite](https://img.shields.io/badge/Database-SQLite-green)

ServicePulse is a Python-based system designed for comprehensive service monitoring, automation, and analytics. It features a modular architecture that handles real-time monitoring, data injection, and automated reporting, all accessible through a graphical user interface.

## 🚀 Features

* **Automated Monitoring:** Continuous tracking and automated scheduling for service health and metrics.
* **Analytics & Reporting:** Built-in tools to process data and generate insightful reports.
* **Graphical User Interface (GUI):** User-friendly interface for interacting with the system and visualizing data.
* **Database Management:** Robust local data storage using SQLite (`servicepulse.db`).
* **Data Injection:** Dedicated scripts for seamless data ingestion and testing.

## 🛠 Tech Stack

* **Language:** Python (92.7%), HTML (7.3%)
* **Database:** SQLite

## 📁 Project Structure

```text
ServicePulse/
├── analytics/         # Data analysis and processing modules
├── automation/        # Automatic monitoring schedulers and scripts
├── database/          # Database connection and query management
├── gui/               # Graphical User Interface components and HTML templates
├── monitoring/        # Core service monitoring logic
├── reports/           # Report generation modules
├── inject_data.py     # Script for injecting test/initial data into the database
├── main.py            # Main entry point of the application
├── servicepulse.db    # SQLite database file
└── readme.md          # Project documentation
```
⚙️ Installation & Setup   
Clone the repository:   

Bash
git clone [https://github.com/Bhuvi16-sys/ServicePulse.git](https://github.com/Bhuvi16-sys/ServicePulse.git)
cd ServicePulse
Set up a virtual environment (Optional but recommended):   

Bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
Install dependencies:   

Bash
pip install -r requirements.txt
Initialize the Database:
Populate the database with initial data using the injection script:

Bash
python inject_data.py
💻 Usage
To start the ServicePulse application, run the main script from the root directory:

Bash
python main.py
👥 Contributors
@Bhuvi16-sys

@aditi-raj-dev

@Ashish-Galaxy07   

@NishthaMaurya06   

@harshityagi811
