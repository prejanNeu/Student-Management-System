#!/usr/bin/env python3
"""
Test script for the Student Management System APIs
Run this script to test the various API endpoints
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"  # Change this to your Django server URL
AUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU2ODExMzIwLCJpYXQiOjE3NTY4MDgzMjAsImp0aSI6IjQwNGJiMDkzZjQ1MTRhZDc4ZmM3N2JhYjY5ZGZiNjAwIiwidXNlcl9pZCI6OX0.kGIh3Um0Rm0hiBFxe18KNumd4E6_go1NcbxXGgyqcxg"  # Replace with actual token

# Headers for authenticated requests
HEADERS = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json"
}

def test_get_exam_types():
    """Test getting all exam types"""
    print("Testing GET /api/exam-types/")
    try:
        response = requests.get(f"{BASE_URL}/api/exam-types/", headers=HEADERS)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")
    print("-" * 50)

def test_add_exam_type():
    """Test adding a new exam type"""
    print("Testing POST /api/exam-types/add/")
    try:
        data = {"name": "Final Term"}
        response = requests.post(
            f"{BASE_URL}/api/exam-types/add/", 
            headers=HEADERS, 
            json=data
        )
        print(f"Status Code: {response.status_code}")
        if response.status_code == 201:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")
    print("-" * 50)

def test_add_marks():
    """Test adding marks"""
    print("Testing POST /api/marks/add/")
    try:
        data = {
            "student_id": 1,
            "subject_id": 1,
            "classlevel_id": 1,
            "examtype_id": 1,
            "full_marks": 100.00,
            "marks": 85.50
        }
        response = requests.post(
            f"{BASE_URL}/api/marks/add/", 
            headers=HEADERS, 
            json=data
        )
        print(f"Status Code: {response.status_code}")
        if response.status_code == 201:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")
    print("-" * 50)

def test_get_marks():
    """Test getting all marks"""
    print("Testing GET /api/marks/")
    try:
        response = requests.get(f"{BASE_URL}/api/marks/", headers=HEADERS)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")
    print("-" * 50)

def test_get_marks_by_class():
    """Test getting marks by class level"""
    print("Testing GET /api/marks/class/1/")
    try:
        response = requests.get(f"{BASE_URL}/api/marks/class/1/", headers=HEADERS)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")
    print("-" * 50)

def test_update_marks():
    """Test updating marks"""
    print("Testing PUT /api/marks/update/1/")
    try:
        data = {"marks": 90.00}
        response = requests.put(
            f"{BASE_URL}/api/marks/update/1/", 
            headers=HEADERS, 
            json=data
        )
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")
    print("-" * 50)

def test_get_mark_detail():
    """Test getting mark details"""
    print("Testing GET /api/marks/1/")
    try:
        response = requests.get(f"{BASE_URL}/api/marks/1/", headers=HEADERS)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")
    print("-" * 50)

def test_performance_stats():
    """Test getting performance statistics"""
    print("Testing GET /api/performance/1/")
    try:
        response = requests.get(f"{BASE_URL}/api/performance/1/", headers=HEADERS)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")
    print("-" * 50)

def main():
    """Run all tests"""
    print("Student Management System API Tests")
    print("=" * 50)
    
    # Test exam type APIs
    test_get_exam_types()
    test_add_exam_type()
    
    # Test marks APIs
    test_add_marks()
    test_get_marks()
    test_get_marks_by_class()
    test_get_mark_detail()
    test_update_marks()
    
    # Test performance API
    test_performance_stats()
    
    print("All tests completed!")

if __name__ == "__main__":
    main() 