from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin

from telebaka_lprmerch_poll.models import PollUser, CustomVariant, Product


@admin.register(PollUser)
class PollUserAdmin(admin.ModelAdmin):
    pass


@admin.register(CustomVariant)
class CustomVariantAdmin(admin.ModelAdmin):
    pass


@admin.register(Product)
class ProductAdmin(SortableAdminMixin, admin.ModelAdmin):
    pass
