import psycopg2
import sys
# Try to connect

try:
   conn=psycopg2.connect("host=ec2-54-225-255-208.compute-1.amazonaws.com dbname=d1npi6l3th4urq user=qfhvpdzhjcvodq password=l8_Nng4uRhGwm9zRN21KEo_nCy")
   print "SUCCESS"
except:
   print "I am unable to connect to the database, exiting."
   
cur = conn.cursor()
try:
   cur.execute("""select * from user_""")
   rows = cur.fetchall()
   for row in rows:
       print "name = ", row[0]
       print "emal = ", row[1]
       print "phone = ", row[2]
       print "active loan = ", row[3], " \n "
       print "fee = ", row[4]
       print "pass = ", row[5]
       print "salt = ", row[6]
       print "accessl = ", row[7] 
       print "lastlog = ", row[8], " \n "
except:
   print "I can't drop our test database, check your isolation level."
