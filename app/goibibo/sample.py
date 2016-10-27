from goibibo import goibiboAPI

GO = goibiboAPI("d5b7e6be", "d3f7ab8509d93ae591d36149d749e2a2")

print GO.FlightSearch("BLR", "HYD", 20161028)
print GO.MinimumFare("BLR", "HYD", 20161028)
print GO.BusSearch("bangalore", "hyderabad", 20141028)
print GO.BusSeatMap("vJ52KC0ymd0635qTD9bDDy9GHBkGl5FJMJje0aFX\
                    _GQTyev_4N9Y62TTfrmS-Re3dCHl0-UxLq4AsoQ%3D")
print GO.SearchHotelsByCity(6771549831164675055)
print GO.GetHotelData([1017089108070373346, 6085103403340214927])
print GO.GetHotelPriceByCity(6771549831164675055, 20141101, 20141102)

