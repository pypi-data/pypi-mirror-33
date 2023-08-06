Table of contents
=================

<!--ts-->
   * [Overview](https://github.com/VerimatrixGen1/ComplianceLedger/wiki#overview)
   * [Access Control](https://github.com/VerimatrixGen1/ComplianceLedger/wiki#access-control)
   * [Installation](#usage)
      * [Ubuntu](https://github.com/VerimatrixGen1/ComplianceLedger/wiki/Ubuntu-Build-and-Install)
      * [MacOS](https://github.com/VerimatrixGen1/ComplianceLedger/wiki/MacOS-Install)
      * [Windows](https://github.com/VerimatrixGen1/ComplianceLedger/wiki/Windows-Install)
   * [User Interface](#usage)
      * [ZigBee User](https://github.com/VerimatrixGen1/ComplianceLedger/wiki/ZigBee-User)
      * [Device Manufacturer](#local-files)
      * [Compliance Organization](#remote-files)
      * [Ledger Guardian](https://github.com/VerimatrixGen1/ComplianceLedger/wiki/Ledger-Guardian)
<!--te-->


# Overview
The Compliance Ledger is an Ethereum Fork which provides a publicly readable ledger with multiple levels of write access with Proof of Authority consensus.  The ledger is managed by a group of Ledger Guardians, who provide the transaction processing, Proof of Authority consensus, and management of Smart Contracts running on the ledger.

The Compliance Ledger is used to provide device information from manufacturers and compliance organizations to network and ecosystem operators.  The information includes compliance status, firmware update links, operating instructions, and expected network behavior.  This information is provided in a machine readable interface for use by onboarding/installer tools, gateways, and backend systems.

![UseCase](https://github.com/VerimatrixGen1/ComplianceLedger/blob/master/Wiki/Images/UseCases.png)


# Access Control
## Private/Public Ethereum
![Ethereum](https://github.com/VerimatrixGen1/ComplianceLedger/blob/master/Wiki/Images/EthereumPermissions.png)

## Compliance Ledger
![ComplianceLedger](https://github.com/VerimatrixGen1/ComplianceLedger/blob/master/Wiki/Images/ComplianceLedgerPermissions.png)

| Use Case | Description | Ethereum | Compliance Ledger |
| ----- | ----- | ----- | ----- |
| 1 | User Bob sends data to user Tom | All users are allowed | Not Allowed |
| 2 | User Bob launches a contract onto the chain | All users are allowed | Only Ledger Guardians are allowed |
| 3 | User Bob writes data into contract | Permissions based on Smart Contract rules | Permissions based on Smart Contract rules |
| 4 | User Bob reads data from contract | All users are allowed | All users are allowed |


