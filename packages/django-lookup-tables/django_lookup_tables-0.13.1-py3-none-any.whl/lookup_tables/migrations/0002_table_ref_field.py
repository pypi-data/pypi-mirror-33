# Generated by Django 2.0.4 on 2018-06-04 23:41

from django.db import migrations, models
import django.db.models.deletion
from django.utils import text


def set_initial_table_ref(apps, schema_editor):
    LookupTable = apps.get_model('lookup_tables', 'LookupTable')
    for lt in LookupTable.objects.filter(table_ref=None):
        lt.table_ref = text.slugify(lt.name)
        lt.save()


class Migration(migrations.Migration):

    dependencies = [
        ('lookup_tables', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='lookuptable',
            name='table_ref',
            field=models.CharField(default=None, null=True, editable=False, max_length=100),
        ),
        migrations.RunPython(set_initial_table_ref, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='lookuptable',
            name='table_ref',
            field=models.CharField(editable=False, max_length=100, unique=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='lookuptableitem',
            name='table',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, to='lookup_tables.LookupTable'),
        ),
    ]
