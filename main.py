from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# --- AYARLAR ---
# Bu değerleri Render panelinde manuel girdiğin için kod buradan çekecek
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "ahiretkazancim_2025")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")

# --- ÖZEL LİNKLER ---
MUHASEBE_LINK = "https://wa.me/905461434445"
HALIL_LINK = "https://wa.me/905422937879"
FATIH_LINK = "https://wa.me/905416043444"
ONLINE_BAGIS_LINK = "https://www.ahiretkazancim.com/bagislar"

@app.route("/", methods=["GET"])
def home():
    return "Ahiret Kazancım Botu Aktif! 🚀"

@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Token Hatalı!", 403
    return "Hata", 400

@app.route("/webhook", methods=["POST"])
def receive_message():
    data = request.get_json()
    
    if data and "object" in data and "entry" in data:
        for entry in data["entry"]:
            for change in entry["changes"]:
                if "messages" in change["value"]:
                    message = change["value"]["messages"][0]
                    gonderen_no = message["from"]
                    
                    if message["type"] == "text":
                        gelen_mesaj = message["text"]["body"].lower()

                        # 1. HALİL VE FATİH YÖNLENDİRMELERİ
                        if "halil" in gelen_mesaj:
                            cevap = "Selamun Aleyküm efendim, Halil Bey ile görüşmek isterseniz buyurun: \n\n" + HALIL_LINK
                            whatsapp_cevap_yolla(gonderen_no, cevap)
                        elif "fatih" in gelen_mesaj:
                            cevap = "Selamun Aleyküm efendim, Fatih Bey ile görüşmek isterseniz buyurun: \n\n" + FATIH_LINK
                            whatsapp_cevap_yolla(gonderen_no, cevap)

                        # 2. FERAH GÖRÜNÜMLÜ IBAN VE BAĞIŞ MESAJI
                        elif any(k in gelen_mesaj for k in ["iban", "hesap", "banka", "bağış", "yardım", "bağiş"]):
                            if gonderen_no.startswith("90"):
                                cevap = (
                                    "Selamun Aleyküm, güzel niyetinizden ötürü Rabbimiz sizlerden razı olsun. 🌸\n\n"
                                    "📌 *Banka Hesap Bilgilerimiz:*\n\n"
                                    "🏦 *Banka:* Vakıf Katılım Bankası\n"
                                    "👤 *Alıcı:* Ahiret Kazancım Eğitim Ve Yardımlaşma Derneği\n"
                                    "🔢 *IBAN:* `TR38 0021 0000 0006 6508 2000 01`\n\n"
                                    "📱 *FAST / Kolay Adres:* 507 971 67 97\n\n"
                                    "✨ ————————————————— ✨\n\n"
                                    "🙏 Hayrınızı yaptıktan sonra; *dekontu* ve bağışın *kimin adına* (Kurban 🐑, Su Kuyusu 💧, Yemek Dağıtımı 🍲 vb.) olduğunu iletirseniz hemen notlarımızı alalım efendim.\n\n"
                                    "🌍 *Yurt Dışı / Döviz İşlemleri İçin:* \n"
                                    "Aşağıdaki linke tıklayarak bizimle iletişime geçebilirsiniz:\n"
                                    "👇👇👇\n"
                                    "https://wa.me/905461434445"
                                )
                                whatsapp_cevap_yolla(gonderen_no, cevap)
                            else:
                                # YURT DIŞI NUMARALARI
                                cevap = (
                                    "Selamun Aleyküm efendim, yurt dışı bağışlarınız için online ödeme sayfamızı kullanabilirsiniz: \n\n"
                                    f"🌍 {ONLINE_BAGIS_LINK}\n\n"
                                    "Dilerseniz şu linkten bizimle doğrudan iletişime geçebilirsiniz:\n"
                                    "👇👇👇\n"
                                    "https://wa.me/905461434445"
                                )
                                whatsapp_cevap_yolla(gonderen_no, cevap)
                                
    return jsonify({"status": "success"}), 200

def whatsapp_cevap_yolla(numara, metin):
    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    payload = {"messaging_product": "whatsapp", "to": numara, "type": "text", "text": {"body": metin}}
    try:
        requests.post(url, headers=headers, json=payload)
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
