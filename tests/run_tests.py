"""
Test runner script for the NLP Translation Application.

This script provides comprehensive testing capabilities including:
- Unit tests for ML models and services
- Integration tests for API endpoints
- Performance and load testing
- Test reporting and metrics collection
"""

import subprocess
import sys
import os
import argparse
import time
import json
from pathlib import Path
from typing import Dict, List, Any
import requests


def check_server_health(url: str = "http://localhost:8000/health", timeout: int = 30) -> bool:
    """Check if the server is healthy and ready for testing."""
    print(f"Checking server health at {url}...")
    
    for i in range(timeout):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    print("✅ Server is healthy and ready for testing")
                    return True
        except requests.RequestException:
            pass
            
        if i < timeout - 1:
            print(f"⏳ Waiting for server... ({i+1}/{timeout})")
            time.sleep(1)
    
    print("❌ Server is not healthy or not responding")
    return False


def run_unit_tests() -> Dict[str, Any]:
    """Run unit tests."""
    print("\n🧪 Running Unit Tests...")
    print("=" * 50)
    
    cmd = [
        "python", "-m", "pytest", 
        "tests/unit/",
        "-v",
        "--tb=short",
        "--junit-xml=test-results/unit-tests.xml",
        "--cov=backend/app",
        "--cov=backend/ml_models", 
        "--cov-report=html:test-results/coverage-html",
        "--cov-report=xml:test-results/coverage.xml"
    ]
    
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    duration = time.time() - start_time
    
    return {
        "name": "Unit Tests",
        "success": result.returncode == 0,
        "duration": duration,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "command": " ".join(cmd)
    }


def run_integration_tests() -> Dict[str, Any]:
    """Run integration tests."""
    print("\n🔗 Running Integration Tests...")
    print("=" * 50)
    
    # Check server health first
    if not check_server_health():
        return {
            "name": "Integration Tests",
            "success": False,
            "duration": 0,
            "stdout": "",
            "stderr": "Server health check failed",
            "command": "server health check"
        }
    
    cmd = [
        "python", "-m", "pytest",
        "tests/integration/",
        "-v",
        "--tb=short",
        "--junit-xml=test-results/integration-tests.xml"
    ]
    
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    duration = time.time() - start_time
    
    return {
        "name": "Integration Tests",
        "success": result.returncode == 0,
        "duration": duration,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "command": " ".join(cmd)
    }


def run_performance_tests() -> Dict[str, Any]:
    """Run performance tests."""
    print("\n🚀 Running Performance Tests...")
    print("=" * 50)
    
    # Check server health first
    if not check_server_health():
        return {
            "name": "Performance Tests",
            "success": False,
            "duration": 0,
            "stdout": "",
            "stderr": "Server health check failed", 
            "command": "server health check"
        }
    
    cmd = [
        "python", "-m", "pytest",
        "tests/performance/",
        "-v",
        "--tb=short", 
        "--junit-xml=test-results/performance-tests.xml",
        "-s"  # Don't capture output for performance logs
    ]
    
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    duration = time.time() - start_time
    
    return {
        "name": "Performance Tests",
        "success": result.returncode == 0,
        "duration": duration,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "command": " ".join(cmd)
    }


def run_smoke_tests() -> Dict[str, Any]:
    """Run basic smoke tests to verify system functionality."""
    print("\n💨 Running Smoke Tests...")
    print("=" * 50)
    
    smoke_tests = []
    
    # Test 1: Server health
    try:
        if check_server_health():
            smoke_tests.append(("Server Health", True, ""))
        else:
            smoke_tests.append(("Server Health", False, "Health check failed"))
    except Exception as e:
        smoke_tests.append(("Server Health", False, str(e)))
    
    # Test 2: Basic translation
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/translate/",
            json={
                "text": "hello",
                "source_language": "en",
                "target_language": "hi",
                "model": "auto"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if "translated_text" in data and len(data["translated_text"]) > 0:
                smoke_tests.append(("Basic Translation", True, ""))
            else:
                smoke_tests.append(("Basic Translation", False, "Empty translation"))
        else:
            smoke_tests.append(("Basic Translation", False, f"HTTP {response.status_code}"))
            
    except Exception as e:
        smoke_tests.append(("Basic Translation", False, str(e)))
    
    # Test 3: Languages endpoint
    try:
        response = requests.get("http://localhost:8000/api/v1/languages/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if "languages" in data and len(data["languages"]) > 0:
                smoke_tests.append(("Languages Endpoint", True, ""))
            else:
                smoke_tests.append(("Languages Endpoint", False, "Missing or empty languages"))
        else:
            smoke_tests.append(("Languages Endpoint", False, f"HTTP {response.status_code}"))
    except Exception as e:
        smoke_tests.append(("Languages Endpoint", False, str(e)))
    
    # Summarize results
    passed = sum(1 for _, success, _ in smoke_tests if success)
    total = len(smoke_tests)
    
    for test_name, success, error in smoke_tests:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} {test_name}")
        if error:
            print(f"    Error: {error}")
    
    return {
        "name": "Smoke Tests",
        "success": passed == total,
        "duration": 0,
        "stdout": f"Passed: {passed}/{total}",
        "stderr": "",
        "tests": smoke_tests
    }


def setup_test_environment():
    """Setup test environment and directories."""
    # Create test results directory
    os.makedirs("test-results", exist_ok=True)
    
    # Set environment variables for testing
    os.environ["TESTING"] = "true"
    os.environ["LOG_LEVEL"] = "INFO"


def generate_test_report(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate comprehensive test report."""
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r["success"])
    total_duration = sum(r["duration"] for r in results)
    
    report = {
        "summary": {
            "total_test_suites": total_tests,
            "passed_test_suites": passed_tests,
            "failed_test_suites": total_tests - passed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "total_duration": total_duration,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        },
        "test_suites": results
    }
    
    return report


def print_test_summary(report: Dict[str, Any]):
    """Print test summary to console."""
    summary = report["summary"]
    
    print("\n" + "=" * 60)
    print("🧪 TEST EXECUTION SUMMARY")
    print("=" * 60)
    print(f"Total Test Suites: {summary['total_test_suites']}")
    print(f"Passed: {summary['passed_test_suites']}")
    print(f"Failed: {summary['failed_test_suites']}")
    print(f"Success Rate: {summary['success_rate']:.1f}%")
    print(f"Total Duration: {summary['total_duration']:.2f}s")
    print(f"Timestamp: {summary['timestamp']}")
    
    print("\n📋 Test Suite Results:")
    for result in report["test_suites"]:
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        duration = f"{result['duration']:.2f}s" if result['duration'] > 0 else "N/A"
        print(f"  {status} {result['name']} ({duration})")
        
        if not result["success"] and result["stderr"]:
            print(f"    Error: {result['stderr'][:200]}...")
    
    overall_status = "✅ ALL TESTS PASSED" if summary["failed_test_suites"] == 0 else "❌ SOME TESTS FAILED"
    print(f"\n{overall_status}")
    print("=" * 60)


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="NLP Translation App Test Runner")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--performance", action="store_true", help="Run performance tests only")
    parser.add_argument("--smoke", action="store_true", help="Run smoke tests only")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--report", type=str, help="Save report to JSON file")
    
    args = parser.parse_args()
    
    # If no specific test type is specified, run smoke tests by default
    if not any([args.unit, args.integration, args.performance, args.smoke, args.all]):
        args.smoke = True
    
    print("🚀 NLP Translation Application Test Runner")
    print("=" * 60)
    
    setup_test_environment()
    
    results = []
    
    try:
        if args.smoke or args.all:
            results.append(run_smoke_tests())
        
        if args.unit or args.all:
            results.append(run_unit_tests())
        
        if args.integration or args.all:
            results.append(run_integration_tests())
        
        if args.performance or args.all:
            results.append(run_performance_tests())
            
    except KeyboardInterrupt:
        print("\n⚠️  Test execution interrupted by user")
        return 1
    
    # Generate and display report
    report = generate_test_report(results)
    print_test_summary(report)
    
    # Save report if requested
    if args.report:
        with open(args.report, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n📄 Test report saved to: {args.report}")
    
    # Return appropriate exit code
    return 0 if report["summary"]["failed_test_suites"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
