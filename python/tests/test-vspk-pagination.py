import pytest
import random
import uuid
from timeit import default_timer as timer
from vspk import v6 as vsdk

page_sizes = [10, 25, 50, 100, 250, 500, 750, 1000]
prefix_count = 20
count_per_prefix = 500

def fetch_items(fetcher, page_size):
    page = 0
    objects = fetcher.get(page=page, page_size=page_size)
    if objects is not None and len(objects) > 0:
        while True:
            page += 1
            tmp_objects = fetcher.get(page=page, page_size=page_size)
            if tmp_objects is None or len(tmp_objects) == 0:
                break
            objects += tmp_objects
    return objects

def rand_mac():
    return "00:%02x:%02x:%02x:%02x:%02x" % (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255)
        )

def test_pagination_with_metadata(printer, nuage_connection):
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    nuage_connection.user.create_child(ent)
    count = 0
    for prefix in range(0, prefix_count):
        md_list = list()
        for num in range(0, count_per_prefix):
            md_list.append(
                    vsdk.NUMetadata(name="{0:d}_{1:d}".format(prefix, num), blob="{0:d}_{1:d}".format(prefix, num))
                )
            ent.create_children(md_list)
        count += count_per_prefix
    md_list = None
    printer("Created {0:d} Metadata objects".format(count))
    printer("Testing Metadata objects:")
    for page_size in page_sizes:
        start=timer()
        mds = fetch_items(fetcher=ent.metadatas, page_size=page_size)
        end=timer()
        if page_size < 1000:
            printer("\tpage-size: {0:d} \t\t {1:f}".format(page_size, (end-start)))
        else: 
            printer("\tpage-size: {0:d} \t {1:f}".format(page_size, (end-start)))
    for md_list in [mds[x:x+150] for x in range(0, len(mds), 150)]:
        nuage_connection.user.bulk_delete(md_list)
    ent.delete()

def test_pagination_with_containers_vports(printer, nuage_connection):
    ent = vsdk.NUEnterprise(name=random.randint(100000,999999))
    nuage_connection.user.create_child(ent)
    dom_template = vsdk.NUDomainTemplate(name=random.randint(100000,999999))
    ent.create_child(dom_template)
    domain = vsdk.NUDomain(name=random.randint(100000,999999), template_id=dom_template.id)
    ent.create_child(domain)
    zone = vsdk.NUZone(name=random.randint(100000,999999))
    domain.create_child(zone)
    subnet_count = 0
    container_count = 0
    for prefix in range(0, prefix_count):
        subnet = vsdk.NUSubnet(name=prefix, address="10.{0:d}.0.0".format(prefix), netmask="255.255.0.0")
        zone.create_child(subnet)
        subnet_count += 1
        container_list = list()
        for num in range(0, count_per_prefix):
            container_list.append(
                    vsdk.NUContainer(
                        name="{0:d}_{1:d}".format(prefix, num),
                        uuid=str(uuid.uuid4()),
                        interfaces=[
                            vsdk.NUContainerInterface(
                                name="{0:d}_{1:d}_eth0".format(prefix, num),
                                mac=rand_mac(),
                                attached_network_id=subnet.id,
                                attached_network_type="SUBNET"
                            )
                        ],
                    )
                )
        nuage_connection.user.create_children(container_list)
        container_count += count_per_prefix
    container_list = None
    printer("Created {0:d} subnets".format(subnet_count))
    printer("Created {0:d} containers, container interfaces and vports".format(container_count))
    printer("Testing vports: ")
    for page_size in page_sizes:
        start=timer()
        vports = fetch_items(fetcher=domain.vports, page_size=page_size)
        end=timer()
        if page_size < 1000:
            printer("\tpage-size: {0:d} \t\t {1:f}".format(page_size, (end-start)))
        else: 
            printer("\tpage-size: {0:d} \t {1:f}".format(page_size, (end-start)))
    printer("Testing containers: ")
    for page_size in page_sizes:
        start=timer()
        containers = fetch_items(fetcher=ent.containers, page_size=page_size)
        end=timer()
        if page_size < 1000:
            printer("\tpage-size: {0:d} \t\t {1:f}".format(page_size, (end-start)))
        else: 
            printer("\tpage-size: {0:d} \t {1:f}".format(page_size, (end-start)))
    for container_list in [containers[x:x+150] for x in range(0, len(containers), 150)]:
        nuage_connection.user.bulk_delete(container_list)
    for vport_list in [vports[x:x+150] for x in range(0, len(vports), 150)]:
        nuage_connection.user.bulk_delete(vport_list)
    domain.delete()
    dom_template.delete()
    ent.delete()

def test_pagination_with_pgc(printer, nuage_connection):
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    nuage_connection.user.create_child(ent)
    count = 0
    for prefix in range(0, prefix_count):
        pgc_list = list()
        for num in range(0, count_per_prefix):
            pgc_list.append(
                    vsdk.NUPolicyGroupCategory(name="{0:d}_{1:d}".format(prefix,num))
                )
        ent.create_children(pgc_list)
        count += count_per_prefix
    pgc_list = None
    printer("Created {0:d} Policy Group Categories".format(count))
    printer("Testing Policy Group Categories:")
    for page_size in page_sizes:
        start=timer()
        pgcs = fetch_items(fetcher=ent.policy_group_categories, page_size=page_size)
        end=timer()
        if page_size < 1000:
            printer("\tpage-size: {0:d} \t\t {1:f}".format(page_size, (end-start)))
        else: 
            printer("\tpage-size: {0:d} \t {1:f}".format(page_size, (end-start)))
    for pgc_list in [pgcs[x:x+150] for x in range(0, len(pgcs), 150)]:
        nuage_connection.user.bulk_delete(pgc_list)
    ent.delete()

