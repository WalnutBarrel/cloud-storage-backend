from django.db.models import F
from .models import StorageAccount

def pick_storage_account(file_size):
    account = StorageAccount.objects.filter(
        used_bytes__lt=F("limit_bytes") - file_size
    ).order_by("used_bytes").first()

    if not account:
        raise Exception("All storage accounts are full")

    return account
