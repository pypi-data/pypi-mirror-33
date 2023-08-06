__author__ = 'SHASHANK'

from datetime import datetime as dt
from datetime import timedelta
from date_utils import DateUtils
import flows
import sys
import json


"""
Assumptions :
    1. PG Transfer Money From midnight to midnight
    2. Timezone is IST
    3. BSE ATIN And BD share same holidays
"""


def setup(transaction_datetime):
    transaction_date = dt.strptime(transaction_datetime, "%Y-%m-%d %H:%M:%S")
    dateutil = DateUtils(transaction_date)
    return dateutil


def setup_for_date(transaction_date):
    dateutil = DateUtils(transaction_date)
    return dateutil


def main(transaction_datetime, basket_items, acc=None):
    result = []
    dateutil = setup(transaction_datetime)
    rnd = basket_items
    next_date = dateutil.get_next_bank_working_day()
    if int(rnd[0]):
        result.append(flows.execute_cube_iccl_flow(next_date, dateutil))
    if int(rnd[1]):
        result.append(flows.execute_cube_nodal_account_flow(next_date, dateutil))
    if int(rnd[2]):
        result.append(flows.execute_cube_current_account_flow(next_date, dateutil))
    if int(rnd[3]):
        result.append(flows.execute_cube_current_account_flow(next_date, dateutil))

    return result

def show_result(event_list):
    for key, val in (event_list.__get__().items()):
        print(key.strftime("%Y-%m-%d %H:%M:%S"), val)

    if len(event_list.__get_mf__()) > 0:
        print("\n-----MF----TATS-----\n")
        print(json.dumps(event_list.__get_mf__()))

if __name__ == "__main__":
    main(sys.argv[1] + " " + sys.argv[2], sys.argv[3], acc=sys.argv[4])


def get(mode, transaction_date, scheme_id):

    if mode == 1:
        date_str = (transaction_date + timedelta(hour=5, minutes=30)).strftime("%Y-%m-%d %H:%M:%S").split(" ");
        event_list, order_dates = main(date_str, "1000", scheme_id)[0]
        return order_dates[scheme_id] - timedelta(hour=5, minutes=30)

    if mode == 2:
        date_str = (transaction_date + timedelta(hour=5, minutes=30)).strftime("%Y-%m-%d %H:%M:%S").split(" ");
        event_list, order_dates = main(date_str, "0010", scheme_id)[0]
        return order_dates['neft'] - timedelta(hour=5, minutes=30)

    if mode == 3:
        date_str = (transaction_date + timedelta(hour=5, minutes=30)).strftime("%Y-%m-%d %H:%M:%S").split(" ");
        event_list, order_dates = main(date_str, "0100", scheme_id)[0]
        return order_dates['bill'] - timedelta(hour=5, minutes=30)

    if mode == 4:
        date_str = (transaction_date + timedelta(hour=5, minutes=30)).strftime("%Y-%m-%d %H:%M:%S").split(" ");
        event_list, order_dates = main(date_str, "0001", scheme_id)[0]
        return order_dates['mfr'] - timedelta(hour=5, minutes=30)

