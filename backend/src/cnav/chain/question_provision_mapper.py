"""
Question-Provision Mapping Engine
Maps assessment questions to specific CSA Cyber Essentials provisions using programmatic logic
"""

import re
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class ProvisionMapping:
    provision_id: str
    provision_text: str
    requirement_type: str  # "shall" or "should"
    mapping_confidence: str  # "high", "medium", "low"
    rationale: str
    keywords_matched: List[str]

@dataclass
class QuestionMappingResult:
    question_id: str
    mapped_provisions: List[ProvisionMapping]
    overall_confidence: str
    additional_notes: str

class QuestionProvisionMapper:
    """
    Programmatic mapper for associating questions with CSA provisions using keyword matching and rules
    """
    
    def __init__(self, provisions_data: List[Dict[str, Any]]):
        self.provisions_data = provisions_data
        self.provision_keywords = self._build_provision_keyword_index()
        self.category_mappings = self._build_category_mappings()
        
    def _build_provision_keyword_index(self) -> Dict[str, Dict[str, Any]]:
        """Build keyword index for each provision"""
        keyword_index = {}
        
        # Define keyword patterns for each CSA category
        category_keywords = {
            "A.1": {  # Assets: People
                "keywords": ["training", "awareness", "education", "staff", "employee", "personnel", 
                           "cybersecurity training", "security awareness", "phishing", "social engineering"],
                "group_tags": ["TRAINING", "CONTEXT"],
                "audience": ["HR", "Employee"]
            },
            "A.2": {  # Assets: Hardware and Software
                "keywords": ["inventory", "asset", "hardware", "software", "device", "system", 
                           "laptop", "server", "workstation", "mobile", "equipment"],
                "group_tags": ["HW/SW INV", "BYOD"],
                "audience": ["IT", "Owner"]
            },
            "A.3": {  # Assets: Data
                "keywords": ["data", "information", "classification", "sensitive", "confidential",
                           "personal", "backup", "storage", "disposal", "destruction"],
                "group_tags": ["DATA INV", "DISPOSAL"],
                "audience": ["IT", "Owner"]
            },
            "A.4": {  # Virus and Malware Protection
                "keywords": ["antivirus", "malware", "virus", "endpoint", "protection", "scanning",
                           "quarantine", "threat", "detection", "signatures"],
                "group_tags": ["MALWARE"],
                "audience": ["IT"]
            },
            "A.5": {  # Access Control
                "keywords": ["access", "authentication", "authorization", "password", "login",
                           "user account", "permissions", "privileges", "multi-factor", "MFA"],
                "group_tags": ["ACCT MGMT"],
                "audience": ["IT", "Owner"]
            },
            "A.6": {  # Secure Configuration
                "keywords": ["configuration", "hardening", "security settings", "default", "baseline",
                           "firewall", "network", "secure", "settings"],
                "group_tags": ["FIREWALL", "NETWORK", "WIFI"],
                "audience": ["IT"]
            },
            "A.7": {  # Software Updates
                "keywords": ["update", "patch", "vulnerability", "software update", "security patch",
                           "version", "upgrade", "maintenance"],
                "group_tags": ["PATCH/VULN"],
                "audience": ["IT"]
            },
            "A.8": {  # Backup
                "keywords": ["backup", "restore", "recovery", "data backup", "business continuity",
                           "disaster recovery", "replication"],
                "group_tags": ["BACKUP"],
                "audience": ["IT", "Owner"]
            },
            "A.9": {  # Incident Response
                "keywords": ["incident", "response", "security incident", "breach", "emergency",
                           "contingency", "escalation", "investigation"],
                "group_tags": ["IR/BCP"],
                "audience": ["IT", "Owner"]
            }
        }
        
        # Map each provision to its category keywords
        for provision in self.provisions_data:
            provision_id = provision.get('_id', '')
            provision_text = provision.get('provision', '').lower()
            
            # Determine category from provision ID
            category = provision_id.split('.')[0] + '.' + provision_id.split('.')[1] if '.' in provision_id else ''
            
            # Get category keywords
            category_info = category_keywords.get(category, {})
            
            # Extract keywords from provision text
            provision_specific_keywords = self._extract_keywords_from_text(provision_text)
            
            # Combine category and provision-specific keywords
            all_keywords = category_info.get('keywords', []) + provision_specific_keywords
            
            keyword_index[provision_id] = {
                'provision_data': provision,
                'keywords': all_keywords,
                'category_keywords': category_info.get('keywords', []),
                'group_tags': category_info.get('group_tags', []),
                'audience': category_info.get('audience', [])
            }
        
        return keyword_index
    
    def _extract_keywords_from_text(self, text: str) -> List[str]:
        """Extract relevant keywords from provision text"""
        # Remove common words and extract meaningful terms
        common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'shall', 'should', 'must', 'may', 'can', 'will', 'would', 'could'}
        
        # Split text and filter
        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [word for word in words if len(word) > 3 and word not in common_words]
        
        # Return unique keywords
        return list(set(keywords))
    
    def _build_category_mappings(self) -> Dict[str, List[str]]:
        """Build mappings from categories to provision IDs"""
        category_map = defaultdict(list)
        
        for provision in self.provisions_data:
            provision_id = provision.get('_id', '')
            # Extract category (e.g., A.1, A.2, etc.)
            if '.' in provision_id:
                category = '.'.join(provision_id.split('.')[:2])
                category_map[category].append(provision_id)
        
        return dict(category_map)
    
    def map_single_question(
        self, 
        question: str, 
        question_id: str,
        group_tag: Optional[str] = None,
        audience: Optional[str] = None,
        cyberessentials_requirement: Optional[str] = None
    ) -> QuestionMappingResult:
        """
        Map a single question to relevant CSA provisions using programmatic logic
        """
        question_lower = question.lower()
        mapped_provisions = []
        
        # Step 1: Keyword-based matching
        keyword_matches = self._find_keyword_matches(question_lower)
        
        # Step 2: Group tag matching
        if group_tag:
            group_tag_matches = self._find_group_tag_matches(group_tag)
            keyword_matches.update(group_tag_matches)
        
        # Step 3: Audience matching
        if audience:
            audience_matches = self._find_audience_matches(audience)
            keyword_matches.update(audience_matches)
        
        # Step 4: Category requirement matching
        if cyberessentials_requirement:
            category_matches = self._find_category_matches(cyberessentials_requirement)
            keyword_matches.update(category_matches)
        
        # Convert matches to ProvisionMapping objects
        for provision_id, match_info in keyword_matches.items():
            provision_data = self.provision_keywords[provision_id]['provision_data']
            
            mapping = ProvisionMapping(
                provision_id=provision_id,
                provision_text=provision_data.get('provision', ''),
                requirement_type=provision_data.get('requirement_type', 'should'),
                mapping_confidence=match_info['confidence'],
                rationale=match_info['rationale'],
                keywords_matched=match_info['keywords_matched']
            )
            mapped_provisions.append(mapping)
        
        # Determine overall confidence
        if not mapped_provisions:
            overall_confidence = "low"
            additional_notes = "No clear mapping found using keyword analysis"
        elif any(m.mapping_confidence == "high" for m in mapped_provisions):
            overall_confidence = "high"
            additional_notes = "Strong keyword matches found"
        elif any(m.mapping_confidence == "medium" for m in mapped_provisions):
            overall_confidence = "medium"
            additional_notes = "Moderate keyword matches found"
        else:
            overall_confidence = "low"
            additional_notes = "Weak keyword matches found"
        
        return QuestionMappingResult(
            question_id=question_id,
            mapped_provisions=mapped_provisions,
            overall_confidence=overall_confidence,
            additional_notes=additional_notes
        )
    
    def _find_keyword_matches(self, question_text: str) -> Dict[str, Dict[str, Any]]:
        """Find provisions that match question keywords"""
        matches = {}
        
        for provision_id, provision_info in self.provision_keywords.items():
            keywords = provision_info['keywords']
            matched_keywords = []
            
            for keyword in keywords:
                if keyword.lower() in question_text:
                    matched_keywords.append(keyword)
            
            if matched_keywords:
                # Calculate confidence based on number of matches
                match_count = len(matched_keywords)
                if match_count >= 3:
                    confidence = "high"
                elif match_count >= 2:
                    confidence = "medium"
                else:
                    confidence = "low"
                
                matches[provision_id] = {
                    'confidence': confidence,
                    'rationale': f"Matched {match_count} keywords: {', '.join(matched_keywords)}",
                    'keywords_matched': matched_keywords
                }
        
        return matches
    
    def _find_group_tag_matches(self, group_tag: str) -> Dict[str, Dict[str, Any]]:
        """Find provisions that match the group tag"""
        matches = {}
        
        for provision_id, provision_info in self.provision_keywords.items():
            if group_tag in provision_info.get('group_tags', []):
                matches[provision_id] = {
                    'confidence': "high",
                    'rationale': f"Matched group tag: {group_tag}",
                    'keywords_matched': [group_tag]
                }
        
        return matches
    
    def _find_audience_matches(self, audience: str) -> Dict[str, Dict[str, Any]]:
        """Find provisions that match the target audience"""
        matches = {}
        
        for provision_id, provision_info in self.provision_keywords.items():
            if audience in provision_info.get('audience', []):
                matches[provision_id] = {
                    'confidence': "medium",
                    'rationale': f"Matched audience: {audience}",
                    'keywords_matched': [f"audience:{audience}"]
                }
        
        return matches
    
    def _find_category_matches(self, cyberessentials_requirement: str) -> Dict[str, Dict[str, Any]]:
        """Find provisions that match the cyber essentials requirement category"""
        matches = {}
        
        # Map common requirement names to categories
        requirement_category_map = {
            'people': 'A.1',
            'assets': 'A.2',
            'data': 'A.3',
            'malware': 'A.4',
            'access': 'A.5',
            'configuration': 'A.6',
            'updates': 'A.7',
            'backup': 'A.8',
            'incident': 'A.9'
        }
        
        category = requirement_category_map.get(cyberessentials_requirement.lower())
        if category and category in self.category_mappings:
            for provision_id in self.category_mappings[category]:
                matches[provision_id] = {
                    'confidence': "high",
                    'rationale': f"Matched cyber essentials category: {cyberessentials_requirement}",
                    'keywords_matched': [cyberessentials_requirement]
                }
        
        return matches
    
    def map_multiple_questions(
        self, 
        questions: List[Dict[str, str]]
    ) -> List[QuestionMappingResult]:
        """
        Map multiple questions to provisions in batch
        """
        results = []
        
        for question_data in questions:
            question_id = question_data.get('_id', question_data.get('id', ''))
            question_text = question_data.get('question', '')
            group_tag = question_data.get('group_tag')
            audience = question_data.get('audience')
            cyberessentials_requirement = question_data.get('cyberessentials_requirement')
            
            if question_text and question_id:
                result = self.map_single_question(
                    question=question_text,
                    question_id=question_id,
                    group_tag=group_tag,
                    audience=audience,
                    cyberessentials_requirement=cyberessentials_requirement
                )
                results.append(result)
        
        return results
    
    def get_mapping_statistics(self, results: List[QuestionMappingResult]) -> Dict[str, Any]:
        """
        Generate statistics about mapping results
        """
        total_questions = len(results)
        high_confidence = len([r for r in results if r.overall_confidence == "high"])
        medium_confidence = len([r for r in results if r.overall_confidence == "medium"])
        low_confidence = len([r for r in results if r.overall_confidence == "low"])
        unmapped = len([r for r in results if not r.mapped_provisions])
        
        # Count provision types
        shall_mappings = 0
        should_mappings = 0
        
        for result in results:
            for mapping in result.mapped_provisions:
                if mapping.requirement_type == "shall":
                    shall_mappings += 1
                elif mapping.requirement_type == "should":
                    should_mappings += 1
        
        return {
            "total_questions": total_questions,
            "high_confidence_mappings": high_confidence,
            "medium_confidence_mappings": medium_confidence,
            "low_confidence_mappings": low_confidence,
            "unmapped_questions": unmapped,
            "shall_provision_mappings": shall_mappings,
            "should_provision_mappings": should_mappings,
            "mapping_success_rate": (total_questions - unmapped) / total_questions if total_questions > 0 else 0
        }
    
    def update_question_provisions(self, mapping_results: List[QuestionMappingResult]) -> List[Dict[str, Any]]:
        """
        Convert mapping results back to question data structure with updated provisions
        """
        updated_questions = []
        
        for result in mapping_results:
            provision_ids = [mapping.provision_id for mapping in result.mapped_provisions]
            
            question_update = {
                "_id": result.question_id,
                "provisions": provision_ids,
                "mapping_confidence": result.overall_confidence,
                "mapping_notes": result.additional_notes,
                "mapped_provisions_details": [
                    {
                        "provision_id": mapping.provision_id,
                        "requirement_type": mapping.requirement_type,
                        "confidence": mapping.mapping_confidence,
                        "rationale": mapping.rationale
                    }
                    for mapping in result.mapped_provisions
                ]
            }
            updated_questions.append(question_update)
        
        return updated_questions 