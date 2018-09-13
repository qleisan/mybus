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


ToDo:
- update this README
    - some info about what this project is about
    - reference to project that inspired this project
    - notes on pythonanywhere (observations, howto)
- investigate if pythonanywhere has a "system clock accuracy" that is ok for my needs
    (believe this is the case, code updated to support timezone and daylightsavings)
- flask not needed on PC? (slows design loop?)

- handle different ways of starting the "flask_app" - directly or indirectly
    affect logfiles/directory
- get the next two options




	1 -> "Hi Google"
	2 -> "Talk to My local traffic planner"
	3 <- Let's get the test version of My local traffic planner
	4 <- "Hi Leif"
	5 -> nu kommer kommandot
	6 <- nu kommer svaret