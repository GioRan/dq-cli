import pandas

from Utilities.Utils import Utils as utils
from Utilities.config import props


class PSGC_NEW:

    def __init__(self) -> None:
        self.df = utils.read_csv(props['psgc_new']['dir'])

        self.df['concat'] = self.df[['PostCode', 'Barangay/District', 'City', 'Province']].agg('_'.join, axis=1)

    def match(self, val: str, column_name: str) -> pandas.DataFrame:
        return self.df[self.df[column_name].str.upper() == val.upper()]