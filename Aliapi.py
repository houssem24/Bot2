#!/usr/bin/env python

# coding: utf-8

import json
import re
import urllib.parse
from urllib.parse import urlparse, parse_qs, urlunparse  # أضف urlunparse هنا
import telebot  # Telegram API library
from aliexpress_api import AliexpressApi, models
from telebot import types
from flask import Flask, request  # لإضافة السيرفر ومعالجة الطلبات
import requests
from keep_alive import keep_alive  # تشغيل السيرفر للحفاظ على النشاط

#########
# إعدادات Aliexpress API
KEY = '511252'
SECRET = '5GD1pusR40ORZvdLSPwHIpzddVlwh1dI'
TRACKING_ID = 'default'

# إعدادات Telegram Bot
API_KEY = '5337612436:AAEfcTXDOXpR_8qQei9lB_4OrCuN8D6kJn0'
bot = telebot.TeleBot(API_KEY)

#########
# دالة لاستخراج الروابط
def extract_links(text):
    """استخراج الروابط من النصوص."""
    links = re.findall(r"(?i)\bhttps?://[^\s]+", text)
    return links

# دالة لتحويل الرابط المختصر
def resolve_shortened_link(shortened_url):
    """تحويل الرابط المختصر إلى الرابط الأصلي."""
    try:
        response = requests.get(shortened_url, allow_redirects=True, timeout=5)
        return response.url  # إرجاع الرابط النهائي بعد إعادة التوجيه
    except requests.exceptions.RequestException:
        return None

#########
# الرد على أوامر البداية
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """إرسال رسالة ترحيب للمستخدم."""
    msg = '''
👋 <b>مرحبًا بك في بوت التخفيضات @Aliexpressgetcod_bot</b>

✅ مهمتي هي مساعدتك للحصول على أفضل العروض ونسبة تخفيض بالنقاط تصل إلى 70%!

💡 كيف تستخدم البوت؟
🔹 انسخ رابط المنتج من AliExpress.
🔹 أرسل الرابط كرسالة لي هنا.
🔹 انتظر لتحصل على رابط التخفيض الأفضل!

🎉 شكراً لاستخدامك البوت!
📌 تابع قناتنا للمزيد: <a href="https://t.me/Aliexpressgetcod_bot">@Aliexpressgetcod_bot</a>
    '''
    bot.reply_to(message, msg, parse_mode='HTML')

#########
# التعامل مع الروابط المرسلة
@bot.message_handler(func=lambda message: True)
def modify_link(message):
    """معالجة الروابط للتحقق منها وتحويلها إذا كانت مختصرة."""
    original_text = message.text
    urls = extract_links(original_text)

    if not urls:
        # إذا لم يتم العثور على روابط
        markup = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton("🔥 قناتنا 🔥", url="https://t.me/Aliexpressgetcod_bot")
        markup.add(button)
        bot.reply_to(message, "⚠️ لم يتم العثور على روابط في رسالتك. يرجى إرسال رابط منتج!", reply_markup=markup)
        return

    try:
        original_link = urls[0]
        resolved_link = resolve_shortened_link(original_link)
        if resolved_link is None:
            bot.reply_to(message, "⚠️ لم يتمكن البوت من تحليل الرابط المختصر. يرجى التأكد من صحة الرابط.")
            return

        # إعداد رسالة المعالجة
        processing_msg = bot.reply_to(message, "⏳ يتم معالجة الرابط للحصول على أفضل التخفيضات...")

        # جلب روابط التخفيض باستخدام Aliexpress API
        aliexpress = AliexpressApi(KEY, SECRET, models.Language.EN, models.Currency.USD, TRACKING_ID)
        affiliate_links = aliexpress.get_affiliate_links(resolved_link)

        # تحسين معالجة الأخطاء عند طلب التفاصيل
        try:
            product_id = re.search(r"(\d+)\.html", resolved_link).group(1)
            product_details = aliexpress.get_products_details([product_id])[0]
            product_title = getattr(product_details, 'product_title', 'غير متوفر')
            target_sale_price = getattr(product_details, 'target_sale_price', 'غير متوفر')
            discount = getattr(product_details, 'discount', 'غير متوفر')

            offer_msg = (
                f"<b>🎯 تفاصيل المنتج:</b>\n\n"
                f"❇️ <b>اسم المنتج:</b> {product_title}\n"
                f"💰 <b>السعر الحالي:</b> {target_sale_price}\n"
                f"📉 <b>التخفيض:</b> {discount}\n"
                f"🔗<b>رابط التخفيض:</b> {affiliate_links[0].promotion_link}\n\n"
                f"✅ شكراً لاستخدامك البوت!"
            )
            bot.delete_message(message.chat.id, processing_msg.message_id)
            bot.reply_to(message, offer_msg, parse_mode='HTML')
        except Exception as e:
            bot.reply_to(message, f"⚠️ حدث خطأ أثناء جلب تفاصيل المنتج: {e}")
            bot.delete_message(message.chat.id, processing_msg.message_id)

    except Exception as e:
        bot.reply_to(message, f"⚠️ حدث خطأ أثناء معالجة الرابط. الرجاء التأكد من الرابط أو المحاولة لاحقًا.")
        bot.delete_message(message.chat.id, processing_msg.message_id)

#########
# إعداد Webhook
WEBHOOK_HOST = 'https://bot2-ak10.onrender.com'  # ضع رابط مشروعك على Render هنا
WEBHOOK_PATH = '/webhook'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# تعيين Webhook
bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL)

#########
# تشغيل Flask لمعالجة طلبات Webhook
app = Flask(__name__)

@app.route(WEBHOOK_PATH, methods=['POST'])
def webhook():
    """معالجة الطلبات القادمة من Telegram API عبر Webhook."""
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "ok", 200

@app.route('/')
def home():
    return "The bot is running successfully!"

#########
# تشغيل التطبيق على المنفذ المناسب
import os

PORT = int(os.environ.get("PORT", 8080))  # Render يوفر المنفذ 8080 بشكل افتراضي
app.run(host="0.0.0.0", port=PORT)  # تشغيل التطبيق على هذا المنفذ