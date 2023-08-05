# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
from django.shortcuts import render
from django.views.generic import TemplateView
from django.db.models import Q, F, Sum, Count
from django.db.models import Case, When, Value, CharField
from dss.Serializer import serializer
from django.apps import apps


# from django.
# Create your views here.
def test(request):
    return render(request, 'bee_django_report/report/pie.html', {"title": "统计模版", "subtext": '模拟数据', "data_list": []})

class IndexView(TemplateView):
    template_name = 'bee_django_report/index.html'

class UserGenderView(TemplateView):
    template_name = 'bee_django_report/report/pie.html'
    user_app = 'bee_django_user'
    user_model = 'UserProfile'
    gender_field = 'preuser__gender'
    condition_list = None  # 格式：[{"key": "name", "value": "bee"}]
    gender_list = ((0, "无"), (1, "女"), (2, "男"))
    case_list = [When(preuser__gender=item[0], then=Value(item[1])) for i, item in enumerate(gender_list)]

    def get_context_data(self, **kwargs):
        context = super(UserGenderView, self).get_context_data(**kwargs)
        context["title"] = '学员性别'
        context["subtext"] = ''
        context["data_list"] = self.get_date_list()

        return context

    def get_date_list(self):

        app = apps.get_app_config(self.user_app)
        model = app.get_model(self.user_model)
        kwargs = {}  # 动态查询的字段
        if self.condition_list:
            for i, value in enumerate(self.condition_list):
                kwargs[value["key"]] = value["value"]
        queryset = model.objects.filter(**kwargs).values(self.gender_field).order_by(self.gender_field) \
            .annotate(value=Count(1)) \
            .annotate(name=Case(*self.case_list, default=Value('未填写'), output_field=CharField()))

        return serializer(queryset, output_type='json')


class UserAgeView(TemplateView):
    template_name = 'bee_django_report/report/pie.html'

    def get_context_data(self, **kwargs):
        context = super(UserAgeView, self).get_context_data(**kwargs)
        context["title"] = '学员年龄'
        context["subtext"] = ''
        context["data_list"] = self.get_date_list()

        return context

    def get_date_list(self):
        from bee_django_user.models import UserProfile
        from bee_django_crm.models import PreUser
        from django.db.models import Case, When, Value, CharField, Func, F
        from dss.Serializer import serializer

        # user_list = PreUser.objects.values("birthday").order_by('birthday').annotate(value=Count("birthday")) \
        #     .annotate(age=Func(Func(F(''), function='CURDATE'), function='YEAR') - Func(F('birthday'), function="YEAR"))

        from django.db import connection

        age_list = ((50, "50以上"), (40, "40-50"), (20, "以下"))

        sql = '''
        SELECT COUNT(C.age_group), C.age_group FROM
        (SELECT
          CASE
            WHEN B.age >= 50 THEN '50以上'
            WHEN B.age >= 40 THEN '40-50'
            WHEN B.age >= 30 THEN '30-40'
            WHEN B.age >= 20 THEN '20-30'
            WHEN B.age < 20 THEN '20以下'
            ELSE '无'
          END AS age_group
        FROM
        (SELECT (A.this_year - A.birth_year) AS age
        FROM
        (SELECT EXTRACT(YEAR FROM CURRENT_DATE) AS this_year, EXTRACT(YEAR FROM "bee_django_crm_preuser".birthday) AS birth_year
        FROM "bee_django_user_profile" INNER JOIN "bee_django_crm_preuser" ON "bee_django_user_profile".preuser_id = "bee_django_crm_preuser".id) AS A) AS B ) AS C GROUP BY C.age_group
        '''
        with connection.cursor() as cursor:
            cursor.execute(sql)
            data = cursor.fetchall()

        rc = []
        for i in data:
            rc.append({"name": i[1], "value": i[0]})
        return json.dumps(rc)

        # return [
        #     {"name": 'A1', "value": 12121},
        #     {"name": 'B1', "value": 23231},
        #     {"name": 'C1', "value": 19191}
        # ]
