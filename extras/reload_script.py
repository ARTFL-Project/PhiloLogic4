from __future__ import absolute_import
from __future__ import print_function
from load_script import *
from philologic.Config import *

## EDIT template_dir to point at your base db BEFORE you run

template_dir = None

if template_dir == "None":
    print("please configure the reload_script.py with a base database before use!")
    exit(1)

if __name__ == "__main__":

    setup_db_dir(db_destination, template_dir)


    ####################
    ## Load the files ##
    ####################

    l = Loader(data_destination,
             load_filters=filters,
             post_filters=post_filters,
             tables=tables,
             xpaths=xpaths,
             metadata_xpaths=metadata_xpaths,
             pseudo_empty_tags=pseudo_empty_tags,
             suppress_tags=suppress_tags,
             token_regex=token_regex,
             default_object_level=default_object_level,
             debug=debug)

    l.add_files(files)
    filenames = l.list_files()
    ## The following line creates a list of the files to parse and sorts the files by filename
    ## Should you need to supply a custom sort order from the command line you need to supply the files variable,
    ## defined at the top of this script, instead of filenames, like so: 
    ## load_metadata = [{"filename":f} for f in files] 
    #load_metadata = [{"filename":f} for f in sorted(filenames)]

    print("parsing headers and sorting:", file=sys.stderr)
    load_metadata = l.sort_by_metadata("date","title","filename",whole_file=True)
    print("load_metadata:", load_metadata, file=sys.stderr)
    l.parse_files(workers,load_metadata)

    l.merge_objects()
    l.analyze()
    l.setup_sql_load()
    l.post_processing()
    l.finish(**extra_locals)

    ## Special reloader stuff; copy over configuration with the important variables intact.
    db_config_path = template_dir+"/data/db.locals.py"
    new_db_config_file = open(db_destination +"/data/db.locals.py", "w")
    db_config = Config(db_config_path,db_locals_defaults,db_locals_header)
    print(db_config, file=new_db_config_file)
    new_db_config_file.close()

    web_config_path = template_dir+"/data/web_config.cfg"
    new_web_config_file = open(db_destination + "/data/web_config.cfg","w")

    web_config = Config(web_config_path,web_config_defaults,web_config_header)
    #  web_config["dbname"] = dbname
    web_config["db_url"] = db_url  
    print(web_config, file=new_web_config_file) 
    new_web_config_file.close()
