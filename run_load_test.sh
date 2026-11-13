#!/bin/bash
# Run locust with 50 users and a spawn rate of 10
# Assumes the FastAPI service is running on http://localhost:8000
locust -f locustfile.py --users 50 --spawn-rate 10 --host http://localhost:8000
