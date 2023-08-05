from .exceptions import InvalidGranuleException
import re
import datetime


class Granule(object):
    """Base class granuel object. pattern needs to be a regex with the same
    number of groups as the length of attributes"""

    def __init__(self, pattern, granule_string, attributes):
        m = re.search(pattern, granule_string)
        if m is None:
            raise InvalidGranuleException(
                "The string given does not describe a valid granule!",
                granule_string
            )

        g = m.groups()
        for i, attribute in enumerate(attributes):
            try:
                setattr(self, attribute, g[i])
            except IndexError:
                break

    # @abstractmethod <- So it works with python2
    def to_str(self):
        pass

    def __str__(self):
        return str(self.to_str())

    def __repr__(self):
        return 'Granule({g})'.format(g=self)


class SentinelGranule(Granule):
    """Object for working with `sentinel granules`_. An example object could be
    made like this:

    .. code-block:: python

       g = 'S1A_IW_GRDH_1SDV_20180330T015147_20180330T015214_021238_024867_4C78'
       SentinelGranule(g)

    :param granule_string: the name of the granule

    .. _datetime.datetime: https://docs.python.org/3.6/library/datetime.html#datetime-objects
    .. _sentinel granules: https://earth.esa.int/web/sentinel/user-guides/sentinel-1-sar/naming-conventions
    """
    pattern_str = r"""
            (S1[AB])_              # Mission ID
            (IW|EW|WV|S[1-6])_     # Mode/Beam
            (GRD|SLC|OCN)          # Product Type
            ([FHM_])_              # Resolution
            ([12])                 # Processing Level
            ([SA])                 # Product Class
            (SH|SV|DH|DV)_         # Polarization
            ([0-9]{8})T([0-9]{6})_ # Start (Date)T(Time)
            ([0-9]{8})T([0-9]{6})_ # End (Date)T(Time)
            ([0-9]{6})_            # Absolut Orbit Number
            ([0-9A-F]{6})_         # Missin Data Take ID
            ([0-9A-F]{4})          # Product Unique ID
    """
    pattern = re.compile(pattern_str, re.VERBOSE)
    pattern_exact = re.compile(r"\A{}\Z".format(pattern_str), re.VERBOSE)

    attributes = [
        "mission",
        "beam_mode",
        "prod_type",
        "res",
        "proc_level",
        "prod_class",
        "pol",
        "start_date",
        "start_time",
        "stop_date",
        "stop_time",
        "orbit",
        "data_id",
        "unique_id"
    ]

    @staticmethod
    def is_valid(possible_granule_string):
        """Check if a string is a valid sentinel granule.

           :returns: bool
        """
        return re.match(
            SentinelGranule.pattern_exact,
            possible_granule_string
        )

    def __init__(self, granule_string):
        length = len(granule_string)

        if length != 67:
            raise InvalidGranuleException(
                "Granule string is too {}! Must be 67 characters".format(
                    "short" if length < 67 else "long"
                ),
                granule_string
            )

        attributes = self.get_attributes()

        super(SentinelGranule, self).__init__(
            SentinelGranule.pattern,
            granule_string,
            attributes
        )

    def __eq__(self, other):
        return str(self) == str(other)

    def to_str(self):
        return "_".join([
            self.mission,
            self.beam_mode,
            self.prod_type + self.res,
            self.proc_level + self.prod_class + self.pol,
            self.start_date + "T" + self.start_time,
            self.stop_date + "T" + self.stop_time,
            self.orbit,
            self.data_id,
            self.unique_id
        ])

    def get_attributes(self):
        """Get all the attributes the granule has. These values can also be
        accessed directly on a SentinelGranule object: ``g.mission``

        **Attributes:**

        +------------+------------+------------+
        | mission    | beam_mode  | prod_type  |
        +------------+------------+------------+
        | res        | proc_level | prod_class |
        +------------+------------+------------+
        | pol        | start_date | start_time |
        +------------+------------+------------+
        | stop_date  | stope_time | orbit      |
        +------------+------------+------------+
        | data_id    | unique_id  |            |
        +------------+------------+------------+

        :returns: List[str]
        """
        return SentinelGranule.attributes

    def get_start_date(self):
        """Get the start date of the granule

        :returns: `datetime.datetime`_
        """
        return self.get_date(self.start_date + self.start_time)

    def get_stop_date(self):
        """Get the end date of the granules

        :returns: `datetime.datetime`_
        """
        return self.get_date(self.stop_date + self.stop_time)

    def get_date(self, date_str):
        return datetime.datetime.strptime(date_str, '%Y%m%d%H%M%S')
