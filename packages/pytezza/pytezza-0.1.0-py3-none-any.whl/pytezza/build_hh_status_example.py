from pytezza import NetezzaConnector

def carls_test():
    """ """
    nzhost="eyc-nps-03"
    nzuser="chess"
    nzpass="nete33a"
    nzdb="rittstanl"
    
    nzconn = NetezzaConnector(nzhost,nzdb,nzuser,nzpass)
    
    nzconn.nzPassthrough("drop table rittstanl..iamcarl if exists;create table rittstanl..iamcarl as select 1 as hipraful;")

if __name__ == "__main__":
    carls_test()
    