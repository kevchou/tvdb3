import re
import os
import tvdb


exts = ('.mkv', '.mp4')


# ----- Regex Expressions -----
# Multi episode files, like 'S09E01 - E02"
multi_ep_regex = re.compile('([sS][0-9]+[eE][0-9]+.*[eE][0-9]+)|([0-9]+(x|\.)[0-9]+(x|\.)[0-9]+)')

# Looks for strings like "S09E01" or "9x01", "9.01"
x_single_ep = re.compile('([sS][0-9]+.?[eE][0-9]+)|([0-9]+(x|\.)[0-9]+)')

# Regex for file extensions
x_video_ext = re.compile('(\.mkv|\.mp4)')

x_season = re.compile('[sS]([0-9]+)')
x_episode = re.compile('[eE]([0-9]+)')
x_alt = re.compile('(x|\.)')


def rename_all_shows_in_dir(d, show_title):
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
            new_file_name = get_new_file_name(old_file_name, show)
            os.rename(root + '/' + old_file_name,
                      root + '/' + new_file_name)
            print(old_file_name + "\t -> \t" + new_file_name)


def get_new_file_name(f, show):
    ep_ext = get_regex_match(f, x_video_ext)
    ep_label = get_regex_match(f, x_single_ep)

    season = num_from_regex_match(ep_label, x_season)
    episode = num_from_regex_match(ep_label, x_episode)

    ep_label = "S{s:02d}E{ep:02d}".format(s=season, ep=episode)
    ep_title = show.get_season(season).get_episode(episode).episode_title

    new_name = "{title} - {sea_ep} - {ep_name}{ext}".format(title=show.show_name,
                                                            sea_ep=ep_label,
                                                            ep_name=ep_title,
                                                            ext=ep_ext)
    return new_name

            
def get_regex_match(text, regex):
    return regex.search(text).group()


def num_from_regex_match(text, regex):
    result = regex.search(text)
    if result:
        return int(result.groups()[0])

    
rename_all_shows_in_dir(".", "king of the hill")    
