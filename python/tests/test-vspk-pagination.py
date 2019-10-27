import pytest
import random
from timeit import default_timer as timer
from vspk import v6 as vsdk

page_sizes = [10, 25, 50, 100, 250, 500, 750, 1000]
prefix_count = 10
count_per_prefix = 500

def build_pgc_list(count=175, prefix=0):
    pgc_list = list()
    for num in range(0,count):
        pgc_list.append(
                vsdk.NUPolicyGroupCategory(name="{0:d}_{1:d}".format(prefix,num))
            )
    return pgc_list

def fetch_policy_group_categories(enterprise, page_size):
    page = 0
    objects = enterprise.policy_group_categories.get(page=page, page_size=page_size)
    if objects is not None and len(objects) > 0:
        while True:
            page += 1
            tmp_objects = enterprise.policy_group_categories.get(page=page, page_size=page_size)
            if tmp_objects is None or len(tmp_objects) == 0:
                break
    objects = None
    tmp_objects = None

def test_pagination(printer, nuage_connection):
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    nuage_connection.user.create_child(ent)
    count = 0
    full_list = []
    for prefix in range(0, prefix_count):
        pgc_list = build_pgc_list(count=count_per_prefix, prefix=prefix)
        ent.create_children(pgc_list)
        count += count_per_prefix
        pgc_list = None
    printer("Created {0:d} Policy Group Categories".format(count))
    for page_size in page_sizes:
        start=timer()
        fetch_policy_group_categories(enterprise=ent, page_size=page_size)
        end=timer()
        if page_size < 1000:
            printer("page-size: {0:d} \t\t {1:f}".format(page_size, (end-start)))
        else: 
            printer("page-size: {0:d} \t {1:f}".format(page_size, (end-start)))
    ent.delete()

