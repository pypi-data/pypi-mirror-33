from __future__ import absolute_import

import string
import random
import unittest


from .OAuthUtils import OAuthUtils

from factern_client import FactsApi
from factern_client import ApiClient
from factern_client import Configuration
from factern_client import ApiEndpoint
from factern_client import FilterStatement
from factern_client import PermissionAction
from factern_client import PermissionEffect
from factern_client import PermissionPolicyDocument
from factern_client import PriceDetails
from factern_client import AddLabelRequest
from factern_client import AddStatementRequest
from factern_client import CreateAliasRequest
from factern_client import CreateBidRequest
from factern_client import CreateMirrorRequest
from factern_client import CreatePermissionRequest
from factern_client import CreatePriceRequest
from factern_client import CreateWatchRequest
from factern_client import DeleteRequest
from factern_client import DescribeRequest
from factern_client import NodeIdRequest
from factern_client import ReadRequest
from factern_client import ReplaceFieldRequest
from factern_client import SearchAliasRequest
from factern_client import SearchEntityRequest
from factern_client import UpdateApplicationRequest
from factern_client import WriteRequest
from factern_client import CreateInformationRequest
from factern_client import CreateMemberRequest
from factern_client import UpdateStatusRequest
from factern_client import CreateApplicationRequest
from factern_client import CreateDomainRequest
from factern_client import CreateFieldRequest
from factern_client import CreateFilterRequest
from factern_client import CreateGroupRequest
from factern_client import CreateEntityRequest
from factern_client import CreateInterfaceRequest
from factern_client import CreateLabelListRequest
from factern_client import CreateScopeRequest
from factern_client import CreateTemplateRequest


def random_str(length=20):
    return ''.join(random.choice(string.ascii_uppercase + string.digits)
                   for _ in range(length))


class FactsApiTest(unittest.TestCase):

    def setUp(self):
        oauth = OAuthUtils()
        access_token = oauth.get_auth_token()

        config = Configuration()
        config.access_token = access_token
        config.debug = True

        client = ApiClient(config)

        client.set_default_header('Content-Type', 'application/json')
        client.set_default_header('Accept', 'application/json')
        client.set_default_header('Authorization', access_token)

        self.facts_api = FactsApi(client)
        self.loginId = "00000000ADD8EE62EAC53F925FD09407AB2AD1DF6E55BFF4"

    def create_entity(self):
        create_entity_request = CreateEntityRequest()

        return self.facts_api.create_entity(
            body=create_entity_request,
            login=self.loginId
        )

    def create_field(self, name=None, unique_by_parent=False, branch=False):
        if name is None:
            name = random_str()

        create_field_request = CreateFieldRequest(
            name=name,
            unique_by_parent=unique_by_parent,
            searchable=True,
            branch=branch
        )

        return self.facts_api.create_field(
            body=create_field_request,
            login=self.loginId
        )

    def test_add_member(self):
        entity_id1 = self.create_entity().node_id
        entity_id2 = self.create_entity().node_id

        create_group_request = CreateGroupRequest(
            member_ids=[entity_id1, entity_id2],
            member_fact_type="Entity",
            name=random_str()
        )

        group_id = self.facts_api.create_group(
            body=create_group_request,
            login=self.loginId
        ).node_id

        entity_id3 = self.create_entity().node_id
        create_member_request = CreateMemberRequest(
            parent_id=group_id,
            member_id=entity_id3
        )

        self.assertIsNotNone(self.facts_api.add_member(
            body=create_member_request,
            login=self.loginId
        ))

    def test_bid(self):
        entity_id = self.create_entity().node_id

        create_price_request = CreatePriceRequest(
            target_node_id=entity_id,
            type="Fixed",
            price_details=PriceDetails(value=100),
            policy=PermissionPolicyDocument(actions=[PermissionAction.READ])
        )

        create_price_response = self.facts_api.create_price(
            body=create_price_request,
            login=self.loginId
        )

        create_bid_request = CreateBidRequest(
            price_id=create_price_response.node_id
        )

        self.assertIsNotNone(self.facts_api.bid(
            body=create_bid_request,
            login=self.loginId
        ))

    def test_create_alias(self):
        entity_id = self.create_entity().node_id

        alias_request = CreateAliasRequest(
            local=False,
            name=random_str(),
            target_node_id=entity_id
        )

        self.assertIsNotNone(self.facts_api.create_alias(
            body=alias_request,
            login=self.loginId
        ))

    def test_create_application(self):
        create_application_request = CreateApplicationRequest(
            name=random_str(),
            redirect_uris=[]
        )

        self.assertIsNotNone(self.facts_api.create_application(
            body=create_application_request,
            login=self.loginId
        ))

    def test_create_domain(self):
        create_domain_request = CreateDomainRequest(
            add_fact=ApiEndpoint(url="https://example.com/add"),
            get_fact=ApiEndpoint(url="https://example.com/get"),
            query_facts=ApiEndpoint(url="https://example.com/query"),
            name=random_str()
        )

        self.assertIsNotNone(self.facts_api.create_domain(
            body=create_domain_request,
            login=self.loginId
        ))

    def test_create_entity(self):
        self.assertIsNotNone(self.create_entity())

    def test_create_field(self):
        self.assertIsNotNone(self.create_field())

    def test_create_filter(self):
        entity_id = self.create_entity().node_id

        create_filter_request = CreateFilterRequest(
            name=random_str(),
            statements=[
                FilterStatement(field="ActionQualifier",
                                arguments=[entity_id])
            ]
        )

        self.assertIsNotNone(self.facts_api.create_filter(
            body=create_filter_request,
            login=self.loginId
        ))

    def test_create_group(self):
        entity_id1 = self.create_entity().node_id
        entity_id2 = self.create_entity().node_id

        create_group_request = CreateGroupRequest(
            member_ids=[entity_id1, entity_id2],
            member_fact_type="Entity",
            name=random_str()
        )

        self.assertIsNotNone(self.facts_api.create_group(
            body=create_group_request,
            login=self.loginId
        ))

    def test_create_information(self):
        entity_id = self.create_entity().node_id
        field_id = self.create_field().node_id
        data = "data" + random_str()

        create_information_request = CreateInformationRequest(
            parent_id=entity_id,
            field_id=field_id,
            data=data
        )

        self.assertIsNotNone(self.facts_api.create_information(
            body=create_information_request,
            login=self.loginId
        ))

    def test_create_interface(self):
        create_interface_request = CreateInterfaceRequest(
            add_data=ApiEndpoint(url="https://example.com/add"),
            get_data=ApiEndpoint(url="https://example.com/get"),
            delete_data=ApiEndpoint(url="https://example.com/delete"),
            name=random_str()
        )

        self.assertIsNotNone(self.facts_api.create_interface(
            body=create_interface_request,
            login=self.loginId
        ))

    def test_create_label_list(self):
        create_label_list_request = CreateLabelListRequest(
            name=random_str(),
            members=["abc", "def"]
        )

        self.assertIsNotNone(self.facts_api.create_label_list(
            body=create_label_list_request,
            login=self.loginId
        ))

    def test_create_mirror(self):
        source_entity_id = self.create_entity().node_id
        target_entity_id = self.create_entity().node_id
        field_id = self.create_field(unique_by_parent=True).node_id
        data = "data" + random_str()

        create_information_request = CreateInformationRequest(
            parent_id=source_entity_id,
            field_id=field_id,
            data=data
        )

        create_template_request = CreateTemplateRequest(
            name=random_str(),
            member_ids=[field_id]
        )

        template_id = self.facts_api.create_template(
            body=create_template_request,
            login=self.loginId
        ).node_id

        self.facts_api.create_information(
            body=create_information_request,
            login=self.loginId
        )

        create_mirror_request = CreateMirrorRequest(
            source_node_id=source_entity_id,
            destination_node_id=target_entity_id,
            template_id=template_id
        )

        self.assertIsNotNone(self.facts_api.create_mirror(
            body=create_mirror_request,
            login=self.loginId
        ))

    def test_create_price(self):
        entity_id = self.create_entity().node_id

        create_price_request = CreatePriceRequest(
            target_node_id=entity_id,
            type="Fixed",
            price_details=PriceDetails(value=100),
            policy=PermissionPolicyDocument(actions=[PermissionAction.READ])
        )

        self.assertIsNotNone(self.facts_api.create_price(
            body=create_price_request,
            login=self.loginId
        ))

    def test_create_scope(self):
        field_id1 = self.create_field().node_id
        field_id2 = self.create_field().node_id

        create_template_request = CreateTemplateRequest(
            name=random_str(),
            member_ids=[field_id1, field_id2]
        )

        template_id = self.facts_api.create_template(
            body=create_template_request,
            login=self.loginId
        ).node_id

        create_scope_request = CreateScopeRequest(
            name=random_str(),
            template_ids=[template_id],
            filter_ids=[]
        )

        self.assertIsNotNone(self.facts_api.create_scope(
            body=create_scope_request,
            login=self.loginId
        ))

    def test_create_statement(self):
        create_application_request = CreateApplicationRequest(
            name="app" + random_str(),
            redirect_uris=[]
        )

        app_id = self.facts_api.create_application(
            body=create_application_request,
            login=self.loginId
        ).node_id

        field_id1 = self.create_field().node_id
        field_id2 = self.create_field().node_id

        create_template_request = CreateTemplateRequest(
            name="template" + random_str(),
            member_ids=[field_id1, field_id2]
        )

        template_id = self.facts_api.create_template(
            body=create_template_request,
            login=self.loginId
        ).node_id

        create_scope_request = CreateScopeRequest(
            name="scope" + random_str(),
            template_ids=[template_id],
            filter_ids=[]
        )

        scope_id = self.facts_api.create_scope(
            body=create_scope_request,
            login=self.loginId
        ).node_id

        add_statement_request = AddStatementRequest(
            target_node_id=app_id,
            action_id="frn:predicate:factern:requiresScope",
            action_qualifier_id=scope_id
        )

        self.assertIsNotNone(self.facts_api.create_statement(
            body=add_statement_request,
            login=self.loginId
        ))

    def test_create_template(self):
        field_id1 = self.create_field().node_id
        field_id2 = self.create_field().node_id

        create_template_request = CreateTemplateRequest(
            name=random_str(),
            member_ids=[field_id1, field_id2]
        )

        self.assertIsNotNone(self.facts_api.create_template(
            body=create_template_request,
            login=self.loginId
        ))

    def test_delete_node(self):
        entity_id = self.create_entity().node_id

        self.assertIsNotNone(self.facts_api.delete_node(
            body=NodeIdRequest(node_id=entity_id),
            login=self.loginId
        ))

    def test_delete(self):
        entity_id = self.create_entity().node_id
        field_id = self.create_field().node_id
        data = "data" + random_str()

        create_information_request = CreateInformationRequest(
            parent_id=entity_id,
            field_id=field_id,
            data=data
        )

        self.facts_api.create_information(
            body=create_information_request,
            login=self.loginId
        )

        self.assertIsNotNone(self.facts_api.delete_node(
            body=DeleteRequest(node_id=entity_id, template_id=[field_id]),
            login=self.loginId
        ))

    def test_describe(self):
        entity_id = self.create_entity().node_id

        response = self.facts_api.describe(
            body=DescribeRequest(node_id=entity_id),
            login=self.loginId
        )

        children = response.children
        self.assertIsNotNone(children)

        list_nodes = children.nodes
        self.assertIsNotNone(list_nodes)
        self.assertEqual(0, len(list_nodes))

        node = response.node
        self.assertIsNotNone(node)
        self.assertTrue(node.fact_type, "Entity")

    def test_history(self):
        entity_id = self.create_entity().node_id
        self.assertIsNotNone(self.facts_api.history(
            body=NodeIdRequest(node_id=entity_id),
            login=self.loginId
        ))

    def test_label(self):
        create_label_list_request = CreateLabelListRequest(
            name=random_str(),
            members=["abc", "def"]
        )

        label_node = self.facts_api.create_label_list(
            body=create_label_list_request,
            login=self.loginId
        ).members[0]

        entity_id = self.create_entity().node_id

        add_label_request = AddLabelRequest(
            target_node_id=entity_id,
            label_id=label_node.node_id
        )

        self.assertIsNotNone(self.facts_api.label(
            body=add_label_request,
            login=self.loginId
        ))

    def test_obliterate(self):
        entity_id = self.create_entity().node_id
        field_id = self.create_field().node_id
        data = "data" + random_str()

        create_information_request = CreateInformationRequest(
            parent_id=entity_id,
            field_id=field_id,
            data=data
        )

        create_information_response = self.facts_api.create_information(
            body=create_information_request,
            login=self.loginId
        )

        self.assertIsNotNone(self.facts_api.obliterate(
            body=NodeIdRequest(node_id=create_information_response.node_id),
            login=self.loginId
        ))

    def test_permission(self):
        entity_id = self.create_entity().node_id

        create_permission_request = CreatePermissionRequest(
            target_node_id=entity_id,
            policy=PermissionPolicyDocument(
                actions=[PermissionAction.READ],
                effect=PermissionEffect.ALLOW
            )
        )

        self.assertIsNotNone(self.facts_api.permission(
            body=create_permission_request,
            login=self.loginId
        ))

    def test_read(self):
        entity_id = self.create_entity().node_id
        field_id = self.create_field().node_id
        data = "data" + random_str()

        create_information_request = CreateInformationRequest(
            parent_id=entity_id,
            field_id=field_id, data=data
        )

        self.facts_api.create_information(
            body=create_information_request,
            login=self.loginId
        )

        self.assertIsNotNone(self.facts_api.read(
            body=ReadRequest(node_id=entity_id,
                             template=[field_id]),
            login=self.loginId
        ))

    def test_replace_information(self):
        entity_id = self.create_entity().node_id
        field_id = self.create_field().node_id
        data = "data" + random_str()

        create_information_request = CreateInformationRequest(
            parent_id=entity_id,
            field_id=field_id,
            data=data
        )

        create_information_response = self.facts_api.create_information(
            body=create_information_request,
            login=self.loginId
        )

        replace_field_request = ReplaceFieldRequest(
            node_id=create_information_response.node_id,
            data="data" + random_str()
        )

        self.assertIsNotNone(self.facts_api.replace_information(
            body=replace_field_request,
            login=self.loginId
        ))

    def test_update_application(self):
        create_application_request = CreateApplicationRequest(
            name=random_str(),
            redirect_uris=[]
        )

        app_id = self.facts_api.create_application(
            body=create_application_request,
            login=self.loginId
        ).node_id

        update_application_request = UpdateApplicationRequest(
            node_id=app_id
        )

        self.assertIsNotNone(self.facts_api.update_application(
            body=update_application_request,
            login=self.loginId
        ))

    def test_search_alias(self):
        entity_id = self.create_entity().node_id
        self.assertIsNotNone(self.facts_api.create_alias(
            body=CreateAliasRequest(local=False,
                                    name=random_str(),
                                    target_node_id=entity_id),
            login=self.loginId
        ))

        self.assertIsNotNone(self.facts_api.search_alias(
            body=SearchAliasRequest(name=random_str()),
            login=self.loginId
        ))

    def test_search_entity(self):
        entity_id = self.create_entity().node_id
        field_id = self.create_field().node_id
        data = "data" + random_str()

        create_information_request = CreateInformationRequest(
            parent_id=entity_id,
            field_id=field_id, data=data
        )

        self.assertIsNotNone(self.facts_api.create_information(
            body=create_information_request,
            login=self.loginId
        ))

        self.assertIsNotNone(self.facts_api.search_entity(
            body=SearchEntityRequest(operator="equals",
                                     term=data,
                                     field_id=field_id),
            login=self.loginId
        ))

        query = {"bool": {"must": {"match_phrase": {"fields.value": data}}}}
        self.assertIsNotNone(self.facts_api.search_entity(
            body=SearchEntityRequest(operator="elasticsearch",
                                     query=query),
            login=self.loginId
        ))

    def test_update_status(self):
        source_entity_id = self.create_entity().node_id
        target_entity_id = self.create_entity().node_id
        field_id = self.create_field(unique_by_parent=True).node_id
        data = "data" + random_str()

        create_information_request = CreateInformationRequest(
            parent_id=source_entity_id,
            field_id=field_id,
            data=data
        )

        create_template_request = CreateTemplateRequest(
            name=random_str(),
            member_ids=[field_id]
        )

        template_id = self.facts_api.create_template(
            body=create_template_request,
            login=self.loginId
        ).node_id

        self.facts_api.create_information(
            body=create_information_request,
            login=self.loginId
        )

        create_mirror_request = CreateMirrorRequest(
            source_node_id=source_entity_id,
            destination_node_id=target_entity_id,
            template_id=template_id
        )

        mirror_id = self.facts_api.create_mirror(
            body=create_mirror_request,
            login=self.loginId
        ).node_id

        update_status_request = UpdateStatusRequest(
            status="disabled",
            node_id=mirror_id
        )

        self.assertIsNotNone(self.facts_api.update_status(
            body=update_status_request,
            login=self.loginId
        ))

    def test_watch(self):
        entity_id = self.create_entity().node_id

        create_watch_request = CreateWatchRequest(
            target_node_id=entity_id
        )

        self.assertIsNotNone(self.facts_api.watch(
            body=create_watch_request,
            login=self.loginId
        ))

    def test_write(self):
        entity_id = self.create_entity().node_id
        field_id = self.create_field().node_id
        data = "data" + random_str()

        write_request = WriteRequest(
            node_id=entity_id,
            template=[field_id],
            values=[data]
        )

        self.assertIsNotNone(self.facts_api.write(
            body=write_request,
            login=self.loginId
        ))


if __name__ == '__main__':
    unittest.main()
