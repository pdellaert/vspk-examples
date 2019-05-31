import pytest
import random
import time

from vspk import v6 as vsdk

# Object instantiate_child?

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
    fetcher, parent, count = nuage_connection.user.enterprises.count(filter="name == '{0}'".format(name))
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
    fetcher, parent, objs = nuage_connection.user.enterprises.fetch()
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

def test_sync_object_delete(nuage_connection):
    # Object delete
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    nuage_connection.user.create_child(ent)
    ent.delete()
    count = nuage_connection.user.enterprises.get_count(filter="name == '{0}'".format(name))
    assert count == 0

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
    obj, conn = wait_for_transaction(trans_id)
    ent.delete(callback=two_args_cb, **async_arg)
    assert conn.response.status_code < 400

def test_async_fetcher_count(nuage_connection, async_arg):
    # Fetcher count
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    nuage_connection.user.create_child(ent)
    trans_id = nuage_connection.user.enterprises.count(filter="name == '{0}'".format(name), callback=three_args_cb, **async_arg)
    fetcher, parent, result = wait_for_fetcher_transaction(trans_id)
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
    fetcher, parent, result = wait_for_fetcher_transaction(trans_id)
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
    obj, conn = wait_for_transaction(trans_id)
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
    obj, conn = wait_for_transaction(trans_id)
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
    obj, conn = wait_for_transaction(trans_id)
    grp_users = grp.users.get()
    usr.delete()
    ent.delete(callback=two_args_cb, **async_arg)
    assert conn.response.status_code < 400
    assert len(grp_users) == 1

def test_async_object_delete(nuage_connection, async_arg):
    # Object delete
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    nuage_connection.user.create_child(ent)
    trans_id = ent.delete(callback=two_args_cb, **async_arg)
    obj, conn = wait_for_transaction(trans_id)
    count = nuage_connection.user.enterprises.get_count(filter="name == '{0}'".format(name))
    assert conn.response.status_code < 400
    assert type(trans_id) is str
    assert count == 0

