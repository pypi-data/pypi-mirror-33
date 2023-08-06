from rethinkdb.errors import *  # noqa
from rethinkdb.errors import ReqlError


class ReqlProgrammingError(ReqlError):
    """Exception raised for programming errors, e.g.
    insert/update/replace/delete response with errors."""

    def __init__(self, response, term=None, frames=None):
        errors = response['errors']
        first_error = response.get('first_error', '')
        msg = f'{first_error} (...total {errors} errors)'
        super().__init__(msg, term=term, frames=frames)
        self.response = response
