from unittest import TestCase
from restclients_core.exceptions import DataFailureException
from uw_trumba import get_calendar_by_name


class TestCalendarParse(TestCase):

    def test_ical_parsing(self):
        calendar = get_calendar_by_name('sea_acad-comm')
        self.assertEquals(len(calendar.walk('vevent')), 4)

        self.assertRaises(DataFailureException,
                          get_calendar_by_name,
                          'sea_none')

    def test_ical_parsing_err(self):
        calendar = get_calendar_by_name('sea_err')
        self.assertEquals(len(calendar.walk('vevent')), 1)
        # can't reprod the issue
        # https://github.com/collective/icalendar/commit/
        # 4f5f70bd5b863e0997ff93e2f9cf9187413730a3
