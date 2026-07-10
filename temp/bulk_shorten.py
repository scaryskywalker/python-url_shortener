import os
import sys
import re
import base64
import requests

# === Configuration ===
# Replace with your actual API key and base URL from the API Docs!
API_KEY = "mQoO0SxCb6zmfrylcctYD-dA2El1yUcyrXPhC1tWHYM"
API_BASE_URL = "https://shortner-n5d5.onrender.com/api/v1"

def main():
    if not os.path.exists("urls.txt"):
        print("Error: urls.txt not found. Please create it with one URL per line.")
        sys.exit(1)
        
    with open("urls.txt", "r") as f:
        urls = [line.strip() for line in f if line.strip()]
        
    if not urls:
        print("No URLs found in urls.txt")
        sys.exit(1)
        
    print(f"Found {len(urls)} URLs to process.\n")
    
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }

    # Create folder for QR codes
    if not os.path.exists("qr_codes"):
        os.makedirs("qr_codes")

    for idx, original_url in enumerate(urls, 1):
        print(f"[{idx}/{len(urls)}] Processing: {original_url}")
        
        # 1. Shorten the URL and generate a QR code simultaneously
        payload = {
            "original_url": original_url,
            "strategy_id": "88223a5c-3cba-4453-860b-549a058c4faa",
            "generate_qr": True  # This tells the API to return a base64 QR code!
        }
        
        try:
            resp = requests.post(
                f"{API_BASE_URL}/urls/shorten-auto",
                headers=headers,
                json=payload
            )
            resp.raise_for_status()
            data = resp.json()
            
            url_id = data.get("url_id")
            short_url = data.get("short_url")
            qr_base64 = data.get("qr_code")
            
            print(f"  -> Short URL: {short_url}")
            
            # 2. Save the QR Code image
            if qr_base64 and qr_base64.startswith("data:image/png;base64,"):
                # Strip the prefix
                base64_data = qr_base64.split(",")[1]
                
                # Sanitize original URL to create a safe filename
                safe_name = re.sub(r'^https?://', '', original_url)
                safe_name = re.sub(r'[^a-zA-Z0-9]', '_', safe_name).strip('_')
                if not safe_name:
                    safe_name = url_id
                    
                qr_filename = f"qr_codes/{safe_name}.png"
                
                with open(qr_filename, "wb") as img_file:
                    img_file.write(base64.b64decode(base64_data))
                print(f"  -> QR Code saved to: {qr_filename}")
                
            # 3. Analytics Facility (Checking the summary endpoint)
            # (Note: For a brand new URL, clicks will be 0, but this shows how to fetch it)
            analytics_resp = requests.get(
                f"{API_BASE_URL}/analytics/{url_id}/summary",
                headers=headers
            )
            if analytics_resp.status_code == 200:
                analytics_data = analytics_resp.json()
                total_clicks = analytics_data.get("total_clicks", 0)
                print(f"  -> Analytics: {total_clicks} total clicks so far.")
            else:
                print(f"  -> Failed to fetch analytics: {analytics_resp.status_code}")
                
            print("-" * 40)
            
        except requests.exceptions.RequestException as e:
            print(f"  -> Error processing {original_url}: {e}")
            print("-" * 40)

if __name__ == "__main__":
    main()