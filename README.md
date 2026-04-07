 #  On-Demand Workforce Platform :ZARIYA

## Project Title

**Development of a Web-Based Platform for Connecting Customers with Unorganized Skilled Workers**

---

## Project Description

The **On-Demand Workforce Platform** is a web-based application designed to connect customers with skilled workers such as plumbers, electricians, carpenters, and painters who are not formally employed.

The platform allows:

* Customers to **search for workers**
* Customers to **post job requirements**
* Workers to **apply for jobs or accept direct requests**

This creates a **two-way interaction system**, improving accessibility, trust, and employment opportunities.

---

## Objectives

* Provide employment opportunities to unorganized workers
* Help customers find trusted workers quickly
* Create a centralized service hiring system
* Enable job posting and worker application system

---

##  Features

### User Authentication

* Separate registration and login for:

  * Customers
  * Workers

---

###  Worker Features

* Create and manage profile:

  * Skills
  * Experience
  * Location
  * Availability
* Browse job postings
* Apply to jobs
* Accept/reject direct job requests

---

### Customer Features

####  Search Workers

* Search by:

  * Skill
  * Location
* View worker profiles
* Send job requests

####  Post Job

* Add job details:

  * Description
  * Required skill
  * Location
  * Budget (optional)
  * Date/Time
* Workers can apply

---

###  Hiring Workflow

1. User registers/logs in
2. Worker creates profile
3. Customer searches or posts job
4. Worker applies or accepts request
5. Customer selects worker
6. Job is assigned
7. Job completed
8. Rating & feedback

---

###  Rating & Feedback

* Customers can rate workers
* Reviews improve trust and ranking

---

##  Tech Stack

| Layer    | Technology Used       |
| -------- | --------------------- |
| Frontend | HTML, CSS, JavaScript |
| Backend  | Python (Flask)        |
| Database | SQLite / MySQL        |

---

##  Database Structure

### Tables:

* **Users** (id, name, email, password, role)
* **WorkerProfile** (user_id, skills, experience, location, availability)
* **Jobs** (id, customer_id, description, skill_required, location, budget, date_time, status)
* **Applications** (id, job_id, worker_id, status)
* **Ratings** (id, job_id, rating, review)

---
##  Installation & Setup


### 1 Create Virtual Environment

```bash
python -m venv venv
```

### 2 Activate Environment

```bash
venv\Scripts\activate   # Windows
source venv/bin/activate  # Mac/Linux
```

### 3 Install Dependencies

```bash
pip install -r requirements.txt
```

###  Run the Application

```bash
python app.py
```

###  Open in Browser

```
http://127.0.0.1:5000/
```

---

##  Future Enhancements

*  Real-time chat system
* Online payment integration
*  Location-based services (Google Maps API)
* AI-based job-worker matching

---



---

##  Contribution

Contributions are welcome! Feel free to fork this repository and submit pull requests.

---



**Your Name**
GitHub: https://github.com/your-username

---

