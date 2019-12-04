# CS50-Final-Project-HAL
Hello world, this is my CS50 final project. When deciding what to do for my project I knew that I wanted to do something sports related that I would use. I realized that I frequently missed Harvard Athletics events I would have been interested in because I did not know about them/did not have them in my calendar. That inspired me to create this program which automatically adds whatever harvard athletics events you want to you google calendar based on sport. 

This is a command-line program so it is going to require the user to download Python but never fear I have added step-by step instructions below in order to make the process as painless as possible. 

# Instructions
1. First thing you'll need to do is download Python to your computer if you don't already have it. This is a simple process that is outlined https://realpython.com/installing-python/ here for most all operating systems. The most important parts of the process are making sure that you have Python added to the PATH of your device and making sure you know where Python is located on your computer so that you can identify where your working directory is. 
2. Using the IDLE application create two new .py files in your working directory where you can copy and paste both config.py and HAL.py. Also make sure that you have requirements.txt and HAL_secret.json in your working directory.
3. Make a new empty JSON file that is named HAL.json which will be where the authorized credentials are stored so that everytime you run HAL.py it doesn't have to ask for authentication every time.
4. Open up your command prompt and first make sure that you have Python installed properly on your device by typing in python. This should show you the version of python that you have. To get back to your command prompt enter quit(). 
5. Now that you know that Python is working properly write the line pip install -r requirements.txt to make sure that you have all of the programs that you need are installed before running config.py and HAL.py.
6. Before running the script if you would like to specify which sports show up in your calendar this needs to be changed within the HAL.py file manually. It's really simple, all you have to do is go to line ___ and right after not in gcal_event_ids you can add and "Hockey" in ical_event.description: to filter all of the events that just involve the hockey teams. I outline this more clearly in my overview video.
7. Finally you can run the config.py and HAL.py. Once you run these This should trigger the OAuth2 authentication process and prompt you to allow the app to access your calendar. It will say that it is unsafe but you're going to have to trust me and allow the process to run by continue past this warning by clicking Advanced > Go to {Project Name} (unsafe). If all goes well your credentials should be stored within HAL.json and the Harvard Athletics Events that you selected should have been put in your calendar!
