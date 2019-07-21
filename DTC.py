import tkinter
from operator import itemgetter
from statistics import mode
from tkinter import Tk, ttk
from webbrowser import open
from math import atan2, cos, radians, sin, sqrt
# from pyodbc import Error, connect
import sqlite3

# set up connection to SQLite3 db
db_file = "chair.db"
conn1 = sqlite3.connect(db_file)
c1 = conn1.cursor()

db_file = "DataDepot.db"
conn2 = sqlite3.connect(db_file)
c2 = conn2.cursor()

db_file = "PMResults.db"
conn3 = sqlite3.connect(db_file)
c3 = conn3.cursor()


def get_radius_tab_choice(parameter):
    clear_results()
    preserve = get_site_info(parameter)
    get_local_techs(parameter)
    if preserve != "yes":
        choiceBoxValue.set('')
        radiusSearchHistory.insert(0, parameter)
        if len(radiusSearchHistory) > 24:
            del radiusSearchHistory[-1]
        radiusSearchHistoryDropDown['values'] = radiusSearchHistory


def get_search_history_choice(var):
    parameter = radiusSearchHistoryDropDown.get()
    get_radius_tab_choice(parameter)


def get_clinic_number_choice(var):
    parameter = choiceBox.get()
    c2.execute(f"SELECT DL_ID FROM DTC_FacDB_2 WHERE GatewayIp='{parameter}'")
    data = c2.fetchone()
    if data is None:
        pass
    else:
        parameter = data[0]
    get_radius_tab_choice(parameter)


def get_local_techs(parameter):
    c2.execute(f"SELECT [User].TechName, [User].AssignedGroup, [User].Notes, [User].Status, "
              f" [Sites].DistanceInMiles, [Sites].TimeInSeconds, [User].ZipCode, [User].UserID, [Sites].ClinicID "
              f" FROM User "
              f" INNER JOIN Sites ON [User].ZipCode = [Sites].TechZip"
              f" WHERE [Sites].ClinicID = '{parameter}' "
              f" ORDER BY [Sites].DistanceInMiles")
    local_tech_data = c2.fetchall()
    for item in local_tech_data:
        tag = str(item[3])
        time = int(item[5])
        time = str(time // 3600) + ':' + str((time % 3600) // 60).zfill(2)
        techTree.insert('', 'end', text=item[0], values=(item[1], item[3], item[4], time, item[2]), tags=(tag,))
    c2.execute(f"SELECT PrefTech FROM PreferredTech WHERE Clinic = '{parameter}'")
    preferred_tech_data = c2.fetchone()
    if preferred_tech_data is None:
        pass
    else:
        prefTechInfo.set(preferred_tech_data[0])


def get_site_info(parameter):
    c2.execute(f"SELECT DL_ID,DL_Name, OG_Name, Address1, Address2, City, State, Zip, Type, Status, Phone, GatewayIp, "
              f" Fax, Operating_Hours, Station_Count, Mitigation, CLINICAL_MGR FROM DTC_FacDB_2 "
              f"WHERE DL_ID = '{parameter}'")
    site_info_data = c2.fetchone()
    if site_info_data is None:
        chosenClinic.set("     Invalid clinic or subnet     ")
        clinicChoice.config(fg='red', font='helvetica 10 bold')
        preserve = "yes"
    else:
        clinicChoice.config(fg='black', font='arial 9')
        chosenClinic.set("     " + parameter)
        clinicNumber.set(site_info_data[0])
        clinicName.set(site_info_data[1])
        ogName.set(site_info_data[2])
        if site_info_data[2] is None:
            zipcodeChoiceBox.delete(0, 'end')
            zipcodeChoiceBox.insert(0, site_info_data[7])
            get_zipcode_tab_choice(site_info_data[7])
        address1.set(site_info_data[3])
        if site_info_data[4] is None:
            address2.set('')
        else:
            address2.set(site_info_data[4])
        city.set(site_info_data[5])
        state.set(site_info_data[6])
        zipCode.set(site_info_data[7])
        typeInfo.set("Type: " + site_info_data[8])
        statusInfo.set(site_info_data[9])
        phoneInfo.set(site_info_data[10])
        gatewayIPInfo.set(site_info_data[11])
        faxInfo.set(site_info_data[12])
        operatingHoursInfo.set(site_info_data[13])
        stationsInfo.set(site_info_data[14])
        if site_info_data[15] == 1:
            mitigationInfo.set("Yes")
        else:
            mitigationInfo.set("No")
        if site_info_data[16] is None:
            clinicMgr.set('')
        else:
            clinicMgr.set(site_info_data[16])
        try:
            intparameter = int(parameter)
            c1.execute(f"SELECT TZone, Helmer FROM Clinic "
                      f" WHERE Clinic_ID = '{intparameter}'")
            timezonedata = c1.fetchone()
            c1.execute("SELECT Printer_Man, Printer_Model, Printer_IP "
                      " FROM Clinic_Printers  WHERE Clinic_ID = {} AND Printer_Man = 'Lexmark' "
                      " AND SUBSTR(Printer_Model,1,2) = 'MX' ORDER BY Printer_IP LIMIT 1".format(parameter))
            printerdata = c1.fetchall()
            if printerdata:
                printerInfo.set(printerdata[0][0] + " " + printerdata[0][1])
                printerIPInfo.set(gatewayIPInfoLabel.get()[0:-1] + printerdata[0][2].strip())
            try:
                helmer = timezonedata[1].strip()
                helmer = helmer.replace("s:", "green .")
                helmer = helmer.replace('h:', 'blue .')
                helmer = helmer.replace(',', ', ')
                both = ['green', 'blue']
                if all(x in helmer for x in both):
                    helmerInfoLabel.configure(background='#99ffcc', foreground='#000000')
                elif 'green' in helmer:
                    helmerInfoLabel.configure(background='#00ff00', foreground='#000000')
                elif 'blue' in helmer:
                    helmerInfoLabel.configure(background='#0099ff', foreground='#000000')
                else:
                    helmerInfoLabel.configure(background='#000000', foreground='#ffffff')
            except TypeError:
                helmer = "Site not in Nagios"
            except AttributeError:
                helmer = "None Monitored"
                helmerInfoLabel.configure(background='#000000', foreground='#ffffff')
            helmerInfo.set(helmer)
            try:
                tz = timezonedata[0][8:]
            except TypeError:
                tz = "No timezone info"
            if tz == "Puerto_Rico":
                timezone = "Georgetown, La Paz, Manaus, San Juan"
            elif tz == "New_York":
                timezone = "Eastern Time"
            elif tz == "Detroit":
                timezone = "Eastern Time"
            elif tz == "Indiana/Indianapolis":
                timezone = "Indiana (East)"
            elif tz == "Chicago":
                timezone = "Central Time"
            elif tz == "Denver":
                timezone = "Mountain Time"
            elif tz == "Phoenix":
                timezone = "Arizona"
            elif tz == "Los_Angeles":
                timezone = "Pacific Time"
            elif tz == "Anchorage":
                timezone = "Alaska"
            elif tz == "Honolulu":
                timezone = "Hawaii"
            else:
                timezone = tz
            timezoneInfo.set(timezone)
        except ValueError:
            timezoneInfo.set("No info available")
            printerInfo.set("No info available")
        # Get and set PM Results Hours data
        prhd = get_pm_results_hours(parameter)
        if prhd == [] or prhd is None:
            pass
        else:
            pmResultDate.set(prhd[0][0])
            mondayPMHoursInfo.set(prhd[0][1] + " - " + prhd[0][2])
            tuesdayPMHoursInfo.set(prhd[0][3] + " - " + prhd[0][4])
            wednesdayPMHoursInfo.set(prhd[0][5] + " - " + prhd[0][6])
            thursdayPMHoursInfo.set(prhd[0][7] + " - " + prhd[0][8])
            fridayPMHoursInfo.set(prhd[0][9] + " - " + prhd[0][10])
            saturdayPMHoursInfo.set(prhd[0][11] + " - " + prhd[0][12])
            sundayPMHoursInfo.set(prhd[0][13] + " - " + prhd[0][14])
        # Get BMT and ATOM info  # TODO make its own function
        c2.execute(f"SELECT FirstName, Last, Descr, GLType, BusinessCell, EmailID"
                  f" FROM BMT_ATOM "
                  f" WHERE SiteID = '{parameter}' AND ALLOCATIONSTATUS = 'ACTIVE'")
        bmtdata = c2.fetchall()
        records = bmtTree.get_children()
        for element in records:
            bmtTree.delete(element)
        for item in bmtdata:
            name = item[0] + " " + item[1]
            bmtTree.insert('', 'end', text=name, values=(item[2], item[3], item[4], item[5]))
        # End Get BMT and ATOM info
        preserve = "no"
    return preserve


def get_zipcode_tab_choice(var):
    if type(var) == str:
        showonfront = "yes"
    else:
        showonfront = "no"
    parameter = zipcodeChoiceBox.get()
    records = tree2.get_children()
    for element in records:
        tree2.delete(element)
    records = tree1.get_children()
    for element in records:
        tree1.delete(element)
    try:
        c2.execute(f"SELECT ID, Zip, Latitude, Longitude "
                  f" FROM  ZipCodeLatLong "
                  f"WHERE Zip = {parameter}")
        data = c2.fetchone()
        if data is None:
            chosenZipcode.set("ZipCode " + zipcodeChoiceBox.get() + " not found in database")
            zipcodeChoice.config(fg='red', font='helvetica 10 bold')
            zipcodeChoiceBox.delete(0, 'end')
        else:
            zipcodeChoice.config(fg='black', font='arial 9')
            chosenZipcode.set("Results for ZipCode " + parameter)
            zipcodeChoiceBox.delete(0, 'end')
            lat, lon = data[2], data[3]
            # Insert tech results
            tech_data = get_techs()
            tech_list = []
            for item in range(len(tech_data)):
                tech_distance = distance((lat, lon), (tech_data[item][3], tech_data[item][4]))
                temp_list = []
                for i in range(6):
                    temp_list.append(tech_data[item][i])
                temp_list.append(tech_distance)
                tech_list.append(temp_list)
            tech_list = sorted(tech_list, key=itemgetter(6))
            for item in tech_list:
                tag = str(item[5])
                tree2.insert('', 'end', text=item[0], values=(item[6], item[1], item[2]), tags=(tag,))
                if showonfront == "yes":
                    techTree.insert('', 'end', text=item[0], values=(item[1], '', item[6], '', ''), tags=(tag,))
            # Insert site results
            site_data = get_sites()
            site_list = []
            for item in range(len(site_data)):
                site_distance = distance((lat, lon), (site_data[item][3], site_data[item][4]))
                temp_list = []
                for i in range(6):
                    temp_list.append(site_data[item][i])
                temp_list.append(site_distance)
                site_list.append(temp_list)
            site_list = sorted(site_list, key=itemgetter(6))
            for item in site_list:
                tag = item[5]
                tree1.insert('', 'end', text=item[0], values=(item[6], item[1], item[2]), tags=(tag,))
            # get most likely OG
            site_mode = []
            for i in range(36):
                if site_list[i][1] is not None:
                    site_mode.append(site_list[i][1])
            zipcodeOGInfo.set(mode(site_mode))
            if showonfront == "yes":
                ogName.set("Best Guess: " + mode(site_mode))
                ogNameLabel.config(fg='green', font='helvetica 10 bold')
            else:
                ogNameLabel.config(fg='black', font='arial 9')
    except:
        chosenZipcode.set("Please enter a valid ZipCode")
        zipcodeChoice.config(fg='red', font='helvetica 10 bold')


def get_sites():
    c2.execute("SELECT [DTC_FacDB_2].DL_ID, [DTC_FacDB_2].OG_Name, "
              " [DTC_FacDB_2].Zip, "
              " [ZipCodeLatLong].Latitude, [ZipCodeLatLong].Longitude, "
              " [DTC_FacDB_2].Status"
              " FROM [DTC_FacDB_2] "
              " INNER JOIN [ZipCodeLatLong] ON [DTC_FacDB_2].Zip = [ZipCodeLatLong].Zip")
    data = c2.fetchall()
    return data


def get_techs():
    c2.execute("SELECT [User].TechName, [User].AssignedGroup, [User].ZipCode,"
              " [ZipCodeLatLong].Latitude, [ZipCodeLatLong].Longitude, [User].Status "
              " FROM User "
              " INNER JOIN ZipCodeLatLong ON [User].ZipCode = [ZipCodeLatLong].Zip"
              " ORDER BY TechName")
    data = c2.fetchall()
    return data


def get_pm_results_hours(parameter):
    c3.execute(f"SELECT Date, "
              f" Normal_Hours_Start_Monday, Normal_Hours_End_Monday, "
              f" Normal_Hours_Start_Tuesday, Normal_Hours_End_Tuesday, "
              f" Normal_Hours_Start_Wednesday, Normal_Hours_End_Wednesday, "
              f" Normal_Hours_Start_Thursday, Normal_Hours_End_Thursday, "
              f" Normal_Hours_Start_Friday, Normal_Hours_End_Friday, "
              f" Normal_Hours_Start_Saturday, Normal_Hours_End_Saturday, "
              f" Normal_Hours_Start_Sunday, Normal_Hours_End_Sunday "
              f" FROM GoodPMFormsData "
              f" WHERE Clinic_ID = '{parameter}'")
    pm_results_hours_data = c3.fetchall()
    prhd = []
    if not pm_results_hours_data:
        pass
    else:
        for item in pm_results_hours_data:
            item = list(item)
            date = item[0]
            date = date.split('/')
            try:
                if len(date[1]) == 1:
                    date[1] = '0' + date[1]
                if len(date[0]) == 1:
                    date[0] = '0' + date[0]
                date = date[2] + date[0] + date[1]
                item.append(date)
                prhd.append(item)
            except IndexError:
                pass
            prhd = sorted(prhd, key=itemgetter(15))
        prhd.reverse()
        return prhd


def distance(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 3959  # mile - 6371 # km

    dlat = radians(lat2-lat1)
    dlon = radians(lon2-lon1)
    a = sin(dlat/2) * sin(dlat/2) + cos(radians(lat1)) \
        * cos(radians(lat2)) * sin(dlon/2) * sin(dlon/2)
    b = 2 * atan2(sqrt(a), sqrt(1-a))
    d = round(radius * b, 2)
    return d


def tree_update(selection):
    r = Tk()
    r.clipboard_clear()
    r.clipboard_append(selection)
    r.update()
    r.destroy()


def select_bmttree_item(a):
    try:
        selection = bmtTree.item(bmtTree.selection()).get("values")[3]
        tree_update(selection)
    except IndexError:
        pass


def select_address(a):
    selection = address1Label.get() + " " + address2Label.get() + " " + cityLabel.get() + " " + stateLabel.get()\
        + " " + zipCodeLabel.get()
    tree_update(selection)


def display_printers(a):
    if printerInfoLabel.get() == '' or printerInfoLabel.get() == "No info available":
        return
    try:
        intparameter = int(clinicChoice.get())
        subnetip = gatewayIPInfoLabel.get()[0:-1]
        c1.execute(f"SELECT Printer_Man, Printer_Model, Printer_IP "
                  f" FROM Clinic_Printers WHERE Clinic_ID = {intparameter}")
        printerdata = c1.fetchall()
        popup = tkinter.Toplevel()
        tkinter.Label(popup, text="Known Printers at Site").pack()
        printer_display = ttk.Treeview(popup, height=len(printerdata), column=['', ''], style='Treeview.Heading')
        printer_display.column('#0', width=100)
        printer_display.column('#1', width=150)
        printer_display.column('#2', width=100)
        printer_display.pack()
        printer_display.heading('#0', text='Make')
        printer_display.heading('#1', text='Model')
        printer_display.heading('#2', text='IP Address')
        for item in printerdata:
            printer_display.insert('', 'end', text=item[0], values=(item[1], subnetip + item[2]))
    except ValueError:
        pass


def display_pm_results(a):
    if pmResultDateLabel.get() == '':
        return
    parameter = clinicChoice.get().strip()
    prhd = get_pm_results_hours(parameter)
    popup = tkinter.Toplevel()
    tkinter.Label(popup, text="PM Survey Hours Results").pack()
    pmresults_display = ttk.Treeview(popup, height=len(prhd), column=['', '', '', '', '', '', ''],
                                     style='Treeview.Heading')
    pmresults_display.column('#0', width=100)
    pmresults_display.column('#1', width=100)
    pmresults_display.column('#2', width=100)
    pmresults_display.column('#3', width=100)
    pmresults_display.column('#4', width=100)
    pmresults_display.column('#5', width=100)
    pmresults_display.column('#6', width=100)
    pmresults_display.column('#7', width=100)
    pmresults_display.pack()
    pmresults_display.heading('#0', text='Date of Survey')
    pmresults_display.heading('#1', text='Monday')
    pmresults_display.heading('#2', text='Tuesday')
    pmresults_display.heading('#3', text='Wednesday')
    pmresults_display.heading('#4', text='Thursday')
    pmresults_display.heading('#5', text='Friday')
    pmresults_display.heading('#6', text='Saturday')
    pmresults_display.heading('#7', text='Sunday')
    for item in prhd:
        pmresults_display.insert('', 'end', text=item[0], values=(item[1] + " - " + item[2],
                                                                  item[3] + " - " + item[4],
                                                                  item[5] + " - " + item[6],
                                                                  item[7] + " - " + item[8],
                                                                  item[9] + " - " + item[10],
                                                                  item[11] + " - " + item[12],
                                                                  item[13] + " - " + item[14]))


def get_google_map(a):
    selection = address1Label.get() + " " + address2Label.get() + " " + cityLabel.get() + " " + stateLabel.get() \
                + " " + zipCodeLabel.get()
    open("https://www.google.com/maps/?q=" + selection + "&z=18", new=1)


def clear_results():
    radiusSearchHistoryDropDown.set('')
    ogNameLabel.config(fg='black', font='arial 9')
    clinicChoice.config(bg='#F0F0F0')
    helmerInfoLabel.config(bg='#f0f0f0', fg='black')
    helmerInfo.set('')
    printerInfo.set('')
    printerIPInfo.set('')
    records = techTree.get_children()
    for element in records:
        techTree.delete(element)
    records = bmtTree.get_children()
    for element in records:
        bmtTree.delete(element)
    clinicNumber.set('')
    clinicName.set('')
    ogName.set('')
    address1.set('')
    address2.set('')
    city.set('')
    state.set('')
    zipCode.set('')
    typeInfo.set('')
    statusInfo.set('')
    phoneInfo.set('')
    gatewayIPInfo.set('')
    faxInfo.set('')
    operatingHoursInfo.set('')
    stationsInfo.set('')
    mitigationInfo.set('')
    timezoneInfo.set('')
    pmResultDate.set('')
    mondayPMHoursInfo.set('')
    tuesdayPMHoursInfo.set('')
    wednesdayPMHoursInfo.set('')
    thursdayPMHoursInfo.set('')
    fridayPMHoursInfo.set('')
    saturdayPMHoursInfo.set('')
    sundayPMHoursInfo.set('')
    prefTechInfo.set('')
    clinicMgr.set('')


# Tkinter window properties
mainWindow = tkinter.Tk()
mainWindow.title("DTC")
mainWindow.option_add("*Font", "arial 9")
mainWindow.option_add("*Background", "#F0F0F0")
tabHolder = ttk.Notebook(mainWindow)
style = ttk.Style()
style.configure('Treeview.Heading', foreground='black', bg='#F0F0F0', font=('arial', 9))

# Variable declaration
choiceBoxValue = tkinter.Variable(mainWindow)
chosenClinic = tkinter.Variable(mainWindow)
clinicNumber = tkinter.Variable(mainWindow)
clinicName = tkinter.Variable(mainWindow)
ogName = tkinter.Variable(mainWindow)
address1 = tkinter.Variable(mainWindow)
address2 = tkinter.Variable(mainWindow)
city = tkinter.Variable(mainWindow)
state = tkinter.Variable(mainWindow)
zipCode = tkinter.Variable(mainWindow)
typeInfo = tkinter.Variable(mainWindow)
statusInfo = tkinter.Variable(mainWindow)
phoneInfo = tkinter.Variable(mainWindow)
gatewayIPInfo = tkinter.Variable(mainWindow)
faxInfo = tkinter.Variable(mainWindow)
operatingHoursInfo = tkinter.Variable(mainWindow)
stationsInfo = tkinter.Variable(mainWindow)
mitigationInfo = tkinter.Variable(mainWindow)
pmResultDate = tkinter.Variable(mainWindow)
timezoneInfo = tkinter.Variable(mainWindow)
mondayPMHoursInfo = tkinter.Variable(mainWindow)
tuesdayPMHoursInfo = tkinter.Variable(mainWindow)
wednesdayPMHoursInfo = tkinter.Variable(mainWindow)
thursdayPMHoursInfo = tkinter.Variable(mainWindow)
fridayPMHoursInfo = tkinter.Variable(mainWindow)
saturdayPMHoursInfo = tkinter.Variable(mainWindow)
sundayPMHoursInfo = tkinter.Variable(mainWindow)
prefTechInfo = tkinter.Variable(mainWindow)
chosenZipcode = tkinter.Variable(mainWindow)
clinicMgr = tkinter.Variable(mainWindow)
zipcodeOGInfo = tkinter.Variable(mainWindow)
helmerInfo = tkinter.Variable(mainWindow)
printerInfo = tkinter.Variable(mainWindow)
printerIPInfo = tkinter.Variable(mainWindow)
radiusSearchHistory = []


# Clinic and Subnet Search Tab
radiusTab = ttk.Frame(tabHolder)
tabHolder.add(radiusTab, text="Clinic and Subnet Search")
tabHolder.pack(expand=1, fill="both")
# Clinic and Subnet Search Tab Top Frame
radiusTabTopFrame = tkinter.Frame(radiusTab)
radiusTabTopFrame.grid(row=0, column=0)
choiceLabel = tkinter.Label(radiusTabTopFrame, text="Enter Clinic ID or Gateway IP:     ", bg='#F0F0F0')
choiceLabel.grid(row=0, column=0)
choiceBox = ttk.Entry(radiusTabTopFrame, textvariable=choiceBoxValue)
choiceBox.grid(row=0, column=1, sticky='ew')
clinicChoice = tkinter.Entry(radiusTabTopFrame, textvariable=chosenClinic, justify='center',  state='readonly')
clinicChoice.grid(row=0, column=2)
spacerLabel = tkinter.Label(radiusTabTopFrame, width=20, text='').grid(row=0, column=3)
radiusSearchHistoryLabel = tkinter.Label(radiusTabTopFrame, text="Search History: ")
radiusSearchHistoryLabel.grid(row=0, column=4)
radiusSearchHistoryDropDown = ttk.Combobox(radiusTabTopFrame, width=15, values=radiusSearchHistory)
radiusSearchHistoryDropDown.grid(row=0, column=5)
# Clinic and Subnet Search Tab Site Info Frame
radiusTabSiteInfoFrame = tkinter.Frame(radiusTab)
radiusTabSiteInfoFrame.grid(row=1, column=0)
# Clinic and Subnet Search Tab Site Info Frame Row 0
clinicLabel = tkinter.Label(radiusTabSiteInfoFrame, text="Clinic")
clinicLabel.grid(row=0, column=0)
clinicNumberLabel = tkinter.Entry(radiusTabSiteInfoFrame, textvariable=clinicNumber, justify='center', state='readonly')
clinicNumberLabel.grid(row=0, column=1)
clinicNameLabel = tkinter.Entry(radiusTabSiteInfoFrame, textvariable=clinicName, justify='center', state='readonly')
clinicNameLabel.grid(row=0, column=2, columnspan=5, sticky='ew')
ogLabel = tkinter.Label(radiusTabSiteInfoFrame, text="OG")
ogLabel.grid(row=0, column=7)
ogNameLabel = tkinter.Entry(radiusTabSiteInfoFrame, textvariable=ogName, justify='center', state='readonly')
ogNameLabel.grid(row=0, column=8, columnspan=2, sticky='ew')
# Clinic and Subnet Search Tab Site Info Frame Row 1
address1Label = tkinter.Entry(radiusTabSiteInfoFrame, textvariable=address1, justify='center', state='readonly')
address1Label.grid(row=1, column=0, columnspan=3, sticky='ew')
address2Label = tkinter.Entry(radiusTabSiteInfoFrame, textvariable=address2, justify='center', state='readonly')
address2Label.grid(row=1, column=3)
cityLabel = tkinter.Entry(radiusTabSiteInfoFrame, textvariable=city, justify='center', state='readonly')
cityLabel.grid(row=1, column=4, columnspan=3, sticky='ew')
stateLabel = tkinter.Entry(radiusTabSiteInfoFrame, textvariable=state, justify='center', state='readonly')
stateLabel.grid(row=1, column=7)
zipCodeLabel = tkinter.Entry(radiusTabSiteInfoFrame, textvariable=zipCode, justify='center', state='readonly')
zipCodeLabel.grid(row=1, column=8, columnspan=2, sticky='ew')
# Clinic and Subnet Search Tab Site Info Frame Row 2
typeLabel = tkinter.Entry(radiusTabSiteInfoFrame, textvariable=typeInfo, justify='center', state='readonly')
typeLabel.grid(row=2, column=0, columnspan=2, sticky='ew')
statusLabel = tkinter.Label(radiusTabSiteInfoFrame, text="Status")
statusLabel.grid(row=2, column=2)
statusInfoLabel = tkinter.Entry(radiusTabSiteInfoFrame, textvariable=statusInfo, justify='center', state='readonly')
statusInfoLabel.grid(row=2, column=3)
gatewayIPLabel = tkinter.Label(radiusTabSiteInfoFrame, text="Gateway IP")
gatewayIPLabel.grid(row=2, column=4)
gatewayIPInfoLabel = tkinter.Entry(radiusTabSiteInfoFrame, textvariable=gatewayIPInfo, justify='center',
                                   state='readonly')
gatewayIPInfoLabel.grid(row=2, column=5)
phoneLabel = tkinter.Label(radiusTabSiteInfoFrame, text="Phone")
phoneLabel.grid(row=2, column=6)
phoneInfoLabel = tkinter.Entry(radiusTabSiteInfoFrame, textvariable=phoneInfo, justify='center', state='readonly')
phoneInfoLabel.grid(row=2, column=7)
faxLabel = tkinter.Label(radiusTabSiteInfoFrame, text="Fax")
faxLabel.grid(row=2, column=8)
faxInfoLabel = tkinter.Entry(radiusTabSiteInfoFrame, textvariable=faxInfo, justify='center', state='readonly')
faxInfoLabel.grid(row=2, column=9)
# Clinic and Subnet Search Tab Site Info Frame Row 3
operatingHoursLabel = tkinter.Label(radiusTabSiteInfoFrame, text="Operating Hours")
operatingHoursLabel.grid(row=3, column=0, columnspan=1)
operatingHoursInfoLabel = tkinter.Entry(radiusTabSiteInfoFrame, textvariable=operatingHoursInfo, justify='center',
                                        state='readonly')
operatingHoursInfoLabel.grid(row=3, column=1, columnspan=3, sticky='ew')
clinicMgrLabel = tkinter.Label(radiusTabSiteInfoFrame, text="Clinic Manager")
clinicMgrLabel.grid(row=3, column=4)
clinicMgrInfoLabel = tkinter.Entry(radiusTabSiteInfoFrame, textvariable=clinicMgr, justify='center', state='readonly')
clinicMgrInfoLabel.grid(row=3, column=5)
stationsLabel = tkinter.Label(radiusTabSiteInfoFrame, text="Stations")
stationsLabel.grid(row=3, column=6)
stationsInfoLabel = tkinter.Entry(radiusTabSiteInfoFrame, textvariable=stationsInfo, justify='center', state='readonly')
stationsInfoLabel.grid(row=3, column=7)
mitigationLabel = tkinter.Label(radiusTabSiteInfoFrame, text="Mitigation")
mitigationLabel.grid(row=3, column=8)
mitigationInfoLabel = tkinter.Entry(radiusTabSiteInfoFrame, textvariable=mitigationInfo, justify='center',
                                    state='readonly')
mitigationInfoLabel.grid(row=3, column=9)
# Clinic and Subnet Search Tab Site Info Frame Row 4
pmResultLabel = tkinter.Label(radiusTabSiteInfoFrame, text="PM Results Hours as of:")
pmResultLabel.grid(row=4, column=0)
mondayPMHoursLabel = tkinter.Label(radiusTabSiteInfoFrame, text="Monday")
mondayPMHoursLabel.grid(row=4, column=3)
tuesdayPMHoursLabel = tkinter.Label(radiusTabSiteInfoFrame, text="Tuesday")
tuesdayPMHoursLabel.grid(row=4, column=4)
wednesdayPMHoursLabel = tkinter.Label(radiusTabSiteInfoFrame, text="Wednesday")
wednesdayPMHoursLabel.grid(row=4, column=5)
thursdayPMHoursLabel = tkinter.Label(radiusTabSiteInfoFrame, text="Thursday")
thursdayPMHoursLabel.grid(row=4, column=6)
fridayPMHoursLabel = tkinter.Label(radiusTabSiteInfoFrame, text="Friday")
fridayPMHoursLabel.grid(row=4, column=7)
saturdayPMHoursLabel = tkinter.Label(radiusTabSiteInfoFrame, text="Saturday")
saturdayPMHoursLabel.grid(row=4, column=8)
sundayPMHoursLabel = tkinter.Label(radiusTabSiteInfoFrame, text="Sunday")
sundayPMHoursLabel.grid(row=4, column=9)
# Clinic and Subnet Search Tab Site Info Frame Row 5
pmResultDateLabel = tkinter.Entry(radiusTabSiteInfoFrame, textvariable=pmResultDate, justify='center', state='readonly')
pmResultDateLabel.grid(row=5, column=0)
timezoneLabel = tkinter.Label(radiusTabSiteInfoFrame, text="Time Zone")
timezoneLabel.grid(row=5, column=1)
timezoneInfoLabel = tkinter.Entry(radiusTabSiteInfoFrame, textvariable=timezoneInfo, justify='center', state='readonly')
timezoneInfoLabel.grid(row=5, column=2)
mondayPMHoursInfoLabel = tkinter.Entry(radiusTabSiteInfoFrame, textvariable=mondayPMHoursInfo, justify='center',
                                       state='readonly')
mondayPMHoursInfoLabel.grid(row=5, column=3)
tuesdayPMHoursInfoLabel = tkinter.Entry(radiusTabSiteInfoFrame, textvariable=tuesdayPMHoursInfo, justify='center',
                                        state='readonly')
tuesdayPMHoursInfoLabel.grid(row=5, column=4)
wednesdayPMHoursInfoLabel = tkinter.Entry(radiusTabSiteInfoFrame, textvariable=wednesdayPMHoursInfo, justify='center',
                                          state='readonly')
wednesdayPMHoursInfoLabel.grid(row=5, column=5)
thursdayPMHoursInfoLabel = tkinter.Entry(radiusTabSiteInfoFrame, textvariable=thursdayPMHoursInfo, justify='center',
                                         state='readonly')
thursdayPMHoursInfoLabel.grid(row=5, column=6)
fridayPMHoursInfoLabel = tkinter.Entry(radiusTabSiteInfoFrame, textvariable=fridayPMHoursInfo, justify='center',
                                       state='readonly')
fridayPMHoursInfoLabel.grid(row=5, column=7)
saturdayPMHoursInfoLabel = tkinter.Entry(radiusTabSiteInfoFrame, textvariable=saturdayPMHoursInfo, justify='center',
                                         state='readonly')
saturdayPMHoursInfoLabel.grid(row=5, column=8)
sundayPMHoursInfoLabel = tkinter.Entry(radiusTabSiteInfoFrame, textvariable=sundayPMHoursInfo, justify='center',
                                       state='readonly')
sundayPMHoursInfoLabel.grid(row=5, column=9)
# Clinic and Subnet Search Tab Site Info Frame Row 6
tkinter.Label(radiusTabSiteInfoFrame, text="").grid(row=6, column=0)
helmerLabel = tkinter.Label(radiusTabSiteInfoFrame, text="Helmer(s):").grid(row=6, column=1)
helmerInfoLabel = tkinter.Entry(radiusTabSiteInfoFrame, textvariable=helmerInfo, justify='center', bg='#f0f0f0')
helmerInfoLabel.grid(row=6, column=2)
tkinter.Label(radiusTabSiteInfoFrame, text="").grid(row=6, column=3, columnspan=2)
printerLabel = tkinter.Label(radiusTabSiteInfoFrame, text="Default Printer:").grid(row=6, column=5)
printerInfoLabel = tkinter.Entry(radiusTabSiteInfoFrame, textvariable=printerInfo, justify='center', state='readonly')
printerInfoLabel.grid(row=6, column=6)
printerIPInfoLabel = tkinter.Entry(radiusTabSiteInfoFrame, textvariable=printerIPInfo, justify='center',
                                   state='readonly')
printerIPInfoLabel.grid(row=6, column=7)
# Clinic and Subnet Search Tab Site Info Frame Row 7
tkinter.Label(radiusTabSiteInfoFrame, text="").grid(row=7, column=0, columnspan=9)
# Clinic and Subnet Search Tab Tech Info Frame
radiusTabTechInfoFrame = tkinter.Frame(radiusTab)
radiusTabTechInfoFrame.grid(row=2, column=0)
prefTechLabel = tkinter.Label(radiusTabTechInfoFrame, text="Preferred Tech").grid(row=0, column=0)
prefTechInfoLabel = tkinter.Entry(radiusTabTechInfoFrame, textvariable=prefTechInfo, justify='center', state='readonly')
prefTechInfoLabel.grid(row=0, column=1)
techTree = ttk.Treeview(radiusTabTechInfoFrame, height=15, column=['', '', '', '', ''], style='Treeview.Heading')
techTree.column('#0', width=150)
techTree.column('#1', width=200)
techTree.column('#2', width=100)
techTree.column('#3', width=95)
techTree.column('#4', width=95)
techTree.column('#5', width=200)
techTree.grid(row=1, column=0, columnspan=3)
techTree.heading('#0', text='Tech Name')
techTree.heading('#1', text='Assigned Group')
techTree.heading('#2', text='Status')
techTree.heading('#3', text='Distance')
techTree.heading('#4', text='Time(hh:mm)')
techTree.heading('#5', text='Notes')
techTree.tag_configure("In", background='#90EE90', font=('helvetica', 10))
techTree.tag_configure('Out', background='#FF6666', font=('helvetica', 10))
techTree.tag_configure('Unavailable', background='#FFFF99', font=('helvetica', 10))
# Clinic and Subnet Search Tab BMT and ATOM Info Frame
radiusTabBMTInfoFrame = tkinter.Frame(radiusTab)
radiusTabBMTInfoFrame.grid(row=3, column=0)
bmtTree = ttk.Treeview(radiusTabBMTInfoFrame, height=10, column=['', '', '', ''])
bmtTree.column('#0', width=150)
bmtTree.column('#1', width=200)
bmtTree.column('#2', width=100)
bmtTree.column('#3', width=100, anchor='center')
bmtTree.column('#3', width=200)
bmtTree.grid(row=0, column=0, columnspan=3)
bmtTree.heading('#0', text='BMT/ATOM Name')
bmtTree.heading('#1', text='Position')
bmtTree.heading('#2', text='Clinic Type')
bmtTree.heading('#3', text='Phone')
bmtTree.heading('#4', text='Email')

# Zip Code Search Tab
zipcodeTab = ttk.Frame(tabHolder)
tabHolder.add(zipcodeTab, text="Zip Code Search")
tabHolder.pack(expand=1, fill="both")
# Zip Code Search Tab Top Frame
zipcodeTabTopFrame = tkinter.Frame(zipcodeTab)
zipcodeTabTopFrame.grid(row=0, column=0)
zipcodeChoiceLabel = tkinter.Label(zipcodeTabTopFrame, text="Enter Zip Code:")
zipcodeChoiceLabel.grid(row=0, column=0)
zipcodeChoiceBox = tkinter.Entry(zipcodeTabTopFrame, width=15)
zipcodeChoiceBox.grid(row=0, column=1, columnspan=1, sticky='ew')
zipcodeChoice = tkinter.Label(zipcodeTabTopFrame, textvariable=chosenZipcode, width=50)
zipcodeChoice.grid(row=0, column=2)
zipcodeOGLabel = tkinter.Label(zipcodeTabTopFrame, text="Best Guess OG:")
zipcodeOGLabel.grid(row=0, column=3)
zipcodeOGInfoLabel = tkinter.Label(zipcodeTabTopFrame, textvariable=zipcodeOGInfo)
zipcodeOGInfoLabel.grid(row=0, column=4)
# Zip Code Search Tab Bottom Frame
zipcodeTabBottomFrame = tkinter.Frame(zipcodeTab)
zipcodeTabBottomFrame.grid(row=1, column=0)
tree1 = ttk.Treeview(zipcodeTabBottomFrame, height=35, column=['', '', ''], style='Treeview.Heading')
tree1.column('#0', width=150)
tree1.column('#1', width=100, anchor='e')
tree1.column('#2', width=200, anchor='center')
tree1.column('#3', width=80, anchor='center')
tree1.grid(row=2, column=0, padx=40)
tree1.heading('#0', text='Site')
tree1.heading('#1', text='Distance')
tree1.heading('#2', text='OG')
tree1.heading('#3', text='Zip')
tree1.tag_configure("PLANNED", background='#B0F4FC', font=('helvetica', 10))
tree1.tag_configure("ACTIVE", background='#90EE90', font=('helvetica', 10))
tree1.tag_configure('CLOSED', background='#FF6666', font=('helvetica', 10))
tree1.tag_configure('SOLD', background='#FF6666', font=('helvetica', 10))
tree1.tag_configure('INACTIVE', background='#FFFF99', font=('helvetica', 10))

tree2 = ttk.Treeview(zipcodeTabBottomFrame, height=35, column=['', '', ''], style='Treeview.Heading')
tree2.column('#0', width=150)
tree2.column('#1', width=100, anchor='e')
tree2.column('#2', width=200, anchor='center')
tree2.column('#3', width=80, anchor='center')
tree2.grid(row=2, column=1, padx=40)
tree2.heading('#0', text='Tech Name')
tree2.heading('#1', text='Distance')
tree2.heading('#2', text='Assigned Group')
tree2.heading('#3', text='Tech Zip')
tree2.tag_configure("In", background='#90EE90', font=('helvetica', 10))
tree2.tag_configure('Out', background='#FF6666', font=('helvetica', 10))
tree2.tag_configure('Unavailable', background='#FFFF99', font=('helvetica', 10))

# Tkinter Setup
choiceBox.focus()
choiceBox.bind("<Return>", get_clinic_number_choice)
zipcodeChoiceBox.bind("<Return>", get_zipcode_tab_choice)
bmtTree.bind('<ButtonRelease-1>', select_bmttree_item)
address1Label.bind('<ButtonRelease-1>', select_address)
address2Label.bind('<ButtonRelease-1>', select_address)
cityLabel.bind('<ButtonRelease-1>', select_address)
stateLabel.bind('<ButtonRelease-1>', select_address)
zipCodeLabel.bind('<ButtonRelease-1>', select_address)
address1Label.bind('<Double-Button-1>', get_google_map)
address2Label.bind('<Double-Button-1>', get_google_map)
cityLabel.bind('<Double-Button-1>', get_google_map)
printerInfoLabel.bind('<Double-Button-1>', display_printers)
printerIPInfoLabel.bind('<Double-Button-1>', display_printers)
pmResultDateLabel.bind('<Double-Button-1>', display_pm_results)
radiusSearchHistoryDropDown.bind("<<ComboboxSelected>>", get_search_history_choice)
radiusSearchHistoryDropDown.bind("<Return>", get_search_history_choice)
zipcodeChoiceBox.focus()
# mainWindow.iconbitmap('DTC_icon.ico')

mainWindow.mainloop()
