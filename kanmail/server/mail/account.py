from kanmail.log import logger

from .connection import ImapConnectionPool, SmtpConnection
from .folder import Folder
from .send import send_email


class Account(object):
    def __init__(self, name, settings):
        self.name = name

        # Map of folder name -> Folder object
        self.folders = {}
        self.query_folders = {}

        # Set the settings
        self.settings = settings

        # Setup/wrap IMAP connection
        self.connection_pool = ImapConnectionPool(
            **settings['imap_connection'],
        )

        # Prepare SMTP connection getter
        self.smtp_connection = SmtpConnection(
            **settings['smtp_connection'],
        )

        with self.connection_pool.get_connection() as connection:
            self.capabilities = connection.capabilities()
            logger.debug(f'Connected to {self.name}, capabilities: {self.capabilities}')

    def get_imap_connection(self):
        return self.connection_pool.get_connection()

    def get_smtp_connection(self):
        return self.smtp_connection.get_connection()

    def get_folders(self):
        '''
        List all available folders for this account.
        '''

        folder_names = []

        with self.get_imap_connection() as connection:
            for flags, delimeter, name in connection.list_folders():
                folder_names.append(name)

        return folder_names

    def get_folder(self, folder, query=None):
        '''
        Get a Folder object for this account.
        '''

        folder_name = folder
        if folder in self.settings['folders']:
            folder_name = self.settings['folders'][folder]

        # Is this a temporary query-based folder?
        cache = self.query_folders if query else self.folders
        cache_key = ''.join((folder_name, query)) if query else folder_name

        if cache_key not in cache:
            cache[cache_key] = Folder(
                folder_name, folder,
                account=self,
                query=query,
            )

        return cache[cache_key]

    def ensure_folder_exists(self, folder):
        folder = self.get_folder(folder)

        if not folder.exists:
            logger.debug(f'Creating folder {self.name}/{folder.name}')

            with self.get_connection() as connection:
                connection.create_folder(folder.name)

            # Reload the folder
            folder.reset()

        return folder.name

    def send_email(self, **send_kwargs):
        return send_email(self.smtp_connection, **send_kwargs)
