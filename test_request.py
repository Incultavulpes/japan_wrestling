import requests as re

weight_classes = ["57", "61", "65", "70", "74", "79", "86", "92", "97", "125"]
for class_weight in weight_classes:
    for current_year in range(2026, 2018, -1):
        URL_REQUEST = "https://uww.org/apiv4/getrankinglist/api/rankings/current/seniors/fs/" + class_weight + "?page=1&season=" + str(current_year)
        status_response = re.get(URL_REQUEST)
        print(status_response)
