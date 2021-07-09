DOMAIN = "fordpass_china"
STATES_MANAGER = "states_manager"
FORD_VEHICLES = "ford_vehicles"
ACCOUNTS = "accounts"
SSO_URL = "https://sso.ci.ford.com.cn/"
CV_URL = "https://cnapi.cv.ford.com.cn/"
API_URL = "https://cn.api.mps.ford.com.cn/"

DEFAULT_SCAN_INTERVAL = 5

CLIENT_ID = "6487f540-5f6b-4c04-8384-23827b00b4ba"
APPLICATION_ID = "46409D04-BD1B-40C6-9D51-13A52666E9F9"

DEFAULT_HEADERS = {
    "Accept": "*/*",
    "Accept-Language": "en-us",
    "User-Agent": "fordpass-ap/93 CFNetwork/1197 Darwin/20.0.0",
    "Accept-Encoding": "gzip, deflate, br",
}

API_HEADERS = {
    **DEFAULT_HEADERS,
    "Content-Type": "application/json",
    "Application-Id": APPLICATION_ID
}