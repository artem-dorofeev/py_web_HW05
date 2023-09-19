import requests
from datetime import datetime, timedelta

# current_date = datetime.now()
link_bank = 'https://api.privatbank.ua/p24api/exchange_rates?date='

def get_list_date(period: int):
    list_date = []
    c_d = datetime.now()
    # if period == 0:
    #     period = 1
    for i in range(period):
        delta_day = timedelta(days=i)
        new_date = c_d - delta_day
        day = str(new_date.day) if new_date.day > 9 else '0' + str(new_date.day)
        month = str(new_date.month) if new_date.month > 9 else '0' + str(new_date.month)
        date_of_change = day + '.' + month + '.' + str(new_date.year)
        list_date.append(date_of_change)

    return list_date


def get_currency(date_of_currency: list):
    result_dict = {}
    result = []
    for i in date_of_currency:
        l_b_new = link_bank + i
        response = requests.get(l_b_new)
        change = response.json()
        for key, value in change.items():
            if key == 'exchangeRate':
                date_dict = {}
                for item in value:
                    if item['currency'] == 'EUR' or item['currency'] == 'USD' :
                        print(f"{i} {item['currency']} Sale: {item['saleRate']} Buy: {item['purchaseRateNB']}")
                        date_dict.update({i: {item['currency']: {'sale': item['saleRate'], 'buy': item['purchaseRateNB']}}})
                        # print(date_dict)
        result_dict.update(date_dict)

    return result_dict



if __name__ == '__main__':
    result = get_list_date(5)
    # print(result)
    res_dict = get_currency(result)
    print(res_dict)





# print(current_date.date())
# month = str(current_date.month) if current_date.month > 9 else '0' + str(current_date.month)
# date_of_change = str(current_date.day) + '.' + month + '.' + str(current_date.year)
# print(date_of_change)
# link_bank = 'https://api.privatbank.ua/p24api/exchange_rates?date=' + date_of_change
# response = requests.get('https://api.privatbank.ua/p24api/exchange_rates?date=03.09.2023')
# # response = requests.get(link_bank)
# change = response.json()



# print(change[date])
# print(change[exchangeRate])

# for key, value in change.items():
#     if key == 'exchangeRate':
#         for i in value:
#             if i['currency'] == 'EUR' or i['currency'] == 'USD' :
#                 print(f"{i['currency']} Sale: {i['saleRate']} Buy: {i['purchaseRateNB']}")

            # print(i['currency'])
        # print(value[1])
        # print(value[6])

# print(change['exchangeRate'])
# # response2 = requests.get('https://api.privatbank.ua/p24api/pubinfo?exchange&coursid=5')
# # change2 = response2.json()
# print(change2[1])

