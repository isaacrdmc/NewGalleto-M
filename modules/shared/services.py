# import requests

# def verify_recaptcha(response):
#     secret_key = "TU_CLAVE_SECRETA"
#     payload = {'secret': secret_key, 'response': response}
#     r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=payload)
#     return r.json().get('success', False)