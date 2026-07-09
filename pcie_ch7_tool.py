#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PCIe Spec Chapter 7 - Software Initialization and Configuration
Interactive Query Tool

Source: project-configured PDF
Chapter 7 (pages from pcie_spec_config.py)
"""

import json
import re
import sys
import os
import io

# Force UTF-8 output
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from typing import List, Dict, Optional
from pcie_spec_config import (
    get_profile,
    current_pdf_name,
    resolve_pdf_path,
)

ACTIVE_SPEC = get_profile(None)

# ============================================================
# 第七章結構化資料庫
# ============================================================

CHAPTER7_TOC = {
    "7.1": {"title": "Configuration Topology", "page": 673},
    "7.2": {"title": "PCI Express Configuration Mechanisms", "page": 675},
    "7.2.1": {"title": "PCI-compatible Configuration Mechanism", "page": 675},
    "7.2.2": {"title": "PCI Express Enhanced Configuration Access Mechanism (ECAM)", "page": 676},
    "7.2.2.1": {"title": "Host Bridge Requirements", "page": 679},
    "7.2.2.2": {"title": "PCI Express Device Requirements", "page": 679},
    "7.2.3": {"title": "Root Complex Register Block (RCRB)", "page": 680},
    "7.3": {"title": "Configuration Transaction Rules", "page": 680},
    "7.3.1": {"title": "Device Number", "page": 680},
    "7.3.2": {"title": "Configuration Transaction Addressing", "page": 681},
    "7.3.3": {"title": "Configuration Request Routing Rules", "page": 681},
    "7.3.4": {"title": "PCI Special Cycles", "page": 683},
    "7.4": {"title": "Configuration Register Types", "page": 683},
    "7.5": {"title": "PCI and PCIe Capabilities Required by the Base Spec for all Ports", "page": 684},
    "7.5.1": {"title": "PCI-Compatible Configuration Registers", "page": 684},
    "7.5.1.1": {"title": "Type 0/1 Common Configuration Space", "page": 684},
    "7.5.1.1.1": {"title": "Vendor ID Register (Offset 00h)", "page": 685},
    "7.5.1.1.2": {"title": "Device ID Register (Offset 02h)", "page": 686},
    "7.5.1.1.3": {"title": "Command Register (Offset 04h)", "page": 686},
    "7.5.1.1.4": {"title": "Status Register (Offset 06h)", "page": 688},
    "7.5.1.1.5": {"title": "Revision ID Register (Offset 08h)", "page": 691},
    "7.5.1.1.6": {"title": "Class Code Register (Offset 09h)", "page": 691},
    "7.5.1.1.7": {"title": "Cache Line Size Register (Offset 0Ch)", "page": 692},
    "7.5.1.1.8": {"title": "Latency Timer Register (Offset 0Dh)", "page": 692},
    "7.5.1.1.9": {"title": "Header Type Register (Offset 0Eh)", "page": 692},
    "7.5.1.1.10": {"title": "BIST Register (Offset 0Fh)", "page": 693},
    "7.5.1.1.11": {"title": "Capabilities Pointer (Offset 34h)", "page": 694},
    "7.5.1.1.12": {"title": "Interrupt Line Register (Offset 3Ch)", "page": 694},
    "7.5.1.1.13": {"title": "Interrupt Pin Register (Offset 3Dh)", "page": 694},
    "7.5.1.1.14": {"title": "Error Registers", "page": 694},
    "7.5.1.2": {"title": "Type 0 Configuration Space Header", "page": 695},
    "7.5.1.2.1": {"title": "Base Address Registers (Offset 10h-24h)", "page": 696},
    "7.5.1.2.2": {"title": "Cardbus CIS Pointer Register (Offset 28h)", "page": 699},
    "7.5.1.2.3": {"title": "Subsystem Vendor ID / Subsystem ID Register (Offset 2Ch/2Eh)", "page": 700},
    "7.5.1.2.4": {"title": "Expansion ROM Base Address Register (Offset 30h)", "page": 700},
    "7.5.1.2.5": {"title": "Min_Gnt / Max_Lat Register (Offset 3Eh/3Fh)", "page": 703},
    "7.5.1.3": {"title": "Type 1 Configuration Space Header", "page": 703},
    "7.5.1.3.1": {"title": "Type 1 Base Address Registers (Offset 10h-14h)", "page": 704},
    "7.5.1.3.2": {"title": "Primary Bus Number Register (Offset 18h)", "page": 705},
    "7.5.1.3.3": {"title": "Secondary Bus Number Register (Offset 19h)", "page": 705},
    "7.5.1.3.4": {"title": "Subordinate Bus Number Register (Offset 1Ah)", "page": 705},
    "7.5.1.3.5": {"title": "Secondary Latency Timer (Offset 1Bh)", "page": 705},
    "7.5.1.3.6": {"title": "I/O Base/Limit Registers (Offset 1Ch/1Dh)", "page": 705},
    "7.5.1.3.7": {"title": "Secondary Status Register (Offset 1Eh)", "page": 706},
    "7.5.1.3.8": {"title": "Memory Base/Limit Register (Offset 20h/22h)", "page": 708},
    "7.5.1.3.9": {"title": "Prefetchable Memory Base/Limit Registers (Offset 24h/26h)", "page": 708},
    "7.5.1.3.10": {"title": "Prefetchable Base/Limit Upper 32 Bits (Offset 28h/2Ch)", "page": 709},
    "7.5.1.3.11": {"title": "I/O Base/Limit Upper 16 Bits (Offset 30h/32h)", "page": 709},
    "7.5.1.3.12": {"title": "Expansion ROM Base Address Register (Offset 38h)", "page": 709},
    "7.5.1.3.13": {"title": "Bridge Control Register (Offset 3Eh)", "page": 709},
    "7.5.2": {"title": "PCI Power Management Capability Structure", "page": 712},
    "7.5.2.1": {"title": "Power Management Capabilities Register (Offset 00h)", "page": 712},
    "7.5.2.2": {"title": "Power Management Control/Status Register (Offset 04h)", "page": 714},
    "7.5.2.3": {"title": "Data Register (Offset 07h)", "page": 716},
    "7.5.3": {"title": "PCI Express Capability Structure", "page": 718},
    "7.5.3.1": {"title": "PCI Express Capability List Register (Offset 00h)", "page": 719},
    "7.5.3.2": {"title": "PCI Express Capabilities Register (Offset 02h)", "page": 720},
    "7.5.3.3": {"title": "Device Capabilities Register (Offset 04h)", "page": 722},
    "7.5.3.4": {"title": "Device Control Register (Offset 08h)", "page": 725},
    "7.5.3.5": {"title": "Device Status Register (Offset 0Ah)", "page": 730},
    "7.5.3.6": {"title": "Link Capabilities Register (Offset 0Ch)", "page": 732},
    "7.5.3.7": {"title": "Link Control Register (Offset 10h)", "page": 736},
    "7.5.3.8": {"title": "Link Status Register (Offset 12h)", "page": 741},
    "7.5.3.9": {"title": "Slot Capabilities Register (Offset 14h)", "page": 744},
    "7.5.3.10": {"title": "Slot Control Register (Offset 18h)", "page": 745},
    "7.5.3.11": {"title": "Slot Status Register (Offset 1Ah)", "page": 748},
    "7.5.3.12": {"title": "Root Control Register (Offset 1Ch)", "page": 750},
    "7.5.3.13": {"title": "Root Capabilities Register (Offset 1Eh)", "page": 752},
    "7.5.3.14": {"title": "Root Status Register (Offset 20h)", "page": 752},
    "7.5.3.15": {"title": "Device Capabilities 2 Register (Offset 24h)", "page": 753},
    "7.5.3.16": {"title": "Device Control 2 Register (Offset 28h)", "page": 758},
    "7.5.3.17": {"title": "Device Status 2 Register (Offset 2Ah)", "page": 761},
    "7.5.3.18": {"title": "Link Capabilities 2 Register (Offset 2Ch)", "page": 761},
    "7.5.3.19": {"title": "Link Control 2 Register (Offset 30h)", "page": 764},
    "7.5.3.20": {"title": "Link Status 2 Register (Offset 32h)", "page": 768},
    "7.5.3.21": {"title": "Slot Capabilities 2 Register (Offset 34h)", "page": 771},
    "7.5.3.22": {"title": "Slot Control 2 Register (Offset 38h)", "page": 771},
    "7.5.3.23": {"title": "Slot Status 2 Register (Offset 3Ah)", "page": 771},
    "7.6": {"title": "PCI Express Extended Capabilities", "page": 771},
    "7.6.1": {"title": "Extended Capabilities in Configuration Space", "page": 772},
    "7.6.2": {"title": "Extended Capabilities in the Root Complex Register Block", "page": 772},
    "7.6.3": {"title": "PCI Express Extended Capability Header", "page": 772},
    "7.7": {"title": "PCI and PCIe Capabilities Required by the Base Spec in Some Situations", "page": 773},
    "7.7.1": {"title": "MSI Capability Structures", "page": 773},
    "7.7.1.1": {"title": "MSI Capability Header (Offset 00h)", "page": 775},
    "7.7.1.2": {"title": "Message Control Register for MSI (Offset 02h)", "page": 776},
    "7.7.1.3": {"title": "Message Address Register for MSI (Offset 04h)", "page": 778},
    "7.7.1.4": {"title": "Message Upper Address Register for MSI (Offset 08h)", "page": 778},
    "7.7.1.5": {"title": "Message Data Register for MSI (Offset 08h or 0Ch)", "page": 779},
    "7.7.1.6": {"title": "Extended Message Data Register for MSI (Optional)", "page": 779},
    "7.7.1.7": {"title": "Mask Bits Register for MSI (Offset 0Ch or 10h)", "page": 780},
    "7.7.1.8": {"title": "Pending Bits Register for MSI (Offset 10h or 14h)", "page": 780},
    "7.7.2": {"title": "MSI-X Capability and Table Structure", "page": 781},
    "7.7.2.1": {"title": "MSI-X Capability Header (Offset 00h)", "page": 784},
    "7.7.2.2": {"title": "Message Control Register for MSI-X (Offset 02h)", "page": 784},
    "7.7.2.3": {"title": "Table Offset/Table BIR Register for MSI-X (Offset 04h)", "page": 785},
    "7.7.2.4": {"title": "PBA Offset/PBA BIR Register for MSI-X (Offset 08h)", "page": 786},
    "7.7.2.5": {"title": "Message Address Register for MSI-X Table Entries", "page": 787},
    "7.7.2.6": {"title": "Message Upper Address Register for MSI-X Table Entries", "page": 787},
    "7.7.2.7": {"title": "Message Data Register for MSI-X Table Entries", "page": 788},
    "7.7.2.8": {"title": "Vector Control Register for MSI-X Table Entries", "page": 788},
    "7.7.2.9": {"title": "Pending Bits Register for MSI-X PBA Entries", "page": 789},
    "7.7.3": {"title": "Secondary PCI Express Extended Capability", "page": 789},
    "7.7.3.1": {"title": "Secondary PCI Express Extended Capability Header (Offset 00h)", "page": 792},
    "7.7.3.2": {"title": "Link Control 3 Register (Offset 04h)", "page": 792},
    "7.7.3.3": {"title": "Lane Error Status Register (Offset 08h)", "page": 793},
    "7.7.3.4": {"title": "Lane Equalization Control Register (Offset 0Ch)", "page": 794},
    "7.7.4": {"title": "Data Link Feature Extended Capability (Cap ID: 0025h)", "page": 796},
    "7.7.4.1": {"title": "Data Link Feature Extended Capability Header (Offset 00h)", "page": 797},
    "7.7.4.2": {"title": "Data Link Feature Capabilities Register (Offset 04h)", "page": 798},
    "7.7.4.3": {"title": "Data Link Feature Status Register (Offset 08h)", "page": 798},
    "7.7.5": {"title": "Physical Layer 16.0 GT/s Extended Capability (Cap ID: 0026h)", "page": 799},
    "7.7.5.1": {"title": "Physical Layer 16.0 GT/s Extended Capability Header (Offset 00h)", "page": 800},
    "7.7.5.2": {"title": "16.0 GT/s Capabilities Register (Offset 04h)", "page": 801},
    "7.7.5.3": {"title": "16.0 GT/s Control Register (Offset 08h)", "page": 801},
    "7.7.5.4": {"title": "16.0 GT/s Status Register (Offset 0Ch)", "page": 802},
    "7.7.5.5": {"title": "16.0 GT/s Local Data Parity Mismatch Status Register (Offset 10h)", "page": 803},
    "7.7.5.6": {"title": "16.0 GT/s First Retimer Data Parity Mismatch Status Register (Offset 14h)", "page": 803},
    "7.7.5.7": {"title": "16.0 GT/s Second Retimer Data Parity Mismatch Status Register (Offset 18h)", "page": 804},
    "7.7.5.9": {"title": "16.0 GT/s Lane Equalization Control Register (Offsets 20h to 3Ch)", "page": 805},
    "7.7.6": {"title": "Physical Layer 32.0 GT/s Extended Capability (Cap ID: 002Ah)", "page": 806},
    "7.7.6.1": {"title": "Physical Layer 32.0 GT/s Extended Capability Header (Offset 00h)", "page": 807},
    "7.7.6.2": {"title": "32.0 GT/s Capabilities Register (Offset 04h)", "page": 808},
    "7.7.6.3": {"title": "32.0 GT/s Control Register (Offset 08h)", "page": 809},
    "7.7.6.4": {"title": "32.0 GT/s Status Register (Offset 0Ch)", "page": 810},
    "7.7.6.5": {"title": "Received Modified TS Data 1 Register (Offset 10h)", "page": 811},
    "7.7.6.6": {"title": "Received Modified TS Data 2 Register (Offset 14h)", "page": 812},
    "7.7.6.7": {"title": "Transmitted Modified TS Data 1 Register (Offset 18h)", "page": 813},
    "7.7.6.8": {"title": "Transmitted Modified TS Data 2 Register (Offset 1Ch)", "page": 814},
    "7.7.6.9": {"title": "32.0 GT/s Lane Equalization Control Register (Offset 20h)", "page": 815},
    "7.7.7": {"title": "Lane Margining at the Receiver Extended Capability (Cap ID: 0027h)", "page": 817},
    "7.7.7.1": {"title": "Lane Margining at the Receiver Extended Capability Header (Offset 00h)", "page": 819},
    "7.7.7.2": {"title": "Margining Port Capabilities Register (Offset 04h)", "page": 819},
    "7.7.7.3": {"title": "Margining Port Status Register (Offset 06h)", "page": 820},
    "7.7.7.4": {"title": "Margining Lane Control Register (Offset 08h)", "page": 820},
    "7.7.7.5": {"title": "Margining Lane Status Register (Offset 0Ah)", "page": 821},
    "7.7.8": {"title": "ACS Extended Capability (Cap ID: 000Dh)", "page": 822},
    "7.7.8.1": {"title": "ACS Extended Capability Header (Offset 00h)", "page": 823},
    "7.7.8.2": {"title": "ACS Capability Register (Offset 04h)", "page": 824},
    "7.7.8.3": {"title": "ACS Control Register (Offset 06h)", "page": 825},
    "7.7.8.4": {"title": "Egress Control Vector Register (Offset 08h)", "page": 827},
    "7.8": {"title": "Common PCI and PCIe Capabilities", "page": 829},
    "7.8.1": {"title": "Power Budgeting Extended Capability (Cap ID: 0004h)", "page": 829},
    "7.8.1.1": {"title": "Power Budgeting Extended Capability Header (Offset 00h)", "page": 829},
    "7.8.1.2": {"title": "Power Budgeting Data Select Register (Offset 04h)", "page": 830},
    "7.8.1.3": {"title": "Power Budgeting Data Register (Offset 08h)", "page": 830},
    "7.8.1.4": {"title": "Power Budgeting Capability Register (Offset 0Ch)", "page": 832},
    "7.8.2": {"title": "Latency Tolerance Reporting (LTR) Extended Capability (Cap ID: 0018h)", "page": 833},
    "7.8.2.1": {"title": "LTR Extended Capability Header (Offset 00h)", "page": 834},
    "7.8.2.2": {"title": "Max Snoop Latency Register (Offset 04h)", "page": 834},
    "7.8.2.3": {"title": "Max No-Snoop Latency Register (Offset 06h)", "page": 835},
    "7.8.3": {"title": "L1 PM Substates Extended Capability (Cap ID: 001Eh)", "page": 835},
    "7.8.3.1": {"title": "L1 PM Substates Extended Capability Header (Offset 00h)", "page": 836},
    "7.8.3.2": {"title": "L1 PM Substates Capabilities Register (Offset 04h)", "page": 837},
    "7.8.3.3": {"title": "L1 PM Substates Control 1 Register (Offset 08h)", "page": 838},
    "7.8.3.4": {"title": "L1 PM Substates Control 2 Register (Offset 0Ch)", "page": 840},
    "7.8.3.5": {"title": "L1 PM Substates Status Register (Offset 10h)", "page": 841},
    "7.8.4": {"title": "Advanced Error Reporting (AER) Extended Capability (Cap ID: 0001h)", "page": 841},
    "7.8.4.1": {"title": "Advanced Error Reporting Extended Capability Header (Offset 00h)", "page": 842},
    "7.8.4.2": {"title": "Uncorrectable Error Status Register (Offset 04h)", "page": 843},
    "7.8.4.3": {"title": "Uncorrectable Error Mask Register (Offset 08h)", "page": 845},
    "7.8.4.4": {"title": "Uncorrectable Error Severity Register (Offset 0Ch)", "page": 846},
    "7.8.4.5": {"title": "Correctable Error Status Register (Offset 10h)", "page": 848},
    "7.8.4.6": {"title": "Correctable Error Mask Register (Offset 14h)", "page": 849},
    "7.8.4.7": {"title": "Advanced Error Capabilities and Control Register (Offset 18h)", "page": 850},
    "7.8.4.8": {"title": "Header Log Register (Offset 1Ch)", "page": 851},
    "7.8.4.9": {"title": "Root Error Command Register (Offset 2Ch)", "page": 851},
    "7.8.4.10": {"title": "Root Error Status Register (Offset 30h)", "page": 852},
    "7.8.4.11": {"title": "Error Source Identification Register (Offset 34h)", "page": 854},
    "7.8.4.12": {"title": "TLP Prefix Log Register (Offset 38h)", "page": 855},
    "7.8.5": {"title": "Enhanced Allocation Capability Structure (EA) (Cap ID: 0014h)", "page": 856},
    "7.8.6": {"title": "Resizable BAR Extended Capability", "page": 862},
    "7.8.7": {"title": "ARI Extended Capability (Cap ID: 000Eh)", "page": 869},
    "7.8.8": {"title": "PASID Extended Capability (Cap ID: 001Bh)", "page": 871},
    "7.8.8.1": {"title": "PASID Extended Capability Header (Offset 00h)", "page": 871},
    "7.8.8.2": {"title": "PASID Capability Register (Offset 04h)", "page": 872},
    "7.8.8.3": {"title": "PASID Control Register (Offset 06h)", "page": 873},
    "7.8.9": {"title": "FRS Queueing Extended Capability (Cap ID: 0021h)", "page": 874},
    "7.8.9.1": {"title": "FRS Queueing Extended Capability Header (Offset 00h)", "page": 875},
    "7.8.9.2": {"title": "FRS Queueing Capability Register (Offset 04h)", "page": 875},
    "7.8.9.3": {"title": "FRS Queueing Status Register (Offset 08h)", "page": 876},
    "7.8.9.4": {"title": "FRS Queueing Control Register (Offset 0Ah)", "page": 877},
    "7.8.9.5": {"title": "FRS Message Queue Register (Offset 0Ch)", "page": 877},
    "7.8.10": {"title": "Flattening Portal Bridge (FPB) Capability (Cap ID: 15h)", "page": 878},
    "7.9": {"title": "Additional PCI and PCIe Capabilities", "page": 888},
    "7.9.1": {"title": "Virtual Channel Extended Capability (Cap ID: 0002h / 0009h)", "page": 888},
    "7.9.1.1": {"title": "Virtual Channel Extended Capability Header (Offset 00h)", "page": 890},
    "7.9.1.2": {"title": "Port VC Capability Register 1 (Offset 04h)", "page": 891},
    "7.9.1.3": {"title": "Port VC Capability Register 2 (Offset 08h)", "page": 892},
    "7.9.1.4": {"title": "Port VC Control Register (Offset 0Ch)", "page": 893},
    "7.9.1.5": {"title": "Port VC Status Register (Offset 0Eh)", "page": 894},
    "7.9.1.6": {"title": "VC Resource Capability Register", "page": 894},
    "7.9.1.7": {"title": "VC Resource Control Register", "page": 896},
    "7.9.1.8": {"title": "VC Resource Status Register", "page": 897},
    "7.9.1.9": {"title": "VC Arbitration Table", "page": 898},
    "7.9.1.10": {"title": "Port Arbitration Table", "page": 899},
    "7.9.2": {"title": "Multi-Function Virtual Channel Extended Capability (Cap ID: 0009h)", "page": 901},
    "7.9.3": {"title": "Device Serial Number Extended Capability (Cap ID: 0003h)", "page": 911},
    "7.9.4": {"title": "Vendor-Specific Capability (Cap ID: 09h)", "page": 913},
    "7.9.5": {"title": "Vendor-Specific Extended Capability (Cap ID: 000Bh)", "page": 914},
    "7.9.6": {"title": "Designated Vendor-Specific Extended Capability (DVSEC) (Cap ID: 0023h)", "page": 916},
    "7.9.7": {"title": "RCRB Header Extended Capability (Cap ID: 000Ah)", "page": 918},
    "7.9.8": {"title": "Root Complex Link Declaration Extended Capability (Cap ID: 0005h)", "page": 921},
    "7.9.9": {"title": "Root Complex Internal Link Control Extended Capability (Cap ID: 0006h)", "page": 927},
    "7.9.10": {"title": "Root Complex Event Collector Endpoint Association Extended Capability (Cap ID: 0007h)", "page": 933},
    "7.9.11": {"title": "Multicast Extended Capability (Cap ID: 0012h)", "page": 936},
    "7.9.12": {"title": "Dynamic Power Allocation Extended Capability (DPA) (Cap ID: 0016h)", "page": 941},
    "7.9.13": {"title": "TPH Requester Extended Capability (Cap ID: 0017h)", "page": 946},
    "7.9.14": {"title": "LN Requester Extended Capability (LNR) (Cap ID: 001Ch)", "page": 950},
    "7.9.15": {"title": "DPC Extended Capability (Cap ID: 001Dh)", "page": 952},
    "7.9.15.1": {"title": "DPC Extended Capability Header (Offset 00h)", "page": 953},
    "7.9.15.2": {"title": "DPC Capability Register (Offset 04h)", "page": 954},
    "7.9.15.3": {"title": "DPC Control Register (Offset 06h)", "page": 955},
    "7.9.15.4": {"title": "DPC Status Register (Offset 08h)", "page": 957},
    "7.9.15.5": {"title": "DPC Error Source ID Register (Offset 0Ah)", "page": 959},
    "7.9.15.6": {"title": "RP PIO Status Register (Offset 0Ch)", "page": 959},
    "7.9.15.7": {"title": "RP PIO Mask Register (Offset 10h)", "page": 960},
    "7.9.15.8": {"title": "RP PIO Severity Register (Offset 14h)", "page": 961},
    "7.9.15.9": {"title": "RP PIO SysError Register (Offset 18h)", "page": 962},
    "7.9.15.10": {"title": "RP PIO Exception Register (Offset 1Ch)", "page": 962},
    "7.9.15.11": {"title": "RP PIO Header Log Register (Offset 20h)", "page": 963},
    "7.9.15.12": {"title": "RP PIO ImpSpec Log Register (Offset 30h)", "page": 964},
    "7.9.15.13": {"title": "RP PIO TLP Prefix Log Register (Offset 34h)", "page": 964},
    "7.9.16": {"title": "Precision Time Management Extended Capability (PTM) (Cap ID: 001Fh)", "page": 965},
    "7.9.16.1": {"title": "PTM Extended Capability Header (Offset 00h)", "page": 966},
    "7.9.16.2": {"title": "PTM Capability Register (Offset 04h)", "page": 966},
    "7.9.16.3": {"title": "PTM Control Register (Offset 08h)", "page": 968},
    "7.9.17": {"title": "Readiness Time Reporting Extended Capability (Cap ID: 0022h)", "page": 969},
    "7.9.17.1": {"title": "Readiness Time Reporting Extended Capability Header (Offset 00h)", "page": 970},
    "7.9.17.2": {"title": "Readiness Time Reporting 1 Register (Offset 04h)", "page": 971},
    "7.9.17.3": {"title": "Readiness Time Reporting 2 Register (Offset 08h)", "page": 972},
    "7.9.18": {"title": "Hierarchy ID Extended Capability (Cap ID: 0028h)", "page": 972},
    "7.9.19": {"title": "Vital Product Data Capability (VPD) (Cap ID: 03h)", "page": 979},
    "7.9.20": {"title": "Native PCIe Enclosure Management Extended Capability (NPEM) (Cap ID: 0029h)", "page": 981},
    "7.9.21": {"title": "Alternate Protocol Extended Capability (Cap ID: 002Bh)", "page": 987},
    "7.9.22": {"title": "Conventional PCI Advanced Features Capability (AF) (Cap ID: 13h)", "page": 991},
    "7.9.23": {"title": "SFI Extended Capability (Cap ID: 002Ch)", "page": 993},
    "7.9.24": {"title": "Subsystem ID and Subsystem Vendor ID Capability (Cap ID: 0Dh)", "page": 998},
}

# Capability ID 對照表 (Cap ID -> Section)
CAPABILITY_ID_MAP = {
    # PCI Capabilities (Offset < 256)
    "01h": {"name": "PCI Power Management", "section": "7.5.2"},
    "05h": {"name": "MSI", "section": "7.7.1"},
    "09h": {"name": "Vendor-Specific", "section": "7.9.4"},
    "0Dh": {"name": "Subsystem ID and Subsystem Vendor ID", "section": "7.9.24"},
    "10h": {"name": "PCI Express", "section": "7.5.3"},
    "11h": {"name": "MSI-X", "section": "7.7.2"},
    "13h": {"name": "Advanced Features (AF)", "section": "7.9.22"},
    "15h": {"name": "Flattening Portal Bridge (FPB)", "section": "7.8.10"},
    # Extended Capabilities (Cap ID >= 0001h)
    "0001h": {"name": "Advanced Error Reporting (AER)", "section": "7.8.4"},
    "0002h": {"name": "Virtual Channel (VC)", "section": "7.9.1"},
    "0003h": {"name": "Device Serial Number", "section": "7.9.3"},
    "0004h": {"name": "Power Budgeting", "section": "7.8.1"},
    "0005h": {"name": "Root Complex Link Declaration", "section": "7.9.8"},
    "0006h": {"name": "Root Complex Internal Link Control", "section": "7.9.9"},
    "0007h": {"name": "Root Complex Event Collector Endpoint Association", "section": "7.9.10"},
    "0009h": {"name": "Multi-Function VC (MFVC) / VC (alternate ID)", "section": "7.9.2"},
    "000Ah": {"name": "RCRB Header", "section": "7.9.7"},
    "000Bh": {"name": "Vendor-Specific Extended Capability (VSEC)", "section": "7.9.5"},
    "000Dh": {"name": "Access Control Services (ACS)", "section": "7.7.8"},
    "000Eh": {"name": "Alternative Routing-ID Interpretation (ARI)", "section": "7.8.7"},
    "0012h": {"name": "Multicast", "section": "7.9.11"},
    "0014h": {"name": "Enhanced Allocation (EA)", "section": "7.8.5"},
    "0016h": {"name": "Dynamic Power Allocation (DPA)", "section": "7.9.12"},
    "0017h": {"name": "TPH Requester", "section": "7.9.13"},
    "0018h": {"name": "Latency Tolerance Reporting (LTR)", "section": "7.8.2"},
    "001Bh": {"name": "PASID", "section": "7.8.8"},
    "001Ch": {"name": "LN Requester (LNR)", "section": "7.9.14"},
    "001Dh": {"name": "Downstream Port Containment (DPC)", "section": "7.9.15"},
    "001Eh": {"name": "L1 PM Substates", "section": "7.8.3"},
    "001Fh": {"name": "Precision Time Measurement (PTM)", "section": "7.9.16"},
    "0021h": {"name": "FRS Queueing", "section": "7.8.9"},
    "0022h": {"name": "Readiness Time Reporting", "section": "7.9.17"},
    "0023h": {"name": "Designated Vendor-Specific Extended Capability (DVSEC)", "section": "7.9.6"},
    "0025h": {"name": "Data Link Feature", "section": "7.7.4"},
    "0026h": {"name": "Physical Layer 16.0 GT/s", "section": "7.7.5"},
    "0027h": {"name": "Lane Margining at the Receiver", "section": "7.7.7"},
    "0028h": {"name": "Hierarchy ID", "section": "7.9.18"},
    "0029h": {"name": "Native PCIe Enclosure Management (NPEM)", "section": "7.9.20"},
    "002Ah": {"name": "Physical Layer 32.0 GT/s", "section": "7.7.6"},
    "002Bh": {"name": "Alternate Protocol", "section": "7.9.21"},
    "002Ch": {"name": "System Firmware Intermediary (SFI)", "section": "7.9.23"},
}

# 暫存器屬性說明
REGISTER_ATTRIBUTES = {
    "HwInit": "Hardware Initialized - 由硬體/韌體初始化，初始化後為唯讀，僅 Conventional Reset 後可重新初始化",
    "RO":     "Read-Only - 唯讀暫存器，軟體不可更改",
    "RW":     "Read-Write - 讀寫暫存器，軟體可設定任意值",
    "RW1C":   "Write-1-to-Clear - 讀取顯示狀態，寫 1 清除，寫 0 無效",
    "ROS":    "Sticky Read-Only - 唯讀 Sticky，不被 Hot Reset 或 FLR 初始化",
    "RWS":    "Sticky Read-Write - 讀寫 Sticky，不被 Hot Reset 或 FLR 初始化",
    "RW1CS":  "Sticky Write-1-to-Clear - Sticky 狀態位元，寫 1 清除",
    "RsvdP":  "Reserved and Preserved - 保留位元，讀取回 0，寫入時必須保留讀取到的值",
    "RsvdZ":  "Reserved and Zero - 保留位元，讀取回 0，寫入時必須使用 0",
}

# 主要暫存器快速查詢資料庫
REGISTER_DB = {
    # Command Register bits
    "command": {
        "section": "7.5.1.1.3",
        "offset": "04h",
        "page": 686,
        "bits": {
            "0": {"name": "I/O Space Enable", "attr": "RW", "desc": "控制 Function 對 I/O Space 的回應。Clear=所有 I/O 請求為 UR；Set=允許解碼 I/O 地址"},
            "1": {"name": "Memory Space Enable", "attr": "RW", "desc": "控制 Function 對 Memory Space 的回應。Clear=所有 Memory 請求為 UR；Set=允許解碼 Memory 地址"},
            "2": {"name": "Bus Master Enable", "attr": "RW", "desc": "Type 0: 控制發出 Memory/I/O 請求的能力（MSI/MSI-X 也會被禁用）。Type 1: 控制 Upstream 方向轉發請求"},
            "6": {"name": "Parity Error Response", "attr": "RW", "desc": "控制 Status Register 中 Master Data Parity Error bit 的記錄"},
            "8": {"name": "SERR# Enable", "attr": "RW", "desc": "啟用 Non-fatal 和 Fatal 錯誤的 Upstream 回報；Type 1 也控制 ERR_NONFATAL/ERR_FATAL 的轉發"},
            "10": {"name": "Interrupt Disable", "attr": "RW", "desc": "控制 INTx 模擬中斷的產生。Set=禁止 INTx 中斷"},
        }
    },
    "status": {
        "section": "7.5.1.1.4",
        "offset": "06h",
        "page": 688,
        "bits": {
            "0": {"name": "Immediate Readiness", "attr": "RO", "desc": "Optional. Set=Function 保證隨時可回應 Config Requests，軟體免除重置後延遲要求"},
            "3": {"name": "Interrupt Status", "attr": "RO", "desc": "Set=有 INTx 中斷待處理"},
            "4": {"name": "Capabilities List", "attr": "RO", "desc": "必須為 1b (PCIe Functions 必須實作 PCI Express Capability)"},
            "8": {"name": "Master Data Parity Error", "attr": "RW1C", "desc": "Parity Error Response=1b 時，收到 Poisoned Completion 或傳出 Poisoned Request 時設置"},
            "11": {"name": "Signaled Target Abort", "attr": "RW1C", "desc": "Function 以 Completer Abort 完成請求時設置"},
            "12": {"name": "Received Target Abort", "attr": "RW1C", "desc": "收到 Completer Abort Completion 時設置"},
            "13": {"name": "Received Master Abort", "attr": "RW1C", "desc": "收到 Unsupported Request Completion 時設置"},
            "14": {"name": "Signaled System Error", "attr": "RW1C", "desc": "傳出 ERR_FATAL/ERR_NONFATAL 且 SERR# Enable=1 時設置"},
            "15": {"name": "Detected Parity Error", "attr": "RW1C", "desc": "收到 Poisoned TLP 時設置（與 Parity Error Response 無關）"},
        }
    },
    "device_capabilities": {
        "section": "7.5.3.3",
        "offset": "04h (PCIe Cap)",
        "page": 722,
        "bits": {
            "2:0": {"name": "Max_Payload_Size Supported", "attr": "RO", "desc": "000b=128B, 001b=256B, 010b=512B, 011b=1024B, 100b=2048B, 101b=4096B"},
            "4:3": {"name": "Phantom Functions Supported", "attr": "RO", "desc": "00b=不使用, 01b=用最高1 bit, 10b=用最高2 bits, 11b=用全部3 bits"},
            "5": {"name": "Extended Tag Field Supported", "attr": "RO", "desc": "0b=5-bit Tag, 1b=8-bit Tag。若 10-Bit Tag Requester Supported=Set 則也必須 Set"},
            "8:6": {"name": "Endpoint L0s Acceptable Latency", "attr": "RO", "desc": "000b=Max 64ns, 001b=128ns, 010b=256ns, 011b=512ns, 100b=1μs, 101b=2μs, 110b=4μs, 111b=無限制"},
            "11:9": {"name": "Endpoint L1 Acceptable Latency", "attr": "RO", "desc": "000b=Max 1μs, 001b=2μs, 010b=4μs, 011b=8μs, 100b=16μs, 101b=32μs, 110b=64μs, 111b=無限制"},
            "15": {"name": "Role-Based Error Reporting", "attr": "RO", "desc": "Set=支援 Role-Based Error Reporting（PCIe 1.1 及後續版本合規的 Function 必須 Set）"},
            "16": {"name": "ERR_COR Subclass Capable", "attr": "RO", "desc": "Set=支援 ERR_COR Messages 中的 Subclass 欄位"},
            "25:18": {"name": "Captured Slot Power Limit Value", "attr": "RO", "desc": "Upstream Ports: 插槽可用電源上限值（配合 Scale 欄位計算實際功耗）"},
            "27:26": {"name": "Captured Slot Power Limit Scale", "attr": "RO", "desc": "00b=1.0x, 01b=0.1x, 10b=0.01x, 11b=0.001x"},
            "28": {"name": "Function Level Reset Capability", "attr": "RO", "desc": "Set=Endpoint 支援 FLR（Function Level Reset）機制"},
        }
    },
    "device_control": {
        "section": "7.5.3.4",
        "offset": "08h (PCIe Cap)",
        "page": 725,
        "bits": {
            "0": {"name": "Correctable Error Reporting Enable", "attr": "RW", "desc": "啟用時傳送 ERR_COR Messages"},
            "1": {"name": "Non-Fatal Error Reporting Enable", "attr": "RW", "desc": "啟用時傳送 ERR_NONFATAL Messages"},
            "2": {"name": "Fatal Error Reporting Enable", "attr": "RW", "desc": "啟用時傳送 ERR_FATAL Messages"},
            "3": {"name": "Unsupported Request Reporting Enable", "attr": "RW", "desc": "啟用時回報 UR 錯誤"},
            "4": {"name": "Enable Relaxed Ordering", "attr": "RW", "desc": "Set=允許在啟動的 Transactions 中設置 Relaxed Ordering attribute"},
            "7:5": {"name": "Max_Payload_Size", "attr": "RW", "desc": "000b=128B, 001b=256B, 010b=512B, 011b=1024B, 100b=2048B, 101b=4096B"},
            "8": {"name": "Extended Tag Field Enable", "attr": "RW", "desc": "Set=允許使用 8-bit Tag field（須配合 10-Bit Tag Requester Enable）"},
            "9": {"name": "Phantom Functions Enable", "attr": "RW", "desc": "Set=允許使用 Phantom Functions 擴展未完成事務數量"},
            "10": {"name": "Aux Power PM Enable", "attr": "RWS", "desc": "Set=允許 Function 獨立於 PME Aux power 消耗輔助電源（Sticky）"},
            "11": {"name": "Enable No Snoop", "attr": "RW", "desc": "Set=允許在啟動的 Transactions 中設置 No Snoop attribute"},
            "14:12": {"name": "Max_Read_Request_Size", "attr": "RW", "desc": "000b=128B, 001b=256B, 010b=512B(預設), 011b=1024B, 100b=2048B, 101b=4096B"},
            "15": {"name": "Bridge Configuration Retry Enable / Initiate FLR", "attr": "RW", "desc": "Bridge: 啟用 CRS 回應；Endpoint(FLR Capable): 寫1b 觸發 FLR"},
        }
    },
    "device_status": {
        "section": "7.5.3.5",
        "offset": "0Ah (PCIe Cap)",
        "page": 730,
        "bits": {
            "0": {"name": "Correctable Error Detected", "attr": "RW1C", "desc": "偵測到可糾正錯誤（無論是否啟用回報）"},
            "1": {"name": "Non-Fatal Error Detected", "attr": "RW1C", "desc": "偵測到 Non-fatal 錯誤"},
            "2": {"name": "Fatal Error Detected", "attr": "RW1C", "desc": "偵測到 Fatal 錯誤"},
            "3": {"name": "Unsupported Request Detected", "attr": "RW1C", "desc": "收到 Unsupported Request"},
            "4": {"name": "AUX Power Detected", "attr": "RO", "desc": "Function 偵測到輔助電源"},
            "5": {"name": "Transactions Pending", "attr": "RO", "desc": "有未完成的 Non-Posted Requests（FLR 完成後必須清除）"},
            "6": {"name": "Emergency Power Reduction Detected", "attr": "RW1C", "desc": "Function 處於 Emergency Power Reduction State"},
        }
    },
    "link_capabilities": {
        "section": "7.5.3.6",
        "offset": "0Ch (PCIe Cap)",
        "page": 732,
        "bits": {
            "3:0": {"name": "Max Link Speed", "attr": "RO", "desc": "0001b=2.5GT/s, 0010b=5.0GT/s, 0011b=8.0GT/s, 0100b=16.0GT/s, 0101b=32.0GT/s"},
            "9:4": {"name": "Maximum Link Width", "attr": "RO", "desc": "000001b=x1, 000010b=x2, 000100b=x4, 001000b=x8, 001100b=x12, 010000b=x16, 100000b=x32"},
            "11:10": {"name": "Active State Power Management (ASPM) Support", "attr": "RO", "desc": "00b=不支援, 01b=L0s, 10b=L1, 11b=L0s+L1"},
            "14:12": {"name": "L0s Exit Latency", "attr": "RO", "desc": "000b=<64ns, 001b=64-128ns, 010b=128-256ns, 011b=256-512ns, 100b=512ns-1μs, 101b=1-2μs, 110b=2-4μs, 111b=>4μs"},
            "17:15": {"name": "L1 Exit Latency", "attr": "RO", "desc": "000b=<1μs, 001b=1-2μs, 010b=2-4μs, 011b=4-8μs, 100b=8-16μs, 101b=16-32μs, 110b=32-64μs, 111b=>64μs"},
            "18": {"name": "Clock Power Management", "attr": "RO", "desc": "Set=支援使用 CLKREQ# 訊號進行時脈電源管理"},
            "19": {"name": "Surprise Down Error Reporting Capable", "attr": "RO", "desc": "Set=支援 Surprise Down Error 回報"},
            "20": {"name": "Data Link Layer Link Active Reporting Capable", "attr": "RO", "desc": "Set=支援 DLL Link Active 狀態回報"},
            "21": {"name": "Link Bandwidth Notification Capability", "attr": "RO", "desc": "Set=支援 Link 頻寬通知機制"},
            "22": {"name": "ASPM Optionality Compliance", "attr": "RO", "desc": "Set=符合 ASPM 可選性合規要求"},
            "31:24": {"name": "Port Number", "attr": "HwInit", "desc": "Port 號碼"},
        }
    },
    "link_control": {
        "section": "7.5.3.7",
        "offset": "10h (PCIe Cap)",
        "page": 736,
        "bits": {
            "1:0": {"name": "ASPM Control", "attr": "RW", "desc": "00b=停用, 01b=L0s Entry Enabled, 10b=L1 Entry Enabled, 11b=L0s+L1 Enabled"},
            "3": {"name": "Read Completion Boundary (RCB)", "attr": "RO/RW", "desc": "0b=64 bytes, 1b=128 bytes（Root Ports 為 RW，其他為 RO）"},
            "4": {"name": "Link Disable", "attr": "RW/RsvdP", "desc": "僅 Downstream Ports: Set=停用 Link（由 LTSSM 進入 Disabled 狀態）"},
            "5": {"name": "Retrain Link", "attr": "RW/RsvdP", "desc": "僅 Downstream Ports: 寫 1b 重新訓練 Link，讀取永遠回 0b"},
            "6": {"name": "Common Clock Configuration", "attr": "RW", "desc": "Set=Link 兩端使用共同參考時脈"},
            "7": {"name": "Extended Synch", "attr": "RW", "desc": "Set=L0s 退出和 Recovery 狀態傳送額外 Ordered Sets（用於外部監測）"},
            "8": {"name": "Enable Clock Power Management", "attr": "RW", "desc": "Set=使用 CLKREQ# 訊號控制時脈（須 Clock Power Management Capable=Set）"},
            "9": {"name": "Hardware Autonomous Width Disable", "attr": "RW", "desc": "Set=禁止硬體自動縮小 Link Width"},
            "10": {"name": "Link Bandwidth Management Interrupt Enable", "attr": "RW", "desc": "Set=Link Bandwidth Management Status 改變時產生中斷"},
            "11": {"name": "Link Autonomous Bandwidth Interrupt Enable", "attr": "RW", "desc": "Set=Link Autonomous Bandwidth Status 改變時產生中斷"},
            "14": {"name": "DRS Signaling Control", "attr": "RW", "desc": "00b=DRS 中斷停用, 01b=啟用 MSI/MSI-X 中斷, 10b=啟用 ERR_COR 訊號"},
        }
    },
    "link_status": {
        "section": "7.5.3.8",
        "offset": "12h (PCIe Cap)",
        "page": 741,
        "bits": {
            "3:0": {"name": "Current Link Speed", "attr": "RO", "desc": "0001b=2.5GT/s, 0010b=5.0GT/s, 0011b=8.0GT/s, 0100b=16.0GT/s, 0101b=32.0GT/s"},
            "9:4": {"name": "Negotiated Link Width", "attr": "RO", "desc": "000001b=x1, 000010b=x2, 000100b=x4, 001000b=x8, 001100b=x12, 010000b=x16, 100000b=x32"},
            "10": {"name": "Undefined", "attr": "RO", "desc": "在舊版規範中用於 Link Training，現在值未定義"},
            "11": {"name": "Link Training", "attr": "RO", "desc": "Set=Link Training 正在進行中"},
            "12": {"name": "Slot Clock Configuration", "attr": "HwInit", "desc": "Set=元件使用實體插槽提供的參考時脈"},
            "13": {"name": "Data Link Layer Link Active", "attr": "RO", "desc": "Set=Data Link Layer 處於 DL_Active 狀態"},
            "14": {"name": "Link Bandwidth Management Status", "attr": "RW1C", "desc": "Set=Link 自主改變 Link speed 或 width 以試圖糾正問題"},
            "15": {"name": "Link Autonomous Bandwidth Status", "attr": "RW1C", "desc": "Set=Link speed 或 width 在不因可靠性問題下自主改變"},
        }
    },
    "device_capabilities_2": {
        "section": "7.5.3.15",
        "offset": "24h (PCIe Cap)",
        "page": 753,
        "bits": {
            "3:0": {"name": "Completion Timeout Ranges Supported", "attr": "HwInit", "desc": "0000b=不支援可程式化, 0001b=A, 0010b=B, 0011b=A+B, 0110b=B+C, 0111b=A+B+C, 1110b=B+C+D, 1111b=A+B+C+D"},
            "4": {"name": "Completion Timeout Disable Supported", "attr": "RO", "desc": "Set=支援停用 Completion Timeout 機制"},
            "5": {"name": "ARI Forwarding Supported", "attr": "RO", "desc": "Switch Downstream Ports 和 Root Ports: Set=支援 ARI Forwarding"},
            "6": {"name": "AtomicOp Routing Supported", "attr": "RO", "desc": "Switch 和 Root Ports: Set=支援 AtomicOp Routing"},
            "7": {"name": "32-bit AtomicOp Completer Supported", "attr": "RO", "desc": "支援 32-bit FetchAdd、Swap、CAS AtomicOps"},
            "8": {"name": "64-bit AtomicOp Completer Supported", "attr": "RO", "desc": "支援 64-bit AtomicOps"},
            "9": {"name": "128-bit CAS Completer Supported", "attr": "RO", "desc": "支援 128-bit CAS AtomicOps"},
            "11": {"name": "LTR Mechanism Supported", "attr": "RO", "desc": "Set=支援可選的 Latency Tolerance Reporting 機制"},
            "13:12": {"name": "TPH Completer Supported", "attr": "RO", "desc": "00b=不支援, 01b=TPH, 11b=TPH+Extended TPH"},
            "16": {"name": "10-Bit Tag Completer Supported", "attr": "HwInit", "desc": "Set=支援 10-Bit Tag Completer"},
            "17": {"name": "10-Bit Tag Requester Supported", "attr": "HwInit", "desc": "Set=支援 10-Bit Tag Requester（必須 10-Bit Tag Completer 也 Set）"},
            "19:18": {"name": "OBFF Supported", "attr": "HwInit", "desc": "00b=不支援, 01b=Message only, 10b=WAKE# only, 11b=WAKE#+Message"},
            "21": {"name": "End-End TLP Prefix Supported", "attr": "HwInit", "desc": "Set=支援接收含 End-End TLP Prefix 的 TLPs"},
            "23:22": {"name": "Max End-End TLP Prefixes", "attr": "HwInit", "desc": "01b=1, 10b=2, 11b=3, 00b=4"},
            "25:24": {"name": "Emergency Power Reduction Supported", "attr": "HwInit", "desc": "00b=不支援, 01b=Device Specific機制, 10b=Form Factor或Device Specific機制"},
            "31": {"name": "FRS Supported", "attr": "HwInit", "desc": "Set=支援可選的 Function Readiness Status (FRS) 功能"},
        }
    },
    "device_control_2": {
        "section": "7.5.3.16",
        "offset": "28h (PCIe Cap)",
        "page": 758,
        "bits": {
            "3:0": {"name": "Completion Timeout Value", "attr": "RW", "desc": "0000b=50μs-50ms, 0001b=50-100μs, 0010b=1-10ms, 0101b=16-55ms, 0110b=65-210ms, 1001b=260ms-900ms, 1010b=1-3.5s, 1101b=4-13s, 1110b=17-64s"},
            "4": {"name": "Completion Timeout Disable", "attr": "RW", "desc": "Set=停用 Completion Timeout 偵測機制"},
            "5": {"name": "ARI Forwarding Enable", "attr": "RW", "desc": "Downstream Ports: Set=啟用 ARI Forwarding，允許 ARI Device 的 Extended Functions"},
            "6": {"name": "AtomicOp Requester Enable", "attr": "RW", "desc": "Set=允許發起 AtomicOp Requests（需 Bus Master Enable 也 Set）"},
            "7": {"name": "AtomicOp Egress Blocking", "attr": "RW", "desc": "Set=阻擋 AtomicOp Requests 通過此 Egress Port"},
            "8": {"name": "IDO Request Enable", "attr": "RW", "desc": "Set=允許在發起的 Requests 中設置 ID-Based Ordering (IDO) attribute"},
            "9": {"name": "IDO Completion Enable", "attr": "RW", "desc": "Set=允許在回傳的 Completions 中設置 IDO attribute"},
            "10": {"name": "LTR Mechanism Enable", "attr": "RW", "desc": "Set=啟用 LTR Messages（Upstream Ports 傳送，Downstream Ports 處理）"},
            "11": {"name": "Emergency Power Reduction Request", "attr": "RW", "desc": "Set=要求所有支援的 Functions 進入 Emergency Power Reduction State"},
            "12": {"name": "10-Bit Tag Requester Enable", "attr": "RW", "desc": "Set=允許使用 10-Bit Tags（若同時設定 Extended Tag Field Enable 則優先）"},
            "14:13": {"name": "OBFF Enable", "attr": "RW", "desc": "00b=停用, 01b=Message(A), 10b=Message(B), 11b=WAKE# 訊號"},
            "15": {"name": "End-End TLP Prefix Blocking", "attr": "RW", "desc": "0b=允許轉發含 E2E TLP Prefix 的 TLPs, 1b=阻擋"},
        }
    },
    "link_capabilities_2": {
        "section": "7.5.3.18",
        "offset": "2Ch (PCIe Cap)",
        "page": 761,
        "bits": {
            "7:1": {"name": "Supported Link Speeds Vector", "attr": "HwInit", "desc": "Bit0=2.5GT/s, Bit1=5.0GT/s, Bit2=8.0GT/s, Bit3=16.0GT/s, Bit4=32.0GT/s（各 bit 為 1 表示支援該速率）"},
            "8": {"name": "Crosslink Supported", "attr": "RO", "desc": "Set=Port 支援 Crosslink（即可在 Downstream/Upstream 之間切換）"},
            "15:9": {"name": "Lower SKP OS Generation Supported Speeds Vector", "attr": "HwInit", "desc": "非零表示 Port 在指定速率支援 SRIS 及軟體控制的 SKP 排程"},
            "22:16": {"name": "Lower SKP OS Reception Supported Speeds Vector", "attr": "HwInit", "desc": "非零表示 Port 在指定速率運行時以 SRNS 定義速率接收 SKP OS"},
            "23": {"name": "Retimer Presence Detect Supported", "attr": "HwInit", "desc": "Set=Port 支援偵測和回報 Retimer 存在（16.0GT/s 及以上必須 Set）"},
            "24": {"name": "Two Retimers Presence Detect Supported", "attr": "HwInit", "desc": "Set=Port 支援偵測兩個 Retimer（16.0GT/s 及以上必須 Set）"},
            "31": {"name": "DRS Supported", "attr": "HwInit", "desc": "Downstream Ports: Set=支援可選的 Device Readiness Status (DRS) 功能"},
        }
    },
    "link_control_2": {
        "section": "7.5.3.19",
        "offset": "30h (PCIe Cap)",
        "page": 764,
        "bits": {
            "3:0": {"name": "Target Link Speed", "attr": "RWS", "desc": "0001b=2.5GT/s, 0010b=5.0GT/s, 0011b=8.0GT/s, 0100b=16.0GT/s, 0101b=32.0GT/s（設定 Link 運作速率上限）"},
            "4": {"name": "Enter Compliance", "attr": "RWS", "desc": "Set=在 Link 兩端都設置後，觸發 Hot Reset 使 Link 進入 Compliance 模式（用於測試）"},
            "5": {"name": "Hardware Autonomous Speed Disable", "attr": "RWS", "desc": "Set=禁止硬體自動改變 Link Speed（不影響初始最高速率協商）"},
            "6": {"name": "Selectable De-emphasis", "attr": "HwInit", "desc": "僅 5.0GT/s: 0b=-6dB, 1b=-3.5dB"},
            "9:7": {"name": "Transmit Margin", "attr": "RWS", "desc": "控制 Transmitter 電壓位準（000b=正常範圍，其餘見 Section 8.3.4）"},
            "10": {"name": "Enter Modified Compliance", "attr": "RWS", "desc": "Set=LTSSM 進入 Polling.Compliance 時傳送 Modified Compliance Pattern"},
            "11": {"name": "Compliance SOS", "attr": "RWS", "desc": "Set=在 Compliance Pattern 間傳送 SKP Ordered Sets"},
            "15:12": {"name": "Compliance Preset/De-emphasis", "attr": "RWS", "desc": "8.0GT/s及以上=TX Preset; 5.0GT/s: 0001b=-3.5dB, 0000b=-6dB"},
        }
    },
    "link_status_2": {
        "section": "7.5.3.20",
        "offset": "32h (PCIe Cap)",
        "page": 768,
        "bits": {
            "0": {"name": "Current De-emphasis Level", "attr": "RO", "desc": "5.0GT/s: 0b=-6dB, 1b=-3.5dB"},
            "1": {"name": "Equalization 8.0 GT/s Complete", "attr": "ROS", "desc": "Set=8.0GT/s TX Equalization 程序已完成"},
            "2": {"name": "Equalization 8.0 GT/s Phase 1 Successful", "attr": "ROS", "desc": "Phase 1 成功"},
            "3": {"name": "Equalization 8.0 GT/s Phase 2 Successful", "attr": "ROS", "desc": "Phase 2 成功"},
            "4": {"name": "Equalization 8.0 GT/s Phase 3 Successful", "attr": "ROS", "desc": "Phase 3 成功"},
            "5": {"name": "Link Equalization Request 8.0 GT/s", "attr": "RW1CS", "desc": "硬體設置以請求執行 8.0GT/s Link Equalization"},
            "6": {"name": "Retimer Presence Detected", "attr": "ROS", "desc": "Set=最近一次 Link 協商中偵測到 Retimer"},
            "7": {"name": "Two Retimers Presence Detected", "attr": "ROS", "desc": "Set=最近一次 Link 協商中偵測到兩個 Retimers"},
            "9:8": {"name": "Crosslink Resolution", "attr": "RO", "desc": "00b=不支援, 01b=Upstream Port, 10b=Downstream Port, 11b=協商尚未完成"},
            "14:12": {"name": "Downstream Component Presence", "attr": "RO", "desc": "000b=Link Down/未確定, 001b=無元件, 010b=有元件但DLL不活躍, 100b=Link Up/有元件, 101b=Link Up/有元件且收到DRS"},
            "15": {"name": "DRS Message Received", "attr": "RW1C", "desc": "Port 收到 DRS Message 時設置，DL_Down 時清除"},
        }
    },

    # ── 7.5.1 PCI-Compatible Registers ──────────────────────────────────────
    "vendor_id": {
        "section": "7.5.1.1.1", "offset": "00h", "page": 685,
        "bits": {
            "15:0": {"name": "Vendor ID", "attr": "HwInit", "desc": "識別 Function 製造商，由 PCI-SIG 分配。FFFFh 表示無 Function 存在。"},
        }
    },
    "device_id": {
        "section": "7.5.1.1.2", "offset": "02h", "page": 686,
        "bits": {
            "15:0": {"name": "Device ID", "attr": "HwInit", "desc": "識別特定 Function，由廠商分配，與 Vendor ID / Revision ID 共同用於驅動程式選擇。"},
        }
    },
    "revision_id": {
        "section": "7.5.1.1.5", "offset": "08h", "page": 691,
        "bits": {
            "7:0": {"name": "Revision ID", "attr": "HwInit", "desc": "廠商自訂的修訂識別碼，0 為合法值。"},
        }
    },
    "class_code": {
        "section": "7.5.1.1.6", "offset": "09h", "page": 691,
        "bits": {
            "7:0":   {"name": "Programming Interface", "attr": "RO", "desc": "指定暫存器級程式介面（如有），讓裝置無關軟體與 Function 互動。"},
            "15:8":  {"name": "Sub-Class Code",        "attr": "RO", "desc": "更具體識別 Function 操作類型的子類別碼。"},
            "23:16": {"name": "Base Class Code",        "attr": "RO", "desc": "廣泛分類 Function 操作類型的基礎類別碼。"},
        }
    },
    "cache_line_size": {
        "section": "7.5.1.1.7", "offset": "0Ch", "page": 692,
        "bits": {
            "7:0": {"name": "Cache Line Size", "attr": "RW", "desc": "由系統韌體或 OS 程式化為系統快取行大小。僅為相容性保留，對 PCIe 裝置行為無影響。預設 00h。"},
        }
    },
    "header_type": {
        "section": "7.5.1.1.9", "offset": "0Eh", "page": 692,
        "bits": {
            "6:0": {"name": "Header Layout",         "attr": "RO", "desc": "識別 Configuration Space 第二部分的佈局：0000000b=Type 0，0000001b=Type 1。"},
            "7":   {"name": "Multi-Function Device", "attr": "RO", "desc": "Set 表示裝置可能包含多個 Functions。Clear 時軟體不得探測 Function 0 以外的 Function（除非 ARI 或 SR-IOV 另有指示）。"},
        }
    },
    "bist": {
        "section": "7.5.1.1.10", "offset": "0Fh", "page": 693,
        "bits": {
            "3:0": {"name": "Completion Code", "attr": "RO",    "desc": "最近一次 BIST 測試的完成狀態，0000b=通過，非零=失敗。BIST Capable=Clear 時 hardwired to 0000b。"},
            "5:4": {"name": "Reserved",         "attr": "RsvdP","desc": "保留。"},
            "6":   {"name": "Start BIST",       "attr": "RW/RO","desc": "BIST Capable=Set 時，寫入 1b 啟動 BIST；Function 完成後自行清除。寫入 0b 無效。BIST Capable=Clear 時 hardwired to 0b。"},
            "7":   {"name": "BIST Capable",     "attr": "HwInit","desc": "Set 表示 Function 支援 BIST；Clear 表示不支援，整個暫存器 hardwired to 00h。"},
        }
    },
    "capabilities_pointer": {
        "section": "7.5.1.1.11", "offset": "34h", "page": 694,
        "bits": {
            "7:0": {"name": "Capabilities Pointer", "attr": "RO", "desc": "指向 Capabilities 鏈結串列的第一個項目。Bit[1:0] 保留（軟體使用前須遮罩）。"},
        }
    },
    "interrupt_line": {
        "section": "7.5.1.1.12", "offset": "3Ch", "page": 694,
        "bits": {
            "7:0": {"name": "Interrupt Line", "attr": "RW", "desc": "傳達中斷線路路由資訊，由系統軟體程式化。Function 本身不使用此值。使用 interrupt pin 的 Function 必須實作。"},
        }
    },
    "interrupt_pin": {
        "section": "7.5.1.1.13", "offset": "3Dh", "page": 694,
        "bits": {
            "7:0": {"name": "Interrupt Pin", "attr": "RO", "desc": "識別 Function 使用的傳統中斷 Message：00h=無，01h=INTA，02h=INTB，03h=INTC，04h=INTD。單一 Function 裝置只能使用 INTA。"},
        }
    },
    "bar_type0": {
        "section": "7.5.1.2.1", "offset": "10h", "page": 696,
        "bits": {
            "0":    {"name": "Memory/IO Space Indicator", "attr": "RO",  "desc": "0b=Memory Space BAR；1b=I/O Space BAR。"},
            "2:1":  {"name": "Memory Type",               "attr": "RO",  "desc": "00b=32-bit BAR；10b=64-bit BAR（下一個 BAR 為高 32 bits）；01b/11b=保留。僅 Memory BAR 有效。"},
            "3":    {"name": "Prefetchable",               "attr": "RO",  "desc": "1b=可預取（無讀取副作用，支援寫入合併）；0b=不可預取。僅 Memory BAR 有效。"},
            "31:4": {"name": "Base Address",               "attr": "RW",  "desc": "Memory 基礎位址高位。寫全 1 後讀回可判斷所需空間大小（2 的冪次，最小 128 bytes）。"},
        }
    },
    "expansion_rom": {
        "section": "7.5.1.2.4", "offset": "30h", "page": 700,
        "bits": {
            "0":     {"name": "Expansion ROM Enable",             "attr": "RW/RO",    "desc": "控制 Function 是否接受 Expansion ROM 存取。0b=停用；1b=啟用地址解碼。Command Register 的 Memory Space Enable 優先。預設 0b。"},
            "3:1":   {"name": "Expansion ROM Validation Status",  "attr": "HwInit/ROS","desc": "硬體驗證 Expansion ROM 內容的狀態：000b=不支援，001b=驗證中，010b=通過，011b=通過且可信任，100b=失敗（無效），101b=失敗（有效但不可信任）。Sticky，僅 Fundamental Reset 後重置。"},
            "10:8":  {"name": "Reserved",                         "attr": "RsvdP",     "desc": "保留。"},
            "31:11": {"name": "Expansion ROM Base Address",        "attr": "RW/RO",    "desc": "Expansion ROM 起始 Memory 位址高 21 bits。寫全 1 後讀回可判斷所需大小（最大 16 MB）。"},
        }
    },
    "bridge_control": {
        "section": "7.5.1.3.13", "offset": "3Eh", "page": 709,
        "bits": {
            "0":    {"name": "Parity Error Response Enable",      "attr": "RW",    "desc": "控制 Secondary Status Register 中 Master Data Parity Error 的記錄。預設 0b。"},
            "1":    {"name": "SERR# Enable",                      "attr": "RW",    "desc": "控制 ERR_COR/NONFATAL/FATAL 從 Secondary 轉發至 Primary 介面。預設 0b。"},
            "2":    {"name": "ISA Enable",                        "attr": "RW",    "desc": "0b=轉發範圍內所有 I/O 位址至下游；1b=僅轉發 ISA I/O（每 1KB 上層 768 bytes）至上游。預設 0b。"},
            "3":    {"name": "VGA Enable",                        "attr": "RW",    "desc": "Set 時，不論 I/O/Memory 範圍為何，將 VGA 位址從 Primary 轉發至 Secondary。預設 0b。"},
            "4":    {"name": "VGA 16-bit Decode",                 "attr": "RW",    "desc": "VGA Enable=Set 時有效：0b=10-bit VGA I/O 解碼；1b=16-bit VGA I/O 解碼。預設 0b。"},
            "5":    {"name": "Master Abort Mode",                 "attr": "RO",    "desc": "不適用於 PCI Express，必須 hardwired to 0b。"},
            "6":    {"name": "Secondary Bus Reset",               "attr": "RW",    "desc": "置 1 觸發對應 PCI Express Port 的 Hot Reset。軟體須確保最小重置持續時間（Trst）。預設 0b。"},
            "11:7": {"name": "Legacy bits (hardwired 0)",         "attr": "RO",    "desc": "前版規範定義的欄位，不適用於 PCI Express，必須 hardwired to 0b。"},
            "15:12":{"name": "Reserved",                          "attr": "RsvdP", "desc": "保留。"},
        }
    },

    # ── 7.5.2 Power Management ───────────────────────────────────────────────
    "pm_capabilities": {
        "section": "7.5.2.1", "offset": "00h", "page": 712,
        "bits": {
            "7:0":   {"name": "Capability ID",                       "attr": "RO",  "desc": "固定為 01h，識別此為 PCI Power Management Capability。"},
            "15:8":  {"name": "Next Capability Pointer",             "attr": "RO",  "desc": "指向下一個 Capability 項目；無更多項目時為 00h。"},
            "18:16": {"name": "Version",                             "attr": "RO",  "desc": "必須 hardwired to 011b（符合本規範的 Function）。"},
            "19":    {"name": "PME Clock",                           "attr": "RO",  "desc": "不適用於 PCI Express，必須 hardwired to 0b。"},
            "20":    {"name": "Immediate Readiness on Return to D0", "attr": "RO",  "desc": "Set 表示 Function 從 D3hot 轉換至 D0 後立即可回應，軟體免除所有延遲要求（含 10ms 延遲）。"},
            "21":    {"name": "Device Specific Initialization",      "attr": "RO",  "desc": "Set 表示 Function 在轉至 D0 uninitalized 狀態後需要裝置特定初始化序列。"},
            "24:22": {"name": "Aux_Current",                         "attr": "RO",  "desc": "Vaux 輔助電源電流需求：000b=0mA，001b=55mA，010b=100mA，011b=160mA，100b=220mA，101b=270mA，110b=320mA，111b=375mA。"},
            "25":    {"name": "D1_Support",                          "attr": "RO",  "desc": "Set 表示支援 D1 Power Management State。"},
            "26":    {"name": "D2_Support",                          "attr": "RO",  "desc": "Set 表示支援 D2 Power Management State。"},
            "31:27": {"name": "PME_Support",                         "attr": "RO",  "desc": "5-bit 向量：bit27=D0，bit28=D1，bit29=D2，bit30=D3hot，bit31=D3cold。各 bit Set 表示可從該狀態產生 PME。bit31 需要輔助電源。"},
        }
    },
    "pmcsr": {
        "section": "7.5.2.2", "offset": "04h", "page": 714,
        "bits": {
            "1:0":   {"name": "PowerState",       "attr": "RW",      "desc": "決定/設定 Function 的目前電源狀態：00b=D0，01b=D1，10b=D2，11b=D3hot。寫入不支援的狀態會被靜默丟棄，狀態不變。預設 00b。"},
            "2":     {"name": "Reserved",          "attr": "RsvdP",   "desc": "保留。"},
            "3":     {"name": "No_Soft_Reset",     "attr": "RO",      "desc": "Set 表示從 D3hot 轉至 D0 時保留內部 Function 狀態（D0 Active，無需額外軟體介入）。Clear 表示內部狀態未定義。"},
            "7:4":   {"name": "Reserved",          "attr": "RsvdP",   "desc": "保留。"},
            "8":     {"name": "PME_En",            "attr": "RW/RWS",  "desc": "Set 時允許 Function 產生 PME。Clear 時停用。若 D3cold PME 被支援則為 RWS（Sticky，不受 Conventional Reset 或 FLR 影響）。"},
            "12:9":  {"name": "Data_Select",       "attr": "RW",      "desc": "選擇透過 Data 暫存器和 Data_Scale 欄位回報的資料。Data 暫存器未實作時 hardwired to 0000b。預設 0000b。"},
            "14:13": {"name": "Data_Scale",        "attr": "RO",      "desc": "Data 暫存器值的縮放因子，依 Data_Select 值而異。Data 暫存器未實作時 hardwired to 00b。"},
            "15":    {"name": "PME_Status",        "attr": "RW1CS",   "desc": "Function 處於可產生 PME 的條件時由硬體 Set。不受 PME_En 影響。Sticky（若支援 D3cold PME 且輔助電源可用）。"},
            "21:16": {"name": "Reserved",          "attr": "RsvdP",   "desc": "保留。"},
            "23:22": {"name": "Undefined",         "attr": "RO",      "desc": "前版規範定義，軟體應忽略讀取值。"},
        }
    },

    # ── 7.5.3 Slot / Root registers ──────────────────────────────────────────
    "slot_capabilities": {
        "section": "7.5.3.9", "offset": "14h", "page": 744,
        "bits": {
            "0":     {"name": "Attention Button Present",           "attr": "HwInit",    "desc": "Set 表示此 Slot 的 Attention Button 由 chassis 電性控制。"},
            "1":     {"name": "Power Controller Present",           "attr": "HwInit",    "desc": "Set 表示此 Slot/Adapter 有軟體可程式化的 Power Controller。"},
            "2":     {"name": "MRL Sensor Present",                 "attr": "HwInit",    "desc": "Set 表示此 Slot 的 chassis 上有 MRL Sensor。"},
            "3":     {"name": "Attention Indicator Present",        "attr": "HwInit",    "desc": "Set 表示 Attention Indicator 由 chassis 電性控制。"},
            "4":     {"name": "Power Indicator Present",            "attr": "HwInit",    "desc": "Set 表示 Power Indicator 由 chassis 電性控制。"},
            "5":     {"name": "Hot-Plug Surprise",                  "attr": "HwInit",    "desc": "Set 表示此 Slot 的 Adapter 可能無任何預先通知即被移除。若 SFI HPS Suppress=Set 則讀回 0b。"},
            "6":     {"name": "Hot-Plug Capable",                   "attr": "HwInit",    "desc": "Set 表示此 Slot 支援 Hot-Plug 操作。"},
            "14:7":  {"name": "Slot Power Limit Value",             "attr": "HwInit",    "desc": "配合 Slot Power Limit Scale 指定 Slot 供電上限（Watts）。>EFh 有特殊編碼：F0h=250W，F1h=275W，F2h=300W。"},
            "16:15": {"name": "Slot Power Limit Scale",             "attr": "HwInit",    "desc": "Slot Power Limit Value 的縮放因子：00b=1.0x，01b=0.1x，10b=0.01x，11b=0.001x。"},
            "17":    {"name": "Electromechanical Interlock Present","attr": "HwInit",    "desc": "Set 表示 chassis 上此 Slot 有 Electromechanical Interlock。"},
            "18":    {"name": "No Command Completed Support",       "attr": "HwInit",    "desc": "Set 表示 Hot-Plug Controller 完成命令時不產生軟體通知。"},
            "31:19": {"name": "Physical Slot Number",               "attr": "HwInit",    "desc": "此 Port 對應的實體 Slot 編號，在 chassis 內須唯一。整合於系統板或同矽晶片的設備須初始化為 0。"},
        }
    },
    "slot_control": {
        "section": "7.5.3.10", "offset": "18h", "page": 745,
        "bits": {
            "0":    {"name": "Attention Button Pressed Enable",       "attr": "RW",    "desc": "Set 時 Attention Button 按下事件產生軟體通知。預設 0b。"},
            "1":    {"name": "Power Fault Detected Enable",           "attr": "RW",    "desc": "Set 時 Power Fault 事件產生軟體通知。預設 0b。"},
            "2":    {"name": "MRL Sensor Changed Enable",             "attr": "RW",    "desc": "Set 時 MRL Sensor 狀態改變事件產生軟體通知。預設 0b。"},
            "3":    {"name": "Presence Detect Changed Enable",        "attr": "RW",    "desc": "Set 時 Presence Detect 狀態改變事件產生軟體通知。預設 0b。"},
            "4":    {"name": "Command Completed Interrupt Enable",    "attr": "RW",    "desc": "No Command Completed Support=0b 時，Set 使 Hot-Plug 命令完成產生通知。預設 0b。"},
            "5":    {"name": "Hot-Plug Interrupt Enable",             "attr": "RW",    "desc": "Set 時 enabled Hot-Plug 事件產生 interrupt。預設 0b。"},
            "7:6":  {"name": "Attention Indicator Control",           "attr": "RW",    "desc": "00b=Reserved，01b=On，10b=Blink，11b=Off。"},
            "9:8":  {"name": "Power Indicator Control",               "attr": "RW",    "desc": "00b=Reserved，01b=On，10b=Blink，11b=Off。"},
            "10":   {"name": "Power Controller Control",              "attr": "RW",    "desc": "0b=Power On，1b=Power Off。"},
            "11":   {"name": "Electromechanical Interlock Control",   "attr": "RW",    "desc": "寫入 1b 切換 Electromechanical Interlock 狀態；讀取永遠返回 0b。"},
            "12":   {"name": "Data Link Layer State Changed Enable",  "attr": "RW",    "desc": "DL Link Active Reporting Capable=1b 時，Set 使 DLL Link Active 改變產生軟體通知。預設 0b。"},
            "13":   {"name": "Auto Slot Power Limit Disable",         "attr": "RW",    "desc": "Set 時停用 Link 從 non-DL_Up 轉 DL_Up 時自動發送 Set_Slot_Power_Limit Message。"},
            "14":   {"name": "In-Band PD Disable",                    "attr": "RW",    "desc": "Set 時停用 in-band presence detect 對 Presence Detect State 的影響，改為僅回報 out-of-band presence detect。預設 0b。"},
            "15":   {"name": "Reserved",                              "attr": "RsvdP", "desc": "保留。"},
        }
    },
    "slot_status": {
        "section": "7.5.3.11", "offset": "1Ah", "page": 748,
        "bits": {
            "0":    {"name": "Attention Button Pressed",         "attr": "RW1C",  "desc": "Attention Button 按下時 Set。"},
            "1":    {"name": "Power Fault Detected",            "attr": "RW1C",  "desc": "Power Controller 偵測到 Power Fault 時 Set。"},
            "2":    {"name": "MRL Sensor Changed",              "attr": "RW1C",  "desc": "偵測到 MRL Sensor State 改變時 Set。"},
            "3":    {"name": "Presence Detect Changed",         "attr": "RW1C",  "desc": "Presence Detect State 改變時 Set。"},
            "4":    {"name": "Command Completed",               "attr": "RW1C",  "desc": "Hot-Plug 命令完成且 Hot-Plug Controller 準備好接受下一個命令時 Set。不支援時 hardwired to 0b。"},
            "5":    {"name": "MRL Sensor State",                "attr": "RO",    "desc": "0b=MRL Closed，1b=MRL Open。"},
            "6":    {"name": "Presence Detect State",           "attr": "RO",    "desc": "0b=Adapter not Present，1b=Adapter Present。In-Band PD Disable=0 時為 in-band 與 out-of-band 的邏輯 OR。"},
            "7":    {"name": "Electromechanical Interlock Status","attr": "RO",  "desc": "0b=Disengaged，1b=Engaged。"},
            "8":    {"name": "Data Link Layer State Changed",   "attr": "RW1C",  "desc": "DLL Link Active 改變時 Set。"},
            "15:9": {"name": "Reserved",                        "attr": "RsvdP", "desc": "保留。"},
        }
    },
    "root_control": {
        "section": "7.5.3.12", "offset": "1Ch", "page": 750,
        "bits": {
            "0":    {"name": "System Error on Correctable Error Enable", "attr": "RW",    "desc": "Set 時，Hierarchy Domain 內任何設備回報 ERR_COR 即產生 System Error。預設 0b。"},
            "1":    {"name": "System Error on Non-Fatal Error Enable",   "attr": "RW",    "desc": "Set 時，Hierarchy Domain 內任何設備回報 ERR_NONFATAL 即產生 System Error。預設 0b。"},
            "2":    {"name": "System Error on Fatal Error Enable",       "attr": "RW",    "desc": "Set 時，Hierarchy Domain 內任何設備回報 ERR_FATAL 即產生 System Error。預設 0b。"},
            "3":    {"name": "PME Interrupt Enable",                     "attr": "RW",    "desc": "Set 時，收到 PME Message 即產生 PME interrupt。預設 0b。"},
            "4":    {"name": "CRS Software Visibility Enable",           "attr": "RW",    "desc": "Set 時，Root Port 將 CRS Completion Status 返回給軟體。不支援時 hardwired to 0b。預設 0b。"},
            "15:5": {"name": "Reserved",                                 "attr": "RsvdP", "desc": "保留。"},
        }
    },
    "root_capabilities": {
        "section": "7.5.3.13", "offset": "1Eh", "page": 752,
        "bits": {
            "0":    {"name": "CRS Software Visibility", "attr": "RO",    "desc": "Set 表示 Root Port 支援將 CRS Completion Status 返回給軟體。"},
            "15:1": {"name": "Reserved",                "attr": "RsvdP", "desc": "保留。"},
        }
    },
    "root_status": {
        "section": "7.5.3.14", "offset": "20h", "page": 752,
        "bits": {
            "15:0": {"name": "PME Requester ID", "attr": "RO",    "desc": "最後一個 PME Requester 的 PCI Requester ID；只有 PME Status=Set 時才有效。"},
            "16":   {"name": "PME Status",       "attr": "RW1C",  "desc": "PME Requester 已 assert PME 時 Set；軟體寫入 1b 清除；後續 PME 保持 pending 直到被清除。預設 0b。"},
            "17":   {"name": "PME Pending",      "attr": "RO",    "desc": "PME Status=Set 時若有另一個 PME pending 則 Set；PME Status 被清除後硬體重新 Set PME Status 遞送 pending PME。"},
            "31:18":{"name": "Reserved",         "attr": "RsvdZ", "desc": "保留（讀取為 0）。"},
        }
    },
    "device_status_2": {
        "section": "7.5.3.17", "offset": "2Ah", "page": 761,
        "bits": {
            "15:0": {"name": "Reserved", "attr": "RsvdZ", "desc": "Placeholder 暫存器，目前無任何 capability 需要此暫存器。整個暫存器視為 RsvdZ。"},
        }
    },
    "slot_capabilities_2": {
        "section": "7.5.3.21", "offset": "34h", "page": 771,
        "bits": {
            "0":    {"name": "In-Band PD Disable Supported", "attr": "HwInit", "desc": "Set 表示此 Slot 支援停用 in-band presence detect（由 Slot Control 的 In-Band PD Disable bit 控制）。若 Slot 無 out-of-band presence detect 機制則須為 Clear。"},
            "15:1": {"name": "Reserved",                     "attr": "RsvdP",  "desc": "保留。"},
        }
    },
    "slot_control_2": {
        "section": "7.5.3.22", "offset": "38h", "page": 771,
        "bits": {
            "15:0": {"name": "Reserved", "attr": "RsvdP", "desc": "Placeholder 暫存器，整個暫存器視為 RsvdP。"},
        }
    },
    "slot_status_2": {
        "section": "7.5.3.23", "offset": "3Ah", "page": 771,
        "bits": {
            "15:0": {"name": "Reserved", "attr": "RsvdZ", "desc": "Placeholder 暫存器，整個暫存器視為 RsvdZ。"},
        }
    },

    # ── 7.7 MSI / MSI-X ──────────────────────────────────────────────────────
    "msi_message_control": {
        "section": "7.7.1.2", "offset": "02h", "page": 776,
        "bits": {
            "0":     {"name": "MSI Enable",                    "attr": "RW",    "desc": "Set 且 MSI-X Enable=Clear 時，Function 使用 MSI 請求服務並禁止 INTx。預設 0b。"},
            "3:1":   {"name": "Multiple Message Capable",      "attr": "RO",    "desc": "Function 請求的 MSI 向量數（2 的冪次）：000b=1，001b=2，010b=4，011b=8，100b=16，101b=32。"},
            "6:4":   {"name": "Multiple Message Enable",       "attr": "RW",    "desc": "軟體分配的向量數（≤請求數）：000b=1，001b=2，010b=4，011b=8，100b=16，101b=32。預設 000b。"},
            "7":     {"name": "64-bit Address Capable",        "attr": "RO",    "desc": "Set 表示支援 64-bit Message Address。PCIe Endpoint 必須 Set。"},
            "8":     {"name": "Per-Vector Masking Capable",    "attr": "RO",    "desc": "Set 表示支援 MSI Per-Vector Masking。SR-IOV 的 PF/VF 必須 Set。"},
            "9":     {"name": "Extended Message Data Capable", "attr": "RO",    "desc": "Set 表示支援 Extended Message Data。"},
            "10":    {"name": "Extended Message Data Enable",  "attr": "RW/RO", "desc": "Set 時啟用 Extended Message Data。Extended Message Data Capable=Set 時為 RW，否則 hardwired to 0b。預設 0b。"},
            "15:11": {"name": "Reserved",                      "attr": "RsvdP", "desc": "保留。"},
        }
    },
    "msi_message_address": {
        "section": "7.7.1.3", "offset": "04h", "page": 778,
        "bits": {
            "1:0":  {"name": "Reserved",        "attr": "RsvdP", "desc": "確保 DWORD 對齊，讀取永遠返回 0，寫入無效。"},
            "31:2": {"name": "Message Address", "attr": "RW",    "desc": "系統指定的 MSI 訊息目標位址（DWORD 對齊）。MSI Enable=Set 時有效。"},
        }
    },
    "msi_message_data": {
        "section": "7.7.1.5", "offset": "08h or 0Ch", "page": 779,
        "bits": {
            "15:0": {"name": "Message Data", "attr": "RW", "desc": "系統指定的 MSI 訊息資料（16-bit）。Multiple Message Enable 決定 Function 可修改哪些低位 bits 來產生分配的向量。"},
        }
    },
    "msi_mask_bits": {
        "section": "7.7.1.7", "offset": "0Ch or 10h", "page": 780,
        "bits": {
            "31:0": {"name": "Mask Bits", "attr": "RW", "desc": "每個 Set 的 Mask bit 禁止 Function 發送對應向量的訊息。僅 Per-Vector Masking Capable=Set 時存在。offset 依 64-bit Address Capable 而定。預設 0。"},
        }
    },
    "msix_message_control": {
        "section": "7.7.2.2", "offset": "02h", "page": 784,
        "bits": {
            "10:0":  {"name": "Table Size",    "attr": "RO",    "desc": "MSI-X Table 大小 N，以 N-1 編碼。例如 0000000011b 表示 Table Size=4。"},
            "13:11": {"name": "Reserved",      "attr": "RsvdP", "desc": "保留。"},
            "14":    {"name": "Function Mask", "attr": "RW",    "desc": "Set 時屏蔽 Function 所有 MSI-X 向量（不論個別 Mask bit）。Clear 時由 per-vector Mask bit 決定。預設 0b。"},
            "15":    {"name": "MSI-X Enable",  "attr": "RW",    "desc": "Set 且 MSI Enable=Clear 時，Function 使用 MSI-X 請求服務並禁止 INTx。預設 0b。"},
        }
    },

    # ── 7.7.3 Secondary PCIe ─────────────────────────────────────────────────
    "link_control_3": {
        "section": "7.7.3.2", "offset": "04h", "page": 792,
        "bits": {
            "0":   {"name": "Perform Equalization",                   "attr": "RW/RsvdP", "desc": "Downstream Port（及 Crosslink 支援的 Upstream Port）：置 1 且配合 Retrain Link 可執行 8.0GT/s+ Link Equalization。預設 0b。"},
            "1":   {"name": "Link Equalization Request Interrupt Enable","attr": "RW/RsvdP","desc": "Set 時，Link Equalization Request bit（8.0/16.0/32.0 GT/s）被設置時產生中斷。Upstream Port 無 Crosslink 支援時為 RsvdP。預設 0b。"},
            "8:2": {"name": "Enable Lower SKP OS Generation Vector",  "attr": "RW/RsvdP", "desc": "7-bit 向量。Link 在 L0 且 Current Link Speed 對應 bit=Set 時，以 SRNS 速率排程 SKP OS。Bit0=2.5GT/s，Bit1=5GT/s，Bit2=8GT/s，Bit3=16GT/s，Bit4=32GT/s。預設 000_0000b。"},
        }
    },
    "lane_error_status": {
        "section": "7.7.3.3", "offset": "08h", "page": 793,
        "bits": {
            "31:0": {"name": "Lane Error Status Bits", "attr": "RW1CS", "desc": "32-bit 向量，每個 bit 對應一個 Lane。1b=該 Lane 偵測到 Lane-based 錯誤。未使用的高位 bit（>Maximum Link Width）為 RsvdZ。預設 0b。"},
        }
    },

    # ── 7.7.4 Data Link Feature ──────────────────────────────────────────────
    "data_link_feature_cap": {
        "section": "7.7.4.2", "offset": "04h", "page": 798,
        "bits": {
            "0":    {"name": "Local Scaled Flow Control Supported",   "attr": "HwInit", "desc": "Set 表示此 Port 支援 Scaled Flow Control。"},
            "22:1": {"name": "Reserved",                              "attr": "RsvdP",  "desc": "保留。"},
            "30:23":{"name": "Reserved",                              "attr": "RsvdP",  "desc": "保留。"},
            "31":   {"name": "Data Link Feature Exchange Enable",     "attr": "HwInit", "desc": "Set 時此 Port 進入 DL_Feature 協商狀態。預設 1b。"},
        }
    },
    "data_link_feature_status": {
        "section": "7.7.4.3", "offset": "08h", "page": 798,
        "bits": {
            "0":    {"name": "Remote Scaled Flow Control Supported",  "attr": "RO",    "desc": "Set 表示遠端 Port 支援 Scaled Flow Control。DL_Inactive 時清除。預設 0b。"},
            "22:1": {"name": "Reserved",                              "attr": "RsvdZ", "desc": "保留。"},
            "30:23":{"name": "Reserved",                              "attr": "RsvdZ", "desc": "保留。"},
            "31":   {"name": "Remote Data Link Feature Supported Valid","attr": "RO",  "desc": "Set 表示已在 DL_Feature 狀態收到 Data Link Feature DLLP，Remote Data Link Feature Supported 欄位有效。DL_Inactive 時清除。預設 0b。"},
        }
    },

    # ── 7.7.5 Physical Layer 16.0 GT/s ───────────────────────────────────────
    "phy16_status": {
        "section": "7.7.5.4", "offset": "0Ch", "page": 802,
        "bits": {
            "0":    {"name": "Equalization 16.0 GT/s Complete",          "attr": "ROS/RsvdZ",  "desc": "Set 表示 16.0GT/s TX Equalization 程序已完成。Multi-Function Upstream Port 中僅 Function 0 實作，其餘為 RsvdZ。預設 0b。"},
            "1":    {"name": "Equalization 16.0 GT/s Phase 1 Successful","attr": "ROS/RsvdZ",  "desc": "Phase 1 成功完成。預設 0b。"},
            "2":    {"name": "Equalization 16.0 GT/s Phase 2 Successful","attr": "ROS/RsvdZ",  "desc": "Phase 2 成功完成。預設 0b。"},
            "3":    {"name": "Equalization 16.0 GT/s Phase 3 Successful","attr": "ROS/RsvdZ",  "desc": "Phase 3 成功完成。預設 0b。"},
            "4":    {"name": "Link Equalization Request 16.0 GT/s",      "attr": "RW1CS/RsvdZ","desc": "硬體設置以請求執行 16.0GT/s Link Equalization。預設 0b。"},
            "31:5": {"name": "Reserved",                                  "attr": "RsvdZ",      "desc": "保留。"},
        }
    },

    # ── 7.7.6 Physical Layer 32.0 GT/s ───────────────────────────────────────
    "phy32_capabilities": {
        "section": "7.7.6.2", "offset": "04h", "page": 808,
        "bits": {
            "0":    {"name": "Equalization Bypass to Highest Rate Supported","attr": "HwInit", "desc": "Set 表示支援控制是否跳過中間速率的 Equalization，直接協商到最高共同支援速率。支援 32.0GT/s 的 Port 必須 Set。"},
            "1":    {"name": "No Equalization Needed Supported",            "attr": "HwInit", "desc": "Set 表示支援控制是否需要 Equalization。"},
            "7:2":  {"name": "Reserved",                                    "attr": "RsvdP",  "desc": "保留。"},
            "8":    {"name": "Modified TS Usage Mode 0 (PCIe) Supported",  "attr": "RO",     "desc": "PCI Express 用途（Usage 000b）。必須為 1b。"},
            "9":    {"name": "Modified TS Usage Mode 1 (Training Set Message) Supported","attr": "HwInit","desc": "Set 表示支援傳送/接收廠商特定 Training Set Messages（Usage 001b）。"},
            "10":   {"name": "Modified TS Usage Mode 2 (Alternate Protocol) Supported","attr": "HwInit","desc": "Set 表示支援協商使用替代協議（Usage 010b）。"},
            "15:11":{"name": "Reserved Modified TS Usage Modes",            "attr": "RO",     "desc": "PCI-SIG 保留的未來用途模式。必須為 0_0000b。"},
            "31:16":{"name": "Reserved",                                    "attr": "RsvdP",  "desc": "保留。"},
        }
    },
    "phy32_control": {
        "section": "7.7.6.3", "offset": "08h", "page": 809,
        "bits": {
            "0":    {"name": "Equalization Bypass to Highest Rate Disable","attr": "RWS/RO",   "desc": "Clear 時，Port 在 Link Training 時指示希望跳過中間速率直接訓練到最高共同速率。Equalization Bypass to Highest Rate Supported=Set 時為 RWS，預設 0b。"},
            "1":    {"name": "No Equalization Needed Disable",             "attr": "RWS/RO",   "desc": "Clear 時 Port 可表示不需要 Equalization；Set 時 Port 必須一律表示需要 Equalization。No Equalization Needed Supported=Set 時為 RWS，預設 0b。"},
            "7:2":  {"name": "Reserved",                                   "attr": "RsvdP",    "desc": "保留。"},
            "10:8": {"name": "Modified TS Usage Mode Selected",            "attr": "RWS/RsvdP","desc": "Downstream Port 下次 Link 進入 L0 時使用的 Usage Mode。未定義行為若選擇不支援的模式。Downstream Port 實作；Upstream Port 為 RsvdP。預設 000b。"},
            "31:11":{"name": "Reserved",                                   "attr": "RsvdP",    "desc": "保留。"},
        }
    },
    "phy32_status": {
        "section": "7.7.6.4", "offset": "0Ch", "page": 810,
        "bits": {
            "0":    {"name": "Equalization 32.0 GT/s Complete",          "attr": "ROS/RsvdZ",  "desc": "Set 表示 32.0GT/s TX Equalization 程序已完成。Multi-Function Upstream Port 中僅 Function 0 實作。預設 0b。"},
            "1":    {"name": "Equalization 32.0 GT/s Phase 1 Successful","attr": "ROS/RsvdZ",  "desc": "Phase 1 成功完成。預設 0b。"},
            "2":    {"name": "Equalization 32.0 GT/s Phase 2 Successful","attr": "ROS/RsvdZ",  "desc": "Phase 2 成功完成。預設 0b。"},
            "3":    {"name": "Equalization 32.0 GT/s Phase 3 Successful","attr": "ROS/RsvdZ",  "desc": "Phase 3 成功完成。預設 0b。"},
            "4":    {"name": "Link Equalization Request 32.0 GT/s",      "attr": "RW1CS/RsvdZ","desc": "硬體設置以請求執行 32.0GT/s Link Equalization。預設 0b。"},
            "5":    {"name": "Modified TS Received",                      "attr": "RO",         "desc": "Set 表示 Received Modified TS Data 1/2 暫存器含有效資料。Link Down 時清除。預設 0b。"},
            "7:6":  {"name": "Received Enhanced Link Behavior Control",  "attr": "RO",         "desc": "最近收到的 TS1/TS2 中的 Enhanced Link Behavior Control bits。DL_Down 時清除。預設 00b。"},
            "8":    {"name": "Transmitter Precoding On",                  "attr": "RO",         "desc": "Receiver 要求此 Transmitter 啟用 Precoding 時 Set。DL_Down 時清除。預設 0b。"},
            "9":    {"name": "Transmitter Precode Request",               "attr": "RO",         "desc": "Set 時此 Port 在 Recovery.Speed 前設置 TS1s/TS2s 中的 Transmitter Precode Request bit 以請求 Transmitter 使用 Precoding。"},
            "10":   {"name": "No Equalization Needed Received",           "attr": "RO",         "desc": "Set 表示收到的 Modified TS1/TS2 中 No Equalization Needed bit=Set，或收到含此編碼的 non-modified TS1/TS2。預設 0b。"},
            "31:11":{"name": "Reserved",                                  "attr": "RsvdZ",      "desc": "保留。"},
        }
    },

    # ── 7.7.7 Lane Margining ─────────────────────────────────────────────────
    "margining_port_cap": {
        "section": "7.7.7.2", "offset": "04h", "page": 819,
        "bits": {
            "0":    {"name": "Margining uses Driver Software", "attr": "HwInit", "desc": "Set 表示 Margining 部分由裝置驅動程式軟體實作；Margining Software Ready 指示軟體何時初始化完成。Clear 表示不需要驅動程式軟體。"},
            "15:1": {"name": "Reserved",                       "attr": "RsvdP",  "desc": "保留。"},
        }
    },
    "margining_port_status": {
        "section": "7.7.7.3", "offset": "06h", "page": 820,
        "bits": {
            "0":    {"name": "Margining Ready",          "attr": "RO",    "desc": "Set 表示 Margining 功能已準備好接受 Margining 命令。Margining uses Driver Software=Set 時，須在 Margining Software Ready=Set 後最晚 100ms 內 Set。"},
            "1":    {"name": "Margining Software Ready", "attr": "RO",    "desc": "Margining uses Driver Software=Set 時，表示所需軟體已完成必要初始化。Margining uses Driver Software=Clear 時值未定義。"},
            "15:2": {"name": "Reserved",                 "attr": "RsvdZ", "desc": "保留。"},
        }
    },
    "margining_lane_control": {
        "section": "7.7.7.4", "offset": "08h", "page": 820,
        "bits": {
            "2:0":  {"name": "Receiver Number",  "attr": "RW",    "desc": "Receiver Number 欄位，見 §8.4.4。DL_Down 時重置為預設值。預設 000b。"},
            "5:3":  {"name": "Margin Type",      "attr": "RW",    "desc": "Margin Type 欄位，見 §8.4.4。DL_Down 時重置。預設 111b。"},
            "6":    {"name": "Usage Model",      "attr": "RW",    "desc": "Usage Model 欄位，見 §8.4.4。DL_Down 時重置。預設 0b。"},
            "7":    {"name": "Reserved",         "attr": "RsvdP", "desc": "保留。"},
            "15:8": {"name": "Margin Payload",   "attr": "RW",    "desc": "Margin Payload 欄位，配合 Margin Type 使用，見 §8.4.4。DL_Down 時重置。預設 9Ch。"},
        }
    },

    # ── 7.7.8 ACS ────────────────────────────────────────────────────────────
    "acs_capability": {
        "section": "7.7.8.2", "offset": "04h", "page": 824,
        "bits": {
            "0":    {"name": "ACS Source Validation",      "attr": "RO", "desc": "Set 表示元件實作 ACS Source Validation。Root Ports 和 Switch Downstream Ports 必須實作；其他 hardwired to 0b。"},
            "1":    {"name": "ACS Translation Blocking",   "attr": "RO", "desc": "Set 表示元件實作 ACS Translation Blocking。Root Ports 和 Switch Downstream Ports 必須實作；其他 hardwired to 0b。"},
            "2":    {"name": "ACS P2P Request Redirect",   "attr": "RO", "desc": "Set 表示元件實作 ACS P2P Request Redirect。Root Ports（支援 P2P）、Switch Downstream Ports、支援 P2P 的 Multi-Function Functions 需實作。"},
            "3":    {"name": "ACS P2P Completion Redirect","attr": "RO", "desc": "Set 表示元件實作 ACS P2P Completion Redirect。所有支援 ACS P2P Request Redirect 的 Functions 需實作。"},
            "4":    {"name": "ACS Upstream Forwarding",    "attr": "RO", "desc": "Set 表示元件實作 ACS Upstream Forwarding。支援 Redirected Request Validation 的 Root Ports 及 Switch Downstream Ports 需實作。"},
            "5":    {"name": "ACS P2P Egress Control",     "attr": "RO", "desc": "Set 表示元件實作 ACS P2P Egress Control（可選）。"},
            "6":    {"name": "ACS Direct Translated P2P",  "attr": "RO", "desc": "Set 表示元件實作 ACS Direct Translated P2P。具 ATS 且支援 P2P 的 Root Ports、Switch Downstream Ports、Multi-Function Functions 需實作。"},
            "7":    {"name": "ACS Enhanced Capability",    "attr": "RO", "desc": "Set 表示元件支援 ACS Enhanced Capability 機制（I/O Request Blocking、DSP/USP Memory Target Access、Unclaimed Request Redirect）。"},
            "15:8": {"name": "Egress Control Vector Size", "attr": "HwInit", "desc": "Egress Control Vector 中適用 bit 的數量：01h~FFh=直接表示數量；00h=256 bits。ACS P2P Egress Control=0b 時值未定義。"},
        }
    },
    "acs_control": {
        "section": "7.7.8.3", "offset": "06h", "page": 825,
        "bits": {
            "0":    {"name": "ACS Source Validation Enable",     "attr": "RW",      "desc": "Set 時，元件驗證 Upstream Requests 的 Requester ID Bus Number 是否在 Secondary/Subordinate Bus Number 範圍內。預設 0b。"},
            "1":    {"name": "ACS Translation Blocking Enable",  "attr": "RW",      "desc": "Set 時，阻擋所有 AT 欄位非預設值的 Upstream Memory Requests。預設 0b。"},
            "2":    {"name": "ACS P2P Request Redirect Enable",  "attr": "RW",      "desc": "配合 P2P Egress Control 和 Direct Translated P2P，決定何時將 P2P Requests 重導至上游。預設 0b。"},
            "3":    {"name": "ACS P2P Completion Redirect Enable","attr": "RW",     "desc": "決定何時將 P2P Completions（Relaxed Ordering Attribute=Clear）重導至上游。預設 0b。"},
            "4":    {"name": "ACS Upstream Forwarding Enable",   "attr": "RW",      "desc": "Set 時，將下游元件重導至上游的 Requests/Completions 轉發至上游。預設 0b。"},
            "5":    {"name": "ACS P2P Egress Control Enable",    "attr": "RW",      "desc": "配合 Egress Control Vector 決定是否允許/阻擋/重導 P2P Requests。預設 0b。"},
            "6":    {"name": "ACS Direct Translated P2P Enable", "attr": "RW",      "desc": "Set 時，AT=Translated 的 P2P Memory Requests 不受 P2P Request Redirect 和 P2P Egress Control 影響（ACS Translation Blocking Enable=Set 時忽略）。預設 0b。"},
            "7":    {"name": "ACS I/O Request Blocking Enable",  "attr": "RW/RsvdP","desc": "Set 時，Downstream Port 收到的 Upstream I/O Requests 視為 ACS Violation。ACS Enhanced Capability=Set 的 Root Ports 和 Switch Downstream Ports 需實作。預設 0b。"},
            "9:8":  {"name": "ACS DSP Memory Target Access Control","attr": "RW/RsvdP","desc": "控制 Downstream Port 如何處理以 Root Port/Switch Downstream Port Memory BAR 為目標的 Upstream Memory Requests：00b=允許直接存取，01b=阻擋，10b=重導，11b=保留。預設 00b。"},
            "11:10":{"name": "ACS USP Memory Target Access Control","attr": "RW/RsvdP","desc": "控制 Switch Downstream Port 如何處理以 Switch Upstream Port Memory BAR 為目標的 Upstream Memory Requests。編碼同上。預設 00b。"},
            "12":   {"name": "ACS Unclaimed Request Redirect Control","attr": "RW/RsvdP","desc": "Set 時，Switch Downstream Port 將在 Upstream Port 孔徑內但未被任何 Downstream Port 聲明的 Requests 轉發至上游；Clear 時視為 UR。Switch Downstream Ports 若 ACS Enhanced Capability=Set 需實作。預設 0b。"},
            "15:13":{"name": "Reserved",                         "attr": "RsvdP",   "desc": "保留。"},
        }
    },

    # ── 7.8.2 LTR ────────────────────────────────────────────────────────────
    "ltr_max_snoop_latency": {
        "section": "7.8.2.2", "offset": "04h", "page": 834,
        "bits": {
            "9:0":   {"name": "Max Snoop LatencyValue", "attr": "RW",    "desc": "最大 Snoop 延遲值，與 LatencyScale 合併決定最大允許 Snoop 延遲（見 §6.18）。預設 0。"},
            "12:10": {"name": "Max Snoop LatencyScale", "attr": "RW",    "desc": "對 Max Snoop LatencyValue 的比例，編碼與 LTR Message LatencyScale 相同。預設 000b。"},
            "15:13": {"name": "Reserved",               "attr": "RsvdP", "desc": "保留。"},
        }
    },
    "ltr_max_nosnoop_latency": {
        "section": "7.8.2.3", "offset": "06h", "page": 835,
        "bits": {
            "9:0":   {"name": "Max No-Snoop LatencyValue", "attr": "RW",    "desc": "最大 No-Snoop 延遲值，與 LatencyScale 合併決定最大允許 No-Snoop 延遲。預設 0。"},
            "12:10": {"name": "Max No-Snoop LatencyScale", "attr": "RW",    "desc": "對 Max No-Snoop LatencyValue 的比例，編碼與 LTR Message LatencyScale 相同。預設 000b。"},
            "15:13": {"name": "Reserved",                  "attr": "RsvdP", "desc": "保留。"},
        }
    },

    # ── 7.8.3 L1 PM Substates ────────────────────────────────────────────────
    "l1pm_capabilities": {
        "section": "7.8.3.2", "offset": "04h", "page": 837,
        "bits": {
            "0":     {"name": "PCI-PM L1.2 Supported",         "attr": "HwInit",     "desc": "Set 表示支援 PCI-PM L1.2。"},
            "1":     {"name": "PCI-PM L1.1 Supported",         "attr": "HwInit",     "desc": "Set 表示支援 PCI-PM L1.1。所有實作 L1 PM Substates 的 Port 必須 Set。"},
            "2":     {"name": "ASPM L1.2 Supported",           "attr": "HwInit",     "desc": "Set 表示支援 ASPM L1.2。"},
            "3":     {"name": "ASPM L1.1 Supported",           "attr": "HwInit",     "desc": "Set 表示支援 ASPM L1.1。"},
            "4":     {"name": "L1 PM Substates Supported",     "attr": "HwInit",     "desc": "Set 表示此 Port 支援 L1 PM Substates。"},
            "5":     {"name": "Link Activation Supported",     "attr": "HwInit/RsvdP","desc": "Downstream Port: Set 表示支援 Link Activation（§5.5.6）。Upstream Port 為 RsvdP。"},
            "7:6":   {"name": "Reserved",                      "attr": "RsvdP",      "desc": "保留。"},
            "15:8":  {"name": "Port Common_Mode_Restore_Time", "attr": "HwInit/RsvdP","desc": "此 Port 重建 common mode 所需的時間（μs，見 Table 5-11）。支援 L1.2 的 Port 需實作，否則為 RsvdP。"},
            "17:16": {"name": "Port T_POWER_ON Scale",         "attr": "HwInit/RsvdP","desc": "T_POWER_ON Value 的比例：00b=2μs，01b=10μs，10b=100μs，11b=保留。支援 L1.2 的 Port 需實作。預設 00b。"},
            "18":    {"name": "Reserved",                      "attr": "RsvdP",      "desc": "保留。"},
            "23:19": {"name": "Port T_POWER_ON Value",         "attr": "HwInit/RsvdP","desc": "與 Port T_POWER_ON Scale 共同決定對端 Port 在 L1.2.Exit 後驅動介面前需等待的時間。預設 00101b。"},
            "31:24": {"name": "Reserved",                      "attr": "RsvdP",      "desc": "保留。"},
        }
    },
    "l1pm_control_1": {
        "section": "7.8.3.3", "offset": "08h", "page": 838,
        "bits": {
            "0":     {"name": "PCI-PM L1.2 Enable",              "attr": "RW",      "desc": "Set 啟用 PCI-PM L1.2。預設 0b。"},
            "1":     {"name": "PCI-PM L1.1 Enable",              "attr": "RW",      "desc": "Set 啟用 PCI-PM L1.1。預設 0b。"},
            "2":     {"name": "ASPM L1.2 Enable",                "attr": "RW",      "desc": "Set 啟用 ASPM L1.2。預設 0b。"},
            "3":     {"name": "ASPM L1.1 Enable",                "attr": "RW",      "desc": "Set 啟用 ASPM L1.1。預設 0b。"},
            "4":     {"name": "Link Activation Interrupt Enable", "attr": "RW/RsvdP","desc": "Set 時 Link Activation 完成後產生中斷。Downstream Port Link Activation Supported=Set 時需實作；Upstream Port 為 RsvdP。預設 0b。"},
            "5":     {"name": "Link Activation Control",         "attr": "RW/RsvdP","desc": "Set 使 Port 啟動 Link Activation 程序（§5.5.6）。Downstream Port 需實作；Upstream Port 為 RsvdP。預設 0b。"},
            "7:6":   {"name": "Reserved",                        "attr": "RsvdP",   "desc": "保留。"},
            "15:8":  {"name": "Common_Mode_Restore_Time",        "attr": "RW/RsvdP","desc": "設定 Downstream Port 重建 common mode 的 T_COMMONMODE（μs，見 Table 5-11）。ASPM/PCI-PM L1.2 Enable=Set 時不得修改。Upstream Port 為 RsvdP。"},
            "25:16": {"name": "LTR_L1.2_THRESHOLD_Value",        "attr": "RW/RsvdP","desc": "與 LTR_L1.2_THRESHOLD_Scale 共同決定 L1 進入 L1.1/L1.2 的 LTR 門檻值。支援 ASPM L1.2 的 Port 需實作。預設 00_0000_0000b。"},
            "28:26": {"name": "Reserved",                        "attr": "RsvdP",   "desc": "保留。"},
            "31:29": {"name": "LTR_L1.2_THRESHOLD_Scale",        "attr": "RW/RsvdP","desc": "LTR_L1.2_THRESHOLD_Value 的比例，編碼與 LTR Message LatencyScale 相同（§6.18）。預設 000b。"},
        }
    },
    "l1pm_control_2": {
        "section": "7.8.3.4", "offset": "0Ch", "page": 840,
        "bits": {
            "1:0":  {"name": "T_POWER_ON Scale", "attr": "RW/RsvdP","desc": "T_POWER_ON Value 的比例：00b=2μs，01b=10μs，10b=100μs，11b=保留。支援 L1.2 的 Port 需實作。預設 00b。"},
            "2":    {"name": "Reserved",          "attr": "RsvdP",   "desc": "保留。"},
            "7:3":  {"name": "T_POWER_ON Value",  "attr": "RW/RsvdP","desc": "與 T_POWER_ON Scale 共同設定 Port 在 L1.2.Exit 後驅動介面前的最小等待時間。預設 00101b。"},
            "31:8": {"name": "Reserved",          "attr": "RsvdP",   "desc": "保留。"},
        }
    },

    # ── 7.8.4 AER ────────────────────────────────────────────────────────────
    "aer_uncorrectable_status": {
        "section": "7.8.4.2", "offset": "04h", "page": 843,
        "bits": {
            "0":     {"name": "Undefined (Link Training Error)",         "attr": "RW",    "desc": "前版規範用於 Link Training Error，現在值未定義。軟體應忽略讀取值。"},
            "3:1":   {"name": "Reserved",                                "attr": "RsvdZ", "desc": "保留（讀取為 0）。"},
            "4":     {"name": "Data Link Protocol Error Status",         "attr": "RW1CS", "desc": "Data Link Protocol Error 狀態。預設 0b。"},
            "5":     {"name": "Surprise Down Error Status",              "attr": "RW1CS", "desc": "（Optional）Surprise Down Error 狀態。預設 0b。"},
            "11:6":  {"name": "Reserved",                                "attr": "RsvdZ", "desc": "保留（讀取為 0）。"},
            "12":    {"name": "Poisoned TLP Received Status",            "attr": "RW1CS", "desc": "收到 Poisoned TLP 的狀態。預設 0b。"},
            "13":    {"name": "Flow Control Protocol Error Status",      "attr": "RW1CS", "desc": "（Optional）Flow Control Protocol Error 狀態。預設 0b。"},
            "14":    {"name": "Completion Timeout Status",               "attr": "RW1CS", "desc": "Completion Timeout 狀態。預設 0b。"},
            "15":    {"name": "Completer Abort Status",                  "attr": "RW1CS", "desc": "（Optional）Completer Abort 狀態。預設 0b。"},
            "16":    {"name": "Unexpected Completion Status",            "attr": "RW1CS", "desc": "Unexpected Completion 狀態。預設 0b。"},
            "17":    {"name": "Receiver Overflow Status",                "attr": "RW1CS", "desc": "（Optional）Receiver Overflow 狀態。預設 0b。"},
            "18":    {"name": "Malformed TLP Status",                    "attr": "RW1CS", "desc": "Malformed TLP 狀態。預設 0b。"},
            "19":    {"name": "ECRC Error Status",                       "attr": "RW1CS", "desc": "（Optional）ECRC Error 狀態。預設 0b。"},
            "20":    {"name": "Unsupported Request Error Status",        "attr": "RW1CS", "desc": "Unsupported Request Error 狀態。預設 0b。"},
            "21":    {"name": "ACS Violation Status",                    "attr": "RW1CS", "desc": "（Optional）ACS Violation 狀態。預設 0b。"},
            "22":    {"name": "Uncorrectable Internal Error Status",     "attr": "RW1CS", "desc": "（Optional）Uncorrectable Internal Error 狀態。預設 0b。"},
            "23":    {"name": "MC Blocked TLP Status",                   "attr": "RW1CS", "desc": "（Optional）MC Blocked TLP 狀態。預設 0b。"},
            "24":    {"name": "AtomicOp Egress Blocked Status",          "attr": "RW1CS", "desc": "（Optional）AtomicOp Egress Blocked 狀態。預設 0b。"},
            "25":    {"name": "TLP Prefix Blocked Error Status",         "attr": "RW1CS", "desc": "（Optional）TLP Prefix Blocked Error 狀態。預設 0b。"},
            "26":    {"name": "Poisoned TLP Egress Blocked Status",      "attr": "RW1CS", "desc": "（Optional）Poisoned TLP Egress Blocked 狀態。預設 0b。"},
            "31:27": {"name": "Reserved",                                "attr": "RsvdZ", "desc": "保留（讀取為 0）。"},
        }
    },
    "aer_uncorrectable_mask": {
        "section": "7.8.4.3", "offset": "08h", "page": 845,
        "bits": {
            "0":     {"name": "Undefined Mask",                          "attr": "RW",    "desc": "前版規範用於 Link Training Error mask，現值未定義。軟體只應寫入 1b。"},
            "3:1":   {"name": "Reserved",                                "attr": "RsvdP", "desc": "保留。"},
            "4":     {"name": "Data Link Protocol Error Mask",           "attr": "RWS",   "desc": "遮罩 Data Link Protocol Error 回報。預設 0b。"},
            "5":     {"name": "Surprise Down Error Mask",                "attr": "RWS",   "desc": "（Optional）遮罩 Surprise Down Error 回報。預設 0b。"},
            "11:6":  {"name": "Reserved",                                "attr": "RsvdP", "desc": "保留。"},
            "12":    {"name": "Poisoned TLP Received Mask",              "attr": "RWS",   "desc": "遮罩 Poisoned TLP Received 回報。預設 0b。"},
            "13":    {"name": "Flow Control Protocol Error Mask",        "attr": "RWS",   "desc": "（Optional）遮罩 Flow Control Protocol Error 回報。預設 0b。"},
            "14":    {"name": "Completion Timeout Mask",                 "attr": "RWS",   "desc": "遮罩 Completion Timeout 回報。預設 0b。"},
            "15":    {"name": "Completer Abort Mask",                    "attr": "RWS",   "desc": "（Optional）遮罩 Completer Abort 回報。預設 0b。"},
            "16":    {"name": "Unexpected Completion Mask",              "attr": "RWS",   "desc": "遮罩 Unexpected Completion 回報。預設 0b。"},
            "17":    {"name": "Receiver Overflow Mask",                  "attr": "RWS",   "desc": "（Optional）遮罩 Receiver Overflow 回報。預設 0b。"},
            "18":    {"name": "Malformed TLP Mask",                      "attr": "RWS",   "desc": "遮罩 Malformed TLP 回報。預設 0b。"},
            "19":    {"name": "ECRC Error Mask",                         "attr": "RWS",   "desc": "（Optional）遮罩 ECRC Error 回報。預設 0b。"},
            "20":    {"name": "Unsupported Request Error Mask",          "attr": "RWS",   "desc": "遮罩 Unsupported Request Error 回報。預設 0b。"},
            "21":    {"name": "ACS Violation Mask",                      "attr": "RWS",   "desc": "（Optional）遮罩 ACS Violation 回報。預設 0b。"},
            "22":    {"name": "Uncorrectable Internal Error Mask",       "attr": "RWS",   "desc": "（Optional）遮罩 Uncorrectable Internal Error 回報。預設 1b。"},
            "23":    {"name": "MC Blocked TLP Mask",                     "attr": "RWS",   "desc": "（Optional）遮罩 MC Blocked TLP 回報。預設 0b。"},
            "24":    {"name": "AtomicOp Egress Blocked Mask",            "attr": "RWS",   "desc": "（Optional）遮罩 AtomicOp Egress Blocked 回報。預設 0b。"},
            "25":    {"name": "TLP Prefix Blocked Error Mask",           "attr": "RWS",   "desc": "（Optional）遮罩 TLP Prefix Blocked Error 回報。預設 0b。"},
            "26":    {"name": "Poisoned TLP Egress Blocked Mask",        "attr": "RWS",   "desc": "（Optional）遮罩 Poisoned TLP Egress Blocked 回報。預設 1b。"},
            "31:27": {"name": "Reserved",                                "attr": "RsvdP", "desc": "保留。"},
        }
    },
    "aer_uncorrectable_severity": {
        "section": "7.8.4.4", "offset": "0Ch", "page": 846,
        "bits": {
            "0":     {"name": "Undefined Severity",                      "attr": "RW",    "desc": "前版規範用於 Link Training Error severity，值未定義。軟體應忽略讀取值。"},
            "3:1":   {"name": "Reserved",                                "attr": "RsvdP", "desc": "保留。"},
            "4":     {"name": "Data Link Protocol Error Severity",       "attr": "RWS",   "desc": "1b=Fatal，0b=Non-Fatal。預設 1b。"},
            "5":     {"name": "Surprise Down Error Severity",            "attr": "RWS",   "desc": "（Optional）1b=Fatal，0b=Non-Fatal。預設 1b。"},
            "11:6":  {"name": "Reserved",                                "attr": "RsvdP", "desc": "保留。"},
            "12":    {"name": "Poisoned TLP Received Severity",          "attr": "RWS",   "desc": "1b=Fatal，0b=Non-Fatal。預設 0b。"},
            "13":    {"name": "Flow Control Protocol Error Severity",    "attr": "RWS",   "desc": "（Optional）1b=Fatal，0b=Non-Fatal。預設 1b。"},
            "14":    {"name": "Completion Timeout Severity",             "attr": "RWS",   "desc": "1b=Fatal，0b=Non-Fatal。預設 0b。"},
            "15":    {"name": "Completer Abort Severity",                "attr": "RWS",   "desc": "（Optional）1b=Fatal，0b=Non-Fatal。預設 0b。"},
            "16":    {"name": "Unexpected Completion Severity",          "attr": "RWS",   "desc": "1b=Fatal，0b=Non-Fatal。預設 0b。"},
            "17":    {"name": "Receiver Overflow Severity",              "attr": "RWS",   "desc": "（Optional）1b=Fatal，0b=Non-Fatal。預設 1b。"},
            "18":    {"name": "Malformed TLP Severity",                  "attr": "RWS",   "desc": "1b=Fatal，0b=Non-Fatal。預設 1b。"},
            "19":    {"name": "ECRC Error Severity",                     "attr": "RWS",   "desc": "（Optional）1b=Fatal，0b=Non-Fatal。預設 0b。"},
            "20":    {"name": "Unsupported Request Error Severity",      "attr": "RWS",   "desc": "1b=Fatal，0b=Non-Fatal。預設 0b。"},
            "21":    {"name": "ACS Violation Severity",                  "attr": "RWS",   "desc": "（Optional）1b=Fatal，0b=Non-Fatal。預設 0b。"},
            "22":    {"name": "Uncorrectable Internal Error Severity",   "attr": "RWS",   "desc": "（Optional）1b=Fatal，0b=Non-Fatal。預設 1b。"},
            "23":    {"name": "MC Blocked TLP Severity",                 "attr": "RWS",   "desc": "（Optional）1b=Fatal，0b=Non-Fatal。預設 0b。"},
            "24":    {"name": "AtomicOp Egress Blocked Severity",        "attr": "RWS",   "desc": "（Optional）1b=Fatal，0b=Non-Fatal。預設 0b。"},
            "25":    {"name": "TLP Prefix Blocked Error Severity",       "attr": "RWS",   "desc": "（Optional）1b=Fatal，0b=Non-Fatal。預設 0b。"},
            "26":    {"name": "Poisoned TLP Egress Blocked Severity",    "attr": "RWS",   "desc": "（Optional）1b=Fatal，0b=Non-Fatal。預設 0b。"},
            "31:27": {"name": "Reserved",                                "attr": "RsvdP", "desc": "保留。"},
        }
    },
    "aer_correctable_status": {
        "section": "7.8.4.5", "offset": "10h", "page": 848,
        "bits": {
            "0":     {"name": "Receiver Error Status",           "attr": "RW1CS",  "desc": "（Optional）Receiver Error 狀態。未實作則為 RsvdZ。預設 0b。"},
            "5:1":   {"name": "Reserved",                        "attr": "RsvdZ",  "desc": "保留（讀取為 0）。"},
            "6":     {"name": "Bad TLP Status",                  "attr": "RW1CS",  "desc": "Bad TLP 狀態。預設 0b。"},
            "7":     {"name": "Bad DLLP Status",                 "attr": "RW1CS",  "desc": "Bad DLLP 狀態。預設 0b。"},
            "8":     {"name": "REPLAY_NUM Rollover Status",      "attr": "RW1CS",  "desc": "REPLAY_NUM Rollover 狀態。預設 0b。"},
            "11:9":  {"name": "Reserved",                        "attr": "RsvdZ",  "desc": "保留（讀取為 0）。"},
            "12":    {"name": "Replay Timer Timeout Status",     "attr": "RW1CS",  "desc": "Replay Timer Timeout 狀態。預設 0b。"},
            "13":    {"name": "Advisory Non-Fatal Error Status", "attr": "RW1CS",  "desc": "Advisory Non-Fatal Error 狀態（預設 mask=1b，見 Correctable Error Mask Register）。預設 0b。"},
            "14":    {"name": "Corrected Internal Error Status", "attr": "RW1CS",  "desc": "（Optional）Corrected Internal Error 狀態。預設 0b。"},
            "15":    {"name": "Header Log Overflow Status",      "attr": "RW1CS",  "desc": "（Optional）Header Log Overflow 狀態。預設 0b。"},
            "31:16": {"name": "Reserved",                        "attr": "RsvdZ",  "desc": "保留（讀取為 0）。"},
        }
    },
    "aer_correctable_mask": {
        "section": "7.8.4.6", "offset": "14h", "page": 849,
        "bits": {
            "0":     {"name": "Receiver Error Mask",              "attr": "RWS",   "desc": "（Optional）遮罩 Receiver Error 回報。未實作則為 RsvdP。預設 0b。"},
            "5:1":   {"name": "Reserved",                         "attr": "RsvdP", "desc": "保留。"},
            "6":     {"name": "Bad TLP Mask",                     "attr": "RWS",   "desc": "遮罩 Bad TLP 回報。預設 0b。"},
            "7":     {"name": "Bad DLLP Mask",                    "attr": "RWS",   "desc": "遮罩 Bad DLLP 回報。預設 0b。"},
            "8":     {"name": "REPLAY_NUM Rollover Mask",         "attr": "RWS",   "desc": "遮罩 REPLAY_NUM Rollover 回報。預設 0b。"},
            "11:9":  {"name": "Reserved",                         "attr": "RsvdP", "desc": "保留。"},
            "12":    {"name": "Replay Timer Timeout Mask",        "attr": "RWS",   "desc": "遮罩 Replay Timer Timeout 回報。預設 0b。"},
            "13":    {"name": "Advisory Non-Fatal Error Mask",    "attr": "RWS",   "desc": "遮罩 Advisory Non-Fatal Error 回報。預設 1b（相容未支援 Role-Based Error Reporting 的軟體）。"},
            "14":    {"name": "Corrected Internal Error Mask",    "attr": "RWS",   "desc": "（Optional）遮罩 Corrected Internal Error 回報。預設 1b。"},
            "15":    {"name": "Header Log Overflow Mask",         "attr": "RWS",   "desc": "（Optional）遮罩 Header Log Overflow 回報。預設 1b。"},
            "31:16": {"name": "Reserved",                         "attr": "RsvdP", "desc": "保留。"},
        }
    },
    "aer_cap_control": {
        "section": "7.8.4.7", "offset": "18h", "page": 850,
        "bits": {
            "4:0":   {"name": "First Error Pointer",                    "attr": "ROS",   "desc": "識別 Uncorrectable Error Status Register 中第一個被回報錯誤的 bit 位置（見 §6.2）。"},
            "5":     {"name": "ECRC Generation Capable",                "attr": "RO",    "desc": "Set 表示 Function 具備產生 ECRC 的能力（§2.7）。"},
            "6":     {"name": "ECRC Generation Enable",                 "attr": "RWS",   "desc": "Set 啟用 ECRC 產生（§2.7）。未實作機制的 Function 可 hardwire to 0b。預設 0b。"},
            "7":     {"name": "ECRC Check Capable",                     "attr": "RO",    "desc": "Set 表示 Function 具備檢查 ECRC 的能力（§2.7）。"},
            "8":     {"name": "ECRC Check Enable",                      "attr": "RWS",   "desc": "Set 啟用 ECRC 檢查（§2.7）。未實作機制的 Function 可 hardwire to 0b。預設 0b。"},
            "9":     {"name": "Multiple Header Recording Capable",      "attr": "RO",    "desc": "Set 表示 Function 具備記錄多個錯誤 Header 的能力（§6.2）。"},
            "10":    {"name": "Multiple Header Recording Enable",       "attr": "RWS",   "desc": "Set 啟用多個錯誤 Header 的記錄功能。預設 0b。"},
            "11":    {"name": "TLP Prefix Log Present",                 "attr": "ROS",   "desc": "Set 且 First Error Pointer 有效時，TLP Prefix Log Register 含有效資料。End-End TLP Prefix Supported=Clear 時為 RsvdP。預設 0b。"},
            "12":    {"name": "Completion Timeout Prefix/Header Log Capable","attr": "RO","desc": "Set 表示 Function 記錄發生 Completion Timeout 的 Request TLP 之 prefix/header。"},
            "31:13": {"name": "Reserved",                               "attr": "RsvdP", "desc": "保留。"},
        }
    },
    "aer_root_error_command": {
        "section": "7.8.4.9", "offset": "2Ch", "page": 851,
        "bits": {
            "0":    {"name": "Correctable Error Reporting Enable",  "attr": "RW",    "desc": "Set 時，Hierarchy Domain 內任何 Function 回報 Correctable Error，Root Port 產生中斷。預設 0b。"},
            "1":    {"name": "Non-Fatal Error Reporting Enable",    "attr": "RW",    "desc": "Set 時，Hierarchy Domain 內任何 Function 回報 Non-Fatal Error，Root Port 產生中斷。預設 0b。"},
            "2":    {"name": "Fatal Error Reporting Enable",        "attr": "RW",    "desc": "Set 時，Hierarchy Domain 內任何 Function 回報 Fatal Error，Root Port 產生中斷。預設 0b。"},
            "31:3": {"name": "Reserved",                            "attr": "RsvdP", "desc": "保留。"},
        }
    },
    "aer_root_error_status": {
        "section": "7.8.4.10", "offset": "30h", "page": 852,
        "bits": {
            "0":     {"name": "ERR_COR Received",                      "attr": "RW1CS", "desc": "收到 Correctable Error Message 且此 bit 尚未 Set 時置 1。預設 0b。"},
            "1":     {"name": "Multiple ERR_COR Received",             "attr": "RW1CS", "desc": "收到 Correctable Error Message 且 ERR_COR Received 已 Set 時置 1。預設 0b。"},
            "2":     {"name": "ERR_FATAL/NONFATAL Received",           "attr": "RW1CS", "desc": "收到 Fatal 或 Non-Fatal Error Message 且此 bit 尚未 Set 時置 1。預設 0b。"},
            "3":     {"name": "Multiple ERR_FATAL/NONFATAL Received",  "attr": "RW1CS", "desc": "收到 Fatal/Non-Fatal Error 且 ERR_FATAL/NONFATAL Received 已 Set 時置 1。預設 0b。"},
            "4":     {"name": "First Uncorrectable Fatal",             "attr": "RW1CS", "desc": "首個收到的 Uncorrectable Error Message 為 Fatal Error 時置 1。預設 0b。"},
            "5":     {"name": "Non-Fatal Error Messages Received",     "attr": "RW1CS", "desc": "收到一個或多個 Non-Fatal Uncorrectable Error Message 時置 1。預設 0b。"},
            "6":     {"name": "Fatal Error Messages Received",         "attr": "RW1CS", "desc": "收到一個或多個 Fatal Uncorrectable Error Message 時置 1。預設 0b。"},
            "8:7":   {"name": "ERR_COR Subclass",                     "attr": "ROS/RsvdZ","desc": "Function 支援 ERR_COR Subclass 且 ERR_COR Received 尚未 Set 時，載入收到的 ERR_COR Message 中的 Subclass 欄位值。不支援時為 RsvdZ。預設 00b。"},
            "26:9":  {"name": "Reserved",                              "attr": "RsvdZ", "desc": "保留（讀取為 0）。"},
            "31:27": {"name": "Advanced Error Interrupt Message Number","attr": "RO",   "desc": "此 Capability 任一 status bit 觸發中斷時使用的 MSI/MSI-X vector 編號。MSI 為相對 base Message Data 的偏移；MSI-X 為 Table entry index（須為前 32 個之一）。"},
        }
    },

    # ── 7.8.8 PASID ──────────────────────────────────────────────────────────
    "pasid_capability": {
        "section": "7.8.8.2", "offset": "04h", "page": 872,
        "bits": {
            "0":    {"name": "Reserved",                      "attr": "RsvdP", "desc": "保留。"},
            "1":    {"name": "Execute Permission Supported",  "attr": "RO",    "desc": "Set 表示 Endpoint 支援傳送含 Execute Requested bit=1 的 TLP。"},
            "2":    {"name": "Privileged Mode Supported",     "attr": "RO",    "desc": "Set 表示 Endpoint 支援 Privileged/Non-Privileged 模式，以及傳送含 Privileged Mode Requested bit=1 的 Request。"},
            "7:3":  {"name": "Reserved",                      "attr": "RsvdP", "desc": "保留。"},
            "12:8": {"name": "Max PASID Width",               "attr": "RO",    "desc": "Endpoint 支援的 PASID 欄位寬度 n，表示支援 PASID 值 0 ~ 2^n-1。值 0=僅支援 PASID(0)；值 20=支援全部 20-bit PASID 值。範圍 0~20。"},
            "15:13":{"name": "Reserved",                      "attr": "RsvdP", "desc": "保留。"},
        }
    },
    "pasid_control": {
        "section": "7.8.8.3", "offset": "06h", "page": 873,
        "bits": {
            "0":    {"name": "PASID Enable",              "attr": "RW",      "desc": "Set 允許 Endpoint 傳送及接收含 PASID TLP Prefix 的 TLP。若 ATS Enable=Set 時更改此 bit，行為未定義。預設 0b。"},
            "1":    {"name": "Execute Permission Enable", "attr": "RW/RsvdP","desc": "Set 允許 Endpoint 傳送 Execute Requested bit=1 的 Request。Execute Permission Supported=Clear 時為 RsvdP。預設 0b。"},
            "2":    {"name": "Privileged Mode Enable",    "attr": "RW/RsvdP","desc": "Set 允許 Endpoint 傳送 Privileged Mode Requested bit=1 的 Request。Privileged Mode Supported=Clear 時為 RsvdP。預設 0b。"},
            "15:3": {"name": "Reserved",                  "attr": "RsvdP",   "desc": "保留。"},
        }
    },

    # ── 7.5.1.3 Type 1 補充暫存器 ──────────────────────────────────────────
    "secondary_status": {
        "section": "7.5.1.3.7", "offset": "1Eh", "page": 706,
        "bits": {
            "4:0":  {"name": "Reserved",                    "attr": "RsvdZ", "desc": "保留，hardwired to 0b。"},
            "7":    {"name": "Fast Back-to-Back Capable",   "attr": "RO",    "desc": "不適用於 PCI Express，hardwired to 0b。"},
            "8":    {"name": "Master Data Parity Error",    "attr": "RW1C",  "desc": "Bridge Control 的 Parity Error Response Enable=Set 時，Secondary Side 收到 Poisoned Completion 或傳送 Poisoned Request 時 Set。預設 0b。"},
            "10:9": {"name": "DEVSEL Timing",               "attr": "RO",    "desc": "不適用於 PCI Express，hardwired to 00b。"},
            "11":   {"name": "Signaled Target Abort",       "attr": "RW1C",  "desc": "Secondary Side 以 Completer Abort 完成請求時 Set。預設 0b。"},
            "12":   {"name": "Received Target Abort",       "attr": "RW1C",  "desc": "Secondary Side 收到 Completer Abort Completion 時 Set。預設 0b。"},
            "13":   {"name": "Received Master Abort",       "attr": "RW1C",  "desc": "Secondary Side 收到 Unsupported Request Completion 時 Set。預設 0b。"},
            "14":   {"name": "Received System Error",       "attr": "RW1C",  "desc": "Secondary Side 收到 ERR_FATAL 或 ERR_NONFATAL Message 時 Set。預設 0b。"},
            "15":   {"name": "Detected Parity Error",       "attr": "RW1C",  "desc": "Secondary Side 收到 Poisoned TLP 時 Set（不受 Parity Error Response Enable 影響）。預設 0b。"},
        }
    },
    "io_base_limit": {
        "section": "7.5.1.3.6", "offset": "1Ch/1Dh", "page": 705,
        "bits": {
            "3:0":   {"name": "I/O Addressing Capability (Base)", "attr": "RO",  "desc": "0h=16-bit I/O addressing，1h=32-bit I/O addressing。"},
            "7:4":   {"name": "I/O Base [15:12]",                 "attr": "RW",  "desc": "I/O Base 位址上 4 bits（Address[15:12]），下 12 bits 假設為 0（4KB 對齊）。不實作 I/O range 的 Bridge 可 hardwired to 0。"},
            "11:8":  {"name": "I/O Addressing Capability (Limit)","attr": "RO",  "desc": "與 Base 相同值，0h=16-bit，1h=32-bit。"},
            "15:12": {"name": "I/O Limit [15:12]",                "attr": "RW",  "desc": "I/O Limit 位址上 4 bits（Address[15:12]），下 12 bits 假設為 FFFh。小於 Base 表示不轉發 I/O。"},
        }
    },

    # ── 7.8.1 Power Budgeting ─────────────────────────────────────────────────
    "power_budgeting_data_select": {
        "section": "7.8.1.2", "offset": "04h", "page": 830,
        "bits": {
            "4:0":  {"name": "Data Select", "attr": "RW",    "desc": "選擇 Power Budgeting Data 暫存器中顯示的 DWORD 索引，從 0 開始，遞增選擇下一個操作條件。預設值未定義。"},
            "31:5": {"name": "Reserved",    "attr": "RsvdP", "desc": "保留。"},
        }
    },
    "power_budgeting_data": {
        "section": "7.8.1.3", "offset": "08h", "page": 831,
        "bits": {
            "7:0":   {"name": "Base Power",   "attr": "RO", "desc": "指定操作條件的基礎功耗（Watts），乘以 Data Scale 得實際值。Data Scale=00b 且 >EFh 時：F0h=≤250W，F1h=≤275W，F2h=≤300W，F3h~FFh=保留(>300W)。"},
            "9:8":   {"name": "Data Scale",   "attr": "RO", "desc": "Base Power 的縮放因子：00b=1.0x，01b=0.1x，10b=0.01x，11b=0.001x。"},
            "12:10": {"name": "PM Sub State", "attr": "RO", "desc": "操作條件的 PM 子狀態：000b=Default Sub State，001b~111b=裝置特定子狀態。"},
            "14:13": {"name": "PM State",     "attr": "RO", "desc": "操作條件的 PM 狀態：00b=D0，01b=D1，10b=D2，11b=D3。"},
            "17:15": {"name": "Type",         "attr": "RO", "desc": "操作條件類型：000b=PME Aux，001b=Auxiliary，010b=Idle，011b=Sustained，100b=Sustained-Emergency，101b=Maximum-Emergency，111b=Maximum。"},
            "20:18": {"name": "Power Rail",   "attr": "RO", "desc": "功耗軌道：000b=Power(12V)，001b=Power(3.3V)，010b=Power(1.5V/1.8V)，111b=Thermal。"},
            "31:21": {"name": "Reserved",     "attr": "RsvdP", "desc": "保留。"},
        }
    },
    "power_budgeting_capability_reg": {
        "section": "7.8.1.4", "offset": "0Ch", "page": 832,
        "bits": {
            "0":    {"name": "System Allocated", "attr": "HwInit", "desc": "Set 表示此裝置的功耗預算已包含在系統功耗預算內。Set 時軟體在做功耗預算決策時應忽略所回報的 Power Budgeting Data。"},
            "31:1": {"name": "Reserved",         "attr": "RsvdP",  "desc": "保留。"},
        }
    },

    # ── 7.8.3 L1 PM Substates Status ─────────────────────────────────────────
    "l1pm_status": {
        "section": "7.8.3.5", "offset": "10h", "page": 841,
        "bits": {
            "0":    {"name": "Link Activation Status", "attr": "RW1C/RsvdZ", "desc": "指示 Link Activation（§5.5.6）的狀態。Downstream Port Link Activation Supported=Set 時需實作；Upstream Port 為 RsvdZ。預設 0b。"},
            "31:1": {"name": "Reserved",               "attr": "RsvdZ",      "desc": "保留，hardwired to 0b。"},
        }
    },

    # ── 7.8.9 FRS Queueing ───────────────────────────────────────────────────
    "frs_queueing_capability": {
        "section": "7.8.9.2", "offset": "04h", "page": 875,
        "bits": {
            "11:0":  {"name": "FRS Queue Max Depth",          "attr": "HwInit", "desc": "實作的佇列深度：001h~FFFh=深度 1~4095；000h=保留。FRS Message Queue Depth 不得超過此值。"},
            "15:12": {"name": "Reserved",                     "attr": "RsvdP",  "desc": "保留。"},
            "20:16": {"name": "FRS Interrupt Message Number", "attr": "RO",     "desc": "FRS Message Received 或 FRS Message Overflow 觸發中斷時使用的 MSI/MSI-X vector 編號。MSI 為相對 base Message Data 的偏移；MSI-X 為 Table entry index（須為前 32 個之一）。"},
            "31:21": {"name": "Reserved",                     "attr": "RsvdP",  "desc": "保留。"},
        }
    },
    "frs_queueing_status": {
        "section": "7.8.9.3", "offset": "08h", "page": 876,
        "bits": {
            "0":    {"name": "FRS Message Received", "attr": "RW1C",  "desc": "收到或產生新的 FRS Message 時 Set。Root Port 在 Link DL_Down 時必須清除此 bit。預設 0b。"},
            "1":    {"name": "FRS Message Overflow",  "attr": "RW1C",  "desc": "FRS Message 佇列已滿且收到或產生新的 FRS Message 時 Set。Root Port 在 Link DL_Down 時必須清除此 bit。預設 0b。"},
            "15:2": {"name": "Reserved",              "attr": "RsvdZ", "desc": "保留，hardwired to 0b。"},
        }
    },
    "frs_queueing_control": {
        "section": "7.8.9.4", "offset": "0Ah", "page": 877,
        "bits": {
            "0":    {"name": "FRS Interrupt Enable", "attr": "RW",    "desc": "Set 且 MSI/MSI-X 啟用時，FRS Message Received 或 FRS Message Overflow 從 0b 轉為 1b 時產生 MSI/MSI-X 中斷。預設 0b。"},
            "15:1": {"name": "Reserved",             "attr": "RsvdP", "desc": "保留。"},
        }
    },
    "frs_message_queue": {
        "section": "7.8.9.5", "offset": "0Ch", "page": 877,
        "bits": {
            "15:0":  {"name": "FRS Message Queue Function ID",  "attr": "RO", "desc": "佇列中最舊 FRS Message 的 Requester ID。FRS Message Queue Depth=000h 時未定義。寫入 byte 0 可從佇列中移除最舊的 FRS Message。"},
            "19:16": {"name": "FRS Message Queue Reason",      "attr": "RO", "desc": "佇列中最舊 FRS Message 的 FRS Reason。FRS Message Queue Depth=000h 時未定義。"},
            "31:20": {"name": "FRS Message Queue Depth",       "attr": "RO", "desc": "佇列中目前的 FRS Message 數量。000h 表示佇列為空。預設 000h。"},
        }
    },

    # ── 7.7.1 MSI Pending Bits ────────────────────────────────────────────────
    "msi_pending_bits": {
        "section": "7.7.1.8", "offset": "10h or 14h", "page": 780,
        "bits": {
            "31:0": {"name": "Pending Bits", "attr": "RO", "desc": "每個 bit 對應一個 MSI 向量。1b 表示對應向量有 PME pending（由硬體 Set，軟體唯讀）。offset 依 64-bit Address Capable 而定。"},
        }
    },

    # ── 7.7.2 MSI-X Table Entry / PBA ────────────────────────────────────────
    "msix_table_message_addr": {
        "section": "7.7.2.5", "offset": "entry+00h", "page": 787,
        "bits": {
            "1:0":  {"name": "Reserved",        "attr": "RsvdP", "desc": "確保 DWORD 對齊（Address[1:0]=00b）。"},
            "31:2": {"name": "Message Address", "attr": "RW",    "desc": "MSI-X Table Entry 的訊息目標位址（32-bit 部分）。"},
        }
    },
    "msix_table_message_upper_addr": {
        "section": "7.7.2.6", "offset": "entry+04h", "page": 787,
        "bits": {
            "31:0": {"name": "Message Upper Address", "attr": "RW", "desc": "MSI-X Table Entry 的訊息目標位址（64-bit 的高 32 bits）。"},
        }
    },
    "msix_table_message_data": {
        "section": "7.7.2.7", "offset": "entry+08h", "page": 788,
        "bits": {
            "31:0": {"name": "Message Data", "attr": "RW", "desc": "MSI-X Table Entry 的訊息資料（32-bit）。低 16 bits 為實際 Message Data；高 16 bits 為保留（實作相依，但 PCIe 只使用低 16 bits）。"},
        }
    },
    "msix_vector_control": {
        "section": "7.7.2.8", "offset": "entry+0Ch", "page": 788,
        "bits": {
            "0":    {"name": "Mask Bit",  "attr": "RW",    "desc": "Set 時此向量被遮罩（Function 不發送對應 MSI-X Message）。預設 1b（所有向量初始遮罩）。"},
            "31:1": {"name": "Reserved",  "attr": "RsvdP", "desc": "保留。"},
        }
    },

    # ── 7.7.3 Secondary PCIe Lane EQ ─────────────────────────────────────────
    "lane_equalization_control": {
        "section": "7.7.3.4", "offset": "0Ch+n*2", "page": 794,
        "bits": {
            "3:0":  {"name": "Downstream Port TX Preset",         "attr": "RW",    "desc": "8.0GT/s 時 Downstream Port Transmitter Preset 設定（P0~P9）。"},
            "6:4":  {"name": "Downstream Port RX Preset Hint",   "attr": "RW",    "desc": "8.0GT/s 時 Downstream Port Receiver Preset Hint（-6dB~0dB）。"},
            "7":    {"name": "Reserved",                          "attr": "RsvdP", "desc": "保留。"},
            "11:8": {"name": "Upstream Port TX Preset",           "attr": "RW",    "desc": "8.0GT/s 時 Upstream Port Transmitter Preset 設定（P0~P9）。"},
            "14:12":{"name": "Upstream Port RX Preset Hint",     "attr": "RW",    "desc": "8.0GT/s 時 Upstream Port Receiver Preset Hint（-6dB~0dB）。"},
            "15":   {"name": "Reserved",                          "attr": "RsvdP", "desc": "保留。"},
        }
    },

    # ── 7.7.5 16GT/s Parity / Lane EQ ────────────────────────────────────────
    "phy16_local_parity_status": {
        "section": "7.7.5.5", "offset": "10h", "page": 803,
        "bits": {
            "31:0": {"name": "Lane N Local Data Parity Mismatch Status", "attr": "RW1CS/RsvdZ",
                     "desc": "每個 bit 對應一個 Lane（bit[0]=Lane 0）。1b 表示該 Lane 的本地 16GT/s Data Parity 不匹配。Maximum Link Width 以上的 bits 為 RsvdZ。預設 0b。"},
        }
    },
    "phy16_first_retimer_parity": {
        "section": "7.7.5.6", "offset": "14h", "page": 803,
        "bits": {
            "31:0": {"name": "Lane N First Retimer Data Parity Mismatch Status", "attr": "RW1CS/RsvdZ",
                     "desc": "每個 bit 對應一個 Lane。1b 表示該 Lane 的 First Retimer 16GT/s Data Parity 不匹配。Maximum Link Width 以上的 bits 為 RsvdZ。預設 0b。"},
        }
    },
    "phy16_second_retimer_parity": {
        "section": "7.7.5.7", "offset": "18h", "page": 804,
        "bits": {
            "31:0": {"name": "Lane N Second Retimer Data Parity Mismatch Status", "attr": "RW1CS/RsvdZ",
                     "desc": "每個 bit 對應一個 Lane。1b 表示該 Lane 的 Second Retimer 16GT/s Data Parity 不匹配。Maximum Link Width 以上的 bits 為 RsvdZ。預設 0b。"},
        }
    },
    "phy16_lane_eq_control": {
        "section": "7.7.5.9", "offset": "20h-3Ch", "page": 805,
        "bits": {
            "3:0":  {"name": "Downstream Port TX Preset",  "attr": "RW",    "desc": "16GT/s Downstream Port Transmitter Preset（P0~P10）。每 byte 對應一個 Lane，每個 DWORD 包含 4 個 Lane。"},
            "7:4":  {"name": "Upstream Port TX Preset",    "attr": "RW",    "desc": "16GT/s Upstream Port Transmitter Preset（P0~P10）。"},
            "15:8": {"name": "Next Lane (DP TX Preset)",   "attr": "RW",    "desc": "下一個 Lane 的 Downstream Port TX Preset。"},
            "23:16":{"name": "Next Lane (USP TX Preset)",  "attr": "RW",    "desc": "下一個 Lane 的 Upstream Port TX Preset。"},
            "31:24":{"name": "Reserved",                   "attr": "RsvdP", "desc": "保留。"},
        }
    },

    # ── 7.7.6 32GT/s Modified TS / Lane EQ ────────────────────────────────────
    "received_modified_ts_data1": {
        "section": "7.7.6.5", "offset": "10h", "page": 811,
        "bits": {
            "2:0":  {"name": "Modified TS Usage Mode",  "attr": "RO", "desc": "收到的 Modified TS1/TS2 中的 Usage Mode 欄位（Symbol 6 bits[2:0]）。DL_Down 時清除。"},
            "15:3": {"name": "Modified TS Info1",       "attr": "RO", "desc": "收到的 Modified TS 中的 Info1 欄位（Symbols 7~9 的相關 bits）。DL_Down 時清除。"},
            "31:16":{"name": "Modified TS Vendor ID",   "attr": "RO", "desc": "收到的 Modified TS 中的 Vendor ID（Symbols 10~11）。DL_Down 時清除。"},
        }
    },
    "received_modified_ts_data2": {
        "section": "7.7.6.6", "offset": "14h", "page": 812,
        "bits": {
            "23:0": {"name": "Modified TS Info2",              "attr": "RO",    "desc": "收到的 Modified TS 中的 Info2 欄位（Symbols 12~14）。DL_Down 時清除。"},
            "25:24":{"name": "Alt Protocol Negotiation Status","attr": "RO",    "desc": "Alternate Protocol 協商狀態，見 §4.2.6.3。DL_Down 時清除。"},
            "31:26":{"name": "Reserved",                       "attr": "RsvdP", "desc": "保留。"},
        }
    },
    "transmitted_modified_ts_data1": {
        "section": "7.7.6.7", "offset": "18h", "page": 813,
        "bits": {
            "2:0":  {"name": "Modified TS Usage Mode (TX)", "attr": "RW",    "desc": "傳送的 Modified TS1/TS2 中的 Usage Mode 欄位（Symbol 6 bits[2:0]），與 Downstream Port 的 Modified TS Usage Mode Selected 一致。"},
            "15:3": {"name": "Modified TS Info1 (TX)",      "attr": "RW",    "desc": "傳送的 Modified TS 中的 Info1 欄位（Symbols 7~9 相關 bits）。"},
            "31:16":{"name": "Modified TS Vendor ID (TX)",  "attr": "RW",    "desc": "傳送的 Modified TS 中的 Vendor ID（Symbols 10~11）。"},
        }
    },
    "transmitted_modified_ts_data2": {
        "section": "7.7.6.8", "offset": "1Ch", "page": 814,
        "bits": {
            "23:0": {"name": "Modified TS Info2 (TX)",              "attr": "RW",    "desc": "傳送的 Modified TS 中的 Info2 欄位（Symbols 12~14）。"},
            "25:24":{"name": "Alt Protocol Negotiation Status (TX)","attr": "RW",    "desc": "傳送的 Modified TS 中的 Alternate Protocol 協商狀態，見 §4.2.6.3。"},
            "31:26":{"name": "Reserved",                            "attr": "RsvdP", "desc": "保留。"},
        }
    },
    "phy32_lane_eq_control": {
        "section": "7.7.6.9", "offset": "20h+", "page": 815,
        "bits": {
            "3:0":  {"name": "Downstream Port TX Preset",  "attr": "RW", "desc": "32GT/s Downstream Port Transmitter Preset（P0~P10）。每 byte 對應一個 Lane，佈局同 16GT/s Lane EQ Control。"},
            "7:4":  {"name": "Upstream Port TX Preset",    "attr": "RW", "desc": "32GT/s Upstream Port Transmitter Preset（P0~P10）。"},
            "15:8": {"name": "Next Lane Presets",          "attr": "RW", "desc": "下一個 Lane 的 DP/USP TX Preset（同樣每 byte 一個 Lane）。"},
            "31:24":{"name": "Next+1 Lane Presets",        "attr": "RW", "desc": "再下一個 Lane 的 DP/USP TX Preset。"},
        }
    },

    # ── 7.7.7 Margining Lane Status ───────────────────────────────────────────
    "margining_lane_status": {
        "section": "7.7.7.5", "offset": "0Ah+n*4", "page": 821,
        "bits": {
            "2:0":  {"name": "Receiver Number Status", "attr": "RO",    "desc": "Margining 執行的 Receiver Number 回報值，對應 Lane Control 的 Receiver Number 欄位。DL_Down 時重置。"},
            "5:3":  {"name": "Margin Type Status",     "attr": "RO",    "desc": "Margining 執行的 Margin Type 回報值，對應 Lane Control 的 Margin Type 欄位。DL_Down 時重置。"},
            "6":    {"name": "Usage Model Status",     "attr": "RO",    "desc": "Margining 執行的 Usage Model 回報值。DL_Down 時重置。"},
            "7":    {"name": "Reserved",               "attr": "RsvdZ", "desc": "保留。"},
            "15:8": {"name": "Margin Payload Status",  "attr": "RO",    "desc": "Margining 執行的 Margin Payload 回報值。DL_Down 時重置。預設 9Ch（與 Lane Control Margin Payload 預設值相同）。"},
        }
    },

    # ── 7.8.4 AER Error Source ID ─────────────────────────────────────────────
    "aer_error_source_id": {
        "section": "7.8.4.11", "offset": "34h", "page": 854,
        "bits": {
            "15:0":  {"name": "ERR_COR Source ID",           "attr": "RO", "desc": "最近一次 ERR_COR Message 的 Source ID（Requester ID）。ERR_COR Received 被清除後硬體會重新 Set（如有 pending ERR_COR）。"},
            "31:16": {"name": "ERR_FATAL/NONFATAL Source ID","attr": "RO", "desc": "最近一次 ERR_FATAL/ERR_NONFATAL Message 的 Source ID（Requester ID）。"},
        }
    },

    # ── 7.9.1 VC Registers ────────────────────────────────────────────────────
    "vc_port_capability_1": {
        "section": "7.9.1.2", "offset": "04h", "page": 891,
        "bits": {
            "2:0":  {"name": "Extended VC Count",                "attr": "RO",    "desc": "此 Port 支援的 Extended Virtual Channels 數量（不含 VC0）。最大值為 6（7 個 VC 總計）。"},
            "3":    {"name": "Reserved",                         "attr": "RsvdP", "desc": "保留。"},
            "6:4":  {"name": "Low Priority Extended VC Count",   "attr": "RO",    "desc": "Extended VCs 中低優先權的數量（從最高 VC ID 算起），須 ≤ Extended VC Count。"},
            "7":    {"name": "Reserved",                         "attr": "RsvdP", "desc": "保留。"},
            "9:8":  {"name": "Reference Clock",                  "attr": "RO",    "desc": "00b=100ns 參考時脈。其他值保留。"},
            "11:10":{"name": "Port Arbitration Table Entry Size","attr": "RO",    "desc": "Port Arbitration Table entry 大小：00b=1 bit，01b=2 bits，10b=4 bits，11b=8 bits。"},
            "31:12":{"name": "Reserved",                         "attr": "RsvdP", "desc": "保留。"},
        }
    },
    "vc_port_capability_2": {
        "section": "7.9.1.3", "offset": "08h", "page": 892,
        "bits": {
            "7:0":  {"name": "VC Arbitration Capability",    "attr": "RO",    "desc": "支援的 VC Arbitration 機制 bitmap：bit0=Hardware Fixed，bit1=WRR 32-phase，bit2=WRR 64-phase，bit3=WRR 128-phase，bit7:4=廠商特定。"},
            "23:8": {"name": "Reserved",                     "attr": "RsvdP", "desc": "保留。"},
            "31:24":{"name": "VC Arbitration Table Offset",  "attr": "RO",    "desc": "VC Arbitration Table 相對於 Extended Capability Header 起始位置的 QWORD（8 bytes）偏移量。0=無 VC Arbitration Table。"},
        }
    },
    "vc_port_control": {
        "section": "7.9.1.4", "offset": "0Ch", "page": 893,
        "bits": {
            "0":    {"name": "Load VC Arbitration Table",   "attr": "RW",    "desc": "寫入 1b 通知 Port 從 VC Arbitration Table 更新 VC 仲裁器。讀取永遠返回 0b。"},
            "3:1":  {"name": "VC Arbitration Select",       "attr": "RW",    "desc": "選擇 VC Arbitration 機制：000b=Hardware Fixed，001b=WRR 32-phase，010b=WRR 64-phase，011b=WRR 128-phase，111b~100b=廠商特定。"},
            "31:4": {"name": "Reserved",                    "attr": "RsvdP", "desc": "保留。"},
        }
    },
    "vc_port_status": {
        "section": "7.9.1.5", "offset": "0Eh", "page": 894,
        "bits": {
            "0":    {"name": "VC Arbitration Table Status", "attr": "RO",    "desc": "Set 表示 VC 仲裁器尚未更新完成（Load VC Arbitration Table 後）；Clear 表示更新完成。"},
            "15:1": {"name": "Reserved",                   "attr": "RsvdZ", "desc": "保留（讀取為 0）。"},
        }
    },
    "vc_resource_capability": {
        "section": "7.9.1.6", "offset": "10h+n*12", "page": 894,
        "bits": {
            "7:0":  {"name": "Port Arbitration Capability",  "attr": "RO",    "desc": "此 VC 支援的 Port Arbitration 機制 bitmap：bit0=Hardware Fixed，bit1=WRR 32-phase，bit2=WRR 64-phase，bit3=WRR 128-phase，bit4=Time-based WRR 128-phase，bit5=WRR 256-phase，bit7:6=廠商特定。"},
            "13:8": {"name": "Reserved",                     "attr": "RsvdP", "desc": "保留。"},
            "14":   {"name": "Undefined",                    "attr": "RO",    "desc": "前版規範的 Advanced Packet Switching 欄位，現已廢棄，值未定義。"},
            "15":   {"name": "Reject Snoop Transactions",    "attr": "RO",    "desc": "Set 表示非 Snoop 的 Transactions 若 Maximum Time Slots 大於 0 時，可在此 VC 中被拒絕。"},
            "22:16":{"name": "Maximum Time Slots",           "attr": "RO",    "desc": "此 VC 支援的 Time-based WRR 最大 Time Slots 數量減 1。"},
            "31:24":{"name": "Port Arbitration Table Offset","attr": "RO",    "desc": "此 VC 的 Port Arbitration Table 相對於 Extended Capability Header 起始位置的 QWORD 偏移量。0=無 Port Arbitration Table。"},
        }
    },
    "vc_resource_control": {
        "section": "7.9.1.7", "offset": "14h+n*12", "page": 896,
        "bits": {
            "7:0":  {"name": "TC/VC Map",                     "attr": "RW",    "desc": "映射到此 VC 的 Traffic Classes bitmap（bit N=TC N）。VC0 必須至少映射 TC0；同一 TC 不得映射到多個 VC。預設 VC0=FFh，其他=00h。"},
            "15:8": {"name": "Reserved",                      "attr": "RsvdP", "desc": "保留。"},
            "16":   {"name": "Load Port Arbitration Table",   "attr": "RW",    "desc": "寫入 1b 通知 Port 從 Port Arbitration Table 更新此 VC 的仲裁器。讀取永遠返回 0b。"},
            "19:17":{"name": "Port Arbitration Select",       "attr": "RW",    "desc": "選擇此 VC 的 Port Arbitration 機制，編碼同 Port Arbitration Capability bitmap 的位元位置。"},
            "23:20":{"name": "Reserved",                      "attr": "RsvdP", "desc": "保留。"},
            "26:24":{"name": "VC ID",                         "attr": "HwInit","desc": "此 VC Resource 的識別符（0~7）。VC0 必須為 0，其他 VC 的 ID 由硬體決定。"},
            "30:27":{"name": "Reserved",                      "attr": "RsvdP", "desc": "保留。"},
            "31":   {"name": "VC Enable",                     "attr": "RW",    "desc": "Set 時啟用此 VC。VC0 永遠啟用（hardwired to 1b）。其他 VC 預設 0b。"},
        }
    },
    "vc_resource_status": {
        "section": "7.9.1.8", "offset": "18h+n*12", "page": 897,
        "bits": {
            "0":    {"name": "Port Arbitration Table Status", "attr": "RO",    "desc": "Set 表示 Port 仲裁器尚未從 Port Arbitration Table 更新完成；Clear 表示更新完成。"},
            "1":    {"name": "VC Negotiation Pending",        "attr": "RO",    "desc": "Set 表示此 VC 的協商尚未完成（VC Enable 寫入後）；Clear 表示 VC 已啟用並可正常使用。"},
            "15:2": {"name": "Reserved",                      "attr": "RsvdZ", "desc": "保留（讀取為 0）。"},
        }
    },

    # ── 7.9.15 DPC Registers ─────────────────────────────────────────────────
    "dpc_capability": {
        "section": "7.9.15.2", "offset": "04h", "page": 954,
        "bits": {
            "4:0":  {"name": "DPC Interrupt Message Number",          "attr": "RO",    "desc": "DPC 中斷使用的 MSI/MSI-X vector 編號。MSI=相對 base Message Data 的偏移；MSI-X=Table entry index（須為前 32 個之一）。"},
            "5":    {"name": "RP Extensions for DPC",                 "attr": "RO",    "desc": "Set 表示 Root Port 支援 DPC RP 特定擴充功能。Switch Downstream Port 不得 Set。"},
            "6":    {"name": "Poisoned TLP Egress Blocking Supported","attr": "RO",    "desc": "Root Port/Switch Downstream Port 可阻擋 Poisoned TLP 從 Egress Port 傳出時 Set。RP Extensions for DPC=Set 時必須 Set。"},
            "7":    {"name": "DPC Software Triggering Supported",     "attr": "RO",    "desc": "Set 表示支援軟體觸發 DPC。RP Extensions for DPC=Set 時必須 Set。"},
            "11:8": {"name": "RP PIO Log Size",                       "attr": "RO",    "desc": "RP PIO log 暫存器（Header Log + ImpSpec Log + TLP Prefix Log）的 DWORD 數量。RP Extensions 支援時 ≥ 4；否則為 0。"},
            "12":   {"name": "DL_Active ERR_COR Signaling Supported", "attr": "RO",    "desc": "Set 表示支援 Link 轉為 DL_Active 時傳送 ERR_COR。RP Extensions for DPC=Set 時必須 Set。"},
            "15:13":{"name": "Reserved",                              "attr": "RsvdP", "desc": "保留。"},
        }
    },
    "dpc_control": {
        "section": "7.9.15.3", "offset": "06h", "page": 955,
        "bits": {
            "1:0":  {"name": "DPC Trigger Enable",                   "attr": "RW",      "desc": "00b=停用；01b=Unmasked uncorrectable error 或 ERR_FATAL 觸發；10b=Unmasked uncorrectable error 或 ERR_NONFATAL/ERR_FATAL 觸發；11b=保留。預設 00b。"},
            "2":    {"name": "DPC Completion Control",               "attr": "RW",      "desc": "0b=以 Completer Abort (CA) 完成 Requests；1b=以 Unsupported Request (UR) 完成。預設 0b。"},
            "3":    {"name": "DPC Interrupt Enable",                 "attr": "RW",      "desc": "Set 時 DPC 觸發後產生中斷。預設 0b。"},
            "4":    {"name": "DPC ERR_COR Enable",                   "attr": "RW",      "desc": "Set 時 DPC 觸發後傳送 ERR_COR Message。預設 0b。"},
            "5":    {"name": "Poisoned TLP Egress Blocking Enable",  "attr": "RW/RO",   "desc": "Poisoned TLP Egress Blocking Supported=Set 時為 RW；否則 hardwired to 0b。預設 0b。"},
            "6":    {"name": "DPC Software Trigger",                 "attr": "RW/RO",   "desc": "DPC Software Triggering Supported=Set 時：寫入 1b 觸發 DPC（DPC Enable 且 DPC Trigger Status=Clear 時）；讀取永遠返回 0b。否則 hardwired to 0b。"},
            "7":    {"name": "DL_Active ERR_COR Enable",             "attr": "RW/RO",   "desc": "DL_Active ERR_COR Signaling Supported=Set 時為 RW；否則 hardwired to 0b。Set 時 Link→DL_Active 傳送 ERR_COR。預設 0b。"},
            "8":    {"name": "DPC SIG_SFW Enable",                   "attr": "RW/RO",   "desc": "ERR_COR Subclass Capable=Set 時為 RW；否則 hardwired to 0b。Set 時 DPC 事件傳送帶 SIG_SFW subclass 的 ERR_COR。預設 0b。"},
            "15:9": {"name": "Reserved",                             "attr": "RsvdP",   "desc": "保留。"},
        }
    },
    "dpc_status": {
        "section": "7.9.15.4", "offset": "08h", "page": 957,
        "bits": {
            "0":    {"name": "DPC Trigger Status",           "attr": "RW1CS",    "desc": "Set 表示 DPC 已觸發（處於 DPC 狀態）。硬體持續將 LTSSM 導向 Disabled 狀態直到此 bit 被軟體清除。清除後軟體須遵守 §6.6.1 的時序。預設 0b。"},
            "2:1":  {"name": "DPC Trigger Reason",           "attr": "ROS",      "desc": "00b=Unmasked uncorrectable error；01b=收到 ERR_NONFATAL；10b=收到 ERR_FATAL；11b=見 DPC Trigger Reason Extension。DPC Trigger Status=Set 時有效。"},
            "3":    {"name": "DPC Interrupt Status",         "attr": "RW1CS",    "desc": "DPC Interrupt Enable=Set 時觸發 DPC 後 Set。預設 0b。"},
            "4":    {"name": "DPC RP Busy",                  "attr": "RO",       "desc": "（僅 Root Port）DPC Trigger Status=Set 且此 bit=Set 時，Root Port 有需要完成的內部活動，軟體不應在此 bit Clear 前清除 DPC Trigger Status。Switch Downstream Port 為 RsvdZ。"},
            "6:5":  {"name": "DPC Trigger Reason Extension", "attr": "ROS",      "desc": "DPC Trigger Reason=11b 時有效：00b=RP PIO error；01b=DPC Software Trigger bit；10b~11b=保留。"},
            "7":    {"name": "Reserved",                     "attr": "RsvdZ",    "desc": "保留。"},
            "12:8": {"name": "RP PIO First Error Pointer",   "attr": "ROS",      "desc": "（僅 Root Port with RP Extensions）識別 RP PIO Status Register 中第一個被回報錯誤的 bit 位置。軟體清除對應 RP PIO Status bit 後此欄位重置為 11111b（永久保留 bit）。Switch Downstream Port 為 RsvdZ。預設 11111b。"},
            "13":   {"name": "DPC SIG_SFW Status",           "attr": "RW1CS/RsvdZ","desc": "ERR_COR Subclass Capable=Set 時為 RW1CS；DPC 事件傳送 SIG_SFW ERR_COR 時 Set。否則 hardwired to 0b。預設 0b。"},
            "15:14":{"name": "Reserved",                     "attr": "RsvdZ",    "desc": "保留。"},
        }
    },
    "dpc_error_source_id": {
        "section": "7.9.15.5", "offset": "0Ah", "page": 959,
        "bits": {
            "15:0": {"name": "DPC Error Source ID", "attr": "ROS", "desc": "DPC Trigger Reason=01b/10b（ERR_NONFATAL/ERR_FATAL）時，包含收到的 Message 的 Requester ID。否則值未定義。"},
        }
    },

    # ── 7.9.16 PTM Registers ─────────────────────────────────────────────────
    "ptm_capability_reg": {
        "section": "7.9.16.2", "offset": "04h", "page": 966,
        "bits": {
            "0":    {"name": "PTM Requester Capable",     "attr": "HwInit",      "desc": "Set 表示 Function 實作 PTM Requester 角色。Endpoints/RCiEPs 可 Set；Switch Upstream Ports 若下游有 PTM Responder 或 PTM Requester 必須 Set。"},
            "1":    {"name": "PTM Responder Capable",     "attr": "HwInit",      "desc": "Root Ports/RCRBs 可 Set；支援 PTM 的 Switches 必須 Set。PTM Root Capable=Set 時此 bit 也必須 Set。"},
            "2":    {"name": "PTM Root Capable",          "attr": "HwInit",      "desc": "Root Ports、RCRBs、Switches 若具備作為 PTM Master Time Source 的能力可 Set。其他 Function 必須 hardwired to 0b。"},
            "3":    {"name": "ePTM Capable",              "attr": "HwInit",      "desc": "Set 表示裝置支援 Enhanced PTM。強烈建議所有 PTM 裝置 Set 此 bit。"},
            "7:4":  {"name": "Reserved",                  "attr": "RsvdP",       "desc": "保留。"},
            "15:8": {"name": "Local Clock Granularity",   "attr": "HwInit/RsvdP","desc": "本地時脈週期（ns）：00h=無本地時脈（從上游傳播時序），01h~FEh=週期ns值，FFh=週期>254ns。PTM Root Capable=Clear 時為 RsvdP。"},
        }
    },
    "ptm_control": {
        "section": "7.9.16.3", "offset": "08h", "page": 968,
        "bits": {
            "0":    {"name": "PTM Enable",           "attr": "RW",      "desc": "Set 時 Function 依其選擇的角色參與 PTM。預設 0b。"},
            "1":    {"name": "Root Select",          "attr": "RW/RO",   "desc": "Set 且 PTM Enable=Set 時，此 Time Source 為 PTM Root。建議軟體選擇最上游的 Time Source 作為 PTM Root。PTM Root Capable=Clear 時可 hardwired to 0b。預設 0b。"},
            "7:2":  {"name": "Reserved",             "attr": "RsvdP",   "desc": "保留。"},
            "15:8": {"name": "Effective Granularity","attr": "RW/RO",   "desc": "PTM Requester Functions 的預期 PTM 時脈精確度（ns）：00h=未知，01h~FEh=精確度ns值，FFh=>254ns。Endpoint 軟體須程式化為 PTM Root 與所有中間 Time Sources 的 Local Clock Granularity 最大值。PTM Requester Capable=Clear 時可 hardwired to 00h。預設 00h。"},
            "31:16":{"name": "Reserved",             "attr": "RsvdP",   "desc": "保留。"},
        }
    },

    # ── 通用 Extended Capability Header（固定格式）────────────────────────────
    "ext_cap_header_generic": {
        "section": "7.6.3", "offset": "00h", "page": 772,
        "bits": {
            "15:0":  {"name": "PCIe Extended Capability ID", "attr": "RO", "desc": "PCI-SIG 定義的 Capability ID，識別此 Extended Capability 的類型。"},
            "19:16": {"name": "Capability Version",          "attr": "RO", "desc": "PCI-SIG 定義的版本號。"},
            "31:20": {"name": "Next Capability Offset",      "attr": "RO", "desc": "指向下一個 Extended Capability 的偏移量（相對於 Configuration Space 起始）。000h 表示無更多 Extended Capabilities。必須為 000h 或大於 0FFh。"},
        }
    },

    # ── 7.5.1 剩餘 Type 0/1 暫存器 ──────────────────────────────────────────
    "error_registers_overview": {
        "section": "7.5.1.1.14", "offset": "04h/06h", "page": 694,
        "bits": {
            "8":    {"name": "Master Data Parity Error (Status[8])",  "attr": "RW1C", "desc": "Status Register bit[8]。Parity Error Response=Set 時，收到 Poisoned Completion 或傳出 Poisoned Request 時 Set。（見 §7.5.1.1.4）"},
            "11":   {"name": "Signaled Target Abort (Status[11])",    "attr": "RW1C", "desc": "Status Register bit[11]。Function 以 Completer Abort 完成請求時 Set。"},
            "12":   {"name": "Received Target Abort (Status[12])",    "attr": "RW1C", "desc": "Status Register bit[12]。收到 Completer Abort Completion 時 Set。"},
            "13":   {"name": "Received Master Abort (Status[13])",    "attr": "RW1C", "desc": "Status Register bit[13]。收到 Unsupported Request Completion 時 Set。"},
            "14":   {"name": "Signaled System Error (Status[14])",    "attr": "RW1C", "desc": "Status Register bit[14]。傳出 ERR_FATAL/ERR_NONFATAL 且 SERR# Enable=Set 時 Set。"},
            "15":   {"name": "Detected Parity Error (Status[15])",   "attr": "RW1C", "desc": "Status Register bit[15]。收到 Poisoned TLP 時 Set（與 Parity Error Response 無關）。"},
            "6":    {"name": "Parity Error Response Enable (Cmd[6])", "attr": "RW",   "desc": "Command Register bit[6]。控制 Master Data Parity Error bit 的記錄。"},
            "8_cmd":{"name": "SERR# Enable (Cmd[8])",                "attr": "RW",   "desc": "Command Register bit[8]。啟用 Non-fatal 和 Fatal 錯誤的 Upstream 回報。（此節說明這兩個控制 bit 和五個 status bit 的組合用途）"},
        }
    },
    "latency_timer": {
        "section": "7.5.1.1.8", "offset": "0Dh", "page": 692,
        "bits": {
            "7:0": {"name": "Latency Timer", "attr": "RO", "desc": "不適用於 PCI Express，必須 hardwired to 00h。對任何 PCIe 裝置行為均無影響。"},
        }
    },
    "cardbus_cis_pointer": {
        "section": "7.5.1.2.2", "offset": "28h", "page": 699,
        "bits": {
            "31:0": {"name": "Cardbus CIS Pointer", "attr": "RO", "desc": "不適用於 PCI Express，必須 hardwired to 0000 0000h。"},
        }
    },
    "subsystem_vendor_id_type0": {
        "section": "7.5.1.2.3", "offset": "2Ch", "page": 700,
        "bits": {
            "15:0": {"name": "Subsystem Vendor ID (SVID)", "attr": "RO", "desc": "唯一識別 PCI Express 元件所在 adapter 或子系統的廠商 ID。必須為 PCI-SIG 指派的 Vendor ID。必須在 Function 進入 Configuration-Ready 狀態前載入，不得透過 Expansion ROM 軟體載入。"},
        }
    },
    "subsystem_id_type0": {
        "section": "7.5.1.2.3", "offset": "2Eh", "page": 700,
        "bits": {
            "15:0": {"name": "Subsystem ID (SSID)", "attr": "RO", "desc": "廠商自行指派的子系統識別 ID。與 SVID 合併形成 PCI 產品的唯一識別符。不應與 Device ID 混用。"},
        }
    },
    "min_gnt": {
        "section": "7.5.1.2.5", "offset": "3Eh", "page": 703,
        "bits": {
            "7:0": {"name": "Min_Gnt", "attr": "RO", "desc": "不適用於 PCI Express，必須 hardwired to 00h。"},
        }
    },
    "max_lat": {
        "section": "7.5.1.2.5", "offset": "3Fh", "page": 703,
        "bits": {
            "7:0": {"name": "Max_Lat", "attr": "RO", "desc": "不適用於 PCI Express，必須 hardwired to 00h。"},
        }
    },
    "primary_bus_number": {
        "section": "7.5.1.3.2", "offset": "18h", "page": 705,
        "bits": {
            "7:0": {"name": "Primary Bus Number", "attr": "RW", "desc": "Type 1 Header 的 Primary Bus Number。PCIe Function 本身不使用此值，但為相容舊版軟體必須實作為 RW，預設 00h。PCIe Function 透過 §2.2.6 機制取得 Bus/Device Number。"},
        }
    },
    "secondary_bus_number": {
        "section": "7.5.1.3.3", "offset": "19h", "page": 705,
        "bits": {
            "7:0": {"name": "Secondary Bus Number", "attr": "RW", "desc": "Bridge 次要介面所連接的 PCI bus segment 的 Bus Number，由 Configuration Software 程式化。Bridge 使用此值決定如何路由 ID-routed TLP（見 §7.3.3）。預設 00h。"},
        }
    },
    "subordinate_bus_number": {
        "section": "7.5.1.3.4", "offset": "1Ah", "page": 705,
        "bits": {
            "7:0": {"name": "Subordinate Bus Number", "attr": "RW", "desc": "位於 Bridge 下游的最高編號 PCI bus segment 的 Bus Number，由 Configuration Software 程式化。Bridge 使用此值決定如何路由 ID-routed TLP。預設 00h。"},
        }
    },
    "memory_base_limit": {
        "section": "7.5.1.3.8", "offset": "20h/22h", "page": 708,
        "bits": {
            "3:0":   {"name": "Memory Base Capability",  "attr": "RO", "desc": "讀回 0h，不編碼任何能力資訊。"},
            "15:4":  {"name": "Memory Base [31:20]",     "attr": "RW", "desc": "Non-Prefetchable Memory Window 基底位址上 12 bits（Address[31:20]），下 20 bits 假設為 0（1MB 對齊）。"},
            "19:16": {"name": "Memory Limit Capability", "attr": "RO", "desc": "讀回 0h，不編碼任何能力資訊。"},
            "31:20": {"name": "Memory Limit [31:20]",    "attr": "RW", "desc": "Non-Prefetchable Memory Window 上限位址上 12 bits（Address[31:20]），下 20 bits 假設為 F FFFFh（1MB 邊界減一）。若無 Memory Window，Limit < Base。"},
        }
    },
    "prefetchable_memory_base_limit": {
        "section": "7.5.1.3.9", "offset": "24h/26h", "page": 708,
        "bits": {
            "3:0":   {"name": "Prefetchable Base Capability",  "attr": "RO", "desc": "0h=僅支援 32-bit 位址；1h=支援 64-bit 位址（Prefetchable Base/Limit Upper 32 Bits 暫存器有效）。"},
            "15:4":  {"name": "Prefetchable Memory Base [31:20]", "attr": "RW", "desc": "Prefetchable Memory Window 基底位址上 12 bits（Address[31:20]），下 20 bits 假設為 0（1MB 對齊）。Bridge 不實作時為 RO=0。"},
            "19:16": {"name": "Prefetchable Limit Capability", "attr": "RO", "desc": "與 Base Capability 相同值（0h 或 1h）。"},
            "31:20": {"name": "Prefetchable Memory Limit [31:20]", "attr": "RW", "desc": "Prefetchable Memory Window 上限位址上 12 bits（Address[31:20]），下 20 bits 假設為 F FFFFh。若無 Prefetchable Window，Limit < Base。"},
        }
    },
    "expansion_rom_type1": {
        "section": "7.5.1.3.12", "offset": "38h", "page": 709,
        "bits": {
            "0":     {"name": "Expansion ROM Enable",      "attr": "RW/RO",    "desc": "控制 Function 是否接受 Expansion ROM 存取。0b=停用；1b=啟用。Command Register 的 Memory Space Enable 優先。無 Expansion ROM 或有 EA entry 時 hardwired to 0b。"},
            "10:1":  {"name": "Reserved",                  "attr": "RsvdP",    "desc": "保留。"},
            "31:11": {"name": "Expansion ROM Base Address","attr": "RW/RO",    "desc": "Type 1 Header 的 Expansion ROM 基底位址上 21 bits。格式與 Type 0 Expansion ROM BAR 相同。"},
        }
    },

    # ── 7.5.2.3 PM Data Register ─────────────────────────────────────────────
    "pm_data_register": {
        "section": "7.5.2.3", "offset": "07h", "page": 716,
        "bits": {
            "7:0": {"name": "Data", "attr": "RO", "desc": "Optional 8-bit RO，提供 Function 功耗/散熱資訊回報機制。回傳值由 PMCSR 的 Data_Select 選擇，以 Data_Scale 換算。Data_Select：0=D0 Power Consumed，1=D1，2=D2，3=D3，4=D0 Power Dissipated，5=D1，6=D2，7=D3，8=Common logic power（MFD Function 0 專用），9-15=保留。未實作時 hardwired to 00h。"},
        }
    },

    # ── 7.7.1 MSI Capability Header 和剩餘暫存器 ─────────────────────────────
    "msi_capability_header": {
        "section": "7.7.1.1", "offset": "00h", "page": 775,
        "bits": {
            "7:0":  {"name": "Capability ID",            "attr": "RO", "desc": "固定為 05h，識別此為 MSI Capability 結構。"},
            "15:8": {"name": "Next Capability Pointer",  "attr": "RO", "desc": "指向下一個 PCI Capability 結構的偏移量；無更多時為 00h。"},
        }
    },
    "msi_message_upper_address": {
        "section": "7.7.1.4", "offset": "08h", "page": 778,
        "bits": {
            "31:0": {"name": "Message Upper Address", "attr": "RW", "desc": "64-bit Address Capable=Set 時存在。MSI 訊息目標位址的高 32 bits（Address[63:32]）。PCIe Endpoint 必須實作；其他 Function 類型為 Optional。MSI Enable=Set 時有效。"},
        }
    },
    "msi_extended_message_data": {
        "section": "7.7.1.6", "offset": "varies", "page": 779,
        "bits": {
            "15:0": {"name": "Extended Message Data", "attr": "RW", "desc": "Optional。Extended Message Data Capable=Set 時存在。Extended Message Data Enable=Set 時，DWORD Memory Write transaction 使用此值作為高 16 bits；否則高 16 bits 使用 0000h。預設 0000h。"},
        }
    },

    # ── 7.7.2 MSI-X Capability Header ────────────────────────────────────────
    "msix_capability_header": {
        "section": "7.7.2.1", "offset": "00h", "page": 784,
        "bits": {
            "7:0":  {"name": "Capability ID",           "attr": "RO", "desc": "固定為 11h，識別此為 MSI-X Capability 結構。"},
            "15:8": {"name": "Next Capability Pointer", "attr": "RO", "desc": "指向下一個 PCI Capability 結構的偏移量；無更多時為 00h。"},
        }
    },

    # ── 7.7.3~7.7.8 Extended Capability Headers ──────────────────────────────
    "secondary_pcie_ext_cap_header": {
        "section": "7.7.3.1", "offset": "00h", "page": 792,
        "bits": {
            "15:0":  {"name": "PCIe Extended Capability ID = 0019h", "attr": "RO", "desc": "Secondary PCI Express Extended Capability 的識別碼 0019h。"},
            "19:16": {"name": "Capability Version = 1h",             "attr": "RO", "desc": "本規範版本號為 1h。"},
            "31:20": {"name": "Next Capability Offset",              "attr": "RO", "desc": "指向下一個 PCIe Extended Capability 的偏移量。000h 表示結束。必須為 000h 或 > 0FFh。"},
        }
    },
    "data_link_feature_ext_cap_header": {
        "section": "7.7.4.1", "offset": "00h", "page": 797,
        "bits": {
            "15:0":  {"name": "PCIe Extended Capability ID = 0025h", "attr": "RO", "desc": "Data Link Feature Extended Capability 的識別碼 0025h。"},
            "19:16": {"name": "Capability Version = 1h",             "attr": "RO", "desc": "本規範版本號為 1h。"},
            "31:20": {"name": "Next Capability Offset",              "attr": "RO", "desc": "指向下一個 PCIe Extended Capability 的偏移量。000h 表示結束。"},
        }
    },
    "phy16_ext_cap_header": {
        "section": "7.7.5.1", "offset": "00h", "page": 800,
        "bits": {
            "15:0":  {"name": "PCIe Extended Capability ID = 0026h", "attr": "RO", "desc": "Physical Layer 16.0 GT/s Extended Capability 的識別碼 0026h。"},
            "19:16": {"name": "Capability Version = 1h",             "attr": "RO", "desc": "本規範版本號為 1h。"},
            "31:20": {"name": "Next Capability Offset",              "attr": "RO", "desc": "指向下一個 PCIe Extended Capability 的偏移量。000h 表示結束。"},
        }
    },
    "phy16_capabilities_reg": {
        "section": "7.7.5.2", "offset": "04h", "page": 801,
        "bits": {
            "31:0": {"name": "Reserved", "attr": "RsvdP", "desc": "整個暫存器為 RsvdP（PCIe 5.0 規範保留，未來版本可能分配 bit fields）。讀取返回 0，寫入無效。"},
        }
    },
    "phy16_control_reg": {
        "section": "7.7.5.3", "offset": "08h", "page": 801,
        "bits": {
            "31:0": {"name": "Reserved", "attr": "RsvdP", "desc": "整個暫存器為 RsvdP（PCIe 5.0 規範保留，未來版本可能分配 bit fields）。讀取返回 0，寫入無效。"},
        }
    },
    "phy32_ext_cap_header": {
        "section": "7.7.6.1", "offset": "00h", "page": 807,
        "bits": {
            "15:0":  {"name": "PCIe Extended Capability ID = 002Ah", "attr": "RO", "desc": "Physical Layer 32.0 GT/s Extended Capability 的識別碼 002Ah。"},
            "19:16": {"name": "Capability Version = 1h",             "attr": "RO", "desc": "本規範版本號為 1h。"},
            "31:20": {"name": "Next Capability Offset",              "attr": "RO", "desc": "指向下一個 PCIe Extended Capability 的偏移量。000h 表示結束。"},
        }
    },
    "lane_margining_ext_cap_header": {
        "section": "7.7.7.1", "offset": "00h", "page": 819,
        "bits": {
            "15:0":  {"name": "PCIe Extended Capability ID = 0027h", "attr": "RO", "desc": "Lane Margining at the Receiver Extended Capability 的識別碼 0027h。"},
            "19:16": {"name": "Capability Version = 1h",             "attr": "RO", "desc": "本規範版本號為 1h。"},
            "31:20": {"name": "Next Capability Offset",              "attr": "RO", "desc": "指向下一個 PCIe Extended Capability 的偏移量。000h 表示結束。"},
        }
    },
    "acs_ext_cap_header": {
        "section": "7.7.8.1", "offset": "00h", "page": 823,
        "bits": {
            "15:0":  {"name": "PCIe Extended Capability ID = 000Dh", "attr": "RO", "desc": "ACS Extended Capability 的識別碼 000Dh。"},
            "19:16": {"name": "Capability Version = 1h",             "attr": "RO", "desc": "本規範版本號為 1h。"},
            "31:20": {"name": "Next Capability Offset",              "attr": "RO", "desc": "指向下一個 PCIe Extended Capability 的偏移量。000h 表示結束。"},
        }
    },

    # ── 7.8.x Extended Capability Headers ────────────────────────────────────
    "power_budgeting_ext_cap_header": {
        "section": "7.8.1.1", "offset": "00h", "page": 830,
        "bits": {
            "15:0":  {"name": "PCIe Extended Capability ID = 0004h", "attr": "RO", "desc": "Power Budgeting Extended Capability 的識別碼 0004h。"},
            "19:16": {"name": "Capability Version = 1h",             "attr": "RO", "desc": "本規範版本號為 1h。"},
            "31:20": {"name": "Next Capability Offset",              "attr": "RO", "desc": "指向下一個 PCIe Extended Capability 的偏移量。000h 表示結束。必須為 000h 或 > 0FFh。"},
        }
    },
    "ltr_ext_cap_header": {
        "section": "7.8.2.1", "offset": "00h", "page": 834,
        "bits": {
            "15:0":  {"name": "PCIe Extended Capability ID = 0018h", "attr": "RO", "desc": "Latency Tolerance Reporting (LTR) Extended Capability 的識別碼 0018h。"},
            "19:16": {"name": "Capability Version = 1h",             "attr": "RO", "desc": "本規範版本號為 1h。"},
            "31:20": {"name": "Next Capability Offset",              "attr": "RO", "desc": "指向下一個 PCIe Extended Capability 的偏移量。000h 表示結束。"},
        }
    },
    "l1pm_ext_cap_header": {
        "section": "7.8.3.1", "offset": "00h", "page": 836,
        "bits": {
            "15:0":  {"name": "PCIe Extended Capability ID = 001Eh", "attr": "RO", "desc": "L1 PM Substates Extended Capability 的識別碼 001Eh。"},
            "19:16": {"name": "Capability Version",                  "attr": "RO", "desc": "若有實作 L1 PM Substates Status Register（§7.8.3.5）則為 2h；否則為 1h。"},
            "31:20": {"name": "Next Capability Offset",              "attr": "RO", "desc": "指向下一個 PCIe Extended Capability 的偏移量。000h 表示結束。"},
        }
    },
    "pasid_ext_cap_header": {
        "section": "7.8.8.1", "offset": "00h", "page": 871,
        "bits": {
            "15:0":  {"name": "PCIe Extended Capability ID = 001Bh", "attr": "RO", "desc": "PASID Extended Capability 的識別碼 001Bh。"},
            "19:16": {"name": "Capability Version = 1h",             "attr": "RO", "desc": "本規範版本號為 1h。"},
            "31:20": {"name": "Next Capability Offset",              "attr": "RO", "desc": "指向下一個 PCIe Extended Capability 的偏移量。000h 表示結束。"},
        }
    },
    "frs_ext_cap_header": {
        "section": "7.8.9.1", "offset": "00h", "page": 875,
        "bits": {
            "15:0":  {"name": "PCIe Extended Capability ID = 0021h", "attr": "RO", "desc": "FRS Queueing Extended Capability 的識別碼 0021h。"},
            "19:16": {"name": "Capability Version = 1h",             "attr": "RO", "desc": "本規範版本號為 1h。"},
            "31:20": {"name": "Next Capability Offset",              "attr": "RO", "desc": "指向下一個 PCIe Extended Capability 的偏移量。000h 表示結束。"},
        }
    },

    # ── 7.9.x Extended Capability Headers ────────────────────────────────────
    "vc_ext_cap_header": {
        "section": "7.9.1.1", "offset": "00h", "page": 890,
        "bits": {
            "15:0":  {"name": "PCIe Extended Capability ID = 0002h", "attr": "RO", "desc": "Virtual Channel Extended Capability 的識別碼 0002h（MFVC 為 0009h）。"},
            "19:16": {"name": "Capability Version = 1h",             "attr": "RO", "desc": "本規範版本號為 1h。"},
            "31:20": {"name": "Next Capability Offset",              "attr": "RO", "desc": "指向下一個 PCIe Extended Capability 的偏移量。000h 表示結束。"},
        }
    },
    "dpc_ext_cap_header": {
        "section": "7.9.15.1", "offset": "00h", "page": 953,
        "bits": {
            "15:0":  {"name": "PCIe Extended Capability ID = 001Dh", "attr": "RO", "desc": "DPC Extended Capability 的識別碼 001Dh。"},
            "19:16": {"name": "Capability Version = 1h",             "attr": "RO", "desc": "本規範版本號為 1h。"},
            "31:20": {"name": "Next Capability Offset",              "attr": "RO", "desc": "指向下一個 PCIe Extended Capability 的偏移量。000h 表示結束。"},
        }
    },
    "dpc_rp_pio_impspec_log": {
        "section": "7.9.15.12", "offset": "30h", "page": 964,
        "bits": {
            "31:0": {"name": "RP PIO ImpSpec Log", "attr": "ROS", "desc": "Optional。包含 Root Port 實作特定資訊（例如產生 Request TLP 的來源）。RP PIO Log Size ≥ 5 時分配空間。若分配空間但未實作則 hardwired to 0b。預設 0。"},
        }
    },
    "dpc_rp_pio_tlp_prefix_log": {
        "section": "7.9.15.13", "offset": "34h", "page": 964,
        "bits": {
            "127:0": {"name": "RP PIO TLP Prefix Log", "attr": "ROS", "desc": "Optional。包含記錄的 RP PIO 錯誤 TLP 的 End-End TLP Prefix。大小（DWORDs）= RP PIO Log Size − 5（Log Size ≤ 9 時）或 4（Log Size > 9 時）。若 Root Port 從不傳送含 E2E TLP Prefix 的 Non-Posted Requests，大小可為 0。未實作的 DWORD hardwired to 0。"},
        }
    },
    "ptm_ext_cap_header": {
        "section": "7.9.16.1", "offset": "00h", "page": 966,
        "bits": {
            "15:0":  {"name": "PCIe Extended Capability ID = 001Fh", "attr": "RO", "desc": "PTM Extended Capability 的識別碼 001Fh。"},
            "19:16": {"name": "Capability Version = 1h",             "attr": "RO", "desc": "本規範版本號為 1h。"},
            "31:20": {"name": "Next Capability Offset",              "attr": "RO", "desc": "指向下一個 PCIe Extended Capability 的偏移量。000h 表示結束。"},
        }
    },
    "readiness_time_ext_cap_header": {
        "section": "7.9.17.1", "offset": "00h", "page": 970,
        "bits": {
            "15:0":  {"name": "PCIe Extended Capability ID = 0022h", "attr": "RO", "desc": "Readiness Time Reporting Extended Capability 的識別碼 0022h。"},
            "19:16": {"name": "Capability Version = 1h",             "attr": "RO", "desc": "本規範版本號為 1h。"},
            "31:20": {"name": "Next Capability Offset",              "attr": "RO", "desc": "指向下一個 PCIe Extended Capability 的偏移量。000h 表示結束（000h 或 > 0FFh）。"},
        }
    },

    # ── 7.9.15 DPC RP PIO Registers ────────────────────────────────────────
    "dpc_rp_pio_status": {
        "section": "7.9.15.6", "offset": "0Ch", "page": 959,
        "bits": {
            "0":    {"name": "Cfg UR Cpl",    "attr": "RW1CS", "desc": "Config Request 收到 UR Completion。預設 0b。"},
            "1":    {"name": "Cfg CA Cpl",    "attr": "RW1CS", "desc": "Config Request 收到 CA Completion。預設 0b。"},
            "2":    {"name": "Cfg CTO",       "attr": "RW1CS", "desc": "Config Request Completion Timeout。預設 0b。"},
            "7:3":  {"name": "Reserved",      "attr": "RsvdZ", "desc": "保留。"},
            "8":    {"name": "I/O UR Cpl",    "attr": "RW1CS", "desc": "I/O Request 收到 UR Completion。預設 0b。"},
            "9":    {"name": "I/O CA Cpl",    "attr": "RW1CS", "desc": "I/O Request 收到 CA Completion。預設 0b。"},
            "10":   {"name": "I/O CTO",       "attr": "RW1CS", "desc": "I/O Request Completion Timeout。預設 0b。"},
            "15:11":{"name": "Reserved",      "attr": "RsvdZ", "desc": "保留。"},
            "16":   {"name": "Mem UR Cpl",    "attr": "RW1CS", "desc": "Memory Request 收到 UR Completion。預設 0b。"},
            "17":   {"name": "Mem CA Cpl",    "attr": "RW1CS", "desc": "Memory Request 收到 CA Completion。預設 0b。"},
            "18":   {"name": "Mem CTO",       "attr": "RW1CS", "desc": "Memory Request Completion Timeout。預設 0b。"},
            "30:19":{"name": "Reserved",      "attr": "RsvdZ", "desc": "保留。"},
            "31":   {"name": "Permanently_Reserved", "attr": "RsvdZ", "desc": "永久保留 bit（RP PIO First Error Pointer 預設指向此 bit = 11111b）。"},
        }
    },
    "dpc_rp_pio_mask": {
        "section": "7.9.15.7", "offset": "10h", "page": 960,
        "bits": {
            "0":    {"name": "Cfg UR Cpl Mask",  "attr": "RWS", "desc": "遮罩 Cfg UR Cpl DPC 觸發。預設 1b。"},
            "1":    {"name": "Cfg CA Cpl Mask",  "attr": "RWS", "desc": "遮罩 Cfg CA Cpl DPC 觸發。預設 1b。"},
            "2":    {"name": "Cfg CTO Mask",     "attr": "RWS", "desc": "遮罩 Cfg CTO DPC 觸發。預設 1b。"},
            "8":    {"name": "I/O UR Cpl Mask",  "attr": "RWS", "desc": "遮罩 I/O UR Cpl DPC 觸發。預設 1b。"},
            "9":    {"name": "I/O CA Cpl Mask",  "attr": "RWS", "desc": "遮罩 I/O CA Cpl DPC 觸發。預設 1b。"},
            "10":   {"name": "I/O CTO Mask",     "attr": "RWS", "desc": "遮罩 I/O CTO DPC 觸發。預設 1b。"},
            "16":   {"name": "Mem UR Cpl Mask",  "attr": "RWS", "desc": "遮罩 Mem UR Cpl DPC 觸發。預設 1b。"},
            "17":   {"name": "Mem CA Cpl Mask",  "attr": "RWS", "desc": "遮罩 Mem CA Cpl DPC 觸發。預設 1b。"},
            "18":   {"name": "Mem CTO Mask",     "attr": "RWS", "desc": "遮罩 Mem CTO DPC 觸發。預設 1b。"},
        }
    },
    "dpc_rp_pio_severity": {
        "section": "7.9.15.8", "offset": "14h", "page": 961,
        "bits": {
            "0":  {"name": "Cfg UR Cpl Severity",  "attr": "RWS", "desc": "1b=Fatal，0b=Non-Fatal。預設 0b。"},
            "1":  {"name": "Cfg CA Cpl Severity",  "attr": "RWS", "desc": "1b=Fatal，0b=Non-Fatal。預設 0b。"},
            "2":  {"name": "Cfg CTO Severity",     "attr": "RWS", "desc": "1b=Fatal，0b=Non-Fatal。預設 0b。"},
            "8":  {"name": "I/O UR Cpl Severity",  "attr": "RWS", "desc": "1b=Fatal，0b=Non-Fatal。預設 0b。"},
            "9":  {"name": "I/O CA Cpl Severity",  "attr": "RWS", "desc": "1b=Fatal，0b=Non-Fatal。預設 0b。"},
            "10": {"name": "I/O CTO Severity",     "attr": "RWS", "desc": "1b=Fatal，0b=Non-Fatal。預設 0b。"},
            "16": {"name": "Mem UR Cpl Severity",  "attr": "RWS", "desc": "1b=Fatal，0b=Non-Fatal。預設 0b。"},
            "17": {"name": "Mem CA Cpl Severity",  "attr": "RWS", "desc": "1b=Fatal，0b=Non-Fatal。預設 0b。"},
            "18": {"name": "Mem CTO Severity",     "attr": "RWS", "desc": "1b=Fatal，0b=Non-Fatal。預設 0b。"},
        }
    },
    "dpc_rp_pio_syserror": {
        "section": "7.9.15.9", "offset": "18h", "page": 962,
        "bits": {
            "0":  {"name": "Cfg UR Cpl SysError",  "attr": "RWS", "desc": "Set 時此錯誤觸發 System Error 訊號。預設 0b。"},
            "1":  {"name": "Cfg CA Cpl SysError",  "attr": "RWS", "desc": "Set 時此錯誤觸發 System Error 訊號。預設 0b。"},
            "2":  {"name": "Cfg CTO SysError",     "attr": "RWS", "desc": "Set 時此錯誤觸發 System Error 訊號。預設 0b。"},
            "8":  {"name": "I/O UR Cpl SysError",  "attr": "RWS", "desc": "Set 時此錯誤觸發 System Error 訊號。預設 0b。"},
            "9":  {"name": "I/O CA Cpl SysError",  "attr": "RWS", "desc": "Set 時此錯誤觸發 System Error 訊號。預設 0b。"},
            "10": {"name": "I/O CTO SysError",     "attr": "RWS", "desc": "Set 時此錯誤觸發 System Error 訊號。預設 0b。"},
            "16": {"name": "Mem UR Cpl SysError",  "attr": "RWS", "desc": "Set 時此錯誤觸發 System Error 訊號。預設 0b。"},
            "17": {"name": "Mem CA Cpl SysError",  "attr": "RWS", "desc": "Set 時此錯誤觸發 System Error 訊號。預設 0b。"},
            "18": {"name": "Mem CTO SysError",     "attr": "RWS", "desc": "Set 時此錯誤觸發 System Error 訊號。預設 0b。"},
        }
    },
    "dpc_rp_pio_exception": {
        "section": "7.9.15.10", "offset": "1Ch", "page": 962,
        "bits": {
            "0":  {"name": "Cfg UR Cpl Exception",  "attr": "RWS", "desc": "Set 時此錯誤為例外條件（見 §6.2.10.3）。預設 0b。"},
            "1":  {"name": "Cfg CA Cpl Exception",  "attr": "RWS", "desc": "Set 時此錯誤為例外條件。預設 0b。"},
            "2":  {"name": "Cfg CTO Exception",     "attr": "RWS", "desc": "Set 時此錯誤為例外條件。預設 0b。"},
            "8":  {"name": "I/O UR Cpl Exception",  "attr": "RWS", "desc": "Set 時此錯誤為例外條件。預設 0b。"},
            "9":  {"name": "I/O CA Cpl Exception",  "attr": "RWS", "desc": "Set 時此錯誤為例外條件。預設 0b。"},
            "10": {"name": "I/O CTO Exception",     "attr": "RWS", "desc": "Set 時此錯誤為例外條件。預設 0b。"},
            "16": {"name": "Mem UR Cpl Exception",  "attr": "RWS", "desc": "Set 時此錯誤為例外條件。預設 0b。"},
            "17": {"name": "Mem CA Cpl Exception",  "attr": "RWS", "desc": "Set 時此錯誤為例外條件。預設 0b。"},
            "18": {"name": "Mem CTO Exception",     "attr": "RWS", "desc": "Set 時此錯誤為例外條件。預設 0b。"},
        }
    },
    "dpc_rp_pio_header_log": {
        "section": "7.9.15.11", "offset": "20h", "page": 963,
        "bits": {
            "127:0": {"name": "RP PIO TLP Header", "attr": "ROS", "desc": "4 DWORDs（128 bits）的 TLP Header，格式與 AER Header Log Register 相同（§7.8.4.8）。包含與記錄的 RP PIO 錯誤相關的 Request TLP 的 header。預設 0。僅在具 RP Extensions for DPC 的 Root Ports 中實作。"},
        }
    },

    # ── 7.9.17 Readiness Time Reporting ──────────────────────────────────────
    "readiness_time_reporting_1": {
        "section": "7.9.17.2", "offset": "04h", "page": 971,
        "bits": {
            "11:0":  {"name": "Reset Time",   "attr": "HwInit/RsvdP", "desc": "Conventional Reset 完成後 Function 成為 Configuration-Ready 所需的時間（Readiness Time 編碼格式，見 §7.9.17）。Immediate Readiness=Set 時為 RsvdP。Valid=Clear 時未定義。最大值為 A1Eh（約 1 秒）。"},
            "23:12": {"name": "DL_Up Time",   "attr": "HwInit/RsvdP", "desc": "Downstream Port 回報 DLL Link Active 後 Function 成為 Configuration-Ready 所需的時間（Readiness Time 編碼格式）。非 Upstream Port 為 RsvdP。Valid=Clear 時未定義。最大值為 A1Eh。"},
            "30:24": {"name": "Reserved",     "attr": "RsvdP",        "desc": "保留。"},
            "31":    {"name": "Valid",         "attr": "HwInit",       "desc": "Set 表示所有時間值均有效；Clear 表示時間值尚未可用。若 Clear 且所有驅動程式啟動後 1 分鐘仍未 Set，軟體可假設此 bit 永遠不會被 Set。"},
        }
    },
    "readiness_time_reporting_2": {
        "section": "7.9.17.3", "offset": "08h", "page": 972,
        "bits": {
            "11:0":  {"name": "FLR Time",           "attr": "HwInit/RsvdP", "desc": "FLR 後 Function 成為 Configuration-Ready 所需的時間（Readiness Time 編碼格式）。FLR Capability bit=Clear 時為 RsvdP。Valid=Clear 時未定義。最大值為 A1Eh。"},
            "23:12": {"name": "D3Hot to D0 Time",   "attr": "HwInit/RsvdP", "desc": "D3hot→D0 轉換後 Function 成為 Configuration-Ready 所需的時間。Immediate_Readiness_on_Return_to_D0=Set 時為 RsvdP。Valid=Clear 時未定義。最大值為 80Ah（約 10ms）。"},
            "31:24": {"name": "Reserved",            "attr": "RsvdP",        "desc": "保留。"},
        }
    },

    # ── 7.7.2 MSI-X PBA ──────────────────────────────────────────────────────
    "msix_pba_entry": {
        "section": "7.7.2.9", "offset": "PBA+k/64*8", "page": 789,
        "bits": {
            "63:0": {"name": "Pending Bits", "attr": "RO", "desc": "64-bit QWORD，每個 bit 對應一個 MSI-X 向量。1b 表示對應向量有 MSI-X Message pending（由硬體 Set，當 Function Mask=0 且 Mask Bit=1 且中斷已觸發時）。軟體唯讀；清除 pending bit 的方式是傳送對應的 MSI-X Message。"},
        }
    },

    # ── 7.7.2 MSI-X Table BIR / PBA BIR ─────────────────────────────────────
    "msix_table_offset_bir": {
        "section": "7.7.2.3", "offset": "04h", "page": 785,
        "bits": {
            "2:0":  {"name": "Table BIR",    "attr": "RO", "desc": "MSI-X Table 所在的 BAR 指示符：000b=BAR0，001b=BAR1，...，101b=BAR5。用於定位 MSI-X Table 的記憶體空間。"},
            "31:3": {"name": "Table Offset", "attr": "RO", "desc": "MSI-X Table 起始位址相對於 Table BIR 對應的 BAR 基底位址的偏移量（8 bytes 對齊）。Bit[2:0] 假設為 000b。"},
        }
    },
    "msix_pba_offset_bir": {
        "section": "7.7.2.4", "offset": "08h", "page": 786,
        "bits": {
            "2:0":  {"name": "PBA BIR",    "attr": "RO", "desc": "MSI-X PBA 所在的 BAR 指示符：000b=BAR0，001b=BAR1，...，101b=BAR5。"},
            "31:3": {"name": "PBA Offset", "attr": "RO", "desc": "MSI-X PBA 起始位址相對於 PBA BIR 對應的 BAR 基底位址的偏移量（8 bytes 對齊）。"},
        }
    },

    # ── 7.7.8 ACS Egress Control Vector ─────────────────────────────────────
    "acs_egress_control_vector": {
        "section": "7.7.8.4", "offset": "08h", "page": 827,
        "bits": {
            "N:0": {"name": "Egress Control Vector", "attr": "RWS", "desc": "每個 bit 對應一個 Downstream Port（bit 0 = Port 0）。ACS P2P Egress Control Enable=Set 時：0b=允許 P2P Requests 到對應 Port；1b=阻擋或重導。大小由 ACS Capability Register 的 Egress Control Vector Size 欄位決定（向上取整為整數個 DWORDs）。預設值未指定。"},
        }
    },

    # ── 7.8.4 AER Header Log / TLP Prefix Log ─────────────────────────────────
    "aer_header_log": {
        "section": "7.8.4.8", "offset": "1Ch", "page": 851,
        "bits": {
            "127:0": {"name": "TLP Header", "attr": "ROS", "desc": "4 DWORDs（128 bits），記錄第一個偵測到的支援錯誤的 TLP Header。Byte 0（最低位）對應 TLP Header 的第一個 byte。用於錯誤診斷。"},
        }
    },
    "aer_tlp_prefix_log": {
        "section": "7.8.4.12", "offset": "38h", "page": 855,
        "bits": {
            "127:0": {"name": "TLP Prefix Log", "attr": "ROS", "desc": "最多 4 個 DWORDs（視 Max End-End TLP Prefixes 而定），記錄與 Header Log 相同 TLP 的 End-End TLP Prefix。僅 End-End TLP Prefix Supported=Set 時實作；否則為 RsvdP。"},
        }
    },
}

# 關鍵詞到章節的映射
KEYWORD_MAP = {
    "ecam": ["7.2.2"],
    "enhanced configuration": ["7.2.2"],
    "configuration access": ["7.2", "7.2.1", "7.2.2"],
    "ecam mapping": ["7.2.2"],
    "rcrb": ["7.2.3", "7.6.2", "7.9.7"],
    "register types": ["7.4"],
    "hwinit": ["7.4"],
    "rw1c": ["7.4"],
    "rwi": ["7.4"],
    "rsvdp": ["7.4"],
    "rsvdz": ["7.4"],
    "vendor id": ["7.5.1.1.1"],
    "device id": ["7.5.1.1.2"],
    "command register": ["7.5.1.1.3"],
    "status register": ["7.5.1.1.4"],
    "bus master": ["7.5.1.1.3"],
    "i/o space enable": ["7.5.1.1.3"],
    "memory space enable": ["7.5.1.1.3"],
    "bar": ["7.5.1.2.1", "7.8.6"],
    "base address": ["7.5.1.2.1"],
    "resizable bar": ["7.8.6"],
    "power management": ["7.5.2"],
    "pmcsr": ["7.5.2.2"],
    "d0 d1 d2 d3": ["7.5.2"],
    "pme": ["7.5.2.1", "7.5.2.2"],
    "pcie capability": ["7.5.3"],
    "device capabilities": ["7.5.3.3"],
    "device control": ["7.5.3.4"],
    "device status": ["7.5.3.5"],
    "link capabilities": ["7.5.3.6"],
    "link control": ["7.5.3.7"],
    "link status": ["7.5.3.8"],
    "slot capabilities": ["7.5.3.9"],
    "slot control": ["7.5.3.10"],
    "slot status": ["7.5.3.11"],
    "root control": ["7.5.3.12"],
    "root status": ["7.5.3.14"],
    "max payload size": ["7.5.3.3", "7.5.3.4"],
    "max read request": ["7.5.3.4"],
    "aspm": ["7.5.3.6", "7.5.3.7"],
    "l0s": ["7.5.3.6", "7.5.3.7"],
    "l1": ["7.5.3.6", "7.5.3.7", "7.8.3"],
    "l1 pm substates": ["7.8.3"],
    "flr": ["7.5.3.3", "7.5.3.4"],
    "function level reset": ["7.5.3.3", "7.5.3.4"],
    "extended tag": ["7.5.3.3", "7.5.3.4"],
    "completion timeout": ["7.5.3.15", "7.5.3.16"],
    "ari": ["7.5.3.16", "7.8.7"],
    "atomicop": ["7.5.3.15", "7.5.3.16"],
    "ltr": ["7.5.3.15", "7.5.3.16", "7.8.2"],
    "obff": ["7.5.3.15", "7.5.3.16"],
    "10-bit tag": ["7.5.3.15", "7.5.3.16"],
    "end-end tlp prefix": ["7.5.3.15", "7.5.3.16"],
    "link capabilities 2": ["7.5.3.18"],
    "link control 2": ["7.5.3.19"],
    "link status 2": ["7.5.3.20"],
    "target link speed": ["7.5.3.19"],
    "equalization": ["7.5.3.20", "7.7.3.4", "7.7.5.4", "7.7.6.4"],
    "enter compliance": ["7.5.3.19"],
    "retimer": ["7.5.3.18", "7.5.3.20"],
    "drs": ["7.5.3.18", "7.5.3.20"],
    "extended capabilities": ["7.6"],
    "extended capability header": ["7.6.3"],
    "msi": ["7.7.1"],
    "msi-x": ["7.7.2"],
    "msix": ["7.7.2"],
    "secondary pcie": ["7.7.3"],
    "lane equalization": ["7.7.3.4"],
    "lane error": ["7.7.3.3"],
    "data link feature": ["7.7.4"],
    "scaled flow control": ["7.7.4"],
    "16gt/s": ["7.7.5"],
    "16.0 gt/s": ["7.7.5"],
    "32gt/s": ["7.7.6"],
    "32.0 gt/s": ["7.7.6"],
    "precoding": ["7.7.6.4"],
    "modified ts": ["7.7.6.5", "7.7.6.6", "7.7.6.7", "7.7.6.8"],
    "lane margining": ["7.7.7"],
    "margining": ["7.7.7"],
    "acs": ["7.7.8", "7.7.8.2", "7.7.8.3"],
    "access control": ["7.7.8"],
    "egress control": ["7.7.8.4"],
    "power budgeting": ["7.8.1"],
    "aer": ["7.8.4"],
    "advanced error": ["7.8.4"],
    "uncorrectable error": ["7.8.4.2", "7.8.4.3", "7.8.4.4"],
    "correctable error": ["7.8.4.5", "7.8.4.6"],
    "ecrc": ["7.8.4.7"],
    "header log": ["7.8.4.8"],
    "root error": ["7.8.4.9", "7.8.4.10"],
    "tlp prefix log": ["7.8.4.12"],
    "enhanced allocation": ["7.8.5"],
    "pasid": ["7.8.8"],
    "frs": ["7.8.9"],
    "fpb": ["7.8.10"],
    "flattening portal bridge": ["7.8.10"],
    "virtual channel": ["7.9.1", "7.9.2"],
    "vc": ["7.9.1", "7.9.2"],
    "device serial number": ["7.9.3"],
    "vsec": ["7.9.5"],
    "dvsec": ["7.9.6"],
    "rcrb header": ["7.9.7"],
    "root complex link": ["7.9.8", "7.9.9"],
    "rcec": ["7.9.10"],
    "root complex event collector": ["7.9.10"],
    "multicast": ["7.9.11"],
    "dpa": ["7.9.12"],
    "tph": ["7.9.13"],
    "lnr": ["7.9.14"],
    "dpc": ["7.9.15"],
    "downstream port containment": ["7.9.15"],
    "ptm": ["7.9.16"],
    "precision time": ["7.9.16"],
    "readiness time": ["7.9.17"],
    "hierarchy id": ["7.9.18"],
    "vpd": ["7.9.19"],
    "vital product data": ["7.9.19"],
    "npem": ["7.9.20"],
    "enclosure management": ["7.9.20"],
    "alternate protocol": ["7.9.21"],
    "advanced features": ["7.9.22"],
    "sfi": ["7.9.23"],
    "system firmware intermediary": ["7.9.23"],
    "subsystem vendor id": ["7.9.24"],
    "ssid": ["7.9.24"],
    "topology": ["7.1"],
    "bus number": ["7.3.1", "7.3.2"],
    "type 0": ["7.5.1.2"],
    "type 1": ["7.5.1.3"],
    "bridge control": ["7.5.1.3.13"],
}


# ============================================================
# 工具函式
# ============================================================

def print_separator(char="─", width=70):
    print(char * width)

def print_header(title: str, width=70):
    print_separator("═", width)
    pad = (width - len(title) - 2) // 2
    print("║" + " " * pad + title + " " * (width - pad - len(title) - 2) + "║")
    print_separator("═", width)

def print_section_header(title: str):
    print()
    print_separator("─")
    print(f"  {title}")
    print_separator("─")

def search_toc(query: str) -> List[tuple]:
    """搜尋目錄（子字串匹配）"""
    q = query.lower()
    results = []
    for section, info in CHAPTER7_TOC.items():
        if q in section.lower() or q in info["title"].lower():
            results.append((section, info))
    return results

def search_keywords(query: str) -> List[str]:
    """根據關鍵詞搜尋相關章節"""
    q = query.lower()
    found = set()
    for keyword, sections in KEYWORD_MAP.items():
        if q in keyword or keyword in q:
            found.update(sections)
    for cap_id, info in CAPABILITY_ID_MAP.items():
        if q in cap_id.lower() or q in info["name"].lower():
            found.add(info["section"])
    return list(found)


def _score_token_match(tokens: List[str], target: str) -> int:
    """Return how many tokens appear in target (for ranking)."""
    t = target.lower()
    return sum(1 for tok in tokens if tok and tok in t)


def fuzzy_search(query: str) -> dict:
    """
    模糊搜尋：把 query 拆成 token，對 sections / cap IDs / registers
    全面搜尋，依相關度排序回傳。

    回傳 dict：
      {
        "sections":  [ (section_id, info, score), ... ],
        "caps":      [ (cap_id,     info, score), ... ],
        "registers": [ (reg_name,   data, score), ... ],
      }
    每個 list 依 score 降冪排列。
    """
    if not query.strip():
        return {"sections": [], "caps": [], "registers": []}

    q       = query.strip().lower()
    tokens  = [t for t in re.split(r"[\s\-_/]+", q) if len(t) >= 2]
    if not tokens:
        tokens = [q]

    # ── helpers ──────────────────────────────────────────────────────────────
    def tok_score(target: str) -> int:
        return _score_token_match(tokens, target)

    def any_in(target: str) -> bool:
        t = target.lower()
        return q in t or any(tok in t for tok in tokens)

    def field_score(texts: List[str]) -> int:
        """Sum token hits across multiple text fields."""
        return sum(tok_score(t) for t in texts)

    # ── 1. Sections ───────────────────────────────────────────────────────────
    sec_results = []
    # from KEYWORD_MAP
    kw_secs: set = set()
    for keyword, secs in KEYWORD_MAP.items():
        if any_in(keyword):
            kw_secs.update(secs)

    for sec_id, info in CHAPTER7_TOC.items():
        title = info["title"]
        score = 0
        # exact query in title or section id
        if q in title.lower():    score += 10
        if q in sec_id.lower():   score += 8
        # token hits in title
        score += tok_score(title) * 3
        # keyword map bonus
        if sec_id in kw_secs:     score += 5
        if score > 0:
            sec_results.append((sec_id, info, score))

    sec_results.sort(key=lambda x: (
        -x[2],
        [int(p) for p in x[0].split(".")]
    ))

    # ── 2. Capability IDs ─────────────────────────────────────────────────────
    cap_results = []
    for cap_id, info in CAPABILITY_ID_MAP.items():
        name  = info["name"]
        score = 0
        if q in cap_id.lower():  score += 12
        if q in name.lower():    score += 10
        score += tok_score(name) * 3
        if score > 0:
            cap_results.append((cap_id, info, score))

    cap_results.sort(key=lambda x: -x[2])

    # ── 3. Registers ──────────────────────────────────────────────────────────
    reg_results = []
    for rn, rd in REGISTER_DB.items():
        name_str = rn.replace("_", " ")
        sec_str  = rd.get("section", "")
        off_str  = rd.get("offset",  "")
        score = 0
        if q in name_str.lower():   score += 10
        if q in sec_str.lower():    score += 6
        if q in off_str.lower():    score += 4
        score += tok_score(name_str) * 3
        # search inside bit fields
        for bi in rd["bits"].values():
            if any_in(bi["name"]):  score += 2
            if any_in(bi["desc"]):  score += 1
        if score > 0:
            reg_results.append((rn, rd, score))

    reg_results.sort(key=lambda x: -x[2])

    return {
        "sections":  sec_results,
        "caps":      cap_results,
        "registers": reg_results,
    }

def format_register_info(reg_name: str, reg_data: dict) -> str:
    """格式化暫存器資訊"""
    output = []
    output.append(f"\n暫存器: {reg_name.upper().replace('_', ' ')}")
    output.append(f"章節: {reg_data['section']}  偏移: {reg_data['offset']}  頁碼: {reg_data['page']}")
    output.append("─" * 70)
    output.append(f"{'Bit位置':<12} {'名稱':<35} {'屬性':<8}")
    output.append("─" * 70)
    
    for bit_pos, bit_info in reg_data["bits"].items():
        output.append(f"[{bit_pos}]{' ' * (10 - len(bit_pos))} {bit_info['name']:<35} {bit_info['attr']}")
        # 截短描述以適應顯示
        desc = bit_info['desc']
        if len(desc) > 65:
            # 分行顯示
            words = desc.split(', ')
            line = ""
            for word in words:
                if len(line) + len(word) > 60:
                    output.append(f"{'':>12}   → {line.rstrip(', ')}")
                    line = word + ", "
                else:
                    line += word + ", "
            if line:
                output.append(f"{'':>12}   → {line.rstrip(', ')}")
        else:
            output.append(f"{'':>12}   → {desc}")
    
    return "\n".join(output)


# ============================================================
# 主要功能
# ============================================================

def cmd_toc(args: Optional[List[str]] = None):
    """顯示第七章目錄"""
    print_header(f"{ACTIVE_SPEC.name} Chapter {ACTIVE_SPEC.chapter} - 目錄")
    
    level_filter = None
    if args:
        try:
            level_filter = int(args[0])
        except:
            pass
    
    last_top = None
    for section, info in CHAPTER7_TOC.items():
        depth = len(section.split(".")) - 1  # 0=7, 1=7.1, 2=7.1.1...
        
        if level_filter is not None and depth > level_filter:
            continue
        
        # 章節分隔
        top = section.split(".")[0] + "." + (section.split(".")[1] if len(section.split(".")) > 1 else "")
        if top != last_top and depth == 1:
            print()
            last_top = top
        
        indent = "  " * depth
        page_str = f"p.{info['page']}"
        title_width = 65 - len(indent)
        print(f"{indent}{section:<20} {info['title'][:title_width]:<{title_width}} {page_str}")


def cmd_search(query: str):
    """搜尋相關章節"""
    print_header(f"搜尋: {query}")
    
    # 1. 搜尋目錄
    toc_results = search_toc(query)
    
    # 2. 關鍵詞搜尋
    kw_sections = search_keywords(query)
    kw_results = [(s, CHAPTER7_TOC[s]) for s in kw_sections if s in CHAPTER7_TOC]
    
    # 合併結果
    all_sections = set()
    all_results = []
    for section, info in toc_results + kw_results:
        if section not in all_sections:
            all_sections.add(section)
            all_results.append((section, info))
    
    # 排序
    all_results.sort(key=lambda x: [int(p) for p in x[0].split(".")])
    
    if not all_results:
        print(f"\n  未找到與 '{query}' 相關的章節。")
        print("\n  提示: 嘗試以下關鍵詞:")
        tips = ["command register", "link status", "aer", "msi", "aspm", "l1 pm", "dpc", "ptm", "acs"]
        for tip in tips[:5]:
            print(f"    - {tip}")
        return
    
    print(f"\n  找到 {len(all_results)} 個相關章節:\n")
    for section, info in all_results:
        print(f"  [{section}] {info['title']}  (p.{info['page']})")


def cmd_section(section_num: str):
    """顯示指定章節詳細資訊"""
    if section_num in CHAPTER7_TOC:
        info = CHAPTER7_TOC[section_num]
        print_header(f"Section {section_num}")
        print(f"\n標題: {info['title']}")
        print(f"頁碼: {info['page']}")
        print(f"\nPDF 路徑: {resolve_pdf_path(ACTIVE_SPEC)}")
        
        # 顯示子章節
        children = []
        for s, i in CHAPTER7_TOC.items():
            if s.startswith(section_num + ".") and s.count(".") == section_num.count(".") + 1:
                children.append((s, i))
        
        if children:
            print(f"\n子章節:")
            for child_section, child_info in children:
                print(f"  [{child_section}] {child_info['title']}  (p.{child_info['page']})")
        
        # 顯示對應的暫存器資訊
        for reg_name, reg_data in REGISTER_DB.items():
            if reg_data.get("section") == section_num:
                print(format_register_info(reg_name, reg_data))
    else:
        # 嘗試搜尋
        print(f"\n  章節 '{section_num}' 不存在，嘗試搜尋...\n")
        results = search_toc(section_num)
        if results:
            for section, info in results[:5]:
                print(f"  [{section}] {info['title']}  (p.{info['page']})")
        else:
            print(f"  未找到相關章節。")


def cmd_reg(reg_name: str):
    """查詢暫存器 bit field 詳細說明"""
    reg_name_lower = reg_name.lower().replace(" ", "_").replace("-", "_")
    
    # 完全匹配
    if reg_name_lower in REGISTER_DB:
        print(format_register_info(reg_name_lower, REGISTER_DB[reg_name_lower]))
        return
    
    # 模糊匹配
    matches = [(name, data) for name, data in REGISTER_DB.items()
               if reg_name_lower in name or name in reg_name_lower]
    
    if len(matches) == 1:
        print(format_register_info(matches[0][0], matches[0][1]))
    elif len(matches) > 1:
        print(f"\n找到多個匹配的暫存器:")
        for name, data in matches:
            print(f"  - {name.replace('_', ' ').title()} (Section {data['section']}, p.{data['page']})")
        print(f"\n請使用更精確的名稱。")
    else:
        print(f"\n  未找到暫存器 '{reg_name}'。")
        print(f"\n  可用的暫存器:")
        for name in sorted(REGISTER_DB.keys()):
            print(f"    - {name.replace('_', ' ')}")


def cmd_cap(cap_id: str):
    """查詢 Capability ID"""
    cap_id_upper = cap_id.upper()
    if not cap_id_upper.endswith("H"):
        cap_id_upper += "H"
    if not cap_id_upper.startswith("0") and len(cap_id_upper) <= 2:
        cap_id_upper = "0" + cap_id_upper
    
    # 標準化格式
    candidates = [cap_id_upper, cap_id.upper()]
    
    found = None
    for candidate in candidates:
        for key, info in CAPABILITY_ID_MAP.items():
            if key.upper() == candidate.upper():
                found = (key, info)
                break
        if found:
            break
    
    if not found:
        # 嘗試搜尋名稱
        query = cap_id.lower()
        matches = [(k, v) for k, v in CAPABILITY_ID_MAP.items()
                   if query in v["name"].lower()]
        
        if matches:
            print(f"\n搜尋 '{cap_id}' 相關 Capability:\n")
            for key, info in matches:
                section = info["section"]
                page = CHAPTER7_TOC.get(section, {}).get("page", "?")
                print(f"  Cap ID: {key:<8} {info['name']}")
                print(f"           章節: {section}  頁碼: p.{page}\n")
        else:
            print(f"\n  未找到 Capability ID '{cap_id}'")
            print(f"\n  所有 Capability IDs:")
            for key, info in sorted(CAPABILITY_ID_MAP.items()):
                print(f"    {key:<8} {info['name']}")
        return
    
    key, info = found
    section = info["section"]
    page = CHAPTER7_TOC.get(section, {}).get("page", "?")
    
    print_header(f"Capability ID: {key}")
    print(f"\n名稱: {info['name']}")
    print(f"章節: {section}")
    print(f"頁碼: p.{page}")
    
    # 顯示子章節
    children = [(s, i) for s, i in CHAPTER7_TOC.items()
                if s.startswith(section + ".") and s.count(".") == section.count(".") + 1]
    if children:
        print(f"\n包含暫存器:")
        for child_s, child_i in children:
            print(f"  [{child_s}] {child_i['title']}  (p.{child_i['page']})")


def cmd_attr(attr_name: str):
    """查詢暫存器屬性說明"""
    attr_upper = attr_name.upper()
    if attr_upper in REGISTER_ATTRIBUTES:
        print(f"\n暫存器屬性: {attr_upper}")
        print(f"  {REGISTER_ATTRIBUTES[attr_upper]}")
        
        # 找出使用此屬性的暫存器
        print(f"\n使用此屬性的暫存器欄位範例:")
        count = 0
        for reg_name, reg_data in REGISTER_DB.items():
            for bit_pos, bit_info in reg_data["bits"].items():
                if bit_info["attr"] == attr_upper:
                    print(f"  {reg_name.replace('_',' ').title()} [bit {bit_pos}] - {bit_info['name']}")
                    count += 1
                    if count >= 5:
                        break
            if count >= 5:
                break
    else:
        print(f"\n  未知屬性 '{attr_name}'。")
        print(f"\n  所有暫存器屬性:")
        for attr, desc in REGISTER_ATTRIBUTES.items():
            print(f"  {attr:<8} {desc[:60]}...")


def cmd_list_caps():
    """列出所有 Capability IDs"""
    print_header("PCIe Capability IDs 速查表")
    
    print("\n【PCI Capabilities (Config Space 0x00-0xFF)】")
    print(f"{'Cap ID':<10} {'Capability 名稱':<45} {'章節'}")
    print_separator()
    pci_caps = [(k, v) for k, v in CAPABILITY_ID_MAP.items() if len(k) <= 3]
    for key, info in sorted(pci_caps):
        print(f"{key:<10} {info['name']:<45} {info['section']}")
    
    print("\n【PCI Express Extended Capabilities (Config Space 0x100+)】")
    print(f"{'Cap ID':<10} {'Capability 名稱':<45} {'章節'}")
    print_separator()
    ext_caps = [(k, v) for k, v in CAPABILITY_ID_MAP.items() if len(k) > 3]
    for key, info in sorted(ext_caps):
        section = info["section"]
        page = CHAPTER7_TOC.get(section, {}).get("page", "?")
        print(f"{key:<10} {info['name']:<45} {section} p.{page}")


def cmd_help():
    """顯示幫助"""
    print_header(f"{ACTIVE_SPEC.name} Ch.{ACTIVE_SPEC.chapter} 查詢工具 - 說明")
    
    commands = [
        ("toc [level]", "顯示章節目錄 (level=1顯示主章節, 2顯示子章節...)"),
        ("search <關鍵詞>", "搜尋相關章節 (支援中英文關鍵詞)"),
        ("section <章節號>", "顯示指定章節詳情 (例: section 7.5.3.4)"),
        ("reg <暫存器名稱>", "查詢暫存器 bit field (例: reg link status)"),
        ("cap <Cap ID>", "查詢 Capability ID (例: cap 0001h 或 cap aer)"),
        ("caps", "列出所有 Capability IDs"),
        ("attr <屬性>", "查詢暫存器屬性說明 (例: attr rw1c)"),
        ("help", "顯示此說明"),
        ("quit / exit", "離開程式"),
    ]
    
    print()
    for cmd, desc in commands:
        print(f"  {cmd:<30} {desc}")
    
    print("\n【快速範例】")
    examples = [
        ("search aspm", "搜尋 ASPM 相關章節"),
        ("search 16gt/s", "搜尋 16GT/s 相關章節"),
        ("section 7.5.3.4", "查看 Device Control Register 詳情"),
        ("reg link control", "查看 Link Control 暫存器所有 bits"),
        ("reg device status", "查看 Device Status 暫存器所有 bits"),
        ("cap 0001h", "查詢 AER Extended Capability"),
        ("cap dpc", "搜尋 DPC 相關 Capability"),
        ("attr rw1c", "了解 RW1C 屬性含義"),
    ]
    for example, desc in examples:
        print(f"  > {example:<30} # {desc}")


def interactive_mode():
    """互動模式主迴圈"""
    print_header(f"{ACTIVE_SPEC.name} Base Spec - Chapter {ACTIVE_SPEC.chapter} 查詢工具")
    print()
    print(f"  資料來源: {current_pdf_name(ACTIVE_SPEC)}")
    print(f"  章節範圍: Chapter {ACTIVE_SPEC.chapter} - {ACTIVE_SPEC.chapter_title}")
    print(f"  涵蓋頁碼: pp. {ACTIVE_SPEC.page_start}-{ACTIVE_SPEC.page_end}")
    print()
    print("  輸入 'help' 查看所有命令，輸入 'quit' 離開")
    print()
    
    while True:
        try:
            user_input = input("pcie-ch7> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n再見！")
            break
        
        if not user_input:
            continue
        
        parts = user_input.split(None, 1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        if cmd in ("quit", "exit", "q"):
            print("再見！")
            break
        elif cmd == "help":
            cmd_help()
        elif cmd == "toc":
            level_args = args.split() if args else []
            cmd_toc(level_args)
        elif cmd == "search":
            if args:
                cmd_search(args)
            else:
                print("  用法: search <關鍵詞>")
        elif cmd == "section":
            if args:
                cmd_section(args.strip())
            else:
                print("  用法: section <章節號> (例: section 7.5.3.4)")
        elif cmd == "reg":
            if args:
                cmd_reg(args.strip())
            else:
                print("  用法: reg <暫存器名稱> (例: reg link status)")
        elif cmd == "cap":
            if args:
                cmd_cap(args.strip())
            else:
                print("  用法: cap <Capability ID> (例: cap 0001h)")
        elif cmd == "caps":
            cmd_list_caps()
        elif cmd == "attr":
            if args:
                cmd_attr(args.strip())
            else:
                print("  用法: attr <屬性名稱> (例: attr rw1c)")
        else:
            # 嘗試直接當作搜尋
            print(f"  未知命令 '{cmd}'，嘗試搜尋...\n")
            cmd_search(user_input)


def main():
    if len(sys.argv) > 1:
        # 命令列模式
        cmd = sys.argv[1].lower()
        args = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        
        if cmd == "search":
            cmd_search(args)
        elif cmd == "section":
            cmd_section(args)
        elif cmd == "reg":
            cmd_reg(args)
        elif cmd == "cap":
            cmd_cap(args)
        elif cmd == "caps":
            cmd_list_caps()
        elif cmd == "toc":
            cmd_toc(args.split() if args else [])
        elif cmd == "attr":
            cmd_attr(args)
        elif cmd == "help":
            cmd_help()
        else:
            cmd_search(" ".join(sys.argv[1:]))
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
