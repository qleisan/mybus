# mybus
google assistant enabled bus advice (specific to my personal needs)

Supported platforms:
pythonanywhere - to get https support and 24/7 access (needed for google assistant)
pc             - for development - pycharm, fast design loop
rpi            - no real need to support, https is an issue


https://developer.vasttrafik.se

https://www.instructables.com/id/Create-Custom-Actions-for-Google-Assistant

https://www.pythonanywhere.com/

https://console.actions.google.com/

https://github.com/qleisan/mybus

https://qleisan.pythonanywhere.com/

python_google_assistant.txt



Fixes:
- /debug html page that shows info about the app
- update this README
    - some info about what this project is about
    - reference to project that inspired this project
    - notes on pythonanywhere (observations, howto)
- investigate if pythonanywhere has a "system clock accuracy" that is ok for my needs
    (believe this is the case, code updated to support timezone and daylightsavings)
- make sure app can only be started indirectly on cloud? (affects where log is written)


New features:
- show WiFi IP when running locally (PC)
- color code depending on time left
- night mode (dark scheme after certain time)
- show actual times (and if delayed or not - probably more accurate est. if not delayed)
- rotating log (must be a limit to size)
- flask / noFlask mode? (today define in code)

ToDo:
- test google assistant part (not working anymore?)
- decide on logging strategy 
- refactor "object oriented"


# Observations
logging

* https://www.pythonanywhere.com/user/qleisan/files/var/log/qleisan.pythonanywhere.com.error.log
* https://www.pythonanywhere.com/user/qleisan/files/home/qleisan/mybus.log
* Tracebacks, output from logger."level"()
* vad är egentligen skillnaden?
* På PC "2018-09-16 20:53:08,471 INFO _internal 88 - 127.0.0.1 - - [16/Sep/2018 20:53:08] "GET /wip HTTP/1.1" 200 -"

* https://www.pythonanywhere.com/user/qleisan/files/var/log/qleisan.pythonanywhere.com.server.log
* => printouts from console (program and "system")


	1 -> "Hi Google"
	2 -> "Talk to My local traffic planner"
	3 <- Let's get the test version of My local traffic planner
	4 <- "Hi Leif"
	5 -> nu kommer kommandot
	6 <- nu kommer svaret


misc:
- PA bandwidth https://www.pythonanywhere.com/forums/topic/11341/
