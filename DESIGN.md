I have spent a lot of time working on Harvard Athletics Link (HAL) and the way that I wanted to implement it and in this document I will take you
through the decision making process.

I started working on my prject over Thanksgiving break, just brainstorming and trying to figure out what the best way to transfer ical to gcal 
data would be. I though about making a SQL database with all of the events from the Harvard Athletics ical in it and then parsing them out to the gcal
but then I decided I didn't need to do that after looking more in-depth at the Google Calendar API. After registering a project through the
Google API Console and getting access to the Google Calendar API in one python document I could pull the ical data for every event and then
put all of the basic information into the Google Calendar without the need of a SQL database. I started writing the code myself but then I realized that
someone probably already has figured out how to change Icalendar events into Google Calendar events. I modified a lot of my code from the github user andrewramsey and
his ical_to_gcal_sync.py. 

At first, I tried to run the code just the way it was in my CS50 IDE to make sure that the code worked. Unfortunetaly I kept on running into a localhost
error that wouldn't allow my identification to be saved in the blank JSON file, therefore not allowing my program access to the Google Calendar. I looked far and wide
for the solution and asked for support from my extremely helpful TF Josh Archibald and finally came to the conclusion that the error was a result of an incorrect
re-direct URL. Since I was running the program through the CS50 IDE and not on my own computer, localhost could not work as the re-direct URL. I found the part of my code that was causing this to happen (within the get_credentials function)
and I tried to adjust it to a different URL or prompt another method of returning authentification. Unfortunetaly I couldn't figure anything out and I was unsure of 
what URL to use in order for the authentification to re-direct back to the CS50 IDE so I accepted the reality that I would have to go to a different platform in order to 
run my code.

From here I tried to use Jupyter Notebook through Anaconda as I had used it to run python in a previous class. Unfortunetaly, I was getting a similar issue from this platform
so I finally 
