import sys, random, webbrowser, argparse, pkg_resources
import giphy_client
from giphy_client.rest import ApiException

__version__ = 'undefined'
try:
    __version__ = pkg_resources.get_distribution('localvariables-demo-giphy')
except:
    pass

def parse_args(argv):
    arg_parser = argparse.ArgumentParser(description='Search through Giphy for whatever you want!')

    arg_parser.add_argument('-v', '--version',
                            action='store_true',
                            default=False,
                            dest='version',
                            help='Display the current version')
    arg_parser.add_argument('-o', '--open',
                            action='store_true',
                            default=False,
                            dest='open_url',
                            help='Open the returned url in the webbrowser')
    arg_parser.add_argument(action='store',
                            dest='search_string',
                            nargs='?',
                            metavar='search_string',
                            help='The search string')
    return arg_parser.parse_args(argv)

def search_giphy(search_string):
    api_key = '0HFudAoHZusm36vnycTndAskLN1uIeQJ'
    giphy = giphy_client.DefaultApi()
    try: 
        api_response = giphy.gifs_search_get(api_key, search_string, limit=1)
        return api_response.data[0].images.original.url
    except ApiException as e:
        print("Exception when calling DefaultApi->gifs_search_get: %s\n" % e)

def main(argv=sys.argv[1:]):
    args = parse_args(argv)
    if args.version:
        print(__version__)
        return
    if not argv:
        print('Please give me something to search')
        return
    url = search_giphy(argv)
    print(url)
    if args.open_url:
        webbrowser.open(url)

if __name__ == '__main__':
    main()
