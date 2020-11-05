import pytest
import random
import time

from vspk import v6 as vsdk
from bambou.exceptions import BambouHTTPError
from urllib.parse import urlparse

def reset_login(nuage_connection, username, password, enterprise):
    url = urlparse(nuage_connection.login_controller.url)
    nuage_connection.reset()
    nuage_connection = vsdk.NUVSDSession(
        username=username,
        password=password,
        enterprise=enterprise,
        api_url='https://{0:s}'.format(url.netloc)
    )
    nuage_connection.start()
    return nuage_connection

def prepare_setup(nuage_connection):
    # Enable Granular permissions
    nuage_connection = reset_login(nuage_connection, 'csproot', 'csproot', 'csp')
    sys_config = nuage_connection.user.system_configs.get_first()
    sys_config.rbac_enabled = True
    sys_config.save()
    
    # Creating test enterprise
    name_int = random.randint(100000,999999)
    rbac_enterprise = vsdk.NUEnterprise(name='RBAC test {0}'.format(name_int))
    nuage_connection.user.create_child(rbac_enterprise)
    
    # Creating administrator in enterprise
    user = vsdk.NUUser(email='rbac-admin@localhost', first_name='RBAC', last_name='Admin', password='rbac-admin', user_name='rbac-admin')
    rbac_enterprise.create_child(user)
    admin_group = rbac_enterprise.groups.get_first(filter='name == "Administrators"')
    admin_group.assign([user], vsdk.NUUser)
    
    nuage_connection = reset_login(nuage_connection, 'rbac-admin', 'rbac-admin', rbac_enterprise.name)

    # Creating users for different users
    alice_user = vsdk.NUUser(email='alice@localhost', first_name='Alice', last_name='Doe', password='alice', user_name='alice')
    bob_user = vsdk.NUUser(email='bob@localhost', first_name='Bob', last_name='Doe', password='bob', user_name='bob')
    carol_user = vsdk.NUUser(email='carol@localhost', first_name='Carol', last_name='Doe', password='carol', user_name='carol')
    dan_user = vsdk.NUUser(email='dan@localhost', first_name='Dan', last_name='Doe', password='dan', user_name='dan')
    erin_user = vsdk.NUUser(email='erin@localhost', first_name='Erin', last_name='Doe', password='erin', user_name='erin')
    frank_user = vsdk.NUUser(email='frank@localhost', first_name='Frank', last_name='Doe', password='frank', user_name='frank')
    ted_user = vsdk.NUUser(email='ted@localhost', first_name='Ted', last_name='Doe', password='ted', user_name='ted')
    rbac_enterprise.create_children([alice_user, bob_user, carol_user, dan_user, erin_user, frank_user, ted_user])
    
    # Creating group for different functions
    na_network_admins = vsdk.NUGroup(name='NA network admins')
    na_security_admins = vsdk.NUGroup(name='NA security admins')
    sa_network_admins = vsdk.NUGroup(name='SA network admins')
    sa_security_admins = vsdk.NUGroup(name='SA security admins')
    rbac_enterprise.create_children([na_network_admins, na_security_admins, sa_network_admins, sa_security_admins])
    
    # Assigning membership
    na_network_admins.assign([alice_user, carol_user, ted_user], vsdk.NUUser)
    na_security_admins.assign([bob_user, carol_user, ted_user], vsdk.NUUser)
    sa_network_admins.assign([dan_user, frank_user, ted_user], vsdk.NUUser)
    sa_security_admins.assign([erin_user, frank_user, ted_user], vsdk.NUUser)
    
    # Creating Domain network admins role
    domain_network_role = vsdk.NURole(name='Domain network admins')
    rbac_enterprise.create_child(domain_network_role)
    # Adding role entries, identifying the permissions this role has
    # Allows read of domain and read of all children of domain
    domain_network_role.create_child(vsdk.NURoleentry(end_point_type='DOMAIN', role_access_type_list=['READ', 'READ_CHILDREN']))
    # Allows CRUD of subnets & zones
    domain_network_role.create_child(vsdk.NURoleentry(end_point_type='ZONE', role_access_type_list=['CREATE', 'READ', 'MODIFY', 'DELETE']))
    domain_network_role.create_child(vsdk.NURoleentry(end_point_type='SUBNET', role_access_type_list=['CREATE', 'READ', 'MODIFY', 'DELETE']))
    
    # Creating Domain security admins role
    domain_security_role = vsdk.NURole(name='Domain security admins')
    rbac_enterprise.create_child(domain_security_role)
    # Adding role entries, identifying the permissions this role has
    # Allows read of domain and read of all children of domain
    domain_security_role.create_child(vsdk.NURoleentry(end_point_type='DOMAIN', role_access_type_list=['READ', 'READ_CHILDREN']))
    # Allows CRUD of ingress ACL, egress ACL & policy groupss
    domain_security_role.create_child(vsdk.NURoleentry(end_point_type='INGRESS_ACL_TEMPLATE', role_access_type_list=['CREATE', 'READ', 'MODIFY', 'DELETE', 'CUD_CHILDREN', 'READ_CHILDREN']))
    domain_security_role.create_child(vsdk.NURoleentry(end_point_type='EGRESS_ACL_TEMPLATE', role_access_type_list=['CREATE', 'READ', 'MODIFY', 'DELETE', 'CUD_CHILDREN', 'READ_CHILDREN']))
    domain_security_role.create_child(vsdk.NURoleentry(end_point_type='POLICY_GROUP', role_access_type_list=['CREATE', 'READ', 'MODIFY', 'DELETE']))
    
    # Creating base domain template and some domains
    base_domain_template = vsdk.NUDomainTemplate(name='Base domain template')
    rbac_enterprise.create_child(base_domain_template)
    na_domain_a = vsdk.NUDomain(name='NA Domain A', template_id=base_domain_template.id)
    na_domain_b = vsdk.NUDomain(name='NA Domain B', template_id=base_domain_template.id)
    sa_domain_a = vsdk.NUDomain(name='SA Domain A', template_id=base_domain_template.id)
    sa_domain_b = vsdk.NUDomain(name='SA Domain B', template_id=base_domain_template.id)
    rbac_enterprise.create_children([na_domain_a, na_domain_b, sa_domain_a, sa_domain_b])
    
    # Creating permissions on specific domains, permission = Group + Role. It identifies that the group has the permissions of that role on the specific entity
    na_domain_a.create_child(vsdk.NUPermission(permitted_action=None, associated_group_id=na_network_admins.id, associated_role_id=domain_network_role.id))
    na_domain_a.create_child(vsdk.NUPermission(permitted_action=None, associated_group_id=na_security_admins.id, associated_role_id=domain_security_role.id))
    na_domain_b.create_child(vsdk.NUPermission(permitted_action=None, associated_group_id=na_network_admins.id, associated_role_id=domain_network_role.id))
    na_domain_b.create_child(vsdk.NUPermission(permitted_action=None, associated_group_id=na_security_admins.id, associated_role_id=domain_security_role.id))
    sa_domain_a.create_child(vsdk.NUPermission(permitted_action=None, associated_group_id=sa_network_admins.id, associated_role_id=domain_network_role.id))
    sa_domain_a.create_child(vsdk.NUPermission(permitted_action=None, associated_group_id=sa_security_admins.id, associated_role_id=domain_security_role.id))
    sa_domain_b.create_child(vsdk.NUPermission(permitted_action=None, associated_group_id=sa_network_admins.id, associated_role_id=domain_network_role.id))
    sa_domain_b.create_child(vsdk.NUPermission(permitted_action=None, associated_group_id=sa_security_admins.id, associated_role_id=domain_security_role.id))

    return rbac_enterprise

def clear_setup(nuage_connection, enterprise):
    try:
        for domain in enterprise.domains.get():
            domain.delete()
        enterprise.delete()
    except:
        pass

def test_alice_positive_permissions(nuage_connection):
    nuage_connection = reset_login(nuage_connection, 'csproot', 'csproot', 'csp')
    enterprise = prepare_setup(nuage_connection)
    # Login as Alice
    nuage_connection = reset_login(nuage_connection, 'alice', 'alice', enterprise.name)
    # Getting only domains Alice has access to
    domains = enterprise.domains.get()
    assert len(domains) == 2
    domain_a = domains[0]
    # Trying to create zone
    zone = vsdk.NUZone(name='Alice Zone')
    domain_a.create_child(zone)
    assert zone.id
    # Trying to get a zone
    change_zone = vsdk.NUZone(id=zone.id)
    change_zone.fetch()
    assert change_zone.name == zone.name
    # Trying to update a zone
    change_zone.name = 'Zone of Alice'
    change_zone.save()
    change_zone.fetch()
    assert change_zone.last_updated_date != zone.last_updated_date
    # Trying to delete a zone
    zone.delete()
    with pytest.raises(BambouHTTPError):
        assert change_zone.fetch()
    # Trying to create a Subnet
    zone = vsdk.NUZone(name='Zone of Alice')
    domain_a.create_child(zone)
    subnet = vsdk.NUSubnet(name='Alice Subnet', address='10.10.10.0', netmask='255.255.255.0')
    zone.create_child(subnet)
    assert subnet.id
    # Trying to get a subnet
    change_subnet = vsdk.NUSubnet(id=subnet.id)
    change_subnet.fetch()
    assert change_subnet.name == subnet.name
    # Trying to update a subnet
    change_subnet.name = 'Subnet of Alice'
    change_subnet.save()
    change_subnet.fetch()
    assert change_subnet.last_updated_date != subnet.last_updated_date
    # Trying to delete a subnet
    subnet.delete()
    with pytest.raises(BambouHTTPError):
        assert change_subnet.fetch()
    # Cleaning up setup
    nuage_connection = reset_login(nuage_connection, 'csproot', 'csproot', 'csp')
    clear_setup(nuage_connection, enterprise)

def test_alice_negative_permissions(nuage_connection):
    nuage_connection = reset_login(nuage_connection, 'csproot', 'csproot', 'csp')
    enterprise = prepare_setup(nuage_connection)
    bad_domain = enterprise.domains.get_first(filter='name == "SA Domain A"')
    # Login as Alice
    nuage_connection = reset_login(nuage_connection, 'alice', 'alice', enterprise.name)
    check_domain = vsdk.NUDomain(id=bad_domain.id)
    with pytest.raises(BambouHTTPError):
        assert check_domain.fetch()
    domain = enterprise.domains.get_first(filter='name == "NA Domain A"')
    with pytest.raises(BambouHTTPError):
        assert domain.create_child(vsdk.NUPolicyGroup(name='Alice PG'))
    # Cleaning up setup
    nuage_connection = reset_login(nuage_connection, 'csproot', 'csproot', 'csp')
    clear_setup(nuage_connection, enterprise)

