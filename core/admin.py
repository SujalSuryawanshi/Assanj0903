from django.contrib import admin
from .models import Staller, MenuItems, Category,Subcat, Egit, Following, Rating, Foo_Category, New_offer, Rater
from embed_video.admin import AdminVideoMixin

class MyModelAdmin(AdminVideoMixin, admin.ModelAdmin):
    pass


class StallerAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'address', 'contact', 'timings', 'rating', 'least_price']
    filter_horizontal = ('categories',)  


admin.site.register(Staller, MyModelAdmin)
admin.site.register(MenuItems)
admin.site.register(Egit)
admin.site.register(Category)
admin.site.register(Subcat)
admin.site.register(Following)
admin.site.register(Rating)
admin.site.register(Foo_Category)
admin.site.register(New_offer)
admin.site.register(Rater)
