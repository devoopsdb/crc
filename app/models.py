from django.db import models
from django.urls import reverse


class CableCal(models.Model):
    order_num = models.CharField(max_length=50, unique=True, db_index=True, verbose_name='Sifarişin nömrəsi')
    cod = models.TextField(verbose_name='Kabelin kodu')
    name = models.TextField(db_index=True, verbose_name='Kabelin adı')
    mass = models.TextField(verbose_name='Kabelin çəkisi, kq/m')
    diameter = models.TextField(verbose_name='Kabelin xarici diametri, mm')
    con_num = models.TextField(verbose_name='Kabelin cəriyan keçirən damarların sayı')
    order_len = models.TextField(verbose_name='sifarişin uzunluğu, m')
    max_len = models.TextField(verbose_name='maksimal istehsalat uzunluğu, m')
    transport = models.ForeignKey('TransportList', null=True, blank=False, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Yaradılma tarixi')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Yeniləmə tarixi')
    reel_name = models.TextField(verbose_name='Baraban adı', blank=True)
    reel_type = models.TextField(verbose_name='Baraban növü', blank=True)
    reel_num = models.TextField(verbose_name='Baraban sayı', blank=True)
    reel_len = models.TextField(verbose_name='Bir barabana dolanan miqdar, m', blank=True)
    bending_radius = models.TextField(verbose_name='Əyilmə radiusu', blank=True)
    netto_1 = models.TextField(verbose_name='Netto 1 baraban', blank=True)
    brutto_1 = models.TextField(verbose_name='Brutto 1 baraban', blank=True)
    netto_all = models.TextField(verbose_name='Netto ümumi', blank=True)
    brutto_all = models.TextField(verbose_name='Brutto ümumi', blank=True)

    def get_absolute_url(self):
        return reverse('cable_detail', kwargs={"pk": self.pk})

    def __str__(self):
        return self.order_num

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']


class ReelsList(models.Model):
    name = models.CharField(max_length=50, verbose_name='Barabanın adı')
    height = models.IntegerField(verbose_name='Barabanın hündürlükü abşıvkalı, mm')
    width = models.IntegerField(verbose_name='Barabanın eni, mm')
    diameter = models.IntegerField(verbose_name='Barabanın diametri, mm')
    diameter_neck = models.IntegerField(verbose_name='Barabanın boğazının diametiri, mm')
    length_neck = models.IntegerField(verbose_name='Barabanın bogazının uzunluğu, mm')
    max_load = models.IntegerField(verbose_name='Maksimal yükləmə, kq')
    mass = models.IntegerField(verbose_name='Barabanın çəkisi, kq')
    reel_type = models.ForeignKey('ReelType', verbose_name='Barabanın növü', null=True, blank=True, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Yaradılma tarixi')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Yeniləmə tarixi')

    def get_absolute_url(self):
        return reverse('reels_list_detail', args=[str(self.pk)])
        # return reverse('reels_list_detail', kwargs={"pk": self.pk})

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Reel'
        verbose_name_plural = 'Reels'
        ordering = ['name']


class ReelType(models.Model):
    name = models.CharField(max_length=50, verbose_name='Barabanın növü')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Yaradılma tarixi')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Yeniləmə tarixi')

    def get_absolute_url(self):
        return reverse('reels_list', kwargs={"pk": self.pk})

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Reel Type'
        verbose_name_plural = 'Reel Types'
        ordering = ['name']


class TransportList(models.Model):
    name = models.CharField(max_length=50, verbose_name='Nəqliyətin adı')
    length = models.IntegerField(verbose_name='Uzunluq, mm')
    width = models.IntegerField(verbose_name='En, mm')
    height = models.IntegerField(verbose_name='Hündürlük, mm')
    max_load = models.IntegerField(verbose_name='maksimal yükləmə, kq')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Yaradılma tarixi')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Yeniləmə tarixi')

    def get_absolute_url(self):
        return reverse('transport_list_detail', kwargs={"pk": self.pk})

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Transport'
        verbose_name_plural = 'Transports'
        ordering = ['created_at']

