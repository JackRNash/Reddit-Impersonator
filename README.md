# Reddit-Impersonator
##### by Jack Nash
A bot trained using a recurrent neural network to impersonate Reddit users(specifically /r/Cornell users)

## About
A bot that is meant to impersonate users of the subreddit `/r/Cornell`. It uses a finetuned model of OpenAI's GPT-2 to generate comments based on the text of a post. For right now, the identity of this bot will remain anonymous as I'm curious how people will interact with it without knowing it's not a human. 

Very much a work in progress right now!

## Setup
Most of the files needed are in the repo. The pretrained model can be downloaded from [here](https://drive.google.com/file/d/1-8ThQb1GKcMl079aN0HQyRUGOxqcwLmU/view?usp=sharing). It is a large file so be warned. Extract `checkpoint_run1.tar` and make sure the directory `main.py` is in also contains `checkpoint\run1`. For now, you need this file to run `main.py`. I'm working on making the interface more robust. The groundwork is there to finetune your own models. 

You also need 
* the package `gpt-2-simple` which can be installed with pip
* a file secrets.py containing your bots' four login credentials: `client_id`, `client_secret`, `username`, `password`
