from cleverbot import Cleverbot
from geopy.geocoders import Nominatim

from pinsey.GoogleSearchByImage import GoogleSearchByImage

google = GoogleSearchByImage()
google.search('http://images.gotinder.com/58392c8d9d1cdf251bc6799b/ca5a9c81-432d-444f-82da-dab559617895.jpg', False)

'''
cb = Cleverbot()
print(cb.ask("What?"))


geolocator = Nominatim()
location = geolocator.geocode("Jalan Putra Mahkota 7/3H, Putra Heights")
print(location.address)

print((location.latitude, location.longitude))
'''



