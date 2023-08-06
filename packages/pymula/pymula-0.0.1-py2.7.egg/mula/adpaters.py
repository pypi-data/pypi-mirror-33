import requests


class MulaAdapter(object):

    SANDBOX_DOMAIN = 'https://beep2.cellulant.com:9001/'

    AUTH_PATH = '/CheckoutV2/checkoutPublicAPI/oauth/token'
    PAYMENT_OPTIONS_PATH = '/CheckoutV2/checkoutPublicAPI/api/payment/options/' \
                           '{client_code}?countryCode={country}&languageCode={language}'
    INITIATE_PAYMENT_PATH = '/CheckoutV2/checkoutPublicAPI/api/transaction'
    PAYMENT_DETAILS_PATH = '/CheckoutV2/checkoutPublicAPI/api/transaction/payment-details'

    def __init__(self, client_id, client_secret, client_code):

        self.client_id = client_id
        self.client_secret = client_secret
        self.client_code = client_code
        self.domain = self.SANDBOX_DOMAIN

    def get_access_token(self):
        url  = "{}{}".format(self.domain, self.AUTH_PATH)

        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'
        }

        response = requests.post(url, payload)
        return response.json().access_token

    def get_payment_options(self):

        path = self.PAYMENT_OPTIONS_PATH.format(
            client_code=self.client_code,
            country='KE',
            languange='en'
        )
        url = "{}{}".format(self.domain, path)
        token = self.get_access_token()
        response = requests.get(url, auth="Bearer {}".format(token))
        print response

    def initiate_transaction(self,
                             msisdn,
                             transaction_reference_id,
                             account_number,
                             amount,
                             currency_code='KES',
                             country_code='KE',
                             payment_method='MPESA',
                             language='en',
                             payment_option='Mobile Money',
                             payment_mode='push notification',
                             callback_url=None):

        url = "{}{}".format(self.domain, self.INITIATE_PAYMENT_PATH)
        token = self.get_access_token()

        payload = {
            "MSISDN": msisdn,
            "payerClientCode": payment_method,
            "serviceCode": self.client_code,
            "countryCode": country_code,
            "transactionReferenceID": transaction_reference_id,
            "paymentOptionCode": payment_option,
            "paymentMode": payment_mode,
            "currencyCode": currency_code,
            "amount": amount,
            "accountNumber": account_number,
            "language": language,
        }
        if callback_url:
            payload['callBackUrl'] = callback_url

        response = requests.post(url, payload, auth="Bearer {}".format(token))


