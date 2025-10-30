#  RMIT COSC3106 – Global Immunisation Dashboard

###  Project Team
- **Mohamad Otman** (s4091213)  
- **Ahnab** (s4200011) 

---

##  Overview
This project is a **Flask web application** built for the RMIT course **COSC3106: Python Studio**, designed to analyse global immunisation and infection data using the provided `immunisation.db` SQLite database.  
It visualises vaccination coverage, infection rates, and regional trends through interactive pages.

---

##  Features

###  A-Level Pages
| Level | Description |
|--------|--------------|
| **A1** | Landing page displaying vaccination insights (year range, vaccine totals, disease count, infectious disease list). |
| **A2** | Interactive analysis of vaccination coverage (≥90%) by year and antigen, showing country-level and regional summaries. |
| **A3** | Displays top countries with the biggest vaccination rate improvements between two years. |

###  B-Level Pages
| Level | Description |
|--------|--------------|
| **B1** | Mission statement with project purpose, personas, and team members. |
| **B2** | Infection analysis by economy type, disease, and year — showing cases per 100,000 people. |
| **B3** | Identifies countries with above-average infection rates using SQL AVG() and LIMIT queries. |

---

## Database Structure
**Database:** `immunisation.db`

Tables used:
- `Vaccination`
- `Country`
- `Region`
- `InfectionData`
- `Infection_Type`
- `Economy`
- `CountryPopulation`

---

## ⚙️ Setup Instructions

### 
```bash
git clone https://github.com/<your-username>/immunisation-dashboard.git
cd immunisation-dashboard

Install dependencies: pip install flask

Place immunisation.db in the project root (same folder as app.py).

Run the Flask app: python app.py
