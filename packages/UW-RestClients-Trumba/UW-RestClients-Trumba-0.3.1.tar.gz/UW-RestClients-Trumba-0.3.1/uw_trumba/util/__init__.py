from restclients_core.util.decorators import use_mock
import sys
from uw_trumba.dao import TrumbaCalendar_DAO, TrumbaSea_DAO, TrumbaBot_DAO,\
                            TrumbaTac_DAO


fdao_trumba_override = use_mock(TrumbaCalendar_DAO())
fdao_trumba_sea_override = use_mock(TrumbaSea_DAO())
fdao_trumba_bot_override = use_mock(TrumbaBot_DAO())
fdao_trumba_tac_override = use_mock(TrumbaTac_DAO())


def to_bytestring(string):
    if (sys.version_info > (3, 0)):
        return string.encode()
    else:
        return bytes(string)
