from api_basics.models import TransactionV2, Wallet
from factory import Sequence, SubFactory, django, post_generation
from users.test.factory import UserFactory


class WalletFactory(django.DjangoModelFactory):
    class Meta:
        model = Wallet

    holder = SubFactory(UserFactory)
    name = Sequence(lambda n: "wallet_{}".format(n))

    @post_generation
    def balance(self, create, extracted, **kwargs):
        if not create:
            return
        self.balance = extracted or 0


class HistoryFactory(django.DjangoModelFactory):
    class Meta:
        model = TransactionV2

    wallet = SubFactory(WalletFactory)
    sender = SubFactory(WalletFactory)
    recipient = SubFactory(WalletFactory)
