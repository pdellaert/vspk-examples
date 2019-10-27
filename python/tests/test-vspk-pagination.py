import pytest
import random
from timeit import default_timer as timer

from vspk import v6 as vsdk

def build_md_list(count=175, prefix=0):
    md_list = list()
    for num in range(0,count):
        md_list.append(
                vsdk.NUMetadata(name="{0:d}_{1:d}".format(prefix,num), blob="{0:d}_{1:d}".format(prefix,num))
            )
    return md_list

def fetch_metadata(enterprise, page_size):
    page = 0
    (fetcher, parent, objects) = enterprise.metadatas.fetch(page=page, page_size=page_size)
    if objects is not None and len(objects) > 0:
        while True:
            page += 1
            (fetcher, parent, tmp_objects) = enterprise.metadatas.fetch(page=page, page_size=page_size)
            if tmp_objects is None or len(tmp_objects) == 0:
                break
            objects += tmp_objects

def test_pagination(nuage_connection, printer):
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    page_sizes = [1, 10, 25, 50, 100, 250, 500]
    nuage_connection.user.create_child(ent)
    full_md_list=[]
    for prefix in range(0,10):
        md_list = build_md_list(count=500, prefix=prefix)
        ent.create_children(md_list)
        full_md_list += md_list
    for page_size in page_sizes:
        start=timer()
        fetch_metadata(enterprise=ent, page_size=page_size)
        end=timer()
        printer("page-size: {0:d} \t {1:d}".format(page_size, (end-start)))
    ent.delete()

