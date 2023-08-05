from orator.migrations import Migration


class CreateOauthAppsTable(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('oauth_apps') as table:
            table.increments('id')
            table.string('name', 45)
            table.text('description').nullable()
            table.string('client_id', 45)
            table.string('client_secret', 45)
            table.string('redirect_uri', 45).nullable()
            table.timestamps()

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('oauth_apps')
