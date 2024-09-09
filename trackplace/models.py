from django.db import models

class CulturewalkTable(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    ctprvn_nm = models.CharField(max_length=255)
    signgu_nm = models.CharField(max_length=255)
    legaldong_nm = models.CharField(max_length=255)
    fclty_nm = models.CharField(max_length=255)
    mlsfc_nm = models.CharField(max_length=255)
    adr_nm = models.CharField(max_length=255)

    class Meta:
        db_table = 'culturewalk_table'  # 데이터베이스의 테이블 이름을 명시적으로 지정
