from app.cloud_storage import CloudStorage

def test_connection():
    storage = CloudStorage()
    status = storage.check_storage_status()
    
    print("Cloud Storage Status:")
    print("-" * 20)
    print(f"Status: {status.get('status')}")
    print(f"Bucket Name: {status.get('bucket_name')}")
    
    if status.get('status') == 'error':
        print(f"Error: {status.get('error')}")
    elif status.get('bucket_exists'):
        print("Bucket Status: Available and accessible")
    else:
        print("Bucket Status: Not found")

if __name__ == "__main__":
    test_connection()