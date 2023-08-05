from orator.migrations import Migration


class CreateOauthScopesTable(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('oauth_scopes') as table:
            table.increments('id')
            table.string('name', 45)
            table.text('description').nullable()
            table.timestamps()

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('oauth_scopes')
