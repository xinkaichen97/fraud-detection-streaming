from feast import FeatureStore

# 1. Load the Store
repo_path = "./feature_repo"
print(f"📂 Loading Feature Store from: {repo_path}")
fs = FeatureStore(repo_path=repo_path)

# 2. Inspect the Config
print("\n🕵️ FEAST CONFIGURATION:")
online_config = fs.config.online_store
print(f"   Online Store Type: {online_config.type}")

# 3. Validation Logic
if online_config.type == "redis":
    print("✅ Configuration is correctly set to REDIS.")
    # Try to print connection string if available
    try:
        print(f"   Connection String: {online_config.connection_string}")
    except:
        print("   (Connection string attribute not directly readable, but type is Redis)")
elif online_config.type == "sqlite":
    print("❌ Configuration is set to SQLITE (File-based).")
    print("   Please check your feature_store.yaml indentation!")
else:
    print(f"⚠️ Unknown Online Store Type: {online_config.type}")

# 4. Check Registry for Feature View
print("\n🔎 Checking Registry for 'transaction_stats_fv'...")
try:
    fv = fs.get_feature_view("transaction_stats_fv")
    print("✅ Feature View found in registry.")
    
    # Check the Entity type
    entity_name = fv.entities[0]
    entity = fs.get_entity(entity_name)
    print(f"   Entity Name: {entity.name}")
    print(f"   Entity Join Key: {entity.join_key}")
    print(f"   (Make sure your 'debug_push.py' uses this exact column name!)")
    
except Exception as e:
    print(f"❌ Feature View NOT FOUND: {e}")