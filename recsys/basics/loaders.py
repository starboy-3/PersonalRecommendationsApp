from functools import reduce
import re
import string

import pandas.io.sql as sqlio   # DB  -> dataframe
from pandas import read_csv     # csv -> dataframe

from nltk.stem.snowball import SnowballStemmer


class StemmerWrapper:
    """ Class wrapper to some language stemmer; Via wrapping, I think,
        it is comfortable to operate with stemmer and functions,
        that formats text for systems.
    """
    def __init__(self, lang="russian"):
        """
        :param lang: Initializing stemmer with setting `lang` language
        """
        self.stemmer = SnowballStemmer(lang)

    def stem(self, *args, **kwargs):
        """ just for beauty and comfortable call"""
        return self.stemmer.stem(*args, **kwargs)

    @staticmethod
    def clean_string(sample_s: str) -> str:
        """
        :param sample_s: string to be formatted
        :return: formatted string
        formats given string by removing unnecessary components for
        building recommendation systems
        """
        # string to lowercase
        sample_s = sample_s.strip().lower()
        # removing one-symbol words
        sample_s = re.sub(r'\b[ЁёА-я]{1}\b', '', sample_s)
        # removing punctuation
        sample_s = re.sub(r'[%s]' % re.escape(string.punctuation), ' ',
                          sample_s)
        # removing one-digit numbers
        sample_s = re.sub(r'\b[0-9]{1}\b', '', sample_s)
        # replacing several-in-a-row space symbols with only one space
        sample_s = re.sub(r'\s+', ' ', sample_s)
        return sample_s.strip()


class Loader:
    """
    Class represents data-loader for systems. This is a base-class,
    so some virtual function must be overwritten.
    """
    def __init__(self, stemmer):
        """
        :param stemmer: language stemmer to be used
        """
        self.stemmer = stemmer

    def merge_contents(self,
                       table: str,
                       main_id: str,
                       content_cname: str,
                       columns: list):
        """
        merges content of selected `columns` from `table`;
        check overwritten function for more info.
        """
        pass

    @staticmethod
    def split_series(series):
        """
        :return: (pd.core.series.Series) updated `series`-copy
        :param series: (pd.core.series.Series)
        Splitting values in cell's of column `series` (in-place)
        """
        # handling None values separately
        return series.apply(lambda x: x.split() if type(x) == str else [])

    def format_columns(self,
                       dataframe,
                       main_id_cname: str,
                       content_cname: str,
                       columns: list):
        """
        :param dataframe: contains data to be formatted and used
        :param main_id_cname: item-representing-column's name
        :param content_cname: content-representing-column's name
        :param columns: names of columns in dataframe
        :return: 2-column dataframe, named as main_id_cname and
            content_cname; second columns contains formatted
            and merged `columns` content
        """
        # initializing new column in dataframe with empty strings
        dataframe[content_cname] = ''

        # remember items-id-representing column
        id_series = dataframe[main_id_cname]

        # set dataframe to a `columns`-containing table,
        # where all string infos was split into lists
        dataframe = dataframe[[content_cname] + columns].apply(
                self.split_series)

        # formatting all rows
        # firstly, we put add all lists to content containing column
        dataframe[content_cname] = reduce(
                lambda prev, el: prev + dataframe[el],
                columns,
                dataframe[content_cname]
        ).apply(  # then we would stem all words in this column
                lambda iterable: [self.stemmer.stem(w) for w in iterable]
        ).apply(  # lastly, we join lists to string
                lambda iterable: ' '.join(iterable)
        ).apply(
                StemmerWrapper.clean_string
        )

        # set item-representing-column's data
        dataframe[main_id_cname] = id_series

        # return table representing relationship item
        return dataframe[[main_id_cname, content_cname]]

    def parse(self, table: str, columns: list):
        """
        parses selected `columns` from `table`;
        check overwritten function for more info.
        """
        pass


class DataBaseLoader(Loader):
    """
    Represents data-loader from postgresql-database
    """
    def __init__(self, stemmer, connection):
        """
        :param stemmer: language stemmer to be used
        :param connection: connection to database
            (only SELECT command will be used my class)
        """
        super().__init__(stemmer)
        self.connection = connection

    def merge_contents(self,
                       table: str,
                       main_id_cname: str,
                       content_cname: str,
                       columns: list):
        """
        :param table: (str) table name, where from data will be read
        :param main_id_cname: (str) item-representing-column's name;
            it is explicit for `table` to have such column
        :param content_cname: (str) content-representing-column's name
        :param columns: (list) columns containing main content,
            that will be used to build a content-based model
        :return: (pd.core.frame.DataFrame) 2-column dataframe
            representing relationship of item and it's content
            (one-to-one relationship)
        """
        return self.format_columns(
                self.parse(table,
                           columns + [main_id_cname]),
                main_id_cname,
                content_cname,
                columns
        )

    def parse(self, table: str, columns: list):
        """
        :param table: database table name
        :param columns: columns to be parsed
        :return: dataframe with parsed columns
        """
        sql = "select {0} from {1};".format(
                ','.join(columns),
                table
        )
        return sqlio.read_sql_query(
                sql,
                self.connection
        )


class CsvLoader(Loader):
    """
    Represents data-loader from csv-file
    """
    def __init__(self, stemmer):
        """
        :param stemmer: language stemmer to be used
        """
        super().__init__(stemmer)

    def merge_contents(self,
                       path: str,
                       main_id_cname: str,
                       content_cname: str,
                       columns: list):
        """
        :param path: (str) path to table, where from data will be read
        :param main_id_cname: (str) item-representing-column's name;
            it is explicit for `path` to have such column
        :param content_cname: (str) content-representing-column's name
        :param columns: (list) columns containing main content,
            that will be used to build a content-based model
        :return: (pd.core.frame.DataFrame) 2-column dataframe
            representing relationship of item and it's content
            (one-to-one relationship)
        """
        return self.format_columns(
                self.parse(path, columns + [main_id_cname]),
                main_id_cname,
                content_cname,
                columns
        )

    def parse(self, table: str, columns: list):
        """
        :param table: database table name
        :param columns: columns to be parsed
        :return: dataframe with parsed columns
        """
        return read_csv(
                table,
                skipinitialspace=True,
                usecols=columns
        )
