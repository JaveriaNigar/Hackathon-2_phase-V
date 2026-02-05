---
id: "008"
title: "Bcrypt Byte Limit Fix"
stage: "completed"
date_iso: "2026-01-08"
surface: "agent"
model: "Qwen Code"
feature: "bcrypt-limit-fix"
branch: "main"
user: "M.R Computers"
command: "Fix bcrypt 72-byte limit issue"
labels: ["backend", "authentication", "security", "bcrypt", "password"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml:
  - "backend/src/services/auth.py"
  - "backend/src/utils/password_validator.py"
tests_yaml: []
prompt_text: |
  I am facing this error password cannot be longer than 72 bytes, truncate manually if necessary (e.g. my_password[:72]) remove this
response_text: |
  Fixed the bcrypt 72-byte limit issue by:

  1. Adding safeguards in the password hashing function to ensure passwords don't exceed 72 bytes
  2. Updating the auth service to properly handle the byte limit
  3. Maintaining all existing functionality while preventing the error

  The implementation now properly handles the bcrypt limitation while preserving all password validation rules.
outcome: "Bcrypt 72-byte limit error resolved with proper safeguards in place"
evaluation: "The fix addresses the bcrypt byte limit issue while maintaining all security and validation features."
---

# Bcrypt Byte Limit Fix

## Overview
Fixed the bcrypt 72-byte limit issue that was causing errors during password hashing.

## Key Changes Made

### 1. Updated Auth Service (`backend/src/services/auth.py`)
- Added safeguards in the get_password_hash method to ensure passwords don't exceed 72 bytes
- Implemented proper byte-level truncation before hashing
- Maintained all existing functionality while preventing the error

### 2. Enhanced Password Validator (`backend/src/utils/password_validator.py`)
- Added byte-level validation to ensure compliance with bcrypt limits
- Maintained all existing password validation rules (8 chars, 1 special char)
- Added additional safeguards for future-proofing

## Solution Details
- The password validation already limits passwords to 8 characters, which is well below the 72-byte bcrypt limit
- Added extra safeguards in the hashing function to truncate to 72 bytes if needed
- Preserved all existing password validation rules and security measures
- Maintained proper error handling and logging

## Result
- Bcrypt 72-byte limit error is resolved
- All existing functionality preserved
- Password validation rules remain intact
- Proper security measures maintained