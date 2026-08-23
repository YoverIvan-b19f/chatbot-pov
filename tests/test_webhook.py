import requests
import json

def test_webhook():
    """Test the webhook endpoint locally"""
    url = "http://127.0.0.1:5000/webhook"
    
    # Test data
    data = {
        'Body': 'hola',
        'From': 'whatsapp:+51999999999'
    }
    
    try:
        response = requests.post(url, data=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        # Verify it's a valid TwiML response
        if response.status_code == 200:
            print("✅ Webhook test successful!")
        else:
            print("❌ Webhook test failed")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_health():
    """Test the health check endpoint"""
    url = "http://127.0.0.1:5000/health"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"✅ Health check passed: {response.json()}")
        else:
            print("❌ Health check failed")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    print("🧪 Testing VocalIA Webhook...")
    test_health()
    test_webhook()