import django_tables2 as tables
from django.utils.safestring import mark_safe


class CosmicModelTable(tables.Table):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.empty_text = self.get_empty_text()
        row_onclick = self.get_row_onclick()
        self.row_attrs = {
            'data-id': lambda record: record.pk,
            'onclick': mark_safe(row_onclick),
            'class': 'table-row',
        }

    def get_empty_text(self):
        return "No " + str(self._meta.model._meta.verbose_name_plural)

    def get_row_onclick_url(self):
        temp_customer_for_url_replace = self._meta.model(pk=0)
        return temp_customer_for_url_replace.get_absolute_url()
    
    def get_row_onclick(self):
        return "temp_url = '"+self.get_row_onclick_url()+"';var url = temp_url.substr(0,temp_url.length-2)+$(this).data('id')+'/';window.location.href = url;"


row_onclick = "if(window.hasOwnProperty('goTo')){if(typeof window.goTo === 'function'){goTo(this);}}"

class MessageTable(tables.Table):
    read = tables.Column(attrs={'th': {'class': 'read_column',}}, order_by='read')
    short_message = tables.Column(verbose_name="Message", order_by='message')
    created_at = tables.Column(verbose_name="Received At")
    def render_read(self, record):
        html = '<i class="fa fa-envelope"></i>'
        if record.read:
            html = '<i class="fa fa-envelope-o"></i>'
        return mark_safe(html)
    def render_short_message(self, record, value):
        html = record.image_tag() + ' ' + value
        return mark_safe(html)
    class Meta:
        empty_text = "No messages"
        row_attrs = {
            'data-id': lambda record: record.pk,
            'onclick': row_onclick,
            'class': 'table-row',
        }


class NotificationTable(tables.Table):
    read = tables.Column(attrs={'th': {'class': 'read_column',}}, order_by='read')
    short_notification = tables.Column(verbose_name="Message", order_by='notification')
    created_at = tables.Column(verbose_name="Received At")
    def render_read(self, record):
        html = '<i class="fa fa-envelope"></i>'
        if record.read:
            html = '<i class="fa fa-envelope-o"></i>'
        return mark_safe(html)
    def render_short_notification(self, record, value):
        icon = ''
        if record.icon_class:
            icon = '<i class="%s"></i>' % record.icon_class
        html = icon + value
        return mark_safe(html)
    class Meta:
        empty_text = "No notifications"
        row_attrs = {
            'data-id': lambda record: record.pk,
            'onclick': row_onclick,
            'class': 'table-row',
        }
