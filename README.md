# House Price Prediction Backend API

This backend exposes a REST API for predicting house prices using a pre-trained machine learning model (`model.joblib`).

# Task 1

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
│   │   └── user_controller.py
│   │
│   ├── core/                     
│   │   ├── config.py
│   │   └── db.py
│   │
│   ├── dtos/                     
│   │   └── user.py
│   │
│   ├── entities/                 
│   │   └── user.py
│   │
│   ├── repositories/             
│   │   └── user_repository.py
│   │
│   ├── services/                 
│   │   ├── auth_service.py
│   │   └── user_service.py
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
    └── test_users.py

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
