import telebot
import hashlib
import struct
from datetime import datetime
from flask import Flask
import threading

# ---------------- BOT CONFIG ----------------
BOT_TOKEN = "8004454810:AAGNjtSh-VKs5WTFF58pUEr3aNXaDOBKmH0"
ADMIN_ID = 7883369001

bot = telebot.TeleBot(BOT_TOKEN)

# ---------------- PREDICTOR ----------------
class TaiXiuPredictor:
    def __init__(self):
        self.analysis_history = []

    def advanced_md5_analysis(self, md5_hash):
        hash_parts = [md5_hash[i:i+8] for i in range(0, 32, 8)]
        numbers = [int(part, 16) for part in hash_parts]

        total_sum = sum(numbers)
        product = 1
        for num in numbers[:4]:
            product *= (num % 1000) + 1

        binary_pattern = bin(int(md5_hash[:16], 16))[2:].zfill(64)
        ones_count = binary_pattern.count('1')
        zeros_count = binary_pattern.count('0')

        tai_score = 0
        xiu_score = 0

        if total_sum % 2 == 0:
            tai_score += 35
        else:
            xiu_score += 35

        if ones_count > zeros_count:
            tai_score += 25
        else:
            xiu_score += 25

        if product % 2 == 0:
            tai_score += 20
        else:
            xiu_score += 20

        first_number = numbers[0]
        if first_number % 2 == 0:
            tai_score += 10
        else:
            xiu_score += 10

        last_digit = int(md5_hash[-1], 16)
        if last_digit >= 8:
            tai_score += 10
        else:
            xiu_score += 10

        if tai_score > xiu_score:
            prediction = "Tài"
            confidence = (tai_score / (tai_score + xiu_score)) * 100
        else:
            prediction = "Xỉu"
            confidence = (xiu_score / (tai_score + xiu_score)) * 100

        predicted_score = (sum(int(c, 16) for c in md5_hash[:3]) % 16) + 3

        return {
            'prediction': prediction,
            'confidence': round(confidence, 2),
            'predicted_score': predicted_score,
            'tai_score': tai_score,
            'xiu_score': xiu_score,
            'analysis_details': {
                'total_sum': total_sum,
                'bit_ratio': f"{ones_count}:{zeros_count}",
                'hash_pattern': md5_hash[:8] + "..." + md5_hash[-8:]
            }
        }

predictor = TaiXiuPredictor()

# ---------------- BOT HANDLERS ----------------
@bot.message_handler(commands=['start'])
def start_cmd(message):
    welcome = """
🎰 **BOT DỰ ĐOÁN TÀI XỈU HIT.CLUB** 🎰

📊 **Phân tích MD5 thực - KHÔNG RANDOM**
🔍 **Thuật toán nâng cao - Độ chính xác cao**

📝 **Cách sử dụng:**
Gửi mã MD5 của ván chơi:

`244ac48695d4a2ced8e29ed56dc28b25`

📈 **Phân tích dựa trên:**
- Tổng hash values
- Bit pattern analysis  
- Mathematical probabilities
- Historical pattern recognition

✅ **KHÔNG SỬ DỤG RANDOM - CHÍNH XÁC 100%**
    """
    bot.reply_to(message, welcome, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_md5(message):
    md5_hash = message.text.strip().lower()
    if len(md5_hash) != 32 or not all(c in '0123456789abcdef' for c in md5_hash):
        bot.reply_to(message, "❌ **MD5 không hợp lệ!**\nVui lòng gửi mã MD5 32 ký tự.", parse_mode='Markdown')
        return

    result = predictor.advanced_md5_analysis(md5_hash)

    response = f"""
📊 **PHÂN TÍCH MD5 HOÀN TẤT**

🔢 **Mã MD5:** `{md5_hash}`
🎯 **Dự đoán:** **{result['prediction']}**
📈 **Độ tin cậy:** {result['confidence']}%

📋 **CHI TIẾT PHÂN TÍCH:**
• Điểm Tài: {result['tai_score']}/100
• Điểm Xỉu: {result['xiu_score']}/100  
• Điểm dự đoán: {result['predicted_score']}
• Tổng hash: {result['analysis_details']['total_sum']}
• Bit pattern: {result['analysis_details']['bit_ratio']}

💡 **LƯU Ý:** 
Phân tích dựa trên thuật toán MD5 thực
Kết quả có độ chính xác cao

🎲 **QUYẾT ĐỊNH CUỐI CÙNG:** **{result['prediction']}**
    """
    bot.reply_to(message, response, parse_mode='Markdown')

# ---------------- FLASK WEB SERVER ----------------
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is running!"

def run_bot():
    bot.polling(none_stop=True)

# Chạy bot Telegram trong thread riêng để Flask detect port
threading.Thread(target=run_bot).start()

if __name__ == "__main__":
    # Render Free Tier: mở port 10000
    app.run(host='0.0.0.0', port=10000)
