import pytest
import random
import time

from vspk import v6 as vsdk

transaction_status = {}

def build_md_list(count=175):
    md_list = list()
    for num in range(0,count):
        md_list.append(
                vsdk.NUMetadata(name=num, blob=num)
            )
    return md_list

def two_args_cb(a, b):
    pass

def bulk_async_cb(result, connection, metadata, errors):
    transaction_status[connection.transaction_id] = {
            'result': result,
            'connection': connection,
            'metadata': metadata,
            'errors': errors
        }

def wait_for_transaction(trans_id, timeout=10):
    wait_time = 0.0
    while trans_id not in transaction_status.keys():
        time.sleep(0.1)
        wait_time += 0.1
        if wait_time >= float(timeout):
            return None, None, None
    result = transaction_status[trans_id]['result']
    connection = transaction_status[trans_id]['connection']
    metadata = transaction_status[trans_id]['metadata']
    errors = transaction_status[trans_id]['errors']
    return result, connection, metadata, errors

def test_sync_bulk_root_object_create_children(nuage_connection, async_arg):
    # Root object create_child
    name_a = random.randint(100000,999999)
    name_b = random.randint(100000,999999)
    ent_a = vsdk.NUEnterprise(name=name_a)
    ent_b = vsdk.NUEnterprise(name=name_b)
    result, connection, metadata, errors = nuage_connection.user.create_children([ent_a, ent_b])
    nuage_connection.user.bulk_delete([ent_a, ent_b], callback=bulk_async_cb, **async_arg)
    assert metadata['total'] == 2
    assert metadata['success'] == 2
    assert metadata['failure'] == 0
    assert len(result) == 2
    assert connection.response.status_code < 400
    assert not errors

def test_sync_bulk_object_single_create_children(nuage_connection, async_arg):
    # Object create_child
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    nuage_connection.user.create_child(ent)
    md_list = build_md_list(count=1)
    result, connection, metadata, errors = ent.create_children(md_list)
    ent.delete(callback=two_args_cb, **async_arg)
    assert metadata['total'] == 1
    assert metadata['success'] == 1
    assert metadata['failure'] == 0
    assert len(result) == 1
    assert connection.response.status_code < 400
    assert not errors

def test_sync_bulk_object_create_children(nuage_connection, async_arg):
    # Object create_child
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    nuage_connection.user.create_child(ent)
    md_list = build_md_list(count=175)
    result, connection, metadata, errors = ent.create_children(md_list)
    ent.delete(callback=two_args_cb, **async_arg)
    assert metadata['total'] == 175
    assert metadata['success'] == 175
    assert metadata['failure'] == 0
    assert len(result) == 175
    assert connection.response.status_code < 400
    assert not errors

def test_sync_bulk_object_single_save(nuage_connection, async_arg):
    # Object save
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    nuage_connection.user.create_child(ent)
    md_list = build_md_list(count=1)
    result, connection, metadata, errors = ent.create_children(md_list)
    for md in md_list:
        md.name += 'u'
    result, connection, metadata, errors = nuage_connection.user.bulk_save(md_list)
    ent.delete(callback=two_args_cb, **async_arg)
    assert metadata['total'] == 1
    assert metadata['success'] == 1
    assert metadata['failure'] == 0
    assert len(result) == 1
    assert connection.response.status_code < 400
    assert not errors

def test_sync_bulk_object_save(nuage_connection, async_arg):
    # Object save
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    nuage_connection.user.create_child(ent)
    md_list = build_md_list(count=175)
    result, connection, metadata, errors = ent.create_children(md_list)
    for md in md_list:
        md.name += 'u'
    result, connection, metadata, errors = nuage_connection.user.bulk_save(md_list)
    ent.delete(callback=two_args_cb, **async_arg)
    assert metadata['total'] == 175
    assert metadata['success'] == 175
    assert metadata['failure'] == 0
    assert len(result) == 175
    assert connection.response.status_code < 400
    assert not errors

def test_sync_bulk_object_single_delete(nuage_connection, async_arg):
    # Object delete
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    nuage_connection.user.create_child(ent)
    md_list = build_md_list(count=1)
    result, connection, metadata, errors = ent.create_children(md_list)
    result, connection, metadata, errors = nuage_connection.user.bulk_delete(md_list)
    ent.delete(callback=two_args_cb, **async_arg)
    assert metadata['total'] == 1
    assert metadata['success'] == 1
    assert metadata['failure'] == 0
    assert len(result) == 1
    assert connection.response.status_code < 400
    assert not errors

def test_sync_bulk_object_delete(nuage_connection, async_arg):
    # Object delete
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    nuage_connection.user.create_child(ent)
    md_list = build_md_list(count=175)
    result, connection, metadata, errors = ent.create_children(md_list)
    result, connection, metadata, errors = nuage_connection.user.bulk_delete(md_list)
    ent.delete(callback=two_args_cb, **async_arg)
    assert metadata['total'] == 175
    assert metadata['success'] == 175
    assert metadata['failure'] == 0
    assert len(result) == 175
    assert connection.response.status_code < 400
    assert not errors

def test_async_bulk_object_single_create_children(nuage_connection, async_arg):
    # Object create_child
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    nuage_connection.user.create_child(ent)
    md_list = build_md_list(count=1)
    trans_id = ent.create_children(md_list, callback=bulk_async_cb, **async_arg)
    result, connection, metadata, errors = wait_for_transaction(trans_id)
    ent.delete(callback=two_args_cb, **async_arg)
    assert metadata['total'] == 1
    assert metadata['success'] == 1
    assert metadata['failure'] == 0
    assert len(result) == 1
    assert connection.response.status_code < 400
    assert not errors

def test_async_bulk_object_create_children(nuage_connection, async_arg):
    # Object create_child
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    nuage_connection.user.create_child(ent)
    md_list = build_md_list(count=175)
    trans_id = ent.create_children(md_list, callback=bulk_async_cb, **async_arg)
    result, connection, metadata, errors = wait_for_transaction(trans_id)
    ent.delete(callback=two_args_cb, **async_arg)
    assert metadata['total'] == 175
    assert metadata['success'] == 175
    assert metadata['failure'] == 0
    assert len(result) == 175
    assert connection.response.status_code < 400
    assert not errors

def test_async_bulk_object_single_save(nuage_connection, async_arg):
    # Object save
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    nuage_connection.user.create_child(ent)
    md_list = build_md_list(count=1)
    result, connection, metadata, errors = ent.create_children(md_list)
    for md in md_list:
        md.name += 'u'
    trans_id = nuage_connection.user.bulk_save(md_list, callback=bulk_async_cb, **async_arg)
    result, connection, metadata, errors = wait_for_transaction(trans_id)
    ent.delete(callback=two_args_cb, **async_arg)
    assert metadata['total'] == 1
    assert metadata['success'] == 1
    assert metadata['failure'] == 0
    assert len(result) == 1
    assert connection.response.status_code < 400
    assert not errors

def test_async_bulk_object_save(nuage_connection, async_arg):
    # Object save
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    nuage_connection.user.create_child(ent)
    md_list = build_md_list(count=175)
    result, connection, metadata, errors = ent.create_children(md_list)
    for md in md_list:
        md.name += 'u'
    trans_id = nuage_connection.user.bulk_save(md_list, callback=bulk_async_cb, **async_arg)
    result, connection, metadata, errors = wait_for_transaction(trans_id)
    ent.delete(callback=two_args_cb, **async_arg)
    assert metadata['total'] == 175
    assert metadata['success'] == 175
    assert metadata['failure'] == 0
    assert len(result) == 175
    assert connection.response.status_code < 400
    assert not errors

def test_async_bulk_object_single_delete(nuage_connection, async_arg):
    # Object delete
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    nuage_connection.user.create_child(ent)
    md_list = build_md_list(count=1)
    result, connection, metadata, errors = ent.create_children(md_list)
    trans_id = nuage_connection.user.bulk_delete(md_list, callback=bulk_async_cb, **async_arg)
    result, connection, metadata, errors = wait_for_transaction(trans_id)
    ent.delete(callback=two_args_cb, **async_arg)
    assert metadata['total'] == 1
    assert metadata['success'] == 1
    assert metadata['failure'] == 0
    assert len(result) == 1
    assert connection.response.status_code < 400
    assert not errors

def test_async_bulk_object_delete(nuage_connection, async_arg):
    # Object delete
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    nuage_connection.user.create_child(ent)
    md_list = build_md_list(count=175)
    result, connection, metadata, errors = ent.create_children(md_list)
    trans_id = nuage_connection.user.bulk_delete(md_list, callback=bulk_async_cb, **async_arg)
    result, connection, metadata, errors = wait_for_transaction(trans_id)
    ent.delete(callback=two_args_cb, **async_arg)
    assert metadata['total'] == 175
    assert metadata['success'] == 175
    assert metadata['failure'] == 0
    assert len(result) == 175
    assert connection.response.status_code < 400
    assert not errors

def test_negative_bulk_object_create_children_without_list(nuage_connection, async_arg):
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    nuage_connection.user.create_child(ent)
    md_list = build_md_list(count=1)
    with pytest.raises(TypeError):
        assert ent.create_children(md_list[0])
    ent.delete(callback=two_args_cb, **async_arg)

def test_negative_bulk_object_create_children_illegal_child(nuage_connection, async_arg):
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    nuage_connection.user.create_child(ent)
    md_list = build_md_list(count=1)
    md_list.append(vsdk.NUMetadata())
    result, connection, metadata, errors = ent.create_children(md_list)
    ent.delete(callback=two_args_cb, **async_arg)
    assert metadata['total'] == 2
    assert metadata['success'] == 1
    assert metadata['failure'] == 1
    assert len(result) == 2
    assert connection.response.status_code < 400
    assert len(errors) == 1
    assert not result[1].id
    assert errors[0]['status'] >= 400

def test_negative_bulk_object_create_children_duplicate_child(nuage_connection, async_arg):
    name = random.randint(100000,999999)
    ent_list = [
            vsdk.NUEnterprise(name=name),
            vsdk.NUEnterprise(name=name)
        ]
    result, connection, metadata, errors = nuage_connection.user.create_children(ent_list)
    for ent in ent_list:
        if ent.id:
            ent.delete(callback=two_args_cb, **async_arg)
    assert metadata['total'] == 2
    assert metadata['success'] == 1
    assert metadata['failure'] == 1
    assert len(result) == 2
    assert connection.response.status_code < 400
    assert len(errors) == 1
    assert not result[0].id or not result[1].id
    assert errors[0]['status'] >= 400

def test_negative_bulk_object_save_without_list(nuage_connection, async_arg):
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    nuage_connection.user.create_child(ent)
    md_list = build_md_list(count=2)
    ent.create_children(md_list)
    md_list[1].blob = None
    with pytest.raises(TypeError):
        assert nuage_connection.user.bulk_save(md_list[1])
    ent.delete(callback=two_args_cb, **async_arg)

def test_negative_bulk_object_save_illegal_object(nuage_connection, async_arg):
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    nuage_connection.user.create_child(ent)
    md_list = build_md_list(count=2)
    ent.create_children(md_list)
    md_list[1].blob = None
    result, connection, metadata, errors = nuage_connection.user.bulk_save(md_list)
    ent.delete(callback=two_args_cb, **async_arg)
    assert metadata['total'] == 2
    assert metadata['success'] == 1
    assert metadata['failure'] == 1
    assert len(result) == 2
    assert connection.response.status_code < 400
    assert len(errors) == 1
    assert errors[0]['status'] >= 400

def test_negative_bulk_object_save_duplicate_object(nuage_connection, async_arg):
    ent_list = [
            vsdk.NUEnterprise(name=random.randint(100000,999999)),
            vsdk.NUEnterprise(name=random.randint(100000,999999))
        ]
    nuage_connection.user.create_children(ent_list)
    ent_list[1].name = ent_list[0].name = random.randint(100000,999999)
    result, connection, metadata, errors = nuage_connection.user.bulk_save(ent_list)
    nuage_connection.user.bulk_delete(ent_list, callback=bulk_async_cb, **async_arg)
    assert metadata['total'] == 2
    assert metadata['success'] == 1
    assert metadata['failure'] == 1
    assert len(result) == 2
    assert connection.response.status_code < 400
    assert len(errors) == 1
    assert errors[0]['status'] >= 400

def test_negative_bulk_object_delete_without_list(nuage_connection, async_arg):
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    nuage_connection.user.create_child(ent)
    md_list = build_md_list(count=2)
    ent.create_children(md_list)
    md_list[1].blob = None
    with pytest.raises(TypeError):
        assert nuage_connection.user.bulk_delete(md_list[1])
    ent.delete(callback=two_args_cb, **async_arg)

def test_negative_bulk_object_delete_illegal_object(nuage_connection, async_arg):
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    nuage_connection.user.create_child(ent)
    md_list = build_md_list(count=2)
    ent.create_children(md_list)
    md_list[1].id = 'non-existing-id'
    result, connection, metadata, errors = nuage_connection.user.bulk_delete(md_list)
    ent.delete(callback=two_args_cb, **async_arg)
    assert metadata['total'] == 2
    assert metadata['success'] == 1
    assert metadata['failure'] == 1
    assert len(result) == 2
    assert connection.response.status_code < 400
    assert len(errors) == 1
    assert errors[0]['status'] >= 400

def test_negative_bulk_object_delete_duplicate_object(nuage_connection, async_arg):
    name = random.randint(100000,999999)
    ent = vsdk.NUEnterprise(name=name)
    nuage_connection.user.create_child(ent)
    md_list = build_md_list(count=1)
    ent.create_children(md_list)
    result, connection, metadata, errors = nuage_connection.user.bulk_delete([md_list[0], md_list[0]])
    ent.delete(callback=two_args_cb, **async_arg)
    assert metadata['total'] == 2
    assert metadata['success'] == 1
    assert metadata['failure'] == 1
    assert len(result) == 2
    assert connection.response.status_code < 400
    assert len(errors) == 1
    assert errors[0]['status'] >= 400

