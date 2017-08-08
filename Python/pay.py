def computepay(h,r):
    if( h <= 40) :
        pay = h * r
    elif (h > 40) :
    	pay = (40*r) + ((h-40)*(r * 1.5))
    return pay


try :
	hrs = raw_input("Enter Hours:")
	h = float(hrs)
	rate = raw_input("Enter Rate:")
	r = float(rate)
except :
    print "Error!! Please enter a numeric value"
    quit()

p = computepay(h,r)
print p