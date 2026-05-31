from django.contrib import admin
from myapp.models import product,usreg
# Register your models here.
class adminproduct(admin.ModelAdmin):
    list_display =('id','tpcode','tpname','tfile','tprice','tstock')
admin.site.register(product,adminproduct)

class adminusreg(admin.ModelAdmin):
    list_display =('id','fn','email','phoneno','un','psw','cpws')
admin.site.register(usreg,adminusreg)