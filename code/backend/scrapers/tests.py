# Currently the scrapers will be manually tested by running this
# script with pytest, but it will eventually be automated and
# write to logs if any problem arises
from scrapers import *


def test_sportsline():
    tmp_writeout_file = '/tmp/basketball.csv'
    assert sports_line_scrape(tmp_writeout_file) == 1
