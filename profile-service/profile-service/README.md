# MatchTal Profile Service

Candidate Profile and Resume Management Microservice for the MatchTal AI Recruitment Platform.

## Overview

This microservice handles candidate profile management and resume metadata for the MatchTal platform. It provides endpoints for candidates to create and manage their profiles, and for recruiters/admins to view and search candidate profiles within their organization.

## Tech Stack

- **Framework**: FastAPI (Python 3.11+)
- **Database**: MongoDB (via Motor async driver)
- **Authentication**: JWT tokens from auth-service
- **File Storage**: S3 (for resume files - integration stubbed)
- **Deployment**: Docker, AWS ECS Fargate
- **CI/CD**: GitHub Actions

## Features

- ✅ Candidate profile creation and management
- ✅ Profile fields: personal info, skills, experience, education
- ✅ Resume metadata management (file upload stubbed for S3 integration)
- ✅ JWT-based authentication integration with auth-service
- ✅ Role-based access control (candidates edit own, recruiters/admins view org profiles)
- ✅ Profile search and filtering (by skills, location, etc.)
- ✅ Organization-based data isolation
- ✅ Comprehensive input validation
- ✅ Health check endpoints
- ✅ Automatic API documentation (Swagger/OpenAPI)
- ✅ Docker containerization
- ✅ AWS deployment ready

## Project Structure

```
profile-service/
├── src/
│   ├── api/
│   │   └── v1/
│   │       └── routes/
│   │           ├── profiles.py          # Profile endpoints
│   │           └── resumes.py            # Resume metadata endpoints
│   ├── config/
│   │   ├── database.py                   # MongoDB connection
│   │   └── settings.py                  # Application settings
│   ├── middleware/
│   │   ├── auth.py                       # JWT authentication middleware
│   │   └── rate_limiter.py              # Rate limiting
│   ├── models/
│   │   ├── profile.py                    # Profile model and schemas
│   │   └── resume.py                    # Resume metadata model
│   ├── utils/
│   │   ├── jwt.py                        # JWT token verification
│   │   └── logger.py                    # Logging configuration
│   └── main.py                          # FastAPI application
├── tests/
│   ├── test_profiles.py                  # Profile endpoint tests
│   └── test_resumes.py                   # Resume endpoint tests
├── aws/
│   ├── task-definition.json              # ECS task definition
│   └── cloudformation-template.yaml      # AWS infrastructure
├── .github/
│   └── workflows/
│       └── ci-cd.yml                    # CI/CD pipeline
├── docker-compose.yml                    # Local development setup
├── Dockerfile                            # Docker image definition
├── requirements.txt                      # Production dependencies
├── requirements-dev.txt                  # Development dependencies
└── README.md                             # This file
```

## Getting Started

### Prerequisites

- Python 3.11 or higher
- MongoDB 7.0 or higher
- Docker and Docker Compose (for containerized setup)
- AWS CLI (for deployment)
- Auth-service running (for JWT token validation)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd profile-service
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Set up environment variables**
   Create a `.env` file:
   ```env
   ENVIRONMENT=development
   PORT=8001
   MONGODB_URI=mongodb://localhost:27017
   MONGODB_DATABASE=matchtal_profiles
   JWT_SECRET_KEY=your-jwt-secret-key-shared-with-auth-service
   JWT_ALGORITHM=HS256
   AUTH_SERVICE_URL=http://localhost:8000
   S3_BUCKET_NAME=matchtal-resumes-dev
   ```

5. **Start MongoDB (using Docker)**
   ```bash
   docker-compose up mongodb -d
   ```

6. **Run the application**
   ```bash
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8001
   ```

   Or using Docker Compose:
   ```bash
   docker-compose up
   ```

7. **Access the API**
   - API: http://localhost:8001
   - API Documentation: http://localhost:8001/docs
   - ReDoc: http://localhost:8001/redoc
   - Health Check: http://localhost:8001/health

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_profiles.py
```

## API Endpoints

### Profiles

- `POST /api/v1/profiles` - Create a new candidate profile (candidate only)
- `GET /api/v1/profiles/{profile_id}` - Get profile by ID
- `GET /api/v1/profiles` - List profiles with filters (skills, location, etc.)
- `PUT /api/v1/profiles/{profile_id}` - Update profile
- `GET /api/v1/profiles/user/{user_id}` - Get profile by user ID

### Resume Metadata

- `POST /api/v1/resumes` - Create resume metadata (file upload stubbed)
- `GET /api/v1/resumes/{resume_id}` - Get resume metadata by ID
- `GET /api/v1/resumes` - List resume metadata with filters
- `PUT /api/v1/resumes/{resume_id}` - Update resume metadata
- `DELETE /api/v1/resumes/{resume_id}` - Soft delete resume metadata

### Health Check

- `GET /health` - Health check endpoint

## Authentication & Authorization

All endpoints require JWT authentication via Bearer token in the Authorization header.

### Role-Based Access

- **Candidates**: Can create, update, and view only their own profile and resumes
- **Recruiters**: Can view and search profiles within their organization
- **Employer Admins**: Can view and search all profiles in their organization

### Example Request

```bash
curl -X GET "http://localhost:8001/api/v1/profiles" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Data Models

### Profile Schema

```json
{
  "userId": "string",
  "firstName": "string",
  "lastName": "string",
  "email": "string",
  "phone": "string (optional)",
  "location": "string (optional)",
  "summary": "string (optional)",
  "skills": ["string"],
  "experience": [
    {
      "company": "string",
      "position": "string",
      "startDate": "YYYY-MM",
      "endDate": "YYYY-MM (optional)",
      "isCurrent": "boolean",
      "description": "string (optional)"
    }
  ],
  "education": [
    {
      "institution": "string",
      "degree": "string",
      "fieldOfStudy": "string (optional)",
      "startDate": "YYYY-MM",
      "endDate": "YYYY-MM (optional)",
      "gpa": "number (optional)"
    }
  ],
  "linkedInUrl": "string (optional)",
  "portfolioUrl": "string (optional)",
  "githubUrl": "string (optional)"
}
```

### Resume Metadata Schema

```json
{
  "profileId": "string",
  "fileName": "string",
  "fileSize": "number",
  "mimeType": "string",
  "s3Key": "string (optional)",
  "s3Bucket": "string (optional)",
  "isActive": "boolean",
  "isPrimary": "boolean",
  "notes": "string (optional)"
}
```

## Environment Variables

Key environment variables:

- `MONGODB_URI`: MongoDB connection string
- `JWT_SECRET_KEY`: Secret key for JWT token validation (must match auth-service)
- `JWT_ALGORITHM`: JWT algorithm (default: HS256)
- `AUTH_SERVICE_URL`: URL of the auth-service (for future token validation calls)
- `S3_BUCKET_NAME`: S3 bucket for resume storage
- `ENVIRONMENT`: Environment (development/staging/production)

## Docker Deployment

### Build Image

```bash
docker build -t matchtal-profile-service:latest .
```

### Run Container

```bash
docker run -p 8001:8001 \
  -e MONGODB_URI=mongodb://host.docker.internal:27017 \
  -e JWT_SECRET_KEY=your-secret-key \
  matchtal-profile-service:latest
```

## AWS Deployment

### Prerequisites

1. AWS CLI configured with appropriate credentials
2. ECR repository created
3. ECS cluster created (shared with auth-service)
4. VPC and subnets configured
5. Secrets stored in AWS Secrets Manager
6. S3 bucket created for resume storage

### Deploy Infrastructure

1. **Create ECR Repository**
   ```bash
   aws ecr create-repository --repository-name matchtal/profile-service
   ```

2. **Store Secrets in Secrets Manager**
   ```bash
   aws secretsmanager create-secret \
     --name matchtal/mongodb-uri \
     --secret-string "mongodb://your-connection-string"
   
   aws secretsmanager create-secret \
     --name matchtal/jwt-secret \
     --secret-string "your-jwt-secret-key"
   ```

3. **Deploy CloudFormation Stack**
   ```bash
   aws cloudformation create-stack \
     --stack-name matchtal-profile-service \
     --template-body file://aws/cloudformation-template.yaml \
     --parameters ParameterKey=VpcId,ParameterValue=vpc-xxx \
                  ParameterKey=SubnetIds,ParameterValue=subnet-xxx,subnet-yyy \
                  ParameterKey=MongoDBUri,ParameterValue=mongodb://... \
                  ParameterKey=JWTSecretKey,ParameterValue=your-secret \
                  ParameterKey=S3BucketName,ParameterValue=matchtal-resumes \
     --capabilities CAPABILITY_NAMED_IAM
   ```

4. **Build and Push Docker Image**
   ```bash
   # Get ECR login
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
   
   # Build and tag
   docker build -t matchtal/profile-service:latest .
   docker tag matchtal/profile-service:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/matchtal/profile-service:latest
   
   # Push
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/matchtal/profile-service:latest
   ```

5. **Update ECS Service**
   ```bash
   aws ecs update-service \
     --cluster matchtal-cluster \
     --service profile-service \
     --force-new-deployment
   ```

## CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/ci-cd.yml`) automatically:

1. Runs tests on every push/PR
2. Builds and pushes Docker image to ECR on push to main/develop
3. Deploys to ECS on push to main branch

### Required GitHub Secrets

- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key

## Integration with Auth Service

The profile-service validates JWT tokens issued by the auth-service using a shared secret key. The token payload should include:

- `sub` or `userId`: User ID
- `email`: User email
- `role`: User role (candidate/recruiter/employer_admin)
- `organizationId`: Organization ID (for recruiters/admins)
- `isActive`: User active status

## Future Enhancements

- [ ] S3 integration for actual resume file uploads
- [ ] Resume parsing and skill extraction
- [ ] Profile completeness scoring
- [ ] Advanced search with full-text indexing
- [ ] Profile versioning/history
- [ ] Integration with matching-service for candidate-job matching

## Security Considerations

- JWT tokens validated with shared secret from auth-service
- Role-based access control enforced at endpoint level
- Organization-based data isolation
- Input validation on all endpoints
- Secrets stored in AWS Secrets Manager (production)
- Rate limiting on all endpoints

## Monitoring

- Health check endpoint: `/health`
- CloudWatch logs: `/ecs/matchtal-profile-service`
- Application logs in JSON format

## Contributing

1. Create a feature branch
2. Make your changes
3. Add tests
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License

## Support

For issues and questions, please open an issue in the repository.





