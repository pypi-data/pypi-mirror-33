from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User,Group,UserManager
from rest_framework.authtoken.models import  Token



class AccountManager(UserManager):
    def get_queryset(self):
        return super(AccountManager, self).get_queryset().filter(valid=True)

class Account(User):
    display_name = models.CharField(max_length=256,default='',verbose_name='昵称')
    valid = models.BooleanField(default=True)

    objects = AccountManager()

    def auth_token(self):
        token,created = Token.objects.get_or_create(user=self)
        return  token.key

    class Meta:
        abstract = True
        permissions = (
            ('base_account_create', 'account create new account'),
            ('base_account_fix', 'account edit other account'),
            ('base_account_delete', 'account drop other account')
        )

    def save(self, *args, **kwargs):
        if not self.username:
            if self.email:
                self.username = self.email
        super(Account, self).save(*args, **kwargs)
        token = Token.objects.get_or_create(user=self)



class SuperAccount(Account):
    class Meta:
        abstract = False
        db_table = 'super_account'