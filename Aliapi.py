#!/usr/bin/env python

# coding: utf-8



import json
import re
import urllib.parse
from urllib.parse import urlparse, parse_qs
import telebot  # type: ignore
from aliexpress_api import AliexpressApi, models
from keep_alive import keep_alive
from telebot import types
from flask import Flask  # لإضافة السيرفر
#########
# إعدادات Aliexpress API
KEY = '511252'
SECRET = '5GD1pusR40ORZvdLSPwHIpzddVlwh1dI'
TRACKING_ID = 'default'

# إعدادات Telegram Bot
API_KEY = '5337612436:AAEfcTXDOXpR_8qQei9lB_4OrCuN8D6kJn0'
bot = telebot.TeleBot(API_KEY)

def extract_links(text):
    """استخراج الروابط من النصوص."""
    links = re.findall(r"(?i)\bhttps?://[^\s]+", text)
    return links

def resolve_shortened_link(shortened_url):
    """تحويل الرابط المختصر إلى الرابط الأصلي."""
    try:
        response = requests.get(shortened_url, allow_redirects=True, timeout=5)
        return response.url  # إرجاع الرابط النهائي بعد إعادة التوجيه
    except requests.exceptions.RequestException:
        return None

def shorten_link(original_url):
    """إعادة اختصار الرابط باستخدام خدمة اختصار (اختياري)."""
    return original_url  # يمكن استبدال هذه الوظيفة بخدمة اختصار أخرى

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
        
        # تحويل الرابط إذا كان مختصرًا
        resolved_link = resolve_shortened_link(original_link)
        if resolved_link is None:
            bot.reply_to(message, "⚠️ لم يتمكن البوت من تحليل الرابط المختصر. يرجى التأكد من صحة الرابط.")
            return

        # إعادة اختصار الرابط (اختياري)
        short_link = shorten_link(resolved_link)

        if 'item' not in resolved_link:
            bot.reply_to(message, f"⚠️ الرابط الأصلي الذي تم تحليله لا يحتوي على معلومات المنتج: {short_link}")
            return

        processing_msg = bot.reply_to(message, "⏳ يتم معالجة الرابط للحصول على أفضل التخفيضات...")
        loading_animation = bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAIU1GYOk5jWvCvtykd7TZkeiFFZRdUYAAIjAAMoD2oUJ1El54wgpAY0BA")
        # استخدم Aliexpress API لجلب التفاصيل
        aliexpress = AliexpressApi(KEY, SECRET, models.Language.EN, models.Currency.USD, TRACKING_ID)
        parsed_url = urlparse(resolved_link)
        new_url = urlunparse(parsed_url._replace(query='')) + "?sourceType=620&channel=coin"

        affiliate_links = aliexpress.get_affiliate_links(new_url)
        product_id = re.search(r"(\d+)\.html", resolved_link).group(1)

        # جلب تفاصيل المنتج
        fields = [
            'productTitle', 'targetSalePrice', 'discount', 'productDetailUrl', 'shopUrl',
            'targetOriginalPrice', 'productMainImageUrl', 'evaluateRate'
        ]
        product = aliexpress.get_products_details(product_ids=[product_id], fields=fields)[0]

        product_title = getattr(product, 'product_title', 'غير متوفر')
        target_sale_price = getattr(product, 'target_sale_price', 'غير متوفر')
        target_original_price = getattr(product, 'target_original_price', 'غير متوفر')
        discount = getattr(product, 'discount', 'غير متوفر')
        evaluate_rate = getattr(product, 'evaluate_rate', 'غير متوفر')
        product_detail_url = getattr(product, 'product_detail_url', 'غير متوفر')
        shop_url = getattr(product, 'shop_url', 'غير متوفر')
        bot.delete_message(message.chat.id, loading_animation.message_id)
        # إعداد رسالة الرد
        offer_msg = (
            f"<b>🎯 تفاصيل المنتج:</b>\n\n"
            f"❇️ <b>اسم المنتج:</b> {product_title}\n"
            f"💰 <b>السعر الحالي:</b> {target_sale_price}\n"
            f"📉 <b>التخفيض:</b> {discount}\n"
            f"⭐️ <b>تقييم المنتج:</b> {evaluate_rate}\n\n"
             f"🏬 <b>رابط المتجر:</b> <a        href='{shop_url}'>المتجر</a>\n\n"
            f"🔗<b>رابط تخفيض النقاط 🛍️:</b>\n\n{affiliate_links[0].promotion_link}\n\n"
            f"<b>🅑🅔🅢🅣 🅒🅞🅤🅟🅞🅝 🅐🅛🅖🅔🅡🅘🅔 🤴 ✅</b>\n\n"

            
        )

        # إعداد زر القناة فقط
        markup = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton("🔥 قناتنا 🔥", url="https://t.me/bestcoupondz")
        markup.add(button)

        bot.delete_message(message.chat.id, processing_msg.message_id)
        bot.send_photo(message.chat.id, product.product_main_image_url, caption=offer_msg, parse_mode='HTML', reply_markup=markup)
    except Exception as e:
        bot.reply_to(message, f"⚠️ حدث خطأ أثناء معالجة الرابط: {e}")
        bot.delete_message(message.chat.id, loading_animation.message_id)
# تشغيل البوت
# تأكد أن السيرفر يعمل باستخدام keep_alive
keep_alive()

# بدء عملية "polling" للبوت
bot.infinity_polling(timeout=10, long_polling_timeout=5)

######### سيرفر Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "The bot is running successfully!"

# التأكد أن السيرفر يعمل
keep_alive()

# بدء البوت
bot.infinity_polling(timeout=10, long_polling_timeout=5)