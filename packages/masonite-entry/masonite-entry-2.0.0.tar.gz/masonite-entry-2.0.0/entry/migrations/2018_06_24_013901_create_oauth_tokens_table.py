from orator.migrations import Migration


class CreateOauthTokensTable(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('oauth_tokens') as table:
            table.increments('id')
            table.string('user_id', 45)
            table.string('token', 255).nullable()
            table.string('code', 255)
            table.string('refresh_token', 255).nullable()
            table.string('scopes', 255).nullable()
            table.datetime('expires_at').nullable()
            table.datetime('refresh_expires_at').nullable()
            table.timestamps()

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('oauth_tokens')
