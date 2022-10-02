from Utilities.Utils import Utils as utils
from Utilities.config import props


class PSGC_OLD:

    def __init__(self) -> None:
        self.df = utils.read_csv(props['psgc_old']['dir'])