from django.urls import reverse
from entries.models import Entry
from rest_framework import serializers


class EntrySerializer(serializers.ModelSerializer):
    acc_dr__name = serializers.CharField(max_length=100, read_only=True)
    acc_cr__name = serializers.CharField(max_length=100, read_only=True)
    acc_cr__results = serializers.CharField(max_length=100, read_only=True)
    update_url = serializers.SerializerMethodField()
    read_url = serializers.SerializerMethodField()

    class Meta:
        model = Entry
        fields = ("id", "date", "acc_dr__name", "acc_cr__name", "total", "comment", "acc_cr__results", "update_url", "read_url")

    def get_update_url(self, obj):
        return reverse("entries:update", kwargs={"pk": obj["id"]})

    def get_read_url(self, obj):
        return reverse("entries:read", kwargs={"pk": obj["id"]})


class EntryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entry
        exclude = ("user", "currency")
