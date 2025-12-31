from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# --- AYARLAR ---
# Bu bilgiler Render'ın "Environment Variables" kısmından çekilecek
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "ahiretkazancim_2025")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")

# --- DERNEK BİLGİLERİ ---
BANKA_ADI = "Vakıf Katılım Bankası"
ALICI_ADI = "AHİRET KAZANCIM EĞİTİM VE YARDIMLAŞMA DERNEĞİ"
IBAN_NO = "TR38 0021 0000 0006 6508 2000 01"

# Linkler
DERNEK_SITE_BAGIS = "https://www.ahiretkazancim.com/bagislar"
MUHASEBE_LINK = "https://wa.me/905461434445"
HALIL_LINK = "https://wa.me/905422937879"

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
                        print(f"Mesaj Geldi ({gonderen_no}): {gelen_mesaj}")

                        # --- MANTIK KURGUSU ---

                        # 1. HALİL'İ SORANLAR
                        if "halil" in gelen_mesaj:
                            cevap = (
                                "Halil Bey ile görüşmek isterseniz, kendisine aşağıdaki linkten doğrudan ulaşabilirsiniz:\n"
                                f"👉 {HALIL_LINK}"
                            )
                            whatsapp_cevap_yolla(gonderen_no, cevap)

                        # 2. IBAN / HESAP / BAĞIŞ İSTEYENLER
                        elif any(kelime in gelen_mesaj for kelime in ["iban", "hesap", "banka", "bağış", "yardım"]):
                            
                            # Yurt İçi Kontrolü (+90 ile başlayanlar)
                            if gonderen_no.startswith("90"):
                                cevap = (
                                    "Güzel düşüncenizden ve niyetinizden ötürü Rabbimiz sizlerden razı olsun. 🌸\n\n"
                                    "📌 **Banka Hesap Bilgilerimiz:**\n"
                                    f"Banka: **{BANKA_ADI}**\n"
                                    f"Alıcı: **{ALICI_ADI}**\n"
                                    f"IBAN: **{IBAN_NO}**\n\n"
                                    "⚠️ Bağışınızı yaptıktan sonra lütfen dekontu ve bağış türünü (zekat, sadaka vb.) şu numaraya iletiniz:\n"
                                    f"📞 **Muhasebe Hattı:** {MUHASEBE_LINK}"
                                )
                                whatsapp_cevap_yolla(gonderen_no, cevap)
                            
                            # Yurt Dışı Kullanıcıları
                            else:
                                cevap = (
                                    "Güzel niyetinizden ötürü Rabbimiz sizlerden razı olsun. 🌸\n\n"
                                    "Sistemimizde numaranızın yurt dışı olduğu görünüyor. Eğer Türk bankalarında hesabınız yoksa, "
                                    "web sitemiz üzerinden güvenli şekilde **Online Bağış** yapabilirsiniz:\n"
                                    f"🌍 **{DERNEK_SITE_BAGIS}**\n\n"
                                    "Detaylı bilgi almak isterseniz WhatsApp hattımızdan bizimle iletişime geçebilirsiniz:\n"
                                    f"📞 {MUHASEBE_LINK}"
                                )
                                whatsapp_cevap_yolla(gonderen_no, cevap)

                        # 3. DİĞER DURUMLAR
                        else:
                            pass

    return jsonify({"status": "success"}), 200

def whatsapp_cevap_yolla(numara, metin):
    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": numara,
        "type": "text",
        "text": {"body": metin}
    }
    try:
        requests.post(url, headers=headers, json=payload)
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
