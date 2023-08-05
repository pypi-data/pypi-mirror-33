import re

import validators
from base import ARMObject, ARMProperty, SubResource
from network import BackendAddressPoolRef, ProbeRef


class Plan(ARMProperty):
    props = {
        'name': (str, False),
        'publisher': (str, False),
        'product': (str, False),
        'promotionCode': (str, False)
    }


class HardwareProfile(ARMProperty):
    props = {
        'vmSize': (str, False)
    }
    # todo add validations


class ImageReference(ARMProperty):
    def __init__(self, title=None, version='latest', **kwargs):
        kwargs['version'] = version
        ARMProperty.__init__(self, title, **kwargs)

    # todo add validations
    props = {
        'publisher': (str, False),
        'offer': (str, False),
        'sku': (str, False),
        'version': (str, False)
    }


class VirtualHardDisk(ARMProperty):
    props = {
        'uri': (str, False)
    }


class ManagedDiskParameters(ARMProperty):
    props = {
        'id': (str, False),
        'storageAccountType': (str, False)  # todo add validation - Standard_LRS or Premium_LRS
    }

    def validate(self):
        if 'storageAccountType' in self.properties:
            if self.properties['storageAccountType'] not in ['Standard_LRS', 'Premium_LRS']:
                raise ValueError('storageAccountType - Possible values are: Standard_LRS or Premium_LRS')


# https://docs.microsoft.com/en-us/azure/templates/microsoft.compute/virtualmachines#OSDisk
class OsDisk(ARMProperty):
    props = {
        'osTpe': (str, False),  # todo add validations: Linux/Windows
        # 'encryptionSettings': (object, False),  # todo add support for encryptionSettings
        'name': (str, False),
        'vhd': (VirtualHardDisk, False),
        'image': (VirtualHardDisk, False),
        # 'caching': (str, False),  # todo add support
        'createOption': (str, True),  # todo add validations
        'diskSizeGB': (int, False),  # todo add validations on max size
        'managedDisk': (ManagedDiskParameters, False)
    }


class StorageProfile(ARMProperty):
    props = {
        'imageReference': (ImageReference, False),
        'osDisk': (OsDisk, False)
        # 'dataDisks':  # todo add support
    }


class WindowsConfiguration(ARMProperty):
    props = {
        'provisionVMAgent': (bool, False),  # default is True
        'enableAutomaticUpdates': (bool, False),
        'timeZone': (str, False),
        # 'additionalUnattendContent': (str, False),  # todo add support
        # 'winRM': (str, False)  # todo add support
    }


class SshPublicKey(ARMProperty):
    props = {
        'path': (str, False),
        'keyData': (str, False)
    }


class SshConfiguration(ARMProperty):
    props = {
        'publicKeys': ((list, SshPublicKey), False)
    }


class LinuxConfiguration(ARMProperty):
    props = {
        'disablePasswordAuthentication': (bool, False),
        'ssh': (SshConfiguration, False)
    }


class OSProfile(ARMProperty):
    # todo add valiation: https://docs.microsoft.com/en-us/azure/templates/microsoft.compute/virtualmachines#OSProfile
    props = {
        'computerName': (str, False),
        'adminUsername': (str, False),
        'adminPassword': (str, False),
        'customData': (str, False),
        'windowsConfiguration': (WindowsConfiguration, False),
        'linuxConfiguration': (LinuxConfiguration, False)
        # 'secrets': (, False)  # todo add support
    }


class NetworkInterfaceReferenceProperties(ARMProperty):
    props = {
        'primary': (bool, False)
    }


class NetworkInterfaceReference(ARMProperty):
    props = {
        'id': (str, False),
        'properties': (NetworkInterfaceReferenceProperties, False)
    }


class NetworkProfile(ARMProperty):
    props = {
        'networkInterfaces': ([NetworkInterfaceReference], False)
    }


class BootDiagnostics(ARMProperty):
    props = {
        'enabled': (bool, False),
        'storageUri': (str, False)
    }


class DiagnosticsProfile(ARMProperty):
    props = {
        'bootDiagnostics': (BootDiagnostics, False)
    }


valid_names_azure_extensions = re.compile(r'^[a-zA-Z0-9_\-/]+$')


class VirtualMachineExtension(ARMObject):
    # name of extension should be "[concat(parameters('vmName'),'/parameters('extensionName')]"
    # and extension should be dependent on a VM
    resource_type = 'Microsoft.Compute/virtualMachines/extensions'
    apiVersion = "2017-12-01"
    location = True

    props = {
        'forceUpdateTag': (bool, False),
        'publisher': (str, False),
        'type': (str, False),
        'typeHandlerVersion': (str, False),
        'autoUpgradeMinorVersion': (bool, False),
        'settings': (dict, False),
        'protectedSettings': (dict, False)
    }

    root_props = {
        'tags': (dict, False)
    }

    def validate_title(self):
        if not valid_names_azure_extensions.match(self.title):
            raise ValueError('Name "%s" is not valid' % self.title)

    @staticmethod
    def create_linux_custom_script(vm, command_to_execute, script=None, file_uris=None, storage_account_name=None,
                                   storage_account_key=None, protected_settings=True, tags=None):

        vm_extention = VirtualMachineExtension(vm.title + '/CustomScriptForLinux',
                                               publisher='Microsoft.Azure.Extensions',
                                               type='CustomScript',
                                               autoUpgradeMinorVersion=True,
                                               typeHandlerVersion='2.0',
                                               dependsOn=vm)

        VirtualMachineExtension._set_common_extension_values(vm_extention=vm_extention,
                                                             vm=vm,
                                                             command_to_execute=command_to_execute,
                                                             script=script,
                                                             file_uris=file_uris,
                                                             storage_account_name=storage_account_name,
                                                             storage_account_key=storage_account_key,
                                                             protected_settings=protected_settings,
                                                             tags=tags)

        return vm_extention

    @staticmethod
    def create_windows_custom_script(vm, command_to_execute, script=None, file_uris=None, storage_account_name=None,
                                     storage_account_key=None, protected_settings=True, tags=None):

        vm_extention = VirtualMachineExtension(vm.title + '/CustomScriptForWindows',
                                               publisher='Microsoft.Compute',
                                               type='CustomScriptExtension',
                                               autoUpgradeMinorVersion=True,
                                               typeHandlerVersion='1.9',
                                               dependsOn=vm)

        VirtualMachineExtension._set_common_extension_values(vm_extention=vm_extention,
                                                             vm=vm,
                                                             command_to_execute=command_to_execute,
                                                             script=script,
                                                             file_uris=file_uris,
                                                             storage_account_name=storage_account_name,
                                                             storage_account_key=storage_account_key,
                                                             protected_settings=protected_settings,
                                                             tags=tags)

        return vm_extention

    @staticmethod
    def _set_common_extension_values(vm_extention, vm, command_to_execute, script=None, file_uris=None,
                                     storage_account_name=None, storage_account_key=None, protected_settings=True,
                                     tags=None):

        if script and file_uris:
            raise ValueError("Must set either script or an array of file uris")
        if not isinstance(vm, VirtualMachine):
            raise ValueError("Must provide a VirtualMachine object")

        settings = {'commandToExecute': command_to_execute}

        if script:
            settings['script'] = script

        if file_uris:
            if isinstance(file_uris, str):
                file_uris = [file_uris]
            settings['fileUris'] = file_uris

        if storage_account_key:
            settings['storageAccountKey'] = storage_account_key

        if storage_account_name:
            settings['storageAccountName'] = storage_account_name

        if tags:
            vm_extention.properties['tags'] = tags

        if protected_settings:
            vm_extention.properties['protectedSettings'] = settings
        else:
            vm_extention.properties['settings'] = settings

        vm_extention.with_depends_on(vm)


class VirtualMachine(ARMObject):
    resource_type = 'Microsoft.Compute/virtualMachines'
    apiVersion = "2017-12-01"
    location = True

    props = {
        'hardwareProfile': (HardwareProfile, False),
        'storageProfile': (StorageProfile, False),
        'osProfile': (OSProfile, False),
        'networkProfile': (NetworkProfile, False),
        'diagnosticsProfile': (DiagnosticsProfile, False),
        # 'availabilitySet': (),  # todo add support
        # 'licenseType': ()  # todo add support
    }

    root_props = {
        'plan': (Plan, False),
        'tags': (dict, False)
    }


class RollingUpgradePolicy(ARMProperty):
    props = {
        'maxBatchInstancePercent': (int, False),
        'maxUnhealthyInstancePercent': (int, False),
        'maxUnhealthyUpgradedInstancePercent': (int, False),
        'pauseTimeBetweenBatches': (str, False)
    }


class UpgradePolicy(ARMProperty):
    props = {
        'mode': (str, False),  # Manual or Automatic
        'rollingUpgradePolicy': (RollingUpgradePolicy, False),
        'automaticOSUpgrade': (bool, False)
    }


# https://docs.microsoft.com/en-us/azure/templates/microsoft.compute/virtualmachinescalesets#VirtualMachineScaleSetOSProfile
class VirtualMachineScaleSetOSProfile(ARMProperty):
    props = {
        'computerNamePrefix': (str, True),
        'adminUsername': (str, True),
        'adminPassword': (str, True),
        'customData': (str, False),
        'windowsConfiguration': (WindowsConfiguration, False),
        'linuxConfiguration': (LinuxConfiguration, False),
        # 'secrets': (list, False),  - not implemented
    }

    def validate(self):
        if 'computerNamePrefix' in self.properties:
            val = self.properties['computerNamePrefix']
            if len(val) < 0 or len(val) > 15:
                raise ValueError("computerNamePrefix - Computer name prefixes must be 1 to 15 characters long.")


# https://docs.microsoft.com/en-us/azure/templates/microsoft.compute/virtualmachinescalesets#VirtualMachineScaleSetOSDisk
class VirtualMachineScaleSetOSDisk(ARMProperty):
    props = {
        'name': (str, False),
        'caching': (str, False),
        'createOption': (str, True),
        'osType': (str, False),
        'image': (VirtualHardDisk, False),
        'vhdContainers': (list, False),
        'managedDisk': (ManagedDiskParameters, False),
    }


class VirtualMachineScaleSetDataDisk(ARMProperty):
    props = {
        'name': (str, False),
        'lun': (int, False),
        'caching': (str, False),
        'createOption': (str, True),
        'diskSizeGB': (int, False),
        'managedDisk': (ManagedDiskParameters, False),
    }


class VirtualMachineScaleSetStorageProfile(ARMProperty):
    props = {
        'imageReference': (ImageReference, False),
        'osDisk': (VirtualMachineScaleSetOSDisk, False),
        'dataDisks': (list, False)  # VirtualMachineScaleSetDataDisk
    }


class VirtualMachineScaleSetPublicIPAddressConfigurationDnsSettings(ARMProperty):
    props = {
        'domainNameLabel': (str, True)
    }


class VirtualMachineScaleSetPublicIPAddressConfiguration(ARMObject):
    # title must be provided
    props = {
        'idleTimeoutInMinutes': (int, False),
        'dnsSettings': (VirtualMachineScaleSetPublicIPAddressConfigurationDnsSettings, False)
    }


class VirtualMachineScaleSetIPConfiguration(ARMObject):
    # title must be provided
    props = {
        'id': (str, False),
        'subnet': (SubResource, False),
        'primary': (bool, False),
        'publicIPAddressConfiguration': (VirtualMachineScaleSetPublicIPAddressConfiguration, False),
        'privateIPAddressVersion': (SubResource, False),  # Possible values are: 'IPv4' and 'IPv6'
        'applicationGatewayBackendAddressPools': ([SubResource], False),
        'loadBalancerBackendAddressPools': ([BackendAddressPoolRef], False),
        'loadBalancerInboundNatPools': ([SubResource], False)
    }

    def to_dict(self):
        self._move_prop_to_root('id')
        return ARMObject.to_dict(self)


class VirtualMachineScaleSetNetworkConfiguration(ARMObject):
    # title must be provided (will be converted to name internally)
    props = {
        'id': (str, False),
        'primary': (bool, False),
        'enableAcceleratedNetworking': (bool, False),
        'networkSecurityGroup': (SubResource, False),
        # 'dnsSettings': (object, False), todo - not implemented
        'ipConfigurations': ([VirtualMachineScaleSetIPConfiguration], False),
        'enableIPForwarding': (bool, False)
    }


class VirtualMachineScaleSetNetworkProfile(ARMProperty):
    props = {
        'healthProbe': (ProbeRef, False),  # this feature is in preview and requires special feature
        'networkInterfaceConfigurations': ([VirtualMachineScaleSetNetworkConfiguration], False)
    }


class VirtualMachineScaleSetExtensionProperties(ARMProperty):
    props = {
        'forceUpdateTag': (str, False),
        'publisher': (str, False),
        'type': (str, False),  # example "CustomScriptExtension"
        'typeHandlerVersion': (str, False),
        'autoUpgradeMinorVersion': (bool, False),
        'settings': (dict, False),
        'protectedSettings': (dict, False)
    }


class VirtualMachineScaleSetExtension(ARMProperty):
    props = {
        'name': (str, False),
        'properties': (VirtualMachineScaleSetExtensionProperties, True)
    }


class VirtualMachineScaleSetExtensionProfile(ARMProperty):
    props = {
        'extensions': ([VirtualMachineScaleSetExtension], True)
    }


class VirtualMachineScaleSetVMProfile(ARMProperty):
    props = {
        'osProfile': (VirtualMachineScaleSetOSProfile, False),
        'storageProfile': (VirtualMachineScaleSetStorageProfile, False),
        'networkProfile': (VirtualMachineScaleSetNetworkProfile, False),
        # 'diagnosticsProfile': (DiagnosticsProfile, False), todo - not implemented
        'extensionProfile': (VirtualMachineScaleSetExtensionProfile, False),
        'licenseType': (str, False)
    }


class VirtualMachineScaleSetSku(ARMProperty):
    props = {
        'name': (str, True),
        'tier': (str, True),  # Standard or Basic
        'capacity': (int, True),
    }


# https://docs.microsoft.com/en-us/azure/templates/microsoft.compute/virtualmachinescalesets#microsoftcomputevirtualmachinescalesets-object
class VirtualMachineScaleSets(ARMObject):
    resource_type = 'Microsoft.Compute/virtualMachineScaleSets'
    apiVersion = "2017-12-01"
    location = True

    props = {
        # 'identity': (object, False),   # root prop - not implemented
        'zones': ([str], False),
        'upgradePolicy': (UpgradePolicy, True),
        'virtualMachineProfile': (VirtualMachineScaleSetVMProfile, False),
        'overprovision': (bool, False),
        'singlePlacementGroup': (bool, False),
    }

    root_props = {
        'sku': (VirtualMachineScaleSetSku, False),
        'plan': (Plan, False),
        'tags': (dict, False)
    }

    def to_dict(self):
        self._move_prop_to_root('zones')
        return ARMObject.to_dict(self)
