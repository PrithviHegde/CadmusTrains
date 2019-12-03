import mysql.connector

def TrainDict():
            con = mysql.connector.connect(host="localhost", user="root", passwd="admin", database="trains" ,auth_plugin='mysql_native_password')
            if con.is_connected():
                print('Connected2')
            mycursor = con.cursor(buffered=True)
            mycursor.execute("use trains")

            d={}
            TrainName = input('Enter train ANem')
            d['TrainName'] = TrainName
            sql2 = 'select trainid, routeid from trains where trainname = ' + "'" + TrainName + "'"
            mycursor.execute(sql2)     
            x=mycursor.fetchall()
            print(x)
            d['TrainID'] = x[0][0]
            sql0 = "select max(sequence) from routes where routeid = " + str(x[0][1])
            mycursor.execute(sql0)
            e = mycursor.fetchone()
            if e == 1:
                sql3 = 'select fromcity, tocity from routes where routeid = ' + str(x[0][1]) + ' and sequence = 1'
                mycursor.execute(sql3)
                y=mycursor.fetchall()
            else:
                sql3 = 'select fromcity, tocity from routes where routeid = ' + str(x[0][1]) + ' and sequence = 1'
                mycursor.execute(sql3)
                y=mycursor.fetchall()
                sql4 = 'select tocity from routes where routeid = ' +str(x[0][1]) + ' and sequence != 1'
                mycursor.execute(sql4)
                z=mycursor.fetchall()
            l=[]
            for i in y:
                for j in i:
                    sql5 = 'select cityname from cities where cityid = ' + str(j)
                    mycursor.execute(sql5)
                    a=mycursor.fetchone()
                    l.append(a[0])
            if z:
                for k in z:
                    for h in k:
                        sql6 = 'select cityname from cities where cityid = ' + str(h)
                        mycursor.execute(sql6)
                        b=mycursor.fetchone()
                        l.append(b[0])
            
            d['cities'] = l
            sql7 = 'select stop_cost from price where trainid = ' + str(x[0][0])
            mycursor.execute(sql7)
            c = mycursor.fetchone()
            d['price_per_stop'] = c[0]

            TrainsDetailsList = []
            TrainsDetailsList.append(d)
            
            return TrainsDetailsList

x = TrainDict()
print(x)
