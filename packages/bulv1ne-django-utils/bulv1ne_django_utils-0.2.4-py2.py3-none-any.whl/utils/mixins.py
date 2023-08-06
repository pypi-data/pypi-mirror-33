from .signing import sign, unsign


class SignedPkMixin(object):
    def get_pk(self):
        try:
            return self.kwargs['pk']
        except KeyError:
            return unsign(self.kwargs['pk_signed'])

    def get_pk_signed(self):
        try:
            return self.kwargs['pk_signed']
        except KeyError:
            return sign(self.kwargs['pk'])
