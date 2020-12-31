import requests

search_book = input("Enter name of book:")
url_parameters = {
    #"key" : "AIzaSyBuc-RoTyhaqKP0LWUrJ0OTiX-G0O_aodc",
    "q" : search_book,
    "maxResults" : 10,
    "startIndex" : 0
}
#with id: https://www.googleapis.com/books/v1/volumes/   f280CwAAQBAJ
#range(maxresults: results shown on screen, start idex, 1 page=10 books): https://www.googleapis.com/books/v1/volumes?q=harry+potter&maxResults=10&startIndex=40
response = requests.get("https://www.googleapis.com/books/v1/volumes", params=url_parameters)
print(response.url)
response_dict = response.json()

display_next= 5
display_start = 0
while input("enter 'stop' to end: ") != "stop":
    print("\n")
    for i in range(display_start, display_next):
        try:
            print(response_dict["items"][i]["volumeInfo"]["title"])
        except IndexError:
            # print("Reached end of list")
            url_parameters["startIndex"] = url_parameters["maxResults"]
            url_parameters["maxResults"] += 10
            response = requests.get("https://www.googleapis.com/books/v1/volumes", params=url_parameters)
            response_dict = response.json()
            print(response_dict["items"][i]["volumeInfo"]["title"])
    display_next += 5
    display_start += 5
