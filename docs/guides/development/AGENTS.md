# agents.md

## Overview

This file defines the agents needed to build a fantasy football player recommendation app. Each agent has specific responsibilities and expertise.

---

## Agent 1: Backend Architect

**Role**: Design and build the Python backend

**Responsibilities**:

- Set up Flask or FastAPI backend for Heroku deployment
- Integrate the API from instructions.md
- Create endpoints for player data, weather analysis, and matchup calculations
- Build the percentage calculator logic
- Handle data processing for AI grading systems
- Design database schema for caching player stats and user preferences
- Implement error handling and rate limiting for API calls

**Deliverables**:

- Backend server ready for Heroku deployment
- API documentation for frontend integration
- Environment configuration files

---

## Agent 2: Frontend Developer

**Role**: Build the user interface with React and shadcn

**Responsibilities**:

- Create responsive layouts for player selection
- Build components using shadcn UI library
- Design player comparison cards showing matchup data
- Implement interactive grading visualizations
- Create weather condition displays
- Build forms for user input and filters
- Connect all components to backend endpoints
- Optimize for mobile and desktop views

**Deliverables**:

- Complete UI components
- Responsive design across devices
- Smooth user interactions

---

## Agent 3: Data Analysis Engineer

**Role**: Build calculation and analysis features

**Responsibilities**:

- Create percentage calculators for player performance predictions
- Build defense matchup rating system
- Design weather impact algorithms
- Calculate historical performance metrics
- Create comparison logic between players
- Build scoring projection models
- Generate confidence intervals for recommendations

**Deliverables**:

- Working calculation functions
- Performance metrics dashboard
- Data transformation pipelines

---

## Agent 4: AI/ML Specialist

**Role**: Implement AI grading and prediction systems

**Responsibilities**:

- Build AI analysis models for player evaluation
- Create grading scales based on multiple factors
- Train models on historical performance data
- Implement prediction algorithms for weekly performance
- Design confidence scoring system
- Build recommendation engine that weighs all factors
- Validate model accuracy

**Deliverables**:

- Trained AI models
- Grading system implementation
- Player recommendation algorithm

---

## Agent 5: DevOps Engineer

**Role**: Handle deployment and infrastructure

**Responsibilities**:

- Configure Heroku deployment pipeline
- Set up environment variables and secrets
- Configure database connections
- Set up logging and monitoring
- Create deployment scripts
- Configure auto-scaling if needed
- Set up CI/CD pipeline
- Handle API key management from instructions.md

**Deliverables**:

- Deployed application on Heroku
- Deployment documentation
- Monitoring setup

---

## Tech Stack

**Backend**: Python with Flask/FastAPI
**Frontend**: React with shadcn components
**Database**: PostgreSQL (Heroku add-on)
**Deployment**: Heroku
**API**: Custom API defined in instructions.md

---

## Workflow

1. Backend Architect reads instructions.md and builds API integration
2. Data Analysis Engineer creates calculation functions
3. AI/ML Specialist builds grading models
4. Frontend Developer creates UI consuming backend endpoints
5. DevOps Engineer deploys to Heroku
6. All agents iterate based on testing feedback

---

## Communication Protocol

Each agent should:

- Document all code and decisions
- Test thoroughly before handoff
- Provide clear integration instructions
- Flag blocking issues immediately
- Review instructions.md for API requirements
