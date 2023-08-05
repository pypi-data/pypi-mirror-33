from .granules import SentinelGranule


class GranulePair(object):
    """Object for working with pairs of granuels"""

    def __init__(self, master, slave):
        self.master = master
        self.slave = slave

    @property
    def tuple(self):
        """Property for getting a tuple with the granules in the pair

        :returns: Tuple[Granule]
        """
        return (self.master, self.slave)

    def __str__(self):
        return "({m}, {s})".format(m=self.master, s=self.slave)

    def __repr__(self):
        return "GranulePair({m}, {s})".format(
            m=self.master,
            s=self.slave
        )


class SentinelGranulePair(GranulePair):
    """Object for working with pairs of sentinel granules.

    .. _datetime.timedelta: https://docs.python.org/3.6/library/datetime.html#timedelta-objects
    """
    @staticmethod
    def time_delta(master, slave):
        return master.get_start_date() - slave.get_start_date()

    def __init__(self, master, slave):
        master, slave = [SentinelGranule(str(g)) for g in (master, slave)]

        delta = SentinelGranulePair.time_delta(master, slave)
        if delta.days < 0:
            master, slave = slave, master

        super(SentinelGranulePair, self).__init__(
            master,
            slave,
        )

    def __eq__(self, other):
        return str(self) == str(other)

    def get_time_delta(self):
        """Get the difference in start times as a datetime object.

        :returns: `datetime.timedelta`_
        """
        return SentinelGranulePair.time_delta(self.master, self.slave)

    def get_dates(self):
        """Get the dates of the granules as a string

        :returns: str
        """
        return self.master.start_date + "_" + self.slave.start_date

    def checksum_str(self):
        """Get the checksums of the granules as a string

        :returns: str
        """
        return "{}-{}".format(self.master.unique_id, self.slave.unique_id)


def get_pairs(granule_list, gap=1, pair_type=GranulePair):
    """pairs up granule, takes a list of granules sorted by time"""
    granule_list.sort(key=lambda g: g.start_date)
    pair_list = []

    for i, granule in enumerate(granule_list):
        try:
            pair = pair_type(granule, granule_list[i + gap])
            pair_list.append(pair)
        except Exception:
            break

    return pair_list
