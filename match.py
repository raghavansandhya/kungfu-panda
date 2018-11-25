import sys, os, argparse, datetime
import pandas as pd


def cleansePol(polDF):
    #Treat missing values
    now=datetime.datetime.now()
    polDF.dropna(subset=['political_id'],inplace=True)
    polDF['city'].fillna("UNKNOWN",inplace=True)
    #Cleanse any birth year greater than 110 years from now with minimum
    polDF.birth_year.replace(polDF[polDF['birth_year'] < now.year - 110].birth_year,now.year - 110,inplace = True)
    return polDF

def cleanseRes(resDF):
    #Treat missing values
    resDF.dropna(subset=['resume_id'],inplace=True)
    return resDF

def transformPol(polDF):
    #Convert cases to ensure correctness of join
    polDF["first_name"] = polDF["first_name"].map(lambda x: x if type(x)!=str else x.upper())
    polDF["last_name"] = polDF["last_name"].map(lambda x: x if type(x)!=str else x.upper())
    polDF["city"] = polDF["city"].map(lambda x: x if type(x)!=str else x.upper())
    #Deleting the duplicates on the join keys 'first_name', 'last_name','city'
    polDF.drop_duplicates(['first_name', 'last_name','city'], keep=False,inplace=True)
    return polDF

def transformRes(resDF):
    #Convert cases to ensure correctness of join
    resDF["first_name"] = resDF["first_name"].map(lambda x: x if type(x)!=str else x.upper())
    resDF["last_name"] = resDF["last_name"].map(lambda x: x if type(x)!=str else x.upper())
    resDF['city'],resDF['state'] = resDF['local_region'].str.split(",").str
    resDF["city"] = resDF["city"].map(lambda x: x if type(x)!=str else x.upper())
    #Deleting the duplicates on the join keys 'first_name', 'last_name','city'
    resDF.drop_duplicates(['first_name', 'last_name','city'], keep=False,inplace=True)
    return resDF
    
def main(args):
    polFile=args.politicalFile
    resFile=args.resumeFile
    colDel=args.delimiter
    #ignoreHdr=args.ignoreHeader
    #tmpFile=args.outFile
    
    #Read the files into data frames
    polDF = pd.read_csv(polFile,escapechar='\\', encoding='utf-8')
    resDF = pd.read_csv(resFile,escapechar='\\', encoding='utf-8')
    resDF = cleanseRes(resDF)
    resDF = transformRes(resDF)
    polDF = cleansePol(polDF)
    polDF = transformPol(polDF)
    
    joinFiles = pd.merge(polDF,resDF, on=['first_name', 'last_name','city'],how="inner")
    joinFiles[['political_id','resume_id']].to_csv('E:/data/applecart/exact_matches.csv', encoding='utf-8',index=False)
    


def parseArguments(parser):
    # Positional mandatory arguments
    parser.add_argument('-f1','--politicalFile',help="Absolute File Name for the Political data vendor File")
    parser.add_argument('-f2','--resumeFile',help="Absolute File Name for the Resume data vendor File")
    # Optional arguments
    parser.add_argument('-d','--delimiter',help="[,:|] Column delimiter for data files. Default is ','", default =",")
    args = parser.parse_args()
    return args
    
if __name__ == "__main__":
    startTime = datetime.datetime.now()
    #Parse the arguments
    parser = argparse.ArgumentParser()
    args = parseArguments(parser)
    
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
  
    