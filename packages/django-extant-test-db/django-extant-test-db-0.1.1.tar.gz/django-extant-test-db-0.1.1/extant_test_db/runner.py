from django.test.runner import DiscoverRunner as BaseDiscoverRunner

try:
    # Pre-Django 1.8
    from django.test.runner import dependency_ordered
except:
    # Django 1.8+
    from django.test.util import dependency_ordered



class DiscoverRunner(BaseDiscoverRunner):
    """
    A Django test runner that uses unittest2 test discovery, and can test
    against a pre-existing database when configured to do so. In order to
    use an extant database for tests (e.g., if you have a large database
    full of read-only data), in your database TEST settings, set a MANAGED
    flag:

        DATABASES = {
            'default': {
                ...
            },
            'warehouse': {
                ...

                'TEST': {
                    'MANAGED': False,
                },
            }
        }

    The database used will be the same as the one used for the webserver,
    though you can also provide an alternative test database name:

        DATABASES = {
            ...
                'TEST': {
                    'MANAGED': False,
                    'NAME': os.environ['TEST_DB_NAME'],
                },
            ...
        }

    """

    def setup_databases(self, **kwargs):
        return setup_databases(
            self.verbosity, self.interactive, self.keepdb, self.debug_sql,
            **kwargs
        )


def setup_databases(verbosity, interactive, keepdb=False, debug_sql=False, **kwargs):
    from django.db import connections, DEFAULT_DB_ALIAS

    # First pass -- work out which databases actually need to be created,
    # and which ones are test mirrors or duplicate entries in DATABASES
    mirrored_aliases = {}
    test_databases = {}
    dependencies = {}
    default_sig = connections[DEFAULT_DB_ALIAS].creation.test_db_signature()
    for alias in connections:
        connection = connections[alias]
        test_settings = connection.settings_dict['TEST']
        if test_settings['MIRROR']:
            # If the database is marked as a test mirror, save
            # the alias.
            mirrored_aliases[alias] = test_settings['MIRROR']
        else:
            # Store a tuple with DB parameters that uniquely identify it.
            # If we have two aliases with the same values for that tuple,
            # we only need to create the test database once.
            item = test_databases.setdefault(
                connection.creation.test_db_signature(),
                (connection.settings_dict['NAME'], set())
            )
            item[1].add(alias)

            if 'DEPENDENCIES' in test_settings:
                dependencies[alias] = test_settings['DEPENDENCIES']
            else:
                if alias != DEFAULT_DB_ALIAS and connection.creation.test_db_signature() != default_sig:
                    dependencies[alias] = test_settings.get('DEPENDENCIES', [DEFAULT_DB_ALIAS])

    # Second pass -- actually create the databases.
    old_names = []
    mirrors = []

    for signature, (db_name, aliases) in dependency_ordered(
            test_databases.items(), dependencies):

        # Actually create the database for the first connection
        for alias in aliases:
            connection = connections[alias]

            # ===== ===== ===== ===== ===== ===== ===== ===== ===== =====
            # Here is where this setup_databases function differs from
            # django.test.runner.setup_databases. It takes into account
            # the MANAGED flag under the TEST settings for the database.
            #
            test_settings = connection.settings_dict.get("TEST", {})
            test_db_managed = test_settings.get("MANAGED", True)
            if test_db_managed:
                test_db_name = None
            else:
                test_db_name = test_settings.get("NAME") or connection.settings_dict['NAME']
            #
            # ===== ===== ===== ===== ===== ===== ===== ===== ===== =====

            if test_db_name is None:
                test_db_name = connection.creation.create_test_db(
                    verbosity,
                    autoclobber=not interactive,
                    keepdb=keepdb,
                    serialize=connection.settings_dict.get("TEST", {}).get("SERIALIZE", True),
                )
                destroy = True
            else:
                connection.settings_dict['NAME'] = test_db_name
                destroy = False
            old_names.append((connection, db_name, destroy))

    for alias, mirror_alias in mirrored_aliases.items():
        mirrors.append((alias, connections[alias].settings_dict['NAME']))
        connections[alias].settings_dict['NAME'] = (
            connections[mirror_alias].settings_dict['NAME'])

    if debug_sql:
        for alias in connections:
            connections[alias].force_debug_cursor = True
    return old_names, mirrors
