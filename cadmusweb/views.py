from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import messages
from cadmusweb.models import querydata
import csv
import mysql.connector
RouteId = 0
StopCount = 0


# Establish and verify connection to database.
con = mysql.connector.connect(host="localhost", user="root", passwd="root",database="cadmus",auth_plugin='mysql_native_password')
if con.is_connected():
    print("Connected to MySQL database")
else:
    print("Not connected to mysql database")


# Create your views here.

# View for the querydata model, to take queries from user. Appends to a CSV file.
def inputform(request):
    if request.method == "POST":
        email = request.POST['email']
        phone = request.POST['phone']
        message = request.POST['message']
        if email == message == '':
            return render(request,'test.html')
        print(email)
        print(phone)
        print(message)
        lst = querydata()
        lst.Sno = 1
        lst.Email = email
        lst.Phone = phone
        lst.Message = message
        lst.save()
        with open('cadmusdata.csv','a') as csvfile:
            wcs = csv.writer(csvfile)
            wcs.writerow(['email',email])
            wcs.writerow(['phone',phone])
            wcs.writerow(['message',message])
        return render(request,'test.html')
    else:
        return render(request,'test.html')

# View for Browsetrains page.
# Takes inputs from user, and uses algorithms to find the best train, sorted by either cost/duration, as inputted by the user.
def browsetrains(request):
    if request.method == 'POST':
        print(request.POST)

        con = mysql.connector.connect(host="localhost", user="root", passwd="root", database="cadmus" ,auth_plugin='mysql_native_password')
        if con.is_connected():
            print('Connected2')
        mycursor = con.cursor(buffered=True)
        mycursor.execute("use cadmus")
        
        #Fxn to find the cityIDs given the citynames
        def FindCityId():
            input_From = request.POST['FromCity']
            input_To = request.POST['ToCity']
            if input_From == input_To:
                messages.add_message(request, messages.WARNING, 'Please enter unique From and To cities')
                return 0, 0
            else:

                con = mysql.connector.connect(host="localhost", user="root", passwd="root", database="cadmus", auth_plugin='mysql_native_password')
                if con.is_connected():
                    print('Connected2')
                mycursor = con.cursor(buffered=True)
                mycursor.execute("use cadmus")


                sql1 = 'select cityid from cities where cityname = ' + "\'" + input_From + "\'"
                mycursor.execute(sql1)
                cityid_From = mycursor.fetchall()
                cityid_From = cityid_From[0][0]

                sql2 = 'select cityid from cities where cityname = ' + "\'" + input_To + "\'"
                mycursor.execute(sql2)
                cityid_To = mycursor.fetchall()
                cityid_To = cityid_To[0][0]

                return cityid_From, cityid_To


        #Fxn to find routes given cityIds
        def Findcadmus(L):

            #L = FindCityId()
            FromCity = L[0]
            ToCity = L[1]

            #for destination1
            sql1="select routeid from routes where FromCity= " + str(FromCity) + ' or ' + 'ToCity = ' + str(FromCity) + ' group by routeid'

            mycursor.execute(sql1)
            result1=mycursor.fetchall()


            #for destination2

            sql2="select routeid from routes where FromCity= " + str(ToCity) + ' or ' + 'ToCity = ' + str(ToCity) + ' group by routeid'
            mycursor.execute(sql2)
            result2=mycursor.fetchall()


            #the prints to verify
            '''print(sql1)
            print('For table1')
            print(result1)
            print('For table2')
            print(result2)'''

            #to put them in an iterable list
            L = []
            for i in result1:
                for j in result2:
                    if i==j:
                        L += i
            return L


        #Find sequence given routes, and find train    
        def FindSequence(choice):
            #Inputs to be taken from findcadmus fxn
            #Therefore changesql3 and sql4 input paramaters
            StationsList = FindCityId()
            RoutesList = Findcadmus(StationsList)
            #print(RoutesList)

            FromCity = StationsList[0]
            #print(StationsList)
            ToCity = StationsList[1]

            #SQL to find sequences
            #inside a for loop, as no of routes b/w two stations is variable
            ResultList = []
            sequencedict = {}
            for i in RoutesList:
                sequencetestFrom = 0
                sequencetestTo = 0
                sql3="select sequence from routes where routeid= " + str(i) + ' and FromCity = ' + str(FromCity)
                mycursor.execute(sql3)
                result3=mycursor.fetchall()
                if result3 == []:
                    sql3="select sequence from routes where routeid= " + str(i) + ' and ToCity = ' + str(FromCity)
                    mycursor.execute(sql3)
                    result3=mycursor.fetchall()
                    sequencetestFrom = 0
                    sequencetestFrom = result3[0][0]
                #print('The sequence for routeID', i, 'is', result3)

                sql4="select sequence from routes where routeid= " + str(i) + ' and ToCity = ' + str(ToCity)
                mycursor.execute(sql4)
                result4=mycursor.fetchall()
                if result4 == []:
                    sql4="select sequence from routes where routeid= " + str(i) + ' and FromCity = ' + str(ToCity)
                    mycursor.execute(sql4)
                    result4=mycursor.fetchall()
                    sequencetestTo = 0
                    sequencetestTo = result4[0][0]
                #print('The sequence for routeID', i, 'is', result4)
                #For the trainname
                sql5 = "select trainname from trains where routeid= " + str(i)
                mycursor.execute(sql5)
                trainname = mycursor.fetchone()
                if trainname == None:
                    pass
                else:
                    #print(trainname)
                    trainname = trainname[0]
                    ResultDict = {}

                trainidsql = 'select trainid from trains where trainname = ' "\'" + str(trainname) + "\'"
                mycursor.execute(trainidsql)
                trainid=mycursor.fetchone()
                trainid = trainid[0]
                costsql = 'select stop_cost from price where trainid = ' + str(trainid)
                mycursor.execute(costsql)
                StopCost = mycursor.fetchone()
                StopCost = int(StopCost[0])

                if result3==[] or result4==[] or result3[0][0]==sequencetestTo or result4[0][0]==sequencetestFrom:
                    #print('No trains running between these cities')
                    pass
                else:    
                    result3=result3[0][0]
                    result4=result4[0][0]
                    result = result4 - result3
                    totalcost = (int(result) + 1)*StopCost

                    citylist2 = []
                    for j in range(int(result3), int(result4) + 1):
                        sqlsequence = 'select FromCity, ToCity from routes where sequence = ' + str(j) + ' and RouteId = ' + str(i)
                        mycursor.execute(sqlsequence)
                        citylist = mycursor.fetchone()
                        citylist2.append(citylist)
                    sequencedict[i] = citylist2

                    # To find the distance between cities using sequences
                    TotalDistance = []

                    for k in sequencedict.values():
                        Distance = 0
                        for i in k:
                            DistanceSQL = 'select Distance from distance where initcity = ' + str(i[0]) + ' and finalcity = ' + str(i[1])
                            mycursor.execute(DistanceSQL)
                            result5=mycursor.fetchone()
                            if result5 == None:
                                DistanceSQL = 'select Distance from distance where initcity = ' + str(i[1]) + ' and finalcity = ' + str(i[0])
                                mycursor.execute(DistanceSQL)
                                result5=mycursor.fetchone()
                            Distance += result5[0]
                        if Distance == 0:
                            pass
                        else:
                            TotalDistance.append(Distance)

                        #To remove reverse trains
                    if result < 0:
                        pass
                    else: 
                
                        #ResultList += [{ trainname : result}]
                        ResultDict['TrainName'] = trainname
                        ResultDict['StopsCount'] = result
                        for i in TotalDistance:
                            ResultDict['StopsDistance'] = i
                        speedsql = 'select TrainSpeed from trains where TrainName = ' "\'" + str(trainname) + "\'"
                        mycursor.execute(speedsql)
                        speed = mycursor.fetchone()
                        speed = int(speed[0])
                        time = int(i)/speed
                        ResultDict['timetaken'] = int(time)
                        ResultDict['TotalCost'] = totalcost

                        ResultList.append(ResultDict)
            
                    #print(ResultList)
            if choice.lower() == 'price':
                ResultList = sorted(ResultList, key = lambda i : i['TotalCost'])
        
            elif choice.lower() == 'time':
                ResultList = sorted(ResultList, key = lambda i : i['timetaken'])
            return ResultList

        choice = request.POST['SelectBy']
        TableList = FindSequence(choice)

        return render(request, 'Browse_trains_page.html',{'TableData':TableList})  
    else:       
        return render(request, 'Browse_trains_page.html',)


# View for deleting or adding train selector.
def Choose(request):
    if request.method == 'POST':
        if request.POST['Choose'] == 'Delete':
            return HttpResponseRedirect('../Delete')
        elif request.POST['Choose'] == 'Update':
            return HttpResponseRedirect('../UpdateTrain')
    else:
        return render(request, 'admin.html')


# View to delete train.
def Delete(request):
    if request.method == 'POST':

        mycursor=con.cursor(buffered=True)
        mycursor.execute("use cadmus")

        TrainName = request.POST['TrainName']

        RouteSQL = 'Select routeID from trains where TrainName = ' + "'" + TrainName + "'"
        mycursor.execute(RouteSQL)
        RouteID = mycursor.fetchone()
        if RouteID == None:
            messages.add_message(request, messages.WARNING, 'Train to be deleted doesnot exist')
            return render(request, 'DeleteTrains.html')
        else:
            RouteID = RouteID[0]

            # To delete the trainrow from the Trains table
            DeleteTrainSQL = 'delete from trains where TrainName = ' + "'" + TrainName + "'"
            mycursor.execute(DeleteTrainSQL)
            
            # To delete the associated route from the Routes table
            DeleteRouteSQL = 'delete from routes where RouteID = ' + str(RouteID)
            mycursor.execute(DeleteRouteSQL)
            con.commit()
            return render(request, 'test.html')
    else:
        return render(request, 'DeleteTrains.html')
    

# View to update train.
def UpdateTrain(request):
    '''imp reminder -- add a message for errenous inputted data'''
    if request.method == 'POST':
        print('[posdt]')
        choice = 'Update'    
        # This fxn is not to be called directly
        def AddTrains():
            con = mysql.connector.connect(host="localhost", user="root", passwd="root", database="cadmus", auth_plugin='mysql_native_password')
            if con.is_connected():
                print('Connected2')
            mycursor = con.cursor(buffered=True)
            mycursor.execute("use cadmus")


            TrainName = request.POST['TrainName']
            TrainSpeed = request.POST['TrainSpeed']
            #global StopCount
            #StopCount = request.POST['StopCount']
            CityListStr = request.POST['CityList']
            CityList = CityListStr.split(",")
            print(CityList)
            
            TrainIdSql = 'select max(TrainId) from Trains'
            mycursor.execute(TrainIdSql)
            TrainIdOld = mycursor.fetchone()
            TrainIdOld = int(TrainIdOld[0])
            TrainIdNew  = TrainIdOld + 1
            global RouteId
            RouteId = TrainIdNew

            AddTrainSql = 'insert into trains values ( ' + str(TrainIdNew) + ',' + "'" + str(TrainName) + "'" + ',' + str(TrainSpeed) + ',' + str(RouteId) + ')'
            mycursor.execute(AddTrainSql)
            con.commit()
            return CityList

        # Call this function
        def AddRoute():
            CityList = AddTrains()
            print(CityList)
            con = mysql.connector.connect(host="localhost", user="root", passwd="root", database="cadmus", auth_plugin='mysql_native_password')
            if con.is_connected():
                print('Connected2')
            mycursor = con.cursor(buffered=True)
            mycursor.execute("use cadmus")
            RouteList = []

            for i in CityList:
                CityIdSql = 'select CityId from cities where CityName = ' + "'" + i + "'" 
                mycursor.execute(CityIdSql)       
                CityId = mycursor.fetchone()
                RouteList.append(CityId[0])
            print(RouteList)

            for i in range(0, len(RouteList)-1):
                AddRouteSql = 'insert into routes values ( ' + str(RouteId) + ',' + str(RouteList[i]) + "," + str(RouteList[i+1]) + "," + str(i+1) + ')'
                print(AddRouteSql)
                mycursor.execute(AddRouteSql)
                con.commit()
            return 0


        call = AddRoute()

        return render(request, 'test.html')
    else:
        print('nopst')
        return render(request, 'UpdateTrain.html') 


# View to return Deletetrain/ updatettrain pages.  
def administrator(request):
    if request.method == 'POST':
        if request.POST['Choose'] == 'Delete':
            return render(request, 'DeleteTrains.html')
        elif request.POST['Choose'] == 'Update':
            return render(request, 'UpdateTrain.html')
        else:
            return render(request, 'test.html')
    else:
        print('Not a post')
        return render(request, 'admin.html')


# View to display train details, for a train inputted by the user.
def TrainDetails(request):
    if request.method  == 'POST':
        def TrainDict():
            con = mysql.connector.connect(host="localhost", user="root", passwd="root", database="cadmus" ,auth_plugin='mysql_native_password')
            if con.is_connected():
                print('Connected2')
            mycursor = con.cursor(buffered=True)
            mycursor.execute("use cadmus")

            d={}
            TrainName = request.POST['TrainName']
            d['TrainName'] = TrainName
            sql2 = 'select trainid, routeid from trains where trainname = ' + "'" + TrainName + "'"
            mycursor.execute(sql2)
            x=mycursor.fetchall()
            if x == []:
                messages.add_message(request, messages.WARNING, 'Please enter unique From and To cities')
                return (0,0,0,0)
            else:

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
            
        Trains = TrainDict()
        return render(request, 'Train_Details_page.html',{'TrainInfo':Trains})
    else:
        return render(request, 'Train_Details_page.html')


# View for the login page.
def Login(request):
    if request.method=="POST":
        mycon=mysql.connector.connect(host="localhost",user="root",passwd="root",database="cadmus")
        u_l=request.POST['username']
        p_l=request.POST['password']
        cursor=mycon.cursor()

        lusers=[]
        lpwd=[]

        sql1="select username from index_login"
        cursor.execute(sql1)
        result=cursor.fetchall()

        for i in result:
            lusers=lusers+[i[0]]
        print(lusers)

        sql2="select password from index_login"
        cursor.execute(sql2)
        result2=cursor.fetchall()

        for j in result2:
            lpwd=lpwd+[j[0]]
        print(lpwd)
        print(u_l, p_l)

        l=(dict(zip(lusers,lpwd)))
        if (u_l in l) and l[u_l]==p_l:
            return HttpResponseRedirect('../administrator')
        else:
            messages.add_message(request, messages.WARNING, 'Incorrect Username/Password')
            return render(request,'AdminLogin.html')
    else:
        return render(request,'AdminLogin.html')
