# Gfetch - back up Gmail correspondence locally

Gfetch is a Gmail correspondence backup app. It saves raw and cleaned versions of your emails with a specified correspondent, including attachments, to your filesystem. It also lets you delete all the downloaded files with the push of a button.

It started life as a [CLI app](https://github.com/jwjacobson/gmailfetcher) but I've since converted it into a web app using Flask.

### Tech stack
Gfetch is built using [Flask](https://flask.palletsprojects.com/en/3.0.x/) 3 and [Python](https://www.python.org/) 3.12. It uses [Redis](https://redis.io/) for server-side caching and [Tailwind CSS](https://tailwindcss.com/) for styling. It downloads emails using the (Gmail API)[https://developers.google.com/gmail/api/guides].  

### Installation
Currently, you have to install Gfetch locally to use it. You will need Python 3.12 or later.
1. Clone this repository.
2. Navigate to the 'gfetch_web' directory.
3. Create a virtual environment ```python -m venv venv''' (Windows/Linux) or ```python3 -m venv venv``` (Mac).
4. Activate the virtual environment ```.\venv\Scripts\activate``` (Windows) or ```source venv/bin/activate```
5. Install the dependencies. 
  You can use the pregenerated requirements.txt file: ```pip install -r requirements.txt```
  Or you can create a new one to install from with ```pip install pip-tools; pip-compile; pip install -r requirements.txt```
6. Create a .env file in the root directory with environment variables (I've supplied a file, env-template, that shows what you need and has some default values (Windows users will need to change the filepath syntax))
7. Now you should be able to run the app with ```flask run```, but you need to do some further set up via Google Cloud to make it functional.

### Setting up Google Cloud
1. Go the the [Google Cloud Console](https://console.cloud.google.com/welcome/) and create an account if you don't have one (you will need to input payment info but won't be charged if you have a free trial)
2. Using the navigation menu in the top-left of the screen, go to ```APIs & Services```, then ```Enable APIs and Services```
3. Search ```gmail``` in the box and find the Gmail API, then enable it
4. In the ```APIs & Services``` menu, click ```Credentials```, then click ```Create Credentials```, then ```OAuth Client ID```
5. Follow the prompts to generate credentials
6. Once you've created the credentials, you should see them on the main credentials page. Download the credentials JSON. If you're using the values from env-template, you should save it in ```gfetch_web/src/app/``` with the filename ```credentials.json```. If you save it anywhere else, make sure the CREDS variable in .env points to that file.

### Running the app
1. Start Flask: ```flask run```
2. Ctrl-click on ```http://127.0.0.1:5000``` — This will open gfetch in your default browser.
3. Enter an email address in the box and click the Fetch Emails button (You will be redirected to authorize the app via your Google account: choose the account you want to use then press Continue twice)
4. Press the Delete downloaded files button to delete any files you downloaded
5. You can close the app by closing your browser and pressing Ctrl-C in the terminal running Flask.

### License
Gfetch is [free software](https://www.fsf.org/about/what-is-free-software), released under version 3.0 of the GPL. Everyone has the right to use, modify, and distribute jazztunes subject to the [stipulations](https://github.com/jwjacobson/jazztunes/blob/main/LICENSE) of that license.
