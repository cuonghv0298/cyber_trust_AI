from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from cnav.api.v1 import questions, organizations, provisions, mappings, self_assessment_answers

# Create FastAPI app instance
app = FastAPI(
    title="CNAV API",
    description="API for Questions, Organizations, Provisions, and Self-Assessment Answers management",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js development server
        "http://127.0.0.1:3000",  # Alternative localhost
        "https://your-production-domain.com",  # Add your production domain here
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Include routers
app.include_router(questions.router, prefix="/api/v1/questions", tags=["questions"])
app.include_router(organizations.router, prefix="/api/v1/organizations", tags=["organizations"])
app.include_router(provisions.router, prefix="/api/v1/provisions", tags=["provisions"])
app.include_router(self_assessment_answers.router, prefix="/api/v1/self-assessment-answers", tags=["self-assessment-answers"])
app.include_router(mappings.router, prefix="/api/v1", tags=["mappings"])  # Keep mappings as is since it's cross-resource

@app.get("/")
async def root():
    return {"message": "Welcome to CNAV API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
