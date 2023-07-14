import plac
import os

import raker


@plac.pos('urls',
          "URLs to crawl content from (comma separated) or a file containing URLs (one per line) to crawl content from",
          type=str, metavar='urls')
@plac.opt('youtube_api_key', "YouTube API key", type=str)
@plac.opt('output', "Output jsonl file path", type=str)
@plac.opt('mongo_uri', "MongoDB URI", type=str, abbrev='m_uri')
@plac.opt('mongo_db', "MongoDB database name", type=str, abbrev='m_db')
@plac.opt('mongo_col', "MongoDB collection name", type=str, abbrev='m_col')
@plac.flg('debug', "Enable debug mode")
def main(urls, debug=False, youtube_api_key=None, mongo_uri=None, mongo_db=None, mongo_col=None, output=None):
    if youtube_api_key:
        os.environ['YOUTUBE_API_KEY'] = youtube_api_key
    if output:
        os.environ['OUTPUT'] = output
    if debug:
        os.environ['RAKER_DEBUG'] = '1'
    if mongo_uri:
        if not mongo_db:
            raise ValueError("MongoDB database name is required")
        os.environ['MONGO_URI'] = mongo_uri
        os.environ['MONGO_DATABASE'] = mongo_db
        if mongo_col:
            os.environ['MONGO_COLLECTION'] = mongo_col
    # check urls is a file path or comma separated list
    if os.path.isfile(urls):
        with open(urls) as f:
            urls = f.readlines()
    else:
        urls = urls.split(',')
    raker.Raker.from_urls(urls)


if __name__ == "__main__":
    plac.call(main)
