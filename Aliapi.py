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


bot = telebot.TeleBot('7259038504:AAHM1zUacyc1sXVRqruVOwPMOA2NmrKZ_BA')



# إعدادات AliExpress API

aliexpress = AliexpressApi('511680', 'taUT7L9YpLRAA4GrFI9jPjrtkmEjTGBl', models.Language.EN, models.Currency.USD, 'default')



# لوحة المفاتيح

keyboardStart = types.InlineKeyboardMarkup(row_width=1)



btn2 = types.InlineKeyboardButton("⭐️تخفيض العملات على منتجات السلة 🛒⭐️",

                                  callback_data='click')

btn3 = types.InlineKeyboardButton("❤️ اشترك في القناة للمزيد من العروض ❤️",

                                  url="https://t.me/bestcoupondz")

btn4 = types.InlineKeyboardButton("🎬 قناة اخرى قد تهمك🎬",

                                  url="https://linktr.ee/bestcouponalgerie")

btn5 = types.InlineKeyboardButton(

    "💰  اضغط هنا لمتابعتنا على الفيس بوك  💰",

    url="https://bit.ly/bestCouponDZfacebook")

keyboardStart.add(btn2, btn3, btn4, btn5)



keyboard = types.InlineKeyboardMarkup(row_width=1)

btn2 = types.InlineKeyboardButton("⭐️تخفيض العملات على منتجات السلة 🛒⭐️",

                                  callback_data='click')

btn3 = types.InlineKeyboardButton("❤️ اشترك في القناة للمزيد من العروض ❤️",

                                  url="https://t.me/bestcoupondz")

btn4 = types.InlineKeyboardButton("🎬 قناة اخرى قد تهمك🎬",

                                  url="https://linktr.ee/bestcouponalgerie")

btn5 = types.InlineKeyboardButton(

    "💰  اضغط هنا لمتابعتنا على الفيس بوك  💰",

    url="https://bit.ly/bestCouponDZfacebook")

keyboard.add(btn2, btn3, btn4, btn5)



@bot.message_handler(commands=['start'])

def welcome_user(message):

    bot.send_message(

        message.chat.id,

        "مرحبا بك، ارسل لنا رابط المنتج الذي تريد شرائه لنوفر لك افضل سعر له 👌 \n",

        reply_markup=keyboardStart)



@bot.callback_query_handler(func=lambda call: call.data == 'click')

def button_click(callback_query):

    bot.edit_message_text(chat_id=callback_query.message.chat.id,

                          message_id=callback_query.message.message_id,

                          text="...")



    text = "✅1-ادخل الى السلة من هنا:\n" \

           " https://s.click.aliexpress.com/e/_oBQ9O9h \n" \

           "✅2-قم باختيار المنتجات التي تريد تخفيض سعرها\n" \

           "✅3-اضغط على زر دفع ليحولك لصفحة التأكيد \n" \

           "✅4-اضغط على الايقونة في الاعلى وانسخ الرابط هنا في البوت لتتحصل على رابط التخفيض"



    img_link1 = "https://i.postimg.cc/HkMxWS1T/photo-5893070682508606111-y.jpg"

    bot.send_photo(callback_query.message.chat.id,

                   img_link1,

                   caption=text,

                   reply_markup=keyboard)



# دالة معالجة الروابط الترويجية

def get_affiliate_links(message, message_id, link):

    global affiliate_link, super_links, limit_links

    try:

        # الحصول على الروابط الترويجية

        affiliate_link = aliexpress.get_affiliate_links(

    f'https://star.aliexpress.com/share/share.htm?platform=AE&businessType=ProductDetail&redirectUrl={link}?sourceType=620&channel=coin&action=buy_now'

)[0].promotion_link



        super_links = aliexpress.get_affiliate_links(

            f'https://star.aliexpress.com/share/share.htm?platform=AE&businessType=ProductDetail&redirectUrl={link}?sourceType=562&aff_fcid='

        )[0].promotion_link



        limit_links = aliexpress.get_affiliate_links(

            f'https://star.aliexpress.com/share/share.htm?platform=AE&businessType=ProductDetail&redirectUrl={link}?sourceType=561&aff_fcid='

        )[0].promotion_link



        # الحصول على تفاصيل المنتج

        product_details = aliexpress.get_products_details([

            f'https://star.aliexpress.com/share/share.htm?platform=AE&businessType=ProductDetail&redirectUrl={link}?sourceType=620&channel=coin'

        ])



        if not product_details or len(product_details) == 0:

            raise ValueError("No product details returned from API.")

        product_details = product_details[0]

        price_pro = product_details.target_sale_price



        # تحويل السعر إذا كان سلسلة نصية

        price_pro = float(price_pro) if isinstance(price_pro, str) else price_pro



        title_link = product_details.product_title

        img_link = product_details.product_main_image_url



        # حساب الأسعار المخفضة

        discount_rate_affiliate = 0.10  # نسبة تخفيض العملات

        discount_rate_super = 0.15      # نسبة تخفيض السوبر

        discount_rate_limited = 0.20    # نسبة تخفيض العرض المحدود



        price_pro_affiliate = price_pro * (1 - discount_rate_affiliate)

        price_pro_super = price_pro * (1 - discount_rate_super)

        price_pro_limited = price_pro * (1 - discount_rate_limited)



        # حذف الرسالة المؤقتة وإرسال الرسالة النهائية

        bot.delete_message(message.chat.id, message_id)

        bot.send_photo(

            message.chat.id,

            img_link,

            caption=f"🛒 منتجك هو : 🔥 \n{title_link} 🛍 \n"

                    f"السعر الأصلي: {price_pro:.2f} دولار 💵\n"

                    "قارن بين الأسعار واشتري 🔥 \n"

                    f"💰 عرض العملات: {price_pro_affiliate:.2f} دولار 💵\nالرابط: {affiliate_link}\n"

                    f"💎 عرض السوبر: {price_pro_super:.2f} دولار 💵\nالرابط: {super_links}\n"

                    f"♨️ عرض محدود: {price_pro_limited:.2f} دولار 💵\nالرابط: {limit_links}\n\n"

                    "🅑🅔🅢🅣 🅒🅞🅤🅟🅞🅝 🅐🅛🅖🅔🅡🅘🅔 🤴 ✅",

            reply_markup=keyboard

        )



    except ValueError as e:

        print(f"Value Error: {e}")

        bot.delete_message(message.chat.id, message_id)

        bot.send_message(

            message.chat.id,

            "حدث خطأ أثناء معالجة الرابط. تحقق من الرابط وأعد المحاولة."

        )

    except Exception as e:

        print(f"Error in get_affiliate_links: {e}")

        bot.delete_message(message.chat.id, message_id)

        bot.send_message(

            message.chat.id,

            "حدث خطأ أثناء معالجة الرابط. الرجاء التأكد من صحة الرابط والمحاولة مرة أخرى."

        )



# تحسين دالة استخراج الروابط

def extract_redirect_url(final_link):

    try:

        # تحليل الرابط النهائي واستخراج "redirectUrl"

        parsed_url = urlparse(final_link)

        query_params = parse_qs(parsed_url.query)

        redirect_url = query_params.get("redirectUrl")

        if redirect_url:

            clean_redirect_url = redirect_url[0].split("?")[0]

            print(f"Extracted Redirect URL: {clean_redirect_url}")

            return clean_redirect_url

        else:

            print("No Redirect URL Found.")

            return final_link.split("?")[0]

    except Exception as e:

        print(f"Error in extract_redirect_url: {e}")

        return final_link.split("?")[0]



@bot.message_handler(func=lambda message: True)

def handle_message(message):

    # استخراج الرابط من الرسالة

    link = extract_link(message.text)

    if link:

        # فك إعادة التوجيه للحصول على الرابط الكامل

        link = resolve_redirects(link)

        link = extract_redirect_url(link)

        print(f"Final Processed Link: {link}")  # طباعة الرابط النهائي



        # إرسال رسالة مؤقتة للمستخدم

        sent_message = bot.send_message(

            message.chat.id, 'المرجو الانتظار قليلا، يتم تجهيز العروض ⏳')

        message_id = sent_message.message_id



        # معالجة الرابط إذا كان صحيحًا وينتمي إلى AliExpress

        if link and "aliexpress.com" in link:

            try:

                get_affiliate_links(message, message_id, link)

            except Exception as e:

                bot.delete_message(message.chat.id, message_id)

                bot.send_message(

                    message.chat.id,

                    f"حدث خطأ أثناء معالجة الرابط: {e}. يرجى إعادة المحاولة. 🤷🏻‍♂️"

                )

        else:

            # حذف الرسالة المؤقتة وإرسال رد للمستخدم إذا كان الرابط غير صحيح

            bot.delete_message(message.chat.id, message_id)

            bot.send_message(

                message.chat.id,

                "الرابط غير صحيح! تأكد من رابط المنتج أو اعد المحاولة.\n"

                " قم بإرسال <b>الرابط فقط</b> بدون عنوان المنتج.",

                parse_mode='HTML'

            )

    else:

        # رد إذا لم يتم العثور على رابط داخل الرسالة

        bot.send_message(

            message.chat.id,

            "يرجى إرسال رابط المنتج الصحيح لمعالجته. تأكد أن الرسالة تحتوي على الرابط فقط."

        )



# دالة استخراج الرابط

def extract_link(text):

    link_pattern = r'https?://\S+|www\.\S+'

    links = re.findall(link_pattern, text)

    if links:

        return links[0]



# دالة فك إعادة التوجيه

def resolve_redirects(url):

    import requests

    try:

        response = requests.get(url, allow_redirects=True)

        print(f"Resolved URL: {response.url}")  # طباعة الرابط بعد فك التوجيه

        return response.url

    except Exception as e:

        print(f"Error resolving URL: {e}")

        return url



# تحسين دالة استخراج الروابط

def extract_redirect_url(final_link):

    try:

        # تحليل الرابط النهائي واستخراج "redirectUrl"

        parsed_url = urlparse(final_link)

        query_params = parse_qs(parsed_url.query)

        redirect_url = query_params.get("redirectUrl")

        if redirect_url:

            clean_redirect_url = redirect_url[0].split("?")[0]

            print(f"Extracted Redirect URL: {clean_redirect_url}")

            return clean_redirect_url

        else:

            print("No Redirect URL Found.")

            return final_link.split("?")[0]

    except Exception as e:

        print(f"Error in extract_redirect_url: {e}")

        return final_link.split("?")[0]

# سيرفر Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "The bot is running successfully!"

# التأكد أن السيرفر يعمل
keep_alive()

# بدء البوت
bot.infinity_polling(timeout=10, long_polling_timeout=5)