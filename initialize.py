#!/usr/bin/python

import shuttle

shuttle.do_login_full("USER", "PASS")
shuttle.download_all_full()
shuttle.download_map_tiles()
