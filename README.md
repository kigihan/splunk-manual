# Install Splunk on AWS

## Prepare OS

- Launch a ubuntu EC2

> 一開始用t2.micro跑結果credit起飛，沒多久就沒有反應爛掉了
![](https://github.com/kigihan/splunk-manual/raw/master/screenshot/t2.micro.png)

- Add EBS 50GB
- [AWS官方文件：mount EBS on ubuntu](https://docs.aws.amazon.com/en_us/AWSEC2/latest/UserGuide/ebs-using-volumes.html) (我 mkdir `/d2`)

## Install splunk

### download install file
```sh
sudo wget -O splunk-7.2.5-088f49762779-Linux-x86_64.tgz 'https://www.splunk.com/bin/splunk/DownloadActivityServlet?architecture=x86_64&platform=linux&version=7.2.5&product=splunk&filename=splunk-7.2.5-088f49762779-Linux-x86_64.tgz&wget=true'
```

### install on what directory you want
*-C* 指定要安裝的目錄

```sh
sudo tar xvzf splunk-7.2.5-088f49762779-Linux-x86_64.tgz -C /d2
```

結果會安裝在指定目錄 ( */d2* ) 下的 `splunk`
```sh
ubuntu@ip-172-31-24-220:/d2$ ll
total 334792
drwxr-xr-x  3 root  root         70 Mar 27 05:41 ./
drwxr-xr-x 24 root  root       4096 Mar 27 05:30 ../
drwxr-xr-x  8 10777 10777       222 Mar 12 03:04 splunk/
-rw-r--r--  1 root  root  342816180 Mar 14 21:42 splunk-7.2.5-088f49762779-Linux-x86_64.tgz
```

### setup config

有需要的話可參考 [調整設定](#custom-usage) 部分

### start splunk via cli

使用安裝目錄下的 `/bin` 目錄下的 `splunk`

```sh
ubuntu@ip-172-31-24-220:/d2/splunk/bin$ sudo ./splunk start
```

安裝後初次執行會跑出好幾頁的使用守則，翻到底輸入 *y* 同意
```sh
Splunk Software License Agreement 10.01.2018
Do you agree with this license? [y/n]: y
```

然後會要你建立一組帳密
```sh
This appears to be your first time running this version of Splunk.

Splunk software must create an administrator account during startup. Otherwise, you cannot log in.
Create credentials for the administrator account.
Characters do not appear on the screen when you type in credentials.

Please enter an administrator username: isadmin
Password must contain at least:
   * 8 total printable ASCII character(s).
Please enter a new password:
Please confirm new password:
```

成功的話最後會長這樣
```sh
All preliminary checks passed.

Starting splunk server daemon (splunkd)...
Generating a 2048 bit RSA private key
...........................................+++++
..............................+++++
writing new private key to 'privKeySecure.pem'
-----
Signature ok
subject=/CN=ip-172-31-24-220/O=SplunkUser
Getting CA Private Key
writing RSA key
Done


Waiting for web server at http://127.0.0.1:8000 to be available.... Done


If you get stuck, we're here to help.
Look for answers here: http://docs.splunk.com

The Splunk web interface is at http://ip-172-31-24-220:8000
```

# custom usage
## parse AD event log

> 要分析AD log，因為不知名的原因，AD的syslog一堆亂碼很難看，所以請NET匯出evtx檔給我們，一樣亂碼，所以搞成下面的奇怪workaround

### evtx轉xml
Windows Event Log 本身是xml格式
找了個python處理evtx檔：[python-evtx](https://github.com/williballenthin/python-evtx)

#### 安裝 python-evtx
```
pip3 install python-evtx
```

#### 產出xml檔
為了讓後續splunk parse欄位方便一點，利用python-evtx，自己再加點code改了些raw data架構

執行程式
```sh
 han.chen@hanchen:/5.solution/Splunk$ python3 evtx_dump.py ./OneDrive_1_2019-3-27/20190327-dc01.evtx
```
輸出的檔名會是 <原檔名>\_new.xml

#### 君子可欺之以方
因為我們用免費版，所以每天log限量**500mb**

建議可以用 **gzip** 壓成 **.gz** 檔，壓縮比不錯高大概有二十幾倍吧

splunk很君子會自動解開 **.gz**檔，*棒棒*

### splunk 解AD的evtx轉出的xml

如果此時匯入splunk看，會發現splunk不認識這份 ~爆改垃圾~ 新的log，完全parse不出欄位

#### 設定檔

參考 [官方文件](https://docs.splunk.com/Documentation/Splunk/7.2.5/Admin/Propsconf) 將 **props.conf** 從 `$HOME/etc/system/default/` 複製到 `$HOME/etc/system/local/`

```sh
ubuntu@ip-172-31-24-220:/d2/splunk/etc/system/local$ sudo cp ../default/props.conf ./props.conf
ubuntu@ip-172-31-24-220:/d2/splunk/etc/system/local$ ll
total 48
drwxr-xr-x 2 10777 10777    98 Mar 27 10:30 ./
drwxr-xr-x 9 10777 10777   104 Mar 12 02:34 ../
-r--r--r-- 1 10777 10777   265 Mar 12 02:20 README
-rw------- 1 root  root     34 Mar 27 05:51 inputs.conf
-rw------- 1 root  root     60 Mar 27 05:51 migration.conf
-r--r--r-- 1 root  root  31434 Mar 27 10:30 props.conf
-rw------- 1 root  root    586 Mar 27 05:51 server.conf
```

但 props.conf 是唯讀的，得改一下

```sh
ubuntu@ip-172-31-24-220:/d2/splunk/etc/system/local$ sudo chmod 644 props.conf
ubuntu@ip-172-31-24-220:/d2/splunk/etc/system/local$ ll
total 48
drwxr-xr-x 2 10777 10777    98 Mar 28 01:47 ./
drwxr-xr-x 9 10777 10777   104 Mar 12 02:34 ../
-r--r--r-- 1 10777 10777   265 Mar 12 02:20 README
-rw------- 1 root  root     34 Mar 27 05:51 inputs.conf
-rw------- 1 root  root     60 Mar 27 05:51 migration.conf
-rw-r--r-- 1 root  root  31434 Mar 27 10:30 props.conf
-rw------- 1 root  root    586 Mar 27 05:51 server.conf
```

### 修改設定

參考 [回答](https://answers.splunk.com/answers/187195/how-to-add-and-parse-xml-data-in-splunk.html) 寫入設定

在 **props.conf** 新增類型 **[DC-xml]** 讓splunk可以parse我們轉出來的xml檔

```props.conf
[DC-xml]
KV_MODE = xml
LINE_BREAKER = (</Event>)
NO_BINARY_CHECK = 1
SHOULD_LINEMERGE = false
TRUNCATE = 0
pulldown_type = 1
BREAK_ONLY_BEFORE_DATE =
DATETIME_CONFIG =
TIME_PREFIX = <TimeCreated>
disabled = false
```

修改後，如果已經啟動splunk，需要重啟splunk
```sh
ubuntu@ip-172-31-24-220:/d2/splunk/bin$ sudo ./splunk restart
```


## optional
```
splunk set  web-port 9000
```

```
splunk set  splunkd-port 9089
```

```
splunk set servername foo
```

```
splunk set datastore-dir /var/splunk/
```


# 使用 splunk

瀏覽器輸入網址： `http://<IP>:8000`

![](https://github.com/kigihan/splunk-manual/raw/master/screenshot/00.png)

輸入帳密登入，看到起始頁面

![](https://github.com/kigihan/splunk-manual/raw/master/screenshot/01.png)

選擇「新增資料」

![](https://github.com/kigihan/splunk-manual/raw/master/screenshot/02.png)

我們用下面的第一個「上傳」

![](https://github.com/kigihan/splunk-manual/raw/master/screenshot/03.png)

點「選擇檔案」上傳要分析的log，等待上傳

完成後點擊「下一步」

![](https://github.com/kigihan/splunk-manual/raw/master/screenshot/04.png)

在「來源類型」下拉選單中找到相應的類型，本例中選擇自訂的「未分類的 > DC-xml」

「來源類型」成功運作的話，會如上圖右側區塊一樣，「時間」與「事件」資料都正常顯示

確認後點擊「下一步」

![](https://github.com/kigihan/splunk-manual/raw/master/screenshot/05.png)

「主機」此處直接以「常數值」手動設定，因為上傳的是DC01的log，就設定為「10.0.1.5-DC01」

範例的使用情境單純，所以自己認得就可以了

之後點擊「檢閱」

![](https://github.com/kigihan/splunk-manual/raw/master/screenshot/06.png)

假裝認真看一下，沒問題就可點擊「送出」，等上傳檔案跑完

![](https://github.com/kigihan/splunk-manual/raw/master/screenshot/07.png)

順利的話，頁面會顯示「檔案已成功上傳」訊息

之後點擊「開始搜尋」就可以看到splunk解析log的結果，並依需求搜尋了

![](https://github.com/kigihan/splunk-manual/raw/master/screenshot/08.png)