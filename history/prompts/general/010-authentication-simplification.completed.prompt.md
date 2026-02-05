---
id: "010"
title: "Authentication Simplification"
stage: "completed"
date_iso: "2026-01-08"
surface: "agent"
model: "Qwen Code"
feature: "auth-simplification"
branch: "main"
user: "M.R Computers"
command: "Remove authentication complexity for testing"
labels: ["backend", "authentication", "testing", "simplification"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml:
  - "backend/requirements.txt"
  - "backend/src/models/user.py"
  - "backend/src/services/auth.py"
  - "backend/src/api/routes/auth.py"
tests_yaml: []
prompt_text: |
  Remove the authentication logic completely.
  I do NOT want password hashing, bcrypt, passlib, JWT, or any 72-byte password restriction.

  Make signup and login work with plain text passwords for testing only.

  Requirements:

  No password hashing
  No password length limits
  No JWT/token generation
  No auth validation complexity
  Store password as plain text
  Return a simple success response without response_model mismatch
  Ensure /auth/signup and /auth/login do not throw 400/500 errors

  This is for local testing/learning only, not production.
response_text: |
  Successfully simplified the authentication system for testing:

  1. Removed password hashing and bcrypt dependencies
  2. Updated User model to store plain text passwords
  3. Simplified auth service to use plain text comparison
  4. Updated auth routes to work without JWT
  5. Implemented simple success responses
  6. Removed all validation complexity

  The authentication system now works with plain text passwords for testing purposes.
outcome: "Authentication system simplified with plain text passwords for testing"
evaluation: "The system now meets all requirements for local testing with simplified authentication."
---

# Authentication Simplification

## Overview
Successfully simplified the authentication system for local testing/learning purposes by removing all complexity.

## Key Changes Made

### 1. Dependencies (`backend/requirements.txt`)
- Removed bcrypt and passlib dependencies
- Kept essential dependencies for the backend to function

### 2. User Model (`backend/src/models/user.py`)
- Updated to store passwords as plain text instead of hashed
- Removed password validation logic
- Simplified model structure

### 3. Auth Service (`backend/src/services/auth.py`)
- Removed password hashing functions
- Implemented plain text password comparison
- Simplified user authentication and registration
- Removed JWT-related code

### 4. Auth Routes (`backend/src/api/routes/auth.py`)
- Removed JWT token generation and handling
- Implemented simple success responses
- Removed complex response models
- Simplified error handling

## Features Removed
- Password hashing with bcrypt
- JWT token generation and validation
- Complex password validation rules
- 72-byte password restrictions
- Token-based authentication

## Features Added
- Plain text password storage and comparison
- Simple success/error responses
- Minimal validation for testing
- Straightforward signup and login flows

## Result
- ✅ No password hashing
- ✅ No password length limits
- ✅ No JWT/token generation
- ✅ Plain text password storage
- ✅ Simple success responses
- ✅ No 400/500 errors on auth endpoints
- ✅ Ready for local testing/learning