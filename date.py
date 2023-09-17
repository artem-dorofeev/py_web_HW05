from datetime import datetime, timedelta

d = datetime.now()
print(d.date())
print(d.month)
delta = timedelta(days=3)
new_date = d - delta
print(new_date.date())
month = str(d.month) if d.month > 9 else '0' + str(d.month)

n_day = 2

list_date = []

d = datetime.now()
for i in range(n_day):
    # print(i)
    delta_day = timedelta(days=i)
    new_date = d - delta_day
    day = str(new_date.day) if new_date.day > 9 else '0' + str(new_date.day)
    month = str(new_date.month) if new_date.month > 9 else '0' + str(new_date.month)
    date_of_change = day + '.' + month + '.' + str(new_date.year)
    list_date.append(date_of_change)

print(list_date)