# TypingTester Full-Stack App

This workspace now contains a modern full-stack application with a React frontend and a Java Spring Boot backend. The architecture is designed for a clean separation of concerns, responsive UI, REST-based communication, and MySQL persistence.

## New Project Structure

```
TypingTester/
├── backend/
│   ├── pom.xml
│   ├── .env.example
│   └── src/
│       └── main/
│           ├── java/com/typingtogether/
│           │   ├── TypingTogetherApplication.java
│           │   ├── config/WebConfig.java
│           │   ├── controller/AuthController.java
│           │   ├── controller/RecordController.java
│           │   ├── dto/
│           │   │   ├── ApiResponse.java
│           │   │   ├── AuthResponse.java
│           │   │   ├── LoginRequest.java
│           │   │   ├── RecordRequest.java
│           │   │   └── UserRequest.java
│           │   ├── exception/
│           │   │   ├── ApiExceptionHandler.java
│           │   │   └── ResourceNotFoundException.java
│           │   ├── model/
│           │   │   ├── TypingRecord.java
│           │   │   └── User.java
│           │   ├── repository/
│           │   │   ├── TypingRecordRepository.java
│           │   │   └── UserRepository.java
│           │   ├── service/
│           │   │   ├── AuthService.java
│           │   │   ├── RecordService.java
│           │   │   └── TokenService.java
│           └── resources/
│               └── application.properties
├── frontend/
│   ├── package.json
│   ├── .env.example
│   ├── public/
│   │   └── index.html
│   └── src/
│       ├── App.js
│       ├── index.js
│       ├── styles.css
│       ├── services/api.js
│       ├── utils/validators.js
│       └── components/
│           ├── ContactForm.jsx
│           ├── Dashboard.jsx
│           ├── ErrorMessage.jsx
│           ├── FeatureCards.jsx
│           ├── Footer.jsx
│           ├── Hero.jsx
│           ├── LoadingSpinner.jsx
│           └── NavBar.jsx
├── .gitignore
└── README.md
```

## Backend Setup

1. Install Java 17+ and Maven.
2. Create a MySQL database named `typing_test`.
3. Copy `backend/.env.example` to `backend/.env` and configure the connection settings.

Example `backend/.env`:

```properties
MYSQL_URL=jdbc:mysql://localhost:3306/typing_test?useSSL=false&serverTimezone=UTC
MYSQL_USERNAME=root
MYSQL_PASSWORD=yourpassword
JWT_SECRET=ReplaceWithAStrongSecret
```

4. Start the backend:

```bash
cd backend
mvn clean package
mvn spring-boot:run
```

The API will start at `http://localhost:8080`.

## Frontend Setup

1. Install Node.js 18+.
2. Copy `frontend/.env.example` to `frontend/.env`.
3. Install dependencies and start the client:

```bash
cd frontend
npm install
npm start
```

The React app will run at `http://localhost:3000`.

## Frontend and Backend Connection

The frontend uses the Fetch API and reads the backend base URL from `REACT_APP_API_BASE_URL`.

The server exposes REST endpoints under `/api/*`, including authentication, dashboard, and record management.

### Key API endpoints

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/dashboard`
- `GET /api/records`
- `POST /api/records`
- `PUT /api/records/{id}`
- `DELETE /api/records/{id}`

### Example request flow

1. The user registers or signs in.
2. Backend validates credentials and returns a JWT token.
3. React stores the token in `localStorage`.
4. Frontend sends `Authorization: Bearer <token>` on protected requests.
5. Backend validates the token and returns JSON data.

## API Example

### Register

```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "tester",
  "email": "tester@example.com",
  "password": "StrongPassword123"
}
```

### Login

```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "tester@example.com",
  "password": "StrongPassword123"
}
```

### Dashboard

```http
GET /api/dashboard
Authorization: Bearer <token>
```

## Notes

- Backend uses MVC architecture with service and controller layers.
- Frontend uses reusable React components and handles loading, validation, and API errors.
- Environment variables secure database credentials and JWT settings.
- CORS is configured so the React frontend can safely talk to the backend.
