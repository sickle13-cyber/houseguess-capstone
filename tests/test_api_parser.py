import responses
from houseguess.api_client import rapidapi_search

@responses.activate
def test_rapidapi_parser_basic():
    fake = {
        "results": [
            {
                "place_id": "abc123",
                "name": "Foo Cafe",
                "country": "US",
                "geometry": {"location": {"lat": 34.05, "lng": -118.24}},
                "types": ["cafe"]
            }
        ]
    }
    responses.add(
        responses.GET,
        "https://maps-data.p.rapidapi.com/searchmaps.php",
        json=fake,
        status=200,
    )
    places = rapidapi_search("Foo", limit=1)
    assert len(places) == 1
    p = places[0]
    assert p.name == "Foo Cafe" and p.country == "US"
    assert abs(p.lat - 34.05) < 1e-6 and abs(p.lon - (-118.24)) < 1e-6
