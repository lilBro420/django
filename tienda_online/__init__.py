from django.db.backends.mysql.base import DatabaseWrapper
from django.db.backends.mysql.features import DatabaseFeatures

# Omitir la comprobacion estricta de version de MariaDB (para compatibilidad con XAMPP / MariaDB 10.4)
DatabaseWrapper.check_database_version_supported = lambda self: None

# MariaDB 10.4 no soporta la clausula RETURNING en INSERT
DatabaseFeatures.can_return_columns_from_insert = property(lambda self: False)
DatabaseFeatures.can_return_rows_from_bulk_insert = property(lambda self: False)

