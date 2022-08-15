from financez.models import Entry
from rest_framework import serializers


class EntrySerializer(serializers.ModelSerializer):
    acc_dr__name = serializers.CharField(max_length=100)
    acc_cr__name = serializers.CharField(max_length=100)
    acc_cr__results = serializers.CharField(max_length=100)

    class Meta:
        model = Entry
        fields = ("id", "date", "acc_dr__name", "acc_cr__name", "total", "comment", "acc_cr__results")
