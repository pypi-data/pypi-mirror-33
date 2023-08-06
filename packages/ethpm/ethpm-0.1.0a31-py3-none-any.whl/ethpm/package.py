import json
from typing import Any, Dict

from eth_utils import to_text
from web3 import Web3
from web3.eth import Contract

from ethpm.backends import get_uri_backend
from ethpm.deployments import Deployments
from ethpm.exceptions import InsufficientAssetsError
from ethpm.typing import ContractName
from ethpm.utils.contract import (
    generate_contract_factory_kwargs,
    validate_contract_name,
    validate_minimal_contract_factory_data,
    validate_w3_instance,
)
from ethpm.utils.deployment_validation import validate_single_matching_uri
from ethpm.utils.filesystem import load_package_data_from_file
from ethpm.utils.manifest_validation import (
    check_for_build_dependencies,
    validate_deployments_are_present,
    validate_manifest_against_schema,
    validate_manifest_deployments,
)
from ethpm.utils.registry import lookup_manifest_uri_located_at_registry_uri
from ethpm.utils.uri import get_manifest_from_content_addressed_uri
from ethpm.validation import validate_registry_uri


class Package(object):
    def __init__(self, manifest: Dict[str, Any], w3: Web3 = None) -> None:
        """
        A package must be constructed with a valid manifest.
        """
        self.w3 = w3

        if not isinstance(manifest, dict):
            raise TypeError(
                "Package object must be initialized with a dictionary. "
                "Got {0}".format(type(manifest))
            )

        validate_manifest_against_schema(manifest)
        validate_manifest_deployments(manifest)
        check_for_build_dependencies(manifest)

        self.package_data = manifest

    def set_default_w3(self, w3: Web3) -> None:
        """
        Set the default Web3 instance.
        """
        self.w3 = w3

    def get_contract_factory(self, name: ContractName, w3: Web3 = None) -> Contract:
        """
        API to generate a contract factory class.
        """
        current_w3 = None

        if w3 is not None:
            current_w3 = w3
        else:
            current_w3 = self.w3

        validate_contract_name(name)
        validate_w3_instance(current_w3)

        try:
            contract_data = self.package_data["contract_types"][name]
            validate_minimal_contract_factory_data(contract_data)
        except KeyError:
            raise InsufficientAssetsError(
                "This package has insufficient package data to generate "
                "a contract factory for contract:{0}.".format(name)
            )

        contract_kwargs = generate_contract_factory_kwargs(contract_data)
        contract_factory = current_w3.eth.contract(**contract_kwargs)
        return contract_factory

    def __repr__(self) -> str:
        name = self.name
        version = self.version
        return "<Package {0}=={1}>".format(name, version)

    @classmethod
    def from_file(cls, file_path_or_obj: str, w3: Web3) -> "Package":
        """
        Allows users to create a Package object
        from a filepath
        """
        if isinstance(file_path_or_obj, str):
            with open(file_path_or_obj) as file_obj:
                package_data = load_package_data_from_file(file_obj)
        elif hasattr(file_path_or_obj, "read") and callable(file_path_or_obj.read):
            package_data = load_package_data_from_file(file_path_or_obj)
        else:
            raise TypeError(
                "The Package.from_file method takes either a filesystem path or a file-like object."
                "Got {0} instead.".format(type(file_path_or_obj))
            )

        return cls(package_data, w3)

    @classmethod
    def from_ipfs(cls, ipfs_uri: str) -> "Package":
        """
        Instantiate and return a Package object from an IPFS URI pointing to a manifest.
        """
        uri_backend = get_uri_backend()
        if uri_backend.can_handle_uri(ipfs_uri):
            raw_package_data = uri_backend.fetch_uri_contents(ipfs_uri)
            package_data = json.loads(to_text(raw_package_data))
        else:
            raise TypeError(
                "The URI Backend: {0} cannot handle the given URI: {1}.".format(
                    type(uri_backend).__name__, ipfs_uri
                )
            )

        return cls(package_data)

    @classmethod
    def from_registry(cls, registry_uri: str, w3: Web3) -> "Package":
        """
        Instantiate a Package object from a valid Registry URI.
        --
        Requires a web3 object connected to the chain the registry lives on.
        """
        validate_registry_uri(registry_uri)
        manifest_uri = lookup_manifest_uri_located_at_registry_uri(registry_uri, w3)
        manifest_data = get_manifest_from_content_addressed_uri(manifest_uri)
        return cls(manifest_data, w3)

    @property
    def name(self) -> str:
        return self.package_data["package_name"]

    @property
    def version(self) -> str:
        return self.package_data["version"]

    #
    # Deployments
    #

    def get_deployments(self, w3: Web3 = None) -> "Deployments":
        """
        API to retrieve instance of deployed contract dependency.
        """
        if w3 is None:
            w3 = self.w3

        validate_w3_instance(w3)
        validate_deployments_are_present(self.package_data)

        all_blockchain_uris = self.package_data["deployments"].keys()
        matching_uri = validate_single_matching_uri(all_blockchain_uris, w3)

        deployments = self.package_data["deployments"][matching_uri]
        all_contract_factories = {
            deployment_data["contract_type"]: self.get_contract_factory(
                deployment_data["contract_type"], w3
            )
            for deployment_data in deployments.values()
        }

        return Deployments(deployments, all_contract_factories, w3)
