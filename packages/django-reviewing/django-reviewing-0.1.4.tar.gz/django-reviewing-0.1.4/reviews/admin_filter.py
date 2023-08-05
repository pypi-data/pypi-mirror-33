from django.contrib import admin
from django.contrib.contenttypes.models import ContentType


def get_generic_foreign_key_filter(title, parameter_name=u'', separator='-', content_type_id_field='content_type', object_id_field='object_id'):
    class GenericForeignKeyFilter(admin.SimpleListFilter):
        def __init__(self, request, params, model, model_admin):
            self.separator = separator
            self.title = title
            self.parameter_name = u'generic_foreign_key_' + parameter_name
            super(GenericForeignKeyFilter, self).__init__(request, params, model, model_admin)

        def lookups(self, request, model_admin):
            qs = model_admin.model.objects.all().order_by(content_type_id_field, object_id_field).distinct(content_type_id_field, object_id_field).values_list(content_type_id_field, object_id_field)

            lookups_list = []
            for content_type_and_obj_id_pair in qs:
                content_type = content_type_and_obj_id_pair[0]
                obj_id = content_type_and_obj_id_pair[1]

                if content_type and obj_id:
                    lookups_list.append((
                        '{1}{0.separator}{2}'.format(self, *content_type_and_obj_id_pair),
                        ContentType.objects.get(id=content_type).model_class().objects.get(pk=obj_id).__str__()
                    ))

            return lookups_list

        def queryset(self, request, queryset):
            try:
                content_type_id, object_id = self.value().split(self.separator)
                return queryset.filter(**({
                    content_type_id_field: content_type_id,
                    object_id_field: object_id,
                }))
            except:
                return queryset

    return GenericForeignKeyFilter
