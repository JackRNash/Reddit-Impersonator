# Reddit-Impersonator
##### by Jack Nash
A bot trained using a recurrent neural network to impersonate Reddit users(specifically /r/Cornell users)

## About
A bot that is meant to impersonate users of the subreddit `/r/Cornell`. It uses a finetuned model of OpenAI's GPT-2 to generate comments based on the text of a post. For right now, the identity of this bot will remain anonymous as I'm curious how people will interact with it without knowing it's not a human. 

Very much a work in progress right now!

## Setup
Most of the files needed are in the repo. The pretrained model can be downloaded from [here](https://drive.google.com/file/d/1-8ThQb1GKcMl079aN0HQyRUGOxqcwLmU/view?usp=sharing). It is a large file so be warned. Extract `checkpoint_run1.tar` and make sure the directory `main.py` is in also contains `checkpoint\run1`. There are command line arguments the program accepts, run `python main.py -h` to see them.

You also need 
* the package `gpt-2-simple` which can be installed with pip
* a file `secrets.py` containing your bots' four login credentials: `client_id`, `client_secret`, `username`, `password`

#### First Run
For your first run, execute

`python main.py --download --from_scratch`

This will download the GPT-2 model without the finetuning. If you downloaded the `checkpoint_run1.tar` file, then omit `--from_scratch` as you'll want to use the finetuned model. If you didn't, you may want to finetune first(results will be *bad* without doing this), so I reccomend adding the argument `--finetune` as well. And finally, if you want to use more subreddits than `/r/Cornell`, use `--scrape <subreddit>`.

## Issues

#### Inference is slow
This is the main issue. Without tensorflow having access to a GPU(a pain to set up on Windows), all the inference is done on the CPU and is painfully slow. Generating one comment takes about 150 seconds on the CPU as opposed to a couple on the GPU. I'm not sure what can be done about this without switching away from using `gpt-2-simple`. More investigation is needed, but it makes optimizing the rest of the code pointless because the bottleneck on inference is so severe. It's worth noting the reason this slow inference has been acceptable is because I only plan on running the program once or twice a day. If the goal is to have the bot always be commenting on new posts, something has to change.

#### Command lines not entirely intuitive
I quickly added the command line options and am not entirely satisfied with them. It feels a little unintuitive as is, will revisit later. I think I'll probably add an explicit flag for whether or not to generate comments instead of the current method.

#### Improved responses
The responses tend to be fairly coherent, but are not always relevant to what they're responding to. Something to play with in the future is different ways to feed in the post and other comments to prime the generator as well as sampling from the generated responses(since the model generates many comments at a time). I'm currently using a pretty naive approach but it seems to work better than randomly selecting a comment from the most recent k generated comments.

#### Easier setup
Things seem a bit complicated right now. I don't want people to need to read a paragraph to get the program to work. Explore config files?

## Fun outputs
To come! I don't want to put anything here until the first phase of the experiment is over because I don't want people to identify the bot.
