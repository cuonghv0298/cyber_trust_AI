"""
Common types and enums used across API models
"""

from typing import Literal
from enum import Enum

# Audience options for questions
AudienceOptions = Literal[
    "Owner",
    "Purchaser", 
    "IT",
    "HR",
    "Employee"
]

# Group tag options for categorizing questions
GroupTagOptions = Literal[
    'CONTEXT', 
    'TRAINING', 
    'POLICY', 
    'HW/SW INV', 
    'DISPOSAL', 
    'CHANGE',
    'DATA INV', 
    'NETWORK', 
    'PHYS-ENV', 
    'MALWARE', 
    'BACKUP', 
    'IR/BCP',
    'FIREWALL', 
    'WIFI', 
    'VENDOR', 
    'ACCT MGMT', 
    'BYOD', 
    'PATCH/VULN'
]

# Answer status options
AnswerStatusOptions = Literal[
    "draft",
    "submitted", 
    "reviewed",
    "approved",
    "requires_clarification"
]

# Confidence level options
ConfidenceLevelOptions = Literal[
    "very_low",
    "low", 
    "medium",
    "high",
    "very_high"
]

# Risk level options
RiskLevelOptions = Literal[
    "low",
    "medium", 
    "high",
    "critical"
] 