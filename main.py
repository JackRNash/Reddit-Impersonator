import praw
import time
import random
import secrets
import argparse
import tqdm
import gpt_2_simple as gpt2 # Can be installed with pip if you don't have

# Just made a seperate file instead of using praw.ini format, had some
# weird issues and this is easier to maintain
# To use your own bot, just make a file with the four variables listed below
reddit = praw.Reddit(user_agent='Reddit impersonator using gpt-2',
                     client_id=secrets.client_id,
                     client_secret=secrets.client_secret,
                     password=secrets.password,
                     username=secrets.username)
comment_delimiter='\n\n\n\n\n'

def get_comments(reddit=reddit, subreddit_str='cornell', print_every=10, comment_delimiter='\n\n\n\n\n', num_posts = 1000):
    """
    Get the comments of the specified subreddit(s)

    reddit - A praw.Reddit object that will be used to scrape the posts
    subreddit_str - String that specifies subreddit(s) to scrape(do multiple with a + like 'cornell+college')
    print_every - How often to print an update (every _ number of posts scanned)
    comment_delimiter - String to be inserted after each comment
    num_posts - Number of posts to scrape(limited due to praw/Reddit api).
                None results in max num of posts
    """
    subreddit = reddit.subreddit(subreddit_str)

    comments = []
    counter = 0
    prev_time = time.time()

    print('\nScraping posts\n' + '-'*20)
    for submission in tqdm(subreddit.hot(limit=num_posts)):
        # Get ALL comments
        submission.comments.replace_more(limit=None, threshold=0)

        for comment in submission.comments:
            # Ignore "users" like /u/Cornell_Class_Bot which aren't actual humans
            if 'bot' in str(comment.author).lower():
                continue
            comments.append(str(comment.body) + comment_delimiter)

        counter += 1
        if counter % print_every == 0:
            print('{0}/{1} ... Time for {3} posts: {2:.3f}s'.format(counter,
                        num_posts, time.time() - prev_time, print_every))
            prev_time = time.time()

    # Write to file, overriding previous one
    file = open('scraped_text\comments_{}.txt'.format(subreddit_str), 'w', encoding="utf-8")
    file.write(''.join(comments))

    print('Saved {} comments from {} posts'.format(len(comments), counter))
    print('Change the name of the file to avoid being overridden in the future.')


def finetune_gpt2(iterations=1000, text_path='scraped_text\comments.txt'):
    """
    Finetune gpt2

    text_path - Directory of text file to use to finetune_gpt
    iterations - Iterations to train gpt2
    """
    if not gpt2.is_gpt2_downloaded(model_name='345M'):
        print('Warning: Downloading large file')
        gpt2.download_gpt2(model_name='345M')
    print('\nFinetuning\nWarning: Very slow without GPU')
    print('-'*30)
    gpt2.finetune(sess,
                  text_path,
                  model_name='345M',
                  overwrite=True,
                  steps=iterations)


def predict_comment(seed_phrase, num_parents):
    """
    Use the loaded gpt2 model to generate predicted comments. On a CPU takes
    quite a while! In my experience, it takes roughly 150 seconds to predict a
    comment

    seed_phrase - String to use as input to prime the model
    num_parents - number of parent comments to comment being replied to
    """
    print('Predicting comment')
    start_time = time.time()
    possible_comments = gpt2.generate(sess, prefix=seed_phrase,
                        include_prefix=False, return_as_list=True)
    print('Time it took to generate: {:.3f}s'.format(time.time()-start_time))
    possible_comments = possible_comments[0].split(comment_delimiter)

    # Comments quickly become irrelevent, so pick one of the more recent comments
    # Pick first generated comment @TODO play with sampling from a range of generated comments
    idx = min(len(possible_comments)-1, num_parents+1)

    comment = possible_comments[idx]
    print('Responded:', comment)
    return comment


def make_comment(subreddit='cornell', num_comments=(3, 7), mode='new', debug_mode=False):
    """
    Method to call for making comments on a subreddit

    subreddit - sub to post on
    num_comments - tuple that is range of comments to post (inclusive)
    mode - pick posts to comment on from the 'hot' posts or the 'new' posts
    debug_mode - if true, don't actually reply
    """
    subreddit = reddit.subreddit(subreddit)
    min_comments, max_comments = num_comments
    num_comments = random.randrange(min_comments, max_comments+1)

    # Pick a random subset of posts to comment on
    if mode == 'hot':
        subreddit_selection = subreddit.hot(limit=2*max_comments)
    else:
        subreddit_selection = subreddit.new(limit=2*max_comments)

    # Get subset of text posts
    posts = [submission for submission in subreddit_selection if len(submission.selftext) > 0]
    posts_to_comment = random.sample(posts, num_comments)

    # Comment on selected posts
    for post in posts_to_comment:
        print('\n\nPost title:', post.title)
        seed_phrase = post.selftext+comment_delimiter

        # REMOVED ABILITY TO RESPOND TO COMMENTS
        # That's what's commented out below. Comments were low quality. Keeping code
        # around for experimentation later

        # seed_phrase = [post.selftext+comment_delimiter] # Use as input to the model
        # post.comments.replace_more(limit=None, threshold=0) # Get all comments
        # comment = random.choice(post.comments)
        # if 'bot' in comment.author.name:
        #     continue # temp fix just skip the bots
        # parent = comment

        # Get all parent comments. Only refresh every 9 levels for efficiency(praw docs)
        # refresh_count = 0
        # num_parents = 0
        # while not parent.is_root:
        #     num_parents += 1
        #     parent = parent.parent()
        #     seed_phrase.prepend(parent.body+comment_delimiter)
        #     if refresh_count % 9 ==0:
        #         parent.refresh()
        #     refresh += 1

        # Put all comment / parent comment / post body text together and use as
        # input for generated comment
        # seed_phrase.append(comment.body+comment_delimiter)
        # seed_phrase = ''.join(seed_phrase)[:1000] # don't want super long seed_phrase
        # bot_comment = predict_comment(seed_phrase, num_parents)
        bot_comment = predict_comment(seed_phrase, 0)
        if not debug_mode:
            post.reply(bot_comment)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--download', action='store_true',
            help='Download the pretrained, but not finetuned model. Should do on first run. Bot will not generate comments.')
    parser.add_argument('-f', '--finetune', action='store_true',
            help='Finetune the model with scraped_text\comments.txt. Bot will not generate comments.')
    parser.add_argument('-s', '--scrape', default='', help='Subreddit to scrape comments from')
    parser.add_argument('-fs', '--from_scratch', action='store_true',
            help='Do not use the saved checkpoint of a finetuned gpt2 model')
    parser.add_argument('--debug', action='store_true',
            help='Enables debug mode where comments are not actually replied to')
    args = parser.parse_args()

    if len(args.scrape) > 0:
        get_comments(subreddit_str=args.scrape)
        print('\n\nNext phase: Predicting comments\nPress CTRL + C to abort')

    sess = gpt2.start_tf_sess()
    if args.download:
        gpt2.download_gpt2(model_name='345M')
    if args.from_scratch:
        gpt2.load_gpt2(sess, run_name='345M', checkpoint_dir='models')
    else:
        print('Loading checkpoint...')
        gpt2.load_gpt2(sess)
    if args.finetune:
        finetune_gpt2()

    # Rarely download/finetune and then want to generate comments, so only gen
    # comments when these options are not enabled.
    if not(args.download or args.finetune):
        make_comment(subreddit='cornell', mode='new', num_comments=(2,6), debug_mode=args.debug)
