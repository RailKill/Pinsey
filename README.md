# Pinsey
Pinsey is sort of a GUI Tinder data-mining bot that saves all user's photos and details for future analysis. 
It also does facial-detection, search image on Google, automated like/dislike, automated messaging, etc. 
It uses PyQt as its GUI, so it should run on most platforms.

There is also a Trello board for this project here: https://trello.com/b/Q1Tumktw/project-pinsey


# How to Use
I did not package this software into .exe or any executables, so you need to run the **Main.py** script to start the GUI. 
I also did not set up virtualenv to manage the dependencies yet, but included the **requirements.txt** file which you can use to install the required packages with pip: ```pip install -r requirements.txt```.
Then you need your Facebook auth key, which you can extract by HTTPS proxying and viewing the authentication request when logging into Tinder. 
You can see [this example guide by Joel Auterson](http://www.joelotter.com/2015/05/17/dj-khaled-tinder-bot.html#my-mate-charles).
By entering your authentication key and ID, you should be able to login.
