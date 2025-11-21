import os
import sys
from estadisticas import Estadisticas

# Mock database connection if needed, or rely on actual DB
# Assuming environment variables are set or config is loaded
# We need to be in the backend directory

def debug():
    try:
        print("Initializing Estadisticas...")
        stats = Estadisticas()
        
        # Test multiple users
        for user_id in [1, 2, 3, 9999]:
            print(f"\n--------------------------------------------------")
            print(f"Testing user_id={user_id}...")
            try:
                resultado = stats.obtener_dashboard_personalizado(user_id)
                print("Result obtained.")
                import json
                json.dumps(resultado)
                print("JSON Serialization SUCCESS")
            except Exception as e:
                print(f"FAILED for user_id={user_id}")
                import traceback
                traceback.print_exc()
        
        import json
        print("Testing JSON serialization...")
        json_str = json.dumps(resultado)
        print("JSON Serialization SUCCESS")
        
    except Exception as e:
        print("CAUGHT EXCEPTION:")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug()
