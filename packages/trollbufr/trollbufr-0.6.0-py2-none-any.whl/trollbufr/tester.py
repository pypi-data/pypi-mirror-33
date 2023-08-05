'''
Created on Mar 2, 2018

@author: amaul
'''
if __name__ == "__main__":
    import os
    import logging
    import json
    from bufr import Bufr
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(levelname)s: %(module)s:%(lineno)d] %(message)s"))
    handler.setLevel(logging.DEBUG)
    logging.getLogger('').setLevel(logging.DEBUG)
    logging.getLogger('').addHandler(handler)

    with open("out.orig.json", "rb")as fh_in:
        json_data = json.load(fh_in)

    bufr = Bufr(tab_fmt="libdwd", tab_path=os.getenv("BUFR_TABLES"))
    bin_data = bufr.encode(json_data[0]["bufr"], load_tables=True)

    with open("out.bin", "wb") as fh_out:
        if json_data[0]["heading"] is not None:
            print >>fh_out, "%s\r\r" % json_data[0]["heading"]
        print >>fh_out, bin_data,
