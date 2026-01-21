import redis

# 1. Try to connect to the Docker Redis directly
try:
    print("🔌 Attempting to connect to Redis at localhost:6379...")
    r = redis.Redis(host='localhost', port=6379, socket_connect_timeout=2)
    
    # 2. Force a write
    r.set('test_key', 'it_works')
    print("✅ Write Successful!")
    
    # 3. Force a read
    val = r.get('test_key')
    print(f"✅ Read Successful! Value: {val.decode('utf-8')}")
    
except Exception as e:
    print(f"❌ CONNECTION FAILED: {e}")