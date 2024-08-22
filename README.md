# Gfetch - back up Gmail correspondence locally

Gfetch is a Gmail correspondence backup app. It saves raw and cleaned versions of your emails with a specified correspondent, including attachments, to your filesystem. It also lets you delete all the downloaded files with the push of a button.

It started life as a [CLI app](https://github.com/jwjacobson/gmailfetcher) but I've since converted it into a web app using Flask.

### Tech stack
Gfetch is built using [Flask](https://flask.palletsprojects.com/en/3.0.x/) 3 and [Python](https://www.python.org/) 3.12. It uses [Redis](https://redis.io/) for server-side caching and [Tailwind CSS](https://tailwindcss.com/) for styling. It downloads emails using the (Gmail API)[https://developers.google.com/gmail/api/guides].  

### Installation
Currently, you have to install Gfetch locally to use it.