"""
Simple test script to verify the chatbot functionality
Run this after setting up the database and starting the server
"""
import requests
import json

# API endpoint
BASE_URL = "http://localhost:8000"
CHAT_URL = f"{BASE_URL}/api/chat"


def test_chat(message: str, description: str):
    """Test a chat message"""
    print(f"\n{'='*60}")
    print(f"TEST: {description}")
    print(f"{'='*60}")
    print(f"User: {message}")
    
    try:
        response = requests.post(
            CHAT_URL,
            json={"message": message, "user_id": 1},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nBot: {data['reply']}")
            print(f"\nIntent: {data['intent']}")
            print(f"Confidence: {data['confidence']:.2f}")
            
            if data.get('data'):
                print(f"Additional Data: {json.dumps(data['data'], indent=2)}")
            
            print("✓ Test PASSED")
            return True
        else:
            print(f"✗ Test FAILED - Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ Test FAILED - Cannot connect to server")
        print("Make sure the server is running: uvicorn main:app --reload")
        return False
    except Exception as e:
        print(f"✗ Test FAILED - Error: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("SMART BANKING ASSISTANT - TEST SUITE")
    print("="*60)
    
    # Check server health
    try:
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code == 200:
            print("✓ Server is online")
        else:
            print("✗ Server health check failed")
            return
    except:
        print("✗ Cannot connect to server")
        print("\nPlease start the server first:")
        print("  uvicorn main:app --reload")
        return
    
    # Test cases
    tests = [
        ("Hello", "Greeting Intent"),
        ("Hi there", "Another Greeting"),
        ("What is my account balance?", "Balance Query"),
        ("How much money do I have?", "Balance Query (Alternative)"),
        ("Show my recent transactions", "Transaction History"),
        ("I want to see my transaction history", "Transaction History (Alternative)"),
        ("I need a loan", "Loan Inquiry"),
        ("Tell me about credit options", "Loan Inquiry (Alternative)"),
        ("What are your business hours?", "Knowledge Base Query"),
        ("How do I reset my password?", "Knowledge Base Query"),
        ("What is the weather today?", "Unknown Intent"),
        ("blah blah blah", "Random Unknown Query"),
    ]
    
    passed = 0
    failed = 0
    
    for message, description in tests:
        if test_chat(message, description):
            passed += 1
        else:
            failed += 1
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Total Tests: {passed + failed}")
    print(f"✓ Passed: {passed}")
    print(f"✗ Failed: {failed}")
    print(f"Success Rate: {(passed/(passed+failed)*100):.1f}%")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
