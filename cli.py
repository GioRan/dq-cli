import click

# from Commands.AddressCleansing.main import cli as address_cleansing
from Commands.GoogleDriveAPI.main import cli as gdrive
from Commands.PSGCValidation.main import cli as psgc_validation
from Commands.PollAddress.main import cli as poll
from Commands.TopErrors.main import cli as top_errors
from Utilities.Utils import Utils as utils

utils.init_logger()


@click.group()
def entry_point():
    pass


if __name__ == '__main__':
    # entry_point.add_command(address_cleansing)
    entry_point.add_command(top_errors)
    entry_point.add_command(psgc_validation)
    entry_point.add_command(poll)
    entry_point.add_command(gdrive)

    entry_point()
