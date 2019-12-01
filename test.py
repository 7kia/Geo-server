from nearest import findNearest as nearest
from route import find_nearest as route
from route import application

from route_railway import findNearest as route_railway
from nearest_railway import findNearest as nearest_railway

from roadSearcher import RoadSearcher


if __name__ == "__main__":
    # environ = {'QUERY_STRING': "data=50.38264432893728,30.61752319335937,ukraine-latest.osm,4"}
    # print("\nnearest")
    # print("Response = " + RoadSearcher.get_response(nearest, environ))

    environ = {'QUERY_STRING': "data=50.385490233198624,30.60464859008789,50.38264432893728,30.61735153198242,"
                               "ukraine-latest.osm,4"}
    print("\nroute")
    print("Response = " + RoadSearcher.get_response(route, environ))

    application(environ, None)
    #
    # environ = {'QUERY_STRING': "data=50.38822651855654,30.55795669555664,ukraine-latest.osm,4"}
    # print("\nnearest_railway")
    # print("Response = " + RoadSearcher.get_response(nearest_railway, environ))
    #
    #
    # environ = {'QUERY_STRING': "data=50.386584766288365,30.5558967590332,50.37914144309975,30.552120208740238,"
    #                            "ukraine-latest.osm,4"}
    # print("\nroute_railway")
    # print("Response = " + RoadSearcher.get_response(route_railway, environ))



