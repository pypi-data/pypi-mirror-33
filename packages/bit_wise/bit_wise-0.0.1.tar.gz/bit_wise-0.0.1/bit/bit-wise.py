'''
Authur: DataScienceStep
E-meil: DataScienceStep.Gmail.com
Date:   6/25/2018  KL
Twitter: @DataScienceStep

A simple class to perform bit-wise operation.
No error handling is implemented

'''
class bit:
#Swaps specified bit
	def Swap(n,b):
		return n^(2**(b-1))
#Sets specified bit to 1
	def Set(n,b):
		return n|(2**(b-1))
#Sets specified bit to 0
	def Clear(n,b):
		i=bit.Swap(n,b)
		return n&i
#Returns True if the specified bit is 1
	def IsOn(n,b):
		i=SetBit(n,b)
		j=i & n
		r=True
		if i>n: 
			r=False
		return r

#44 = 101100    100100=36
#bit.Bit(44,4)         #Out: 36
#bit.Set(36,4)          #Out: 44
#bit.Clear(36,4)        #Out: 36
#bit.Clear(44,4)        #Out: 36
#print(bit.IsOn(44,2))  #Out: False

bit.Clear(66,2)