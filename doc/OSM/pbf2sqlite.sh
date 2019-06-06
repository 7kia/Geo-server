#!/bin/sh

spatialite_osm_net -o pbf/$1 -d sqlite/$1.sqlite --roads -T roads -tf road_template.conf
ping -n 1 -w 2000 192.168.254.254 > /dev/null
spatialite_network -d sqlite/$1.sqlite -T roads -f node_from -t node_to -g geometry --oneway-tofrom oneway_tofrom --oneway-fromto oneway_fromto -n name -o roads_net_data --overwrite-output
ping -n 1 -w 2000 192.168.254.254 > /dev/null
spatialite sqlite/$1.sqlite "CREATE VIRTUAL TABLE roads_net USING VirtualNetwork('roads_net_data')"

# -d or --db-path pathname          the SpatiaLite db path
# -T or --table table_name          the db table to be validated
# -f or --from-column col_name      the column for FromNode
# -t or --to-column col_name        the column for ToNode
# -g or --geometry-column col_name  the column for Geometry
# -c or --cost-column col_name      the column for Cost
#                                  if omitted, GLength(g)
#                                  will be used by defualt
# --oneway-tofrom col_name
# --oneway-fromto col_name