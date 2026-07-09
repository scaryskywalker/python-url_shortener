# Protechy API - Bulk URL Shortener

This program demonstrates how to interact with the Protechy URL Shortener REST API using Python. It takes a list of long URLs from a text file, automates shortening them via the API, downloads their associated QR codes, and fetches basic analytics data.

## 🚀 How It Works

The `bulk_shorten.py` script performs the following three steps for each URL listed in `urls.txt`:

1. **Shorten the URL & Generate QR**
   - **Endpoint:** `POST https://shortner-n5d5.onrender.com/api/v1/urls/shorten-auto`
   - **How:** The script sends the `original_url` and a specific `strategy_id` to the API. It also sets `"generate_qr": True` in the JSON payload, which instructs the backend to generate a Base64-encoded QR code on the fly and return it in the exact same response, saving us an extra API call!

2. **Save the QR Code**
   - **How:** The script extracts the Base64 image string (`qr_code`) from the JSON response, decodes it into binary data, and saves it as a `.png` image inside the `qr_codes/` folder. 
   - **Naming:** The PNG file is intelligently named after the original URL (e.g. `google_com.png`).

3. **Fetch Analytics**
   - **Endpoint:** `GET https://shortner-n5d5.onrender.com/api/v1/analytics/{url_id}/summary`
   - **How:** Using the unique `url_id` returned from step 1, the script makes a GET request to the analytics endpoint to retrieve data such as the total clicks that the shortened link has received.

---

## 💻 How to Run It

### Prerequisites
Make sure you have Python installed, and install the `requests` library if you haven't already:
```bash
pip install requests
```

### Setup
1. **Add your URLs:** Open `urls.txt` and paste all the original URLs you want to shorten. Put exactly one URL per line.
2. **API Credentials:** The script is already configured with your `API_KEY` and `strategy_id`. (If you rotate your API key in the future, be sure to update it at the top of `bulk_shorten.py`).

### Execution
Simply run the script in your terminal:
```bash
python bulk_shorten.py
```

### Output
- You will see live processing logs in your console showing the newly generated Short URLs and their click counts.
- A new folder named `qr_codes/` will automatically be created containing the PNG images of your QR codes, cleanly named after each website!
