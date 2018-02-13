# Pinsey
Pinsey is sort of a GUI Tinder data-mining bot that saves all user's photos and details for future analysis. 
It also does facial-detection, search image on Google, automated like/dislike, automated messaging, etc. 
It uses PyQt as its GUI, so it should run on most platforms.

Near the end of 2017, this project was temporarily discontinued because of the lack of updates from [Pynder](https://github.com/charliewolf/pynder).
It requires you to proxy HTTPS to extract your Facebook auth key in order to login to Tinder, but I'm too lazy to do that again since I don't actually use Tinder. 
Since this project is outdated, some things might not work. By the way, Tinder is also now available on the Web.

If you can update or fix some problems regarding Pynder / Tinder API, it should still work well. 
If you wish to continue this project, please fork this. 
There is also a Trello board for this project here: https://trello.com/b/Q1Tumktw/project-pinsey


# How to Use
I did not package this software into .exe or any executables, so you need to run the **Main.py** script to start the GUI. 
Then you need your Facebook auth key, which you can extract by HTTPS proxying and viewing the authentication request when logging into Tinder. 
You can see [this example guide by Joel Auterson](http://www.joelotter.com/2015/05/17/dj-khaled-tinder-bot.html#my-mate-charles).
By entering your authentication details, you should be able to login. Though it may not work because this project is outdated.
