# Embedded file name: scripts/client/CAPTCHA/Kong.py
from CAPTCHA.CAPTCHABase import CAPTCHABase
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION, LOG_DEBUG
import time
import urllib

class Kong(CAPTCHABase):
    _SERVER_API_URL = 'http://katpcha.worldoftanks.cn:8081'
    _SERVER_ERROR_CODES = {'unknown': '#kong_captcha:error-codes/unknown',
     'empty response': '#kong_captcha:error-codes/empty-response',
     'wrong response': '#kong_captcha:error-codes/wrong-response',
     'invalid challenge code': '#kong_captcha:error-codes/invalid-challenge-code'}
    _RESPONSE_IS_INCORRECT_CODE = 'wrong response'
    _IMAGE_SIZE = (300, 60)

    def getImageSource(self, publicKey, *args):
        """
        Gets image binary source for Kong Captcha.
        @param publicKey: CAPTCHA public key
        @param args:
        @return: tuple(<image url>, <value of challenge>). If an error occurs while loading or parsing, than routine return (None, None)
        """
        start = time.time()
        pic = None
        challenge = ''
        resp = None
        try:
            resp = urllib.urlopen('%s/captcha.jsp' % self._SERVER_API_URL)
            challenge = resp.read()
            params = urllib.urlencode({'s': challenge})
            resp = urllib.urlopen('%s/verifyCodeServlet?%s' % (self._SERVER_API_URL, params))
            contentType = resp.headers.get('content-type')
            if contentType == 'image/jpeg':
                pic = resp.read()
            else:
                LOG_ERROR('Client can not load reCAPTCHA image. contentType = {0}, response code = {1}'.format(contentType, resp.code))
        except:
            LOG_ERROR('client can not load KONG CAPTCHA image')
            LOG_CURRENT_EXCEPTION()
        finally:
            if resp is not None:
                resp.close()

        LOG_DEBUG('get image from web for %.02f seconds' % (time.time() - start))
        return (pic, challenge)