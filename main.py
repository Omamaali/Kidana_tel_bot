import os
import json
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from google import genai

app = Flask(__name__)

# جلب المفاتيح من متغيرات البيئة (Environment Variables)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# تهيئة عميل Gemini وعميل Telegram
ai_client = genai.Client(api_key=GEMINI_API_KEY)
bot = Bot(token=TELEGRAM_TOKEN)

SYSTEM_PROMPT = """
أنت 'مستشار كدانة للسياحة' الذكي، ممثل رسمي لشركة كدانة للسياحة.
مهمتك:
1. الترحيب بالعملاء بأسلوب مهني وودود وجذاب.
2. مساعدة العميل في تخطيط رحلاته (سياحة داخلية أو رحلات خارجية وعمرة).
3. استخراج تفاصيل العميل بلباقة: الوجهة، عدد الأفراد، ميعاد السفر، والميزانية.
4. اقتراح برامج سياحية متكاملة وممتعة.
5. توجيه العميل لترك رقم هاتفه للتواصل مع قسم الحجوزات لتأكيد الحجز.
كن مختصراً ومقنعاً ونسق إجابتك بنقاط واضحة.
"""

@app.route("/", methods=["POST"])
def webhook():
    """استقبال رسائل تيليجرام عبر Webhook"""
    update_data = request.get_json(force=True)
    
    if "message" in update_data and "text" in update_data["message"]:
        chat_id = update_data["message"]["chat"]["id"]
        user_text = update_data["message"]["text"]

        if user_text.startswith("/start"):
            reply = (
                "مرحباً بك في كدانة للسياحة! 🌍✈️\n\n"
                "أنا مستشارك السياحي الذكي، جاهز لتفصيل أفضل عروض وبرامج السفر داخل مصر وخارجها.\n\n"
                "ما هي وجهتك المفضلة لرحلتك القادمة؟"
            )
        else:
            try:
                # استدعاء Gemini Flash للإجابة الفورية
                response = ai_client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=user_text,
                    config={"system_instruction": SYSTEM_PROMPT}
                )
                reply = response.text
            except Exception as e:
                reply = "أهلاً بك، يسعدنا تواصلك مع خدمة عملاء كدانة للسياحة لتزويدك بأدق التفاصيل والأسعار."

        # إرسال الرد للعميل على تيليجرام
        bot.send_message(chat_id=chat_id, text=reply)

    return "OK", 200

@app.route("/health", methods=["GET"])
def health():
    return "Service is running perfectly", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
