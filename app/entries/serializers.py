from entries.models import Entry
from rest_framework import serializers


class EntrySerializer(serializers.ModelSerializer):
    acc_dr__name = serializers.CharField(max_length=100, read_only=True)
    acc_cr__name = serializers.CharField(max_length=100, read_only=True)
    acc_cr__results = serializers.CharField(max_length=100, read_only=True)

    class Meta:
        model = Entry
        fields = ("id", "date", "acc_dr__name", "acc_cr__name", "total", "comment", "acc_cr__results")


class EntryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entry
        fields = "__all__"
