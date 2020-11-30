import pytest
import random
import time

from vspk import v6 as vsdk

# Object instantiate_child?
def generate_children(parent, child_type, prefix_count=5, count_per_prefix=500):
    count = 0
    for prefix in range(0, prefix_count):
        child_list = list()
        for num in range(0, count_per_prefix):
            child_list.append(
                    child_type(name="{0:d}_{1:d}".format(prefix,num))
                )
        parent.create_children(child_list)
        count += count_per_prefix
    child_list = None

def test_sync_object_create_child(nuage_connection):
    # Object create_child
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    nuage_connection.user.create_child(ent)
    ent.delete()
    assert ent.id
    assert ent.name == '{0}'.format(name)

def test_sync_fetcher_count(nuage_connection):
    # Fetcher count
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    nuage_connection.user.create_child(ent)
    _, _, count = nuage_connection.user.enterprises.count(filter="name == '{0}'".format(name))
    ent.delete()
    assert count == 1

def test_sync_fetcher_get_count(nuage_connection):
    # Fetcher get_count
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    nuage_connection.user.create_child(ent)
    count = nuage_connection.user.enterprises.get_count(filter="name == '{0}'".format(name))
    ent.delete()
    assert count == 1

def test_sync_fetcher_fetch(nuage_connection):
    # Fetcher fetch
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    nuage_connection.user.create_child(ent)
    _, _, objs = nuage_connection.user.enterprises.fetch()
    ent.delete()
    assert len(objs) >= 1

def test_sync_fetcher_get(nuage_connection):
    # Fetcher get
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    nuage_connection.user.create_child(ent)
    objs = nuage_connection.user.enterprises.get()
    ent.delete()
    assert len(objs) >= 1

def test_sync_fetcher_get_all(nuage_connection):
    # Fetcher get_all
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    nuage_connection.user.create_child(ent)
    prefix_count = 3
    count_per_prefix = 300
    generate_children(ent, vsdk.NUPolicyGroupCategory, prefix_count=prefix_count, count_per_prefix=count_per_prefix)
    objs = ent.policy_group_categories.get_all()
    ent.delete()
    assert len(objs) >= (prefix_count * count_per_prefix)

def test_sync_fetcher_get_all_filter(nuage_connection):
    # Fetcher get_all with filter
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    nuage_connection.user.create_child(ent)
    prefix_count = 3
    count_per_prefix = 300
    generate_children(ent, vsdk.NUPolicyGroupCategory, prefix_count=prefix_count, count_per_prefix=count_per_prefix)
    objs = ent.policy_group_categories.get_all(filter="'name' CONTAINS '1_'")
    ent.delete()
    assert len(objs) == count_per_prefix

def test_sync_fetcher_get_first(nuage_connection):
    # Fetcher get_first
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    nuage_connection.user.create_child(ent)
    obj = nuage_connection.user.enterprises.get_first()
    ent.delete()
    assert type(obj) is vsdk.NUEnterprise

def test_sync_object_fetch(nuage_connection):
    # Object fetch
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    nuage_connection.user.create_child(ent)
    ent_new = vsdk.NUEnterprise(id=ent.id)
    ent_new.fetch()
    ent.delete()
    assert ent_new.name == '{0}'.format(name)

def test_sync_object_save(nuage_connection):
    # Object save
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    nuage_connection.user.create_child(ent)
    new_name = random.randint(1000000,9999999)
    ent.name = new_name
    ent.save()
    ent.fetch()
    ent.delete()
    assert ent.name == '{0}'.format(new_name)

def test_sync_object_assign(nuage_connection):
    # Object assign
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    nuage_connection.user.create_child(ent)
    usr = vsdk.NUUser(user_name="sync-user", password="sync-user", first_name="sync", last_name="user", email="sync@user.local")
    ent.create_child(usr)
    grp = ent.groups.get_first()
    grp.assign([usr], vsdk.NUUser)
    grp_users = grp.users.get()
    usr.delete()
    ent.delete()
    assert len(grp_users) == 1

def test_sync_object_add_member(nuage_connection):
    # Object add member
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    nuage_connection.user.create_child(ent)
    usr_a = vsdk.NUUser(user_name="sync-user-a", password="sync-user-a", first_name="sync", last_name="user-a", email="sync@user.a.local")
    usr_b = vsdk.NUUser(user_name="sync-user-b", password="sync-user-b", first_name="sync", last_name="user-b", email="sync@user.b.local")
    ent.create_children([usr_a, usr_b])
    grp = ent.groups.get_first()
    grp.assign([usr_a], vsdk.NUUser)
    count_a = grp.users.get_count()
    grp.add_members([usr_b], vsdk.NUUser)
    count_b = grp.users.get_count()
    nuage_connection.user.bulk_delete([usr_a, usr_b])
    ent.delete()
    assert count_a == 1
    assert count_b == 2

def test_sync_object_remove_member(nuage_connection):
    # Object remove_member
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    nuage_connection.user.create_child(ent)
    usr_a = vsdk.NUUser(user_name="sync-user-a", password="sync-user-a", first_name="sync", last_name="user-a", email="sync@user.a.local")
    usr_b = vsdk.NUUser(user_name="sync-user-b", password="sync-user-b", first_name="sync", last_name="user-b", email="sync@user.b.local")
    ent.create_children([usr_a, usr_b])
    grp = ent.groups.get_first()
    grp.assign([usr_a, usr_b], vsdk.NUUser)
    count_a = grp.users.get_count()
    grp.remove_members([usr_b], vsdk.NUUser)
    count_b = grp.users.get_count()
    nuage_connection.user.bulk_delete([usr_a, usr_b])
    ent.delete()
    assert count_a == 2
    assert count_b == 1

def test_sync_object_delete(nuage_connection):
    # Object delete
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    nuage_connection.user.create_child(ent)
    ent.delete()
    count = nuage_connection.user.enterprises.get_count(filter="name == '{0}'".format(name))
    assert count == 0

def test_sync_object_delete_response_choice_false(nuage_connection):
    # Object delete with response_choice=0
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    nuage_connection.user.create_child(ent)
    _, conn = ent.delete(response_choice=0)
    count = nuage_connection.user.enterprises.get_count(filter="name == '{0}'".format(name))
    ent.delete()
    assert conn.response.status_code == 300
    assert count == 1

transaction_status = {}
def two_args_cb(obj, conn):
    transaction_status[conn.transaction_id] = {
        'obj': obj,
        'conn': conn
    }

def three_args_cb(fetcher, parent, result):
    transaction_status[fetcher.transaction_id] = {
        'fetcher': fetcher,
        'parent': parent,
        'result': result
    }

def wait_for_transaction(trans_id, timeout=5):
    wait_time = 0.0
    while trans_id not in transaction_status.keys():
        time.sleep(0.1)
        wait_time += 0.1
        if wait_time >= float(timeout):
            return None, None
    obj = transaction_status[trans_id]['obj']
    conn = transaction_status[trans_id]['conn']
    return obj, conn

def wait_for_fetcher_transaction(trans_id, timeout=5):
    wait_time = 0.0
    while trans_id not in transaction_status.keys():
        time.sleep(0.1)
        wait_time += 0.1
        if wait_time >= float(timeout):
            return None, None
    fetcher = transaction_status[trans_id]['fetcher']
    parent = transaction_status[trans_id]['parent']
    result = transaction_status[trans_id]['result']
    return fetcher, parent, result

def test_async_object_create_child(nuage_connection, async_arg):
    # Object create_child
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    trans_id = nuage_connection.user.create_child(ent, callback=two_args_cb, **async_arg)
    _, conn = wait_for_transaction(trans_id)
    ent.delete(callback=two_args_cb, **async_arg)
    assert conn.response.status_code < 400

def test_async_fetcher_count(nuage_connection, async_arg):
    # Fetcher count
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    nuage_connection.user.create_child(ent)
    trans_id = nuage_connection.user.enterprises.count(filter="name == '{0}'".format(name), callback=three_args_cb, **async_arg)
    _, _, result = wait_for_fetcher_transaction(trans_id)
    ent.delete(callback=two_args_cb, **async_arg)
    assert result == 1

def test_async_fetcher_get_count(nuage_connection, async_arg):
    # Fetcher get_count
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    nuage_connection.user.create_child(ent)
    count = nuage_connection.user.enterprises.get_count(filter="name == '{0}'".format(name))
    ent.delete(callback=two_args_cb, **async_arg)
    assert count == 1

def test_async_fetcher_fetch(nuage_connection, async_arg):
    # Fetcher fetch
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    nuage_connection.user.create_child(ent)
    trans_id = nuage_connection.user.enterprises.fetch(callback=three_args_cb, **async_arg)
    _, _, result = wait_for_fetcher_transaction(trans_id)
    ent.delete(callback=two_args_cb, **async_arg)
    assert len(result) >= 1

def test_async_fetcher_get(nuage_connection, async_arg):
    # Fetcher get
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    nuage_connection.user.create_child(ent)
    objs = nuage_connection.user.enterprises.get()
    ent.delete(callback=two_args_cb, **async_arg)
    assert len(objs) >= 1

def test_async_fetcher_get_first(nuage_connection, async_arg):
    # Fetcher get_first
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    nuage_connection.user.create_child(ent)
    obj = nuage_connection.user.enterprises.get_first()
    ent.delete(callback=two_args_cb, **async_arg)
    assert type(obj) is vsdk.NUEnterprise

def test_async_object_fetch(nuage_connection, async_arg):
    # Object fetch
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    nuage_connection.user.create_child(ent)
    ent_new = vsdk.NUEnterprise(id=ent.id)
    trans_id = ent_new.fetch(callback=two_args_cb, **async_arg)
    _, conn = wait_for_transaction(trans_id)
    ent.delete(callback=two_args_cb, **async_arg)
    assert conn.response.status_code < 400
    assert ent_new.name == '{0}'.format(name)

def test_async_object_save(nuage_connection, async_arg):
    # Object save
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    nuage_connection.user.create_child(ent)
    new_name = random.randint(1000000,9999999)
    ent.name = new_name
    trans_id = ent.save(callback=two_args_cb, **async_arg)
    _, conn = wait_for_transaction(trans_id)
    ent.fetch()
    ent.delete(callback=two_args_cb, **async_arg)
    assert conn.response.status_code < 400
    assert type(trans_id) is str
    assert ent.name == '{0}'.format(new_name)

def test_async_object_assign(nuage_connection, async_arg):
    # Object assign
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    nuage_connection.user.create_child(ent)
    usr = vsdk.NUUser(user_name="sync-user", password="sync-user", first_name="sync", last_name="user", email="sync@user.local")
    ent.create_child(usr)
    grp = ent.groups.get_first()
    trans_id = grp.assign([usr], vsdk.NUUser, callback=two_args_cb, **async_arg)
    _, conn = wait_for_transaction(trans_id)
    grp_users = grp.users.get()
    usr.delete()
    ent.delete(callback=two_args_cb, **async_arg)
    assert conn.response.status_code < 400
    assert len(grp_users) == 1

def test_async_object_add_member(nuage_connection, async_arg):
    # Object add member
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    nuage_connection.user.create_child(ent)
    usr_a = vsdk.NUUser(user_name="sync-user-a", password="sync-user-a", first_name="sync", last_name="user-a", email="sync@user.a.local")
    usr_b = vsdk.NUUser(user_name="sync-user-b", password="sync-user-b", first_name="sync", last_name="user-b", email="sync@user.b.local")
    ent.create_children([usr_a, usr_b])
    grp = ent.groups.get_first()
    grp.assign([usr_a], vsdk.NUUser)
    count_a = grp.users.get_count()
    trans_id = grp.add_members([usr_b], vsdk.NUUser, callback=two_args_cb, **async_arg)
    _, conn = wait_for_transaction(trans_id)
    count_b = grp.users.get_count()
    nuage_connection.user.bulk_delete([usr_a, usr_b])
    ent.delete()
    assert count_a == 1
    assert conn.response.status_code < 400
    assert count_b == 2

def test_async_object_remove_member(nuage_connection, async_arg):
    # Object remove_member
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    nuage_connection.user.create_child(ent)
    usr_a = vsdk.NUUser(user_name="sync-user-a", password="sync-user-a", first_name="sync", last_name="user-a", email="sync@user.a.local")
    usr_b = vsdk.NUUser(user_name="sync-user-b", password="sync-user-b", first_name="sync", last_name="user-b", email="sync@user.b.local")
    ent.create_children([usr_a, usr_b])
    grp = ent.groups.get_first()
    grp.assign([usr_a, usr_b], vsdk.NUUser)
    count_a = grp.users.get_count()
    trans_id = grp.remove_members([usr_b], vsdk.NUUser, callback=two_args_cb, **async_arg)
    _, conn = wait_for_transaction(trans_id)
    count_b = grp.users.get_count()
    nuage_connection.user.bulk_delete([usr_a, usr_b])
    ent.delete()
    assert count_a == 2
    assert conn.response.status_code < 400
    assert count_b == 1

def test_async_object_delete(nuage_connection, async_arg):
    # Object delete
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    nuage_connection.user.create_child(ent)
    trans_id = ent.delete(callback=two_args_cb, **async_arg)
    _, conn = wait_for_transaction(trans_id)
    count = nuage_connection.user.enterprises.get_count(filter="name == '{0}'".format(name))
    assert conn.response.status_code < 400
    assert type(trans_id) is str
    assert count == 0

def test_async_object_delete_response_choice_false(nuage_connection, async_arg):
    # Object delete with response_choice=0
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    nuage_connection.user.create_child(ent)
    trans_id = ent.delete(response_choice=0, callback=two_args_cb, **async_arg)
    _, conn = wait_for_transaction(trans_id)
    count = nuage_connection.user.enterprises.get_count(filter="name == '{0}'".format(name))
    ent.delete()
    assert conn.response.status_code == 300
    assert type(trans_id) is str
    assert count == 1
