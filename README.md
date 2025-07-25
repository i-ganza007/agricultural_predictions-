<p align="center">
  <a href="" rel="noopener">
</p>
<h3 align="center">Agricultural Yield Prediction</h3>

<div align="center">

</div>

---

## 📝 Table of Contents

- [Problem Statement](#problem_statement)
- [Dependencies / Limitations](#limitations)
- [Future Scope](#future_scope)
- [Setting up a local environment](#getting_started)
- [Usage](#usage)
- [Technology Stack](#tech_stack)
- [Authors](#authors)

## 🧐 Project Description <a name = "problem_statement"></a>

This project integrates relational and non-relational databases with a machine learning model to provide a RESTful API for predictive analytics. Using a structured dataset, the system enables data storage, retrieval, and real-time prediction via a FastAPI-based backend.

Key components include:

    A MySQL database with a well-designed schema (including stored procedures and triggers).

    A MongoDB database for storing unstructured or historical prediction logs.

    A machine learning model trained on the selected dataset (e.g., health, loan approval, churn, etc.).

    A FastAPI interface with CRUD endpoints to interact with the databases and invoke the prediction model.



## ⛓️ Dependencies / Limitations <a name = "limitations"></a>

1. fastapi==0.116.0

   Purpose: Core web framework for creating APIs.

   Use: Defines your routes, handles requests/responses, integrates with Pydantic for validation.

2. sqlmodel==0.0.24

   Purpose: ORM that combines Pydantic and SQLAlchemy.

   Use: Models your SQL tables and handles database queries cleanly.

3. SQLAlchemy==2.0.41

   Purpose: Underlying ORM that sqlmodel is built on.

   Use: Manages database connections, queries, transactions.

4. PyMySQL==1.1.1

   Purpose: Database driver to connect Python to MySQL.

   Use: Used internally by SQLAlchemy/SQLModel to talk to MySQL on Railway.

5. uvicorn==0.35.0

   Purpose: ASGI server to run FastAPI apps.

   Use: Launches your backend locally or in deployment.

6. pydantic==2.11.7

   Purpose: Data validation and serialization library.

   Use: Validates API input/output, used in FastAPI and SQLModel.

7. python-dotenv==1.1.1

   Purpose: Loads environment variables from a .env file.

   Use: Securely manages DB credentials and settings (like DATABASE_URL).

8. starlette==0.46.2

   Purpose: ASGI framework FastAPI is built on.

   Use: Handles lower-level HTTP and WebSocket routes, background tasks, etc.

9. h11==0.16.0

   Purpose: HTTP/1.1 protocol implementation.

   Use: Used internally by uvicorn for handling HTTP connections.

10. anyio==4.9.0

    Purpose: Async concurrency backend.

    Use: Enables async/await support in Uvicorn, Starlette, FastAPI.

11. typing_extensions==4.14.1

    Purpose: Backport of newer typing features.

    Use: Ensures compatibility with typing in older Python versions.

12. annotated-types==0.7.0

    Purpose: Support for Annotated[] in validation schemas.

    Use: Helps Pydantic with custom constraints.

13. typing-inspection==0.4.1

    Purpose: Introspects typing info.

    Use: Used by Pydantic internally.

14. pycountry==24.6.1

    Purpose: Returns country metadata (names, ISO codes, etc.).

    Use: Only needed if your app handles location-based data. If unused in your models or logic, it’s safe to remove.

## 🚀 Future Scope <a name = "future_scope"></a>

In the future, this system can be extended to serve as an agricultural decision-support tool for farmers, cooperatives, and government agencies. By integrating real-time data sources such as weather APIs, soil quality sensors, and satellite imagery, the model can predict crop yields with increasing accuracy.

## 🏁 Getting Started <a name = "getting_started"></a>

These instructions will get you a copy of the project up and running on your local machine for development
and testing purposes. See [deployment](#deployment) for notes on how to deploy the project on a live system.

### Prerequisites

You need to install the above packages and frameworks specified in the Dependencies / Limitations section .

### Installing

```bash
# Navigate to project directory
cd agricultural_predictions-

# Create and activate virtual environment (Windows Git Bash)
python -m venv venv
source venv/Scripts/activate

# Install dependencies
pip install -r requirements.txt

# Navigate to FastAPI directory
cd fastapi

# Set up environment variables (create .env file with database URLs)
# DATABASE_URL=your_mysql_connection_string
# MONGO_URL=your_mongodb_connection_string

# Initialize database with data
python data_proces.py

# Start the FastAPI application
uvicorn main:app --reload
```

The application will be available at `http://127.0.0.1:8000`
The link of the deployed API is https://agricultural-predictions.onrender.com
The link to the deployed MySQL instance is https://railway.com/invite/B-W_QqdlI4L

### API Endpoints for Predictions

- **ML Model Predictions**: `POST /predict/ml` - Uses trained machine learning model with database data
- **History Data Predictions**: `GET /predict/history` - Gets history of prediction


## ⛏️ Built With <a name = "tech_stack"></a>

- [MongoDB](https://www.mongodb.com/) - Database
- [FastAPI](https://fastapi.tiangolo.com/) - Server Framework
- [RailWay](https://railway.com/) - MySQL Hosted Database

## ✍️ Authors <a name = "authors"></a>

- Ian Ganza --> MySQL and FastAPI endpoints
- Annabelle Ineza --> Model prediction script and prediction saving to database
- Owen Yhaan --> NoSQL and MongoDB endpoints initialisation and configuration 
