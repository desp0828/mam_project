This project is a combination of scraper, database and web. It is deployed on the Azure cloud platform, including virtual machine, microsoft SQL and the webapp.

# 1.The project requirements

Build a data pipeline from **web** to **sql database** and present the result using **dashboard**.

#### i. Create an mssql sql database, virtual machine

#### ii. Web scraping the following https://www.ccilindia.com/FPI_ARCV.aspx. Create the data store using the following two steps:

##### a. Backfill: download the 2nd table for all dates. Create **ONE** table in sql database to store all the data. Use **bcp utility** for bulk insert. 

##### b. Increment: create scheduled task to web scrape the website hourly. If there is any update, insert the incremental records into the database. Use **crontab** to schedule the run.

#### iii. Present the result in **dashboard**. The dashboard has the following function: select one ISIN in dropdown list, the chart will plots the time series of the daily Indicative Value Of Aggregate Holding of FPIS (INR CR#) for that ISIN.

# 2.Web scraping

Use browser developer mode (press F12) to see the format of postdata and header.

In the postdata of given webpage 'https://www.ccilindia.com/FPI_ARCV.aspx', there are some strange fields:


```
    '__EVENTTARGET': '',
    '__EVENTARGUMENT':'', 
    '__LASTFOCUS':'', 
    '__VIEWSTATE': '',
    '__VIEWSTATEGENERATOR': '',
    '__VIEWSTATEENCRYPTED':'', 
    '__EVENTVALIDATION': '',
    'drpArchival': ''
```

The `__EVENTTARGET` can be one of `['grdFPISWH$ctl19$ctl00','grdFPISWH$ctl19$ctl01','grdFPISWH$ctl19$ctl02','grdFPISWH$ctl19$ctl03','grdFPISWH$ctl19$ctl014']`, and it indicates the page that user selected. And the filed `drpArchival` indicates the 'Date' user selected. Other values are some very long irregular strings.

So the most difficult thing for scraping is: these long irregular strings will change with each click. How to post the right value to the server is the key point.

We use the following method:

#### i. Firstly, use 'urllib2.Request' to get these fileds' values for the first time posting.
#### ii. Then use the previously obtained values to fill postdata structure and post it to the server. For the first time, only the date list is gotten from the server and it can be used for checking whether there is any update on the web.
#### iii. After checking updates, there are three functions to process when: a) there is no update; b) there are updates; c) the program is the first time to run.
#### iv. If the program goes b) and c), it will need to post on this url for lots of times. Here, during each posting, we should store the fields' values mentioned before and use them in the next posting. Just like the first time.

The data scraped from web are saved as follow:

```
IN0020190016,07.27 GS 2026,8769.60000,55000.00000,15.94,2020-02-14
IN0020130061,08.83 GS 2023,13017.83600,83000.00000,15.68,2020-02-14
IN0020180025,07.37 GS 2023,5963.85900,39987.81300,14.91,2020-02-14
IN0020130012,07.16 GS 2023,9885.13900,77100.00000,12.82,2020-02-14
IN0020150010,07.68 GS 2023,10003.15700,88132.01200,11.35,2020-02-14
IN0020070028,08.08 GS 2022,7594.44100,68969.41100,11.01,2020-02-14
```

Running method: `python mam_scraper.py`. Before executing, you should modify the personal information, such as username and password.

***Using `crontab` to set program running hourly.***

Open config file:

```
crontab -e
```

Add following event:

```
0 */1 * * * ./mam_scraper.py
```

The format of cron event is `m h dom mon dow command`. The example shows how to run `mam_scraper.py` every hour. You can change the interval by modifing 1 to 2,3 or other numbers. Don't forget to change `./mam_scraper.py` to your own path and cammand.

# 3.SQL operations

Create Microsoft SQL database and server on Azure.

Install the `mssql-tools` in the virtual machine. So that `sqlcmd` and `bcp` can be used in the virtual machine to connect to the mssql.

***The ip of virtual machine should be added to mssql server firewall exception, otherwise you will never connect to mssql!!!***

Firstly, use `sqlcmd` to connect to mssql and create a table.

Connecting:

```
sqlcmd -S <servername/ip> -d <database_name> -U <your_username> -P <your_password>
```

The `-S <servername/ip>` is the instance of database server, it can be both `<ip>` and the `<url>`, and here is using url. The parameter `-d` means which database you want to connect, so the `<database_name>` should be your database name. And username and password are contained in `-U` and `-P` parameters.

Create table `mam`:
```
1> create table mam
2> (ISIN varchar(20),
3> SD varchar(50),
4> INR decimal(11,5),
5> Security_INR decimal(12,5),
6> Sec_Holding decimal(5,2),
7> Date date)
8> go
```

After the table is created, we can use `bcp` to insert and read from databse.

Here is a command to read all data from table `mam`:


```
bcp <tablename> out output.txt -S <servername/ip> -U <your_username> -P <your_password> -f mam.fmt

```

Other test cases are in `tools/query.sh` and `tools/insert.sh`. Change the personal information when you use.

Another thing is how to generate format file. Before using `bcp` to operate mssql, you should first generate a fomat file, like:

```
bcp <tablename> out output.txt -S <servername/ip> -U <your_username> -P <your_password> -f mam.fmt
```

You can modify the format file `mam.fmt` as you want.

So in the `mam_scraper.py`, the data file will be inserted into database by directly using `bcp` command.

# 4.Display

To install dashboard in python, use `pip`:

```
pip install dash
```

Considering mssql operations are also needed, install `pyodbc`:


```
pip install pyodbc
```

Other requirements are shown in `dash-az/requirements.txt`

The `application.py` is very easy as it is rewritten from the basic framework of dashboard. The logic is: First, query the database to get all the ISINs. The ISINs are stored in an array for the dropdown displaying. After each time the dropdown is clicked, a callback function will be triggered to query the database and return the corresponding 'date' and 'INR'. Arrays of these two values are directly used as the x and y coordinates of the drawing, respectively.

To run as: `python application.py`. Also, you should fill in your own SQL information.

You can also run it in the background: `nohup python application.py &` and kill it by `pkill application.py`

The final effect:
![dashboard display](https://github.com/desp0828/mam_project/blob/master/screenshot/display.png)

