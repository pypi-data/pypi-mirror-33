import base64

from django.core.signing import Signer, TimestampSigner


def fix_missing_padding(s):
    # For some reason, some browsers go to the url without the padding =
    missing_padding = len(s) % 4
    if missing_padding != 0:
        s += '=' * (4 - missing_padding)
    return s


class UrlSafeMixin(object):
    def sign(self, value):
        value = super().sign(str(value)).encode('utf-8')
        return base64.urlsafe_b64encode(value).decode('utf-8')

    def unsign(self, value, *args, **kwargs):
        value = base64.urlsafe_b64decode(fix_missing_padding(value)).decode('utf-8')
        return super().unsign(value, *args, **kwargs)


class UrlSafeTimestampSigner(UrlSafeMixin, TimestampSigner):
    pass


class UrlSafeSigner(UrlSafeMixin, Signer):
    pass


default_signer = UrlSafeTimestampSigner()
sign = default_signer.sign
unsign = default_signer.unsign
