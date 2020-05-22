from app import db
from app.models import Date_f2, Date_f4


class Cached_data_querier():
    def __init__(self):
        super().__init__()
        self.datesF2 = None
        self.datesF4 = None

    def getDateF2(self, dateCode):
        dateF2 = [dateF2 for dateF2 in self.datesF2 if dateF2.code == dateCode]
        if any(dateF2):
            return dateF2[0]

        return super().getDateF2(dateCode)

    def getAllDatesF2(self):
        return self.datesF2

    def getDateF4(self, dateCode):
        dateF4 = [dateF4 for dateF4 in self.datesF4 if dateF4.code == dateCode]
        if any(dateF4):
            return dateF4[0]

        return super().getDateF4(dateCode)

    def getAllDatesF4(self):
        return self.datesF4

# Global variable to hold the cached dates DataQuerier
cached_data_querier = None


def invalidateCached_data_querier():
    global cached_data_querier
    if cached_data_querier:
        cached_data_querier = None


def getCached_data_querier(forceRead: bool=False) -> Cached_data_querier:
    global cached_data_querier
    if forceRead or cached_data_querier is None:
        cached_data_querier.datesF2 = Date_f2.query.with_entities(Date_f2.code, Date_f2.date1, Date_f2.date2) \
            .all()
        cached_data_querier.datesF4 = Date_f4.query.with_entities(Date_f4.code, Date_f4.date1, Date_f4.date2, \
                                                                 Date_f4.date3, Date_f4.date4) \
            .all()

    return cached_data_querier
