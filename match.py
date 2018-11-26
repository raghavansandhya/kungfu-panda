import sys
import os
import argparse
import datetime
import pandas as pd


def cleanse_pol(polDF):
    #Treat missing values
    now=datetime.datetime.now()
    polDF.dropna(subset=['political_id'],inplace=True)
    #Cleanse any birth year greater than 110 years from now with minimum
    polDF.birth_year.replace(polDF[polDF['birth_year'] < now.year - 110].birth_year,now.year - 110,inplace = True)
    return polDF

def cleanse_res(resDF):
    #Treat missing values
    resDF.dropna(subset=['resume_id'],inplace=True)
    return resDF

def transform_pol(polDF):
	#Convert cases to ensure correctness of join
	polDF["first_name"] = polDF["first_name"].map(lambda x: x if type(x)!=str else x.upper())
	polDF["last_name"] = polDF["last_name"].map(lambda x: x if type(x)!=str else x.upper())
	polDF["city"] = polDF["city"].map(lambda x: x if type(x)!=str else x.upper())
	#Deleting the duplicates on the join keys 'first_name', 'last_name','city'
	polDF.drop_duplicates(['first_name', 'last_name','city'], keep=False,inplace=True)
	#Deleting duplicates on first_name and last_name alone
	polDFTmp1 = polDF.drop_duplicates(['first_name', 'last_name'], keep=False)
	return polDF, polDFTmp1

def transform_res(resDF):
	#Convert cases to ensure correctness of join
	resDF["first_name"] = resDF["first_name"].map(lambda x: x if type(x)!=str else x.upper())
	resDF["last_name"] = resDF["last_name"].map(lambda x: x if type(x)!=str else x.upper())
	resDF['city'],resDF['state'] = resDF['local_region'].str.split(",").str
	resDF["city"] = resDF["city"].map(lambda x: x if type(x)!=str else x.upper())
	#Deleting the duplicates on the join keys 'first_name', 'last_name','city'
	resDF.drop_duplicates(['first_name', 'last_name','city'], keep=False,inplace=True)
	#Deleting duplicates on first_name and last_name alone
	resDFTmp1 = resDF.drop_duplicates(['first_name', 'last_name'], keep=False)
	return resDF,resDFTmp1
    
def main(args):
	polFile = args.politicalFile
	resFile = args.resumeFile
	colDel = args.delimiter
	outputFile = args.outputFile
	#Read the files into data frames
	polDF = pd.read_csv(polFile,escapechar='\\', encoding='utf-8')
	resDF = pd.read_csv(resFile,escapechar='\\', encoding='utf-8')
	resDF = cleanse_res(resDF)
	resDF,resDFTmp1 = transform_res(resDF)
	polDF = cleanse_pol(polDF)
	polDF,polDFTmp1 = transform_pol(polDF)
	#Join files based on the  'first_name', 'last_name','city' from the file with removed duplicates
	joinFnmLnmCi = pd.merge(polDF,resDF, on=['first_name', 'last_name','city'],how="inner")
	outFile = joinFnmLnmCi[['political_id','resume_id']]
	outFile = outFile.assign(same_first_name = 1,same_last_name = 1,same_city_name = 1)
	#Join files based on the  'first_name', 'last_name' using the temp data frame
	joinFnmLnm = pd.merge(polDFTmp1,resDFTmp1, on=['first_name', 'last_name'],how="inner")
	#Get only records that were not a part of the previous join
	joinTmp=  pd.merge(joinFnmLnm,joinFnmLnmCi,on=['first_name', 'last_name'],how="left", indicator=True)
	joinTmp = joinTmp[joinTmp['_merge'] == 'left_only']
	outFile1 = joinTmp[['political_id_x','resume_id_x']]
	outFile1.columns = ['political_id','resume_id']
	outFile1 = outFile1.assign(same_first_name = 1,same_last_name = 1,same_city_name = 0)
	#concat the 2 output data frames
	outFile = pd.concat([outFile,outFile1])
	#Write the output data frame to the 
	outFile.to_csv(outputFile, encoding='utf-8',index=False)

def parsearguments(parser):
    # Positional mandatory arguments
	parser.add_argument('-f1','--politicalFile',help="Absolute File Name for the Political data vendor File")
	parser.add_argument('-f2','--resumeFile',help="Absolute File Name for the Resume data vendor File")
	parser.add_argument('-o','--outputFile',help="Absolute File Name for the output file to be written")
	# Optional arguments
	parser.add_argument('-d','--delimiter',help="[,:|] Column delimiter for data files. Default is ','", default =",")
	args = parser.parse_args()
	return args
    
if __name__ == "__main__":
	startTime = datetime.datetime.now()
	#Parse the arguments
	parser = argparse.ArgumentParser()
	args = parsearguments(parser)
	# Raw print arguments
	print("You are running the script with arguments: ")
	for a in args.__dict__:
		if args.__dict__[a]:
			print("Values provided for : "+ str(a) + ": " + str(args.__dict__[a]))
		else:
			parser.print_help()
			sys.exit(0)
	main(args)
	print(datetime.datetime.now() - startTime)
  
    