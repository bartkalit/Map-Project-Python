This dataset includes check-in history of 1488 users of Foursquare and their social links.

The file Checkins_data.txt contains 1400009 check-ins of 1488 users.
The file contains 5 tab separated columns, which are:

1. UserID (anonymized)
2. Checkin time (UTC ISO format)
3. Latitude
4. Longitude
5. LocationID (anonymized)

The file Social_Network.txt contains 6956 social links between 1488 users.
This file contains 2 tab separated columns, which are:

1. UserID_A 
2. UserID_B

Each row represents one directional social link between UserID_A and UserID_B.

Example:

a) 2	53

user 2 is a friend of user 53

b) 53	2

user 53 is a friend of user 2