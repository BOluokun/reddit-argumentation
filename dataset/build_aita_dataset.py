import json

import praw
from praw.models import Comment, Submission
import pandas as pd

from credentials import CLIENT_ID, CLIENT_SECRET, USER_AGENT, REFRESH

VERDICTS = {'not the a-hole': 'NTA', 'asshole': 'YTA', 'no a-holes here': 'NTA', 'everyone sucks': 'YTA'}

NUM_POSTS = 1000
NUM_LEVELS = 5
MAX_WIDTH = 10


def build_thread_from(sub_thread: list, parent: Comment, level: int, i: int):
    if level < NUM_LEVELS:
        parent_node = {'score': parent.score, 'content': parent.body, 'id': i, 'comments': []}
        i += 1
        sub_thread.append(parent_node)
        replies = [com for com in parent.replies if isinstance(com, Comment)]
        replies.sort(key=lambda com: com.score, reverse=True)
        replies = replies[:MAX_WIDTH] if len(replies) >= MAX_WIDTH else replies
        for r in replies:
            i = build_thread_from(parent_node['comments'], r, level + 1, i)
    return i


def process_post(submission: Submission, data_dict: dict, verdict: str, id: int):
    print(submission.title)
    print(submission.link_flair_text)

    data_dict['title'].append(submission.title)
    data_dict['verdict'].append(verdict)

    i, l = 1, 0 # comment id, level counter
    thread = {'post content': submission.selftext, 'id': i, 'comments': []}
    i += 1
    # Get the top level comments and order by vote score (filtering out the MoreComment objects)
    top_level_comments = [com for com in submission.comments if isinstance(com, Comment)]
    top_level_comments.sort(key=lambda com: com.score, reverse=True)
    top_level_comments = top_level_comments[:MAX_WIDTH] if len(top_level_comments) >= MAX_WIDTH else top_level_comments
    for tlc in top_level_comments:
        i = build_thread_from(thread['comments'], tlc, l, i)

    data_dict['total comments'].append(i - 1)

    thread_filename = f'aita_posts/post_thread_{id}.json'
    with open(thread_filename, 'w') as thread_file:
        json.dump(thread, thread_file, indent=2)
    data_dict['thread file'].append(thread_filename)


if __name__ == '__main__':
    reddit = praw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        refresh_token=REFRESH,
        user_agent=USER_AGENT,
    )

    # Print the username to verify successful authentication
    print(f'Logged in as: {reddit.user.me()} \nWith scopes {reddit.auth.scopes()}')

    # Access AITA subreddit
    subreddit = reddit.subreddit("AmItheAsshole")
    aita_data = {'title': [], 'verdict': [], 'thread file': [], 'total comments': []}
    n = 0
    num_per_verdict = NUM_POSTS // 4

    for v in VERDICTS.keys():
        v_count = 0
        v_posts = subreddit.search(query=f'flair:{v}', sort='comments', time_filter='all', limit=num_per_verdict * 2)
        for submission in v_posts:
            flair_text = submission.link_flair_text.lower()
            verdict = VERDICTS.get(flair_text, '')
            if verdict:
                process_post(submission, aita_data, verdict, n)
                v_count += 1
                n += 1
            else:
                print(f'Skipping submission because flair is "{flair_text}"')
            if v_count >= num_per_verdict:
                break

    df = pd.DataFrame(aita_data)
    with open('post_dataset.tsv', 'wb') as dataset_file:
        df.to_csv(dataset_file, encoding='utf-16', sep='\t')


