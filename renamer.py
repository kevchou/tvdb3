import re
import os
import argparse

import tvdb

# Video file extentions to look for
exts = ('.mkv', '.mp4')

# ----- Regex Expressions -----
# Multi episode files, like 'S09E01 - E02"
multi_ep_regex = re.compile('([sS][0-9]+[eE][0-9]+.*[eE][0-9]+)|([0-9]+(x|\.)[0-9]+(x|\.)[0-9]+)')

# Looks for strings like "S09E01" or "9x01", "9.01"
x_single_ep = re.compile('([sS][0-9]+.?[eE][0-9]+)|([0-9]+(x|\.)[0-9]+)')

# Regex for file extensions
x_video_ext = re.compile("(" + "|".join(["\\" + e for e in exts]) + ")")

x_season = re.compile('[sS]([0-9]+)')
x_episode = re.compile('[eE]([0-9]+)')
x_alt = re.compile('(x|\.)')


def rename_all_shows_in_dir(d, show_title, include_title):
    show = tvdb.Show(list(tvdb.show_search(show_title).keys())[0])

    dirpath = os.path.realpath(d)
    for root, directory, files in os.walk(dirpath):
        # Look for all video files
        ep_files = [f for f in files if f.endswith(exts) and f[0] != '.']

        if len(ep_files) > 0:
            print(root)

        # Loop through each file
        for i in range(len(ep_files)):
            old_file_name = ep_files[i]
            new_file_name = get_new_file_name(old_file_name, show, include_title)
            os.rename(root + '/' + old_file_name,
                      root + '/' + new_file_name)

            print(old_file_name + "\t -> \t" + new_file_name)


def get_new_file_name(old_file_name, show, include_title=False):

    season, episode = get_season_episode_num(old_file_name)

    ep_ext = get_regex_match(old_file_name, x_video_ext)
    ep_label = "S{s:02d}E{ep:02d}".format(s=season, ep=episode)
    ep_title = show.get_season(season).get_episode(episode).episode_title

    new_name = "{sea_ep} - {ep_name}{ext}".format(sea_ep=ep_label,
                                                  ep_name=ep_title,
                                                  ext=ep_ext)

    if include_title:
        new_name = show.show_name + " - " + new_name

    return new_name


def get_season_episode_num(label):
    extracted_label = get_regex_match(label, x_single_ep)
    season_num = num_from_regex_match(extracted_label, x_season)
    episode_num = num_from_regex_match(extracted_label, x_episode)
    return season_num, episode_num


def get_regex_match(text, regex):
    return regex.search(text).group()


def num_from_regex_match(text, regex):
    result = regex.search(text)
    if result:
        return int(result.groups()[0])


def main():
    
    parser = argparse.ArgumentParser(description="Renames file names")
    parser.add_argument('--show', dest="show_name", help="Show title", required=True)
    parser.add_argument('--includetitle', dest="include_title",
                        help="If show title should be included in the renamed files",
                        required=False,
                        action='store_true')
    args = parser.parse_args()

    print(args.show_name)
    print(args.include_title)
    
    rename_all_shows_in_dir(os.getcwd(), args.show_name, args.include_title)

    
if __name__ == "__main__":
    main()
