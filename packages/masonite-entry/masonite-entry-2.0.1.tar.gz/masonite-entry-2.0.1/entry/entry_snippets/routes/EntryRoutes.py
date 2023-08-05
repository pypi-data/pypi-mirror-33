
# Entry Web Routes
from entry.api.TokenAuthentication import TokenAuthentication

ROUTES += TokenAuthentication.routes()