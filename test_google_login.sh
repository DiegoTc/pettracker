#!/bin/bash

# Test if the Google OAuth login endpoint works
echo "Testing login endpoint..."
curl -X GET http://localhost:5000/api/auth/login/ -H "Accept: application/json" -v