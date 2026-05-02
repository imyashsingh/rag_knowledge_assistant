#!/usr/bin/env python3
"""
Comprehensive API Testing Script for DocuMind RAG Knowledge Assistant

This script tests all API endpoints to ensure they work correctly.
It can be run with or without a running server.
"""

import asyncio
import json
import os
import sys
import time
from typing import Dict, Any, Optional
import httpx
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class APITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.Client(timeout=30.0)
        self.auth_token = None
        self.test_results = []

    def log_test(self, test_name: str, status: str, details: str = ""):
        """Log test results"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": time.time()
        }
        self.test_results.append(result)
        status_symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_symbol} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")

    def test_connection(self):
        """Test basic server connection"""
        try:
            response = self.client.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Server Connection", "PASS",
                              f"API Version: {data.get('version')}")
                return True
            else:
                self.log_test("Server Connection", "FAIL",
                              f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Server Connection", "FAIL", str(e))
            return False

    def test_health_endpoints(self):
        """Test all health check endpoints"""
        health_endpoints = [
            ("/api/v1/health/", "Comprehensive Health Check"),
            ("/api/v1/health/simple", "Simple Health Check"),
            ("/api/v1/health/ready", "Readiness Check"),
            ("/api/v1/health/live", "Liveness Check")
        ]

        for endpoint, name in health_endpoints:
            try:
                response = self.client.get(f"{self.base_url}{endpoint}")
                if response.status_code == 200:
                    self.log_test(
                        name, "PASS", f"Status: {response.status_code}")
                else:
                    self.log_test(
                        name, "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(name, "FAIL", str(e))

    def test_authentication_flow(self):
        """Test complete authentication flow"""
        # Test user registration
        try:
            user_data = {
                "email": "test@example.com",
                "password": "testpassword123"
            }
            response = self.client.post(
                f"{self.base_url}/api/v1/auth/register", json=user_data)

            if response.status_code in [200, 201]:
                token_data = response.json()
                self.auth_token = token_data.get("access_token")
                self.log_test("User Registration", "PASS",
                              "User registered successfully")
            elif response.status_code == 400 and "already exists" in response.text:
                # User might already exist, try login
                self.log_test("User Registration", "SKIP",
                              "User already exists")
            else:
                self.log_test("User Registration", "FAIL",
                              f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("User Registration", "FAIL", str(e))
            return False

        # Test user login
        try:
            login_data = {
                "email": "test@example.com",
                "password": "testpassword123"
            }
            response = self.client.post(
                f"{self.base_url}/api/v1/auth/login", json=login_data)

            if response.status_code == 200:
                token_data = response.json()
                self.auth_token = token_data.get("access_token")
                self.log_test("User Login", "PASS", "Login successful")
                return True
            else:
                self.log_test("User Login", "FAIL",
                              f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("User Login", "FAIL", str(e))
            return False

    def test_protected_endpoints(self):
        """Test endpoints that require authentication"""
        if not self.auth_token:
            self.log_test("Protected Endpoints", "SKIP",
                          "No auth token available")
            return

        headers = {"Authorization": f"Bearer {self.auth_token}"}

        # Test getting current user info
        try:
            response = self.client.get(
                f"{self.base_url}/api/v1/auth/me", headers=headers)
            if response.status_code == 200:
                self.log_test("Get Current User", "PASS",
                              "User info retrieved")
            else:
                self.log_test("Get Current User", "FAIL",
                              f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("Get Current User", "FAIL", str(e))

        # Test token refresh
        try:
            # Simplified for testing
            refresh_data = {"refresh_token": self.auth_token}
            response = self.client.post(
                f"{self.base_url}/api/v1/auth/refresh", json=refresh_data)
            if response.status_code == 200:
                self.log_test("Token Refresh", "PASS", "Token refreshed")
            else:
                self.log_test("Token Refresh", "FAIL",
                              f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Token Refresh", "FAIL", str(e))

        # Test logout
        try:
            response = self.client.post(
                f"{self.base_url}/api/v1/auth/logout", headers=headers)
            if response.status_code == 200:
                self.log_test("User Logout", "PASS", "Logout successful")
            else:
                self.log_test("User Logout", "FAIL",
                              f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("User Logout", "FAIL", str(e))

    def test_document_endpoints(self):
        """Test document management endpoints"""
        if not self.auth_token:
            self.log_test("Document Endpoints", "SKIP",
                          "No auth token available")
            return

        headers = {"Authorization": f"Bearer {self.auth_token}"}

        # Test document listing
        try:
            response = self.client.get(
                f"{self.base_url}/api/v1/documents/", headers=headers)
            if response.status_code == 200:
                self.log_test("List Documents", "PASS",
                              f"Documents retrieved: {len(response.json())}")
            else:
                self.log_test("List Documents", "FAIL",
                              f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("List Documents", "FAIL", str(e))

        # Test document upload (create a sample file)
        try:
            sample_content = "This is a test document for API testing."
            files = {"file": ("test.txt", sample_content, "text/plain")}
            data = {"title": "Test Document"}

            response = self.client.post(
                f"{self.base_url}/api/v1/documents/upload",
                headers=headers,
                files=files,
                data=data
            )

            if response.status_code in [200, 201]:
                doc_data = response.json()
                doc_id = doc_data.get("id")
                self.log_test("Document Upload", "PASS",
                              f"Document ID: {doc_id}")

                # Test document retrieval
                if doc_id:
                    try:
                        response = self.client.get(
                            f"{self.base_url}/api/v1/documents/{doc_id}", headers=headers)
                        if response.status_code == 200:
                            self.log_test("Get Document", "PASS",
                                          f"Document retrieved: {doc_id}")
                        else:
                            self.log_test("Get Document", "FAIL",
                                          f"Status: {response.status_code}")
                    except Exception as e:
                        self.log_test("Get Document", "FAIL", str(e))
            else:
                self.log_test("Document Upload", "FAIL",
                              f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Document Upload", "FAIL", str(e))

    def test_chat_endpoints(self):
        """Test chat/RAG endpoints"""
        if not self.auth_token:
            self.log_test("Chat Endpoints", "SKIP", "No auth token available")
            return

        headers = {"Authorization": f"Bearer {self.auth_token}"}

        # Test chat query
        try:
            query_data = {
                "query": "What is this system about?",
                "max_sources": 5
            }
            response = self.client.post(
                f"{self.base_url}/api/v1/chat/query", json=query_data, headers=headers)

            if response.status_code == 200:
                self.log_test("Chat Query", "PASS",
                              "Query processed successfully")
            else:
                self.log_test("Chat Query", "FAIL",
                              f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Chat Query", "FAIL", str(e))

        # Test workspace stats
        try:
            response = self.client.get(
                f"{self.base_url}/api/v1/chat/stats", headers=headers)
            if response.status_code == 200:
                self.log_test("Chat Stats", "PASS", "Stats retrieved")
            else:
                self.log_test("Chat Stats", "FAIL",
                              f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Chat Stats", "FAIL", str(e))

        # Test cache clearing
        try:
            response = self.client.post(
                f"{self.base_url}/api/v1/chat/clear-cache", headers=headers)
            if response.status_code == 200:
                self.log_test("Clear Cache", "PASS", "Cache cleared")
            else:
                self.log_test("Clear Cache", "FAIL",
                              f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Clear Cache", "FAIL", str(e))

    def test_error_handling(self):
        """Test error handling and edge cases"""
        # Test invalid endpoint
        try:
            response = self.client.get(f"{self.base_url}/api/v1/invalid")
            if response.status_code == 404:
                self.log_test("404 Error Handling", "PASS",
                              "Correct 404 response")
            else:
                self.log_test("404 Error Handling", "FAIL",
                              f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_test("404 Error Handling", "FAIL", str(e))

        # Test invalid auth
        try:
            headers = {"Authorization": "Bearer invalid_token"}
            response = self.client.get(
                f"{self.base_url}/api/v1/auth/me", headers=headers)
            if response.status_code in [401, 403]:
                self.log_test("Invalid Auth Handling",
                              "PASS", "Correct auth error")
            else:
                self.log_test("Invalid Auth Handling", "FAIL",
                              f"Expected 401/403, got {response.status_code}")
        except Exception as e:
            self.log_test("Invalid Auth Handling", "FAIL", str(e))

        # Test invalid data
        try:
            response = self.client.post(
                f"{self.base_url}/api/v1/auth/login", json={"invalid": "data"})
            if response.status_code == 422:
                self.log_test("Validation Error Handling",
                              "PASS", "Correct validation error")
            else:
                self.log_test("Validation Error Handling", "FAIL",
                              f"Expected 422, got {response.status_code}")
        except Exception as e:
            self.log_test("Validation Error Handling", "FAIL", str(e))

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Comprehensive API Testing for DocuMind")
        print("=" * 60)

        # Test basic connection first
        if not self.test_connection():
            print("\n❌ Server is not running. Please start the server first:")
            print("   uvicorn app.main:app --host 0.0.0.0 --port 8000")
            return False

        print("\n📊 Testing Health Check Endpoints...")
        self.test_health_endpoints()

        print("\n🔐 Testing Authentication Flow...")
        if self.test_authentication_flow():
            print("\n🛡️ Testing Protected Endpoints...")
            self.test_protected_endpoints()

            print("\n📄 Testing Document Management...")
            self.test_document_endpoints()

            print("\n💬 Testing Chat/RAG Functionality...")
            self.test_chat_endpoints()

        print("\n🚨 Testing Error Handling...")
        self.test_error_handling()

        return self.generate_report()

    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 60)
        print("📋 TEST REPORT")
        print("=" * 60)

        passed = len([r for r in self.test_results if r["status"] == "PASS"])
        failed = len([r for r in self.test_results if r["status"] == "FAIL"])
        skipped = len([r for r in self.test_results if r["status"] == "SKIP"])
        total = len(self.test_results)

        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️ Skipped: {skipped}")
        print(
            f"Success Rate: {(passed/total*100):.1f}%" if total > 0 else "N/A")

        if failed > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"   - {result['test']}: {result['details']}")

        # Save detailed report
        report_file = "api_test_report.json"
        with open(report_file, "w") as f:
            json.dump(self.test_results, f, indent=2)
        print(f"\n📄 Detailed report saved to: {report_file}")

        return failed == 0


def main():
    """Main function to run tests"""
    import argparse

    parser = argparse.ArgumentParser(description="Test DocuMind API endpoints")
    parser.add_argument("--url", default="http://localhost:8000",
                        help="Base URL for API testing")
    parser.add_argument("--quick", action="store_true",
                        help="Run quick tests only")

    args = parser.parse_args()

    tester = APITester(base_url=args.url)

    if args.quick:
        print("🚀 Running Quick API Tests...")
        if tester.test_connection():
            tester.test_health_endpoints()
            tester.test_error_handling()
        tester.generate_report()
    else:
        success = tester.run_all_tests()

        if success:
            print("\n🎉 All tests completed successfully!")
            sys.exit(0)
        else:
            print("\n⚠️ Some tests failed. Check the report above.")
            sys.exit(1)


if __name__ == "__main__":
    main()
