# House Price Prediction Backend API

This backend exposes a REST API for predicting house prices using a pre-trained machine learning model (`model.joblib`).

# Task 1 - User CRUD

## Step 0: Environment Setup
- Installed Python 3.9.13
- Created virtual environment
- Installed dependencies using `pip install -r requirements.txt`

## Step 1: Project Structure (Layered Architecture)

I organized the backend using a layered architecture for clarity and scalability:

```text
backend_assignment/
│
├── app/
│   ├── controllers/
│   │   ├── auth_controller.py
│   │   ├── user_controller.py
│   │   └── prediction_controller.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── db.py
│   │
│   ├── dtos/
│   │   ├── user.py
│   │   └── prediction_dto.py
│   │
│   ├── entities/
│   │   ├── user.py
│   │   └── prediction.py
│   │
│   ├── repositories/
│   │   ├── user_repository.py
│   │   └── prediction_repository.py
│   │
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   └── prediction_service.py
│   │
│   ├── main.py
│   └── router.py
│
├── model.joblib
├── housing.csv
│
├── requirements.txt
├── Dockerfile                    # (To be completed in upcoming tasks)
├── docker-compose.yml            # (To be completed in upcoming tasks)
│
└── tests/
    ├── conftest.py
    ├── test_users.py
    └── test_prediction.py


```

This structure ensures:
- Controllers handle only HTTP request/response
- Services contain the core business logic
- Repositories provide abstracted database operations
- Entities represent clean domain models
- DTOs validate and shape request/response data
- Core manages configuration and shared utilities

## Step 2: User Authentication & CRUD

### Implemented Endpoints

| Operation            | Method   | Endpoint                                       | Description                         |
|--------------------- |--------- |----------------------------------------------- |-------------------------------------|
| Register user        | `POST`   | `/api-deutsche/auth/register`                  | Creates a user with hashed password |
| Login user           | `POST`   | `/api-deutsche/auth/login`                     | Validates credentials               |
| Change password      | `PATCH`  | `/api-deutsche/auth/change-password/{id}`      | User updates their own password     |
| Admin reset password | `PATCH`  | `/api-deutsche/auth/admin/reset-password/{id}` | Admin resets a password             |
| Get all users        | `GET`    | `/api-deutsche/users`                          | Returns a list of all users         |
| Get user by id       | `GET`    | `/api-deutsche/users/{id}`                     | Returns a user                      |
| Update username      | `PATCH`  | `/api-deutsche/users/{id}`                     | Updates username                    |
| Delete user          | `DELETE` | `/api-deutsche/users/{id}`                     | Deletes a single user               |
| Delete all users     | `DELETE` | `/api-deutsche/users`                          | Removes all users                   |


### Password Security 
- Passwords are hashed using Passlib + bcrypt before storage.

# Task 2 - JWT Authentication & Rate Limiting

In this task, I enhanced the security layer of the API by replacing the simple username-password login flow with JWT-based authentication and adding rate limiting to protect against brute-force login attempts.

## Step 0: JWT Access Token Login

- When a user logs in, the server now generates a JWT token containing the username and user ID.
- The token is signed using SECRET_KEY and has a configurable expiration time.
- The client must include the token in all protected requests using: `Authorization: Bearer <access_token>`

## Step 1: Rate Limiting for Login

- The `/api-deutsche/auth/login` endpoint is limited to 10 login attempts per minute per username.
- This prevents brute-force attacks and ensures secure authentication behavior. 
- When the limit is exceeded, the server returns `429 Too Many Requests`.
 
# Task 3 - Predictions (protected)

In this task, I added support for running price predictions using the provided `model.joblib`, and storing each prediction in the database together with the user who generated it.

| DTO                  | Purpose                                                                             |
| -------------------- | ----------------------------------------------------------------------------------- |
| **PredictionInput**  | Validates and structures the input features required for prediction.                |
| **PredictionOutput** | Defines what is returned after a prediction: the predicted price and prediction ID. |
| **PredictionRead**   | Used for returning stored past predictions per user.                                |



- Prediction API (protected via JWT):
  
- - `POST /api-deutsche/predict` - run a prediction and store it
- - `GET /api-deutsche/predict` - list predictions for the authenticated user

Model Input Encoding

The model expects exactly 13 features in the same order it was originally trained. Therefore, the categorical field ocean_proximity is one-hot encoded using a fixed category ordering:

| Type                    | Features                                                                                                                    |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| Numeric (8)             | `longitude`, `latitude`, `housing_median_age`, `total_rooms`, `total_bedrooms`, `population`, `households`, `median_income` |
| One-hot categorical (5) | one element set to `1`, the others `0`, based on `ocean_proximity` category                                                 |


# Task 4 - Docker

| Action                  | Command                                 | Notes                                     |
| ----------------------- | --------------------------------------- | ----------------------------------------- |
| Run tests inside Docker | `docker compose run --rm api pytest -q` | Uses the same environment as production   |
| Start the application   | `docker compose up -d --build`          | Builds and launches both API + PostgreSQL |


Resulting Containers

When the application is running, Docker will create the following containers:

| Container          | Description                                           |
| ------------------ | ----------------------------------------------------- |
| `house-price-api`  | The FastAPI backend service                           |
| `house-price-db`   | PostgreSQL database                                   |
| `house-price-test` | (Optional) used only when running tests inside Docker |
