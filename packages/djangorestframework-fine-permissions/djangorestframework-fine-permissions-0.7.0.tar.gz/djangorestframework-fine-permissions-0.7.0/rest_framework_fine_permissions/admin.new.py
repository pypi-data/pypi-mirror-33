# -*- coding: utf-8 -*-

"""
"""

from collections import OrderedDict

from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.contenttypes.models import ContentType

from django.db.models import Q
from .models import FieldPermission, UserFieldPermissions, FilterPermissionModel
from .utils import get_field_permissions
from .serializers import QSerializer


class UserFieldPermissionsForm(forms.ModelForm):

    """
    """

    permissions = forms.MultipleChoiceField(
        widget=FilteredSelectMultiple(
            verbose_name='User field permissions',
            is_stacked=False,
        )
    )

    class Meta:
        model = UserFieldPermissions
        exclude = ('content_type',)

    def __init__(self, *args, **kwargs):
        super(UserFieldPermissionsForm, self).__init__(*args, **kwargs)

        # Choices
        choice_str = lambda model, field, sep:\
            '{model[0]}{sep}{model[1]}{sep}{field}'\
                .format(model=model.split('.'), field=field, sep=sep)

        choices = []
        for model, fields in get_field_permissions().items():
            choices += [(choice_str(model, field, '.'), choice_str(model, field, ' | '))
                        for field in fields]
        self.fields['permissions'].choices = sorted(choices)

        # Initial datas
        instance = kwargs.get('instance')
        if instance:
            fps = ['.'.join(fp) for fp in instance.permissions.all()
                   .values_list(
                        'content_type__app_label',
                        'content_type__model',
                        'name'
                    )
            ]
            self.initial['permissions'] = fps

#    def save(self, commit=True):
#        form = super(UserFieldPermissionsForm, self).save(commit=False)
#        cleaned = self.cleaned_data
#        print('PPPPPPPPPPPPPPPPOST')
#        field_permissions = []
#        for permission in cleaned['permissions']:
#            app_label, model_name, field = permission.split('.')
#            ct = ContentType.objects.get_by_natural_key(app_label, model_name)
#            fp = FieldPermission.objects.get_or_create(
#                content_type=ct,
#                name=field
#            )[0]
#            field_permissions.append(fp.pk)
#
#        self.cleaned_data['permissions'] = field_permissions
#
#        if commit:
#            form.save()
#            form.save_m2m()
#        print('REEEEEEEEEEET')
#        return form


class UserFieldPermissionsAdmin(admin.ModelAdmin):

    """
    """
    list_display = ('user', )
    form = UserFieldPermissionsForm

    def changelist_view(self, request, extra_context=None):
        summary = OrderedDict()
        cts = ContentType.objects\
            .filter(fieldpermission__user_field_permissions__isnull=False)\
            .order_by('app_label', 'model')\
            .distinct()

        for ct in cts:
            fps = FieldPermission.objects\
                .filter(user_field_permissions__isnull=False, content_type=ct)\
                .prefetch_related("user_field_permissions", "user_field_permissions__user", "content_type")\
                .order_by('content_type__app_label', 'content_type__model', 'name')\
                .distinct()

            perms = OrderedDict((fp.name, fp.user_field_permissions.values_list('user__username', flat=True)) for fp in fps)
            key = '{0.app_label} | {0.model}'.format(ct)
            summary[key] = perms

        extract_context = {'summary': summary}

        return super(UserFieldPermissionsAdmin, self)\
            .changelist_view(request, extra_context=extract_context)

    def save_related(self, request, form, formsets, change):
        if change:
            field_permissions = set()
            permissions = form.instance.permissions
            current_permissions = set(permissions.all().values_list('pk', flat=True))

            for permission in form.cleaned_data['permissions']:
                app_label, model_name, field = permission.split('.')
                ct = ContentType.objects.get_by_natural_key(app_label, model_name)
                fp = FieldPermission.objects.get_or_create(content_type=ct, name=field)[0]
                if fp.pk not in current_permissions:
                    permissions.add(fp)
                    field_permissions.add(fp.pk)
                else:
                    current_permissions.remove(fp.pk)

            # Delete old permissions
            for permission in (current_permissions - field_permissions):
                permissions.remove(permission)


class ContentTypeChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s | %s" % (obj.app_label, obj.model)


class UserFilterPermissionsForm(forms.ModelForm):
    """
    filter permissions form
    """

    current_filter = forms.CharField(required=False)
    content_type = ContentTypeChoiceField(queryset=ContentType.objects.all().order_by('app_label', 'model'))

    class Meta:
        model = FilterPermissionModel
        exclude = []

    def __init__(self, *args, **kwargs):
        form = super(UserFilterPermissionsForm, self).__init__(*args, **kwargs)

        # Initial datas
        instance = kwargs.get('instance')
        self.fields['current_filter'].widget.attrs['readonly'] = True
        self.fields['current_filter'].widget.attrs['size'] = 130

        if instance:
            myq = QSerializer(base64=True).loads(instance.filter)
            current_filter = myq.__str__()
        else:
            myq = Q(myfield="myvalue")
            current_filter = ""

        self.initial['current_filter'] = current_filter
        self.initial['filter'] = QSerializer().dumps(myq)

        self.fields['filter'].widget.attrs['rows'] = len(self.initial['filter'].splitlines()) + 4

    def clean_filter(self):
        data = self.cleaned_data['filter']
        if data:
            try:
                myq = QSerializer().loads(data)
            except:
                raise forms.ValidationError("filter is not a valid entry for a q object !")
            else:
                if isinstance(myq, Q):
                    data = QSerializer(base64=True).dumps(myq)
                else:
                    raise forms.ValidationError("filter is not a q object !")

        return data

    def save(self, commit=True):
        form = super(UserFilterPermissionsForm, self).save(commit=False)

        if commit:
            form.save()
            form.save_m2m()

        return form


class UserFilterPermissionsAdmin(admin.ModelAdmin):
    """
    filter permissions admin
    """
    list_display = ('user', 'content_type')
    form = UserFilterPermissionsForm


admin.site.register(UserFieldPermissions, UserFieldPermissionsAdmin)
admin.site.register(FilterPermissionModel, UserFilterPermissionsAdmin)
