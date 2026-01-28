import asyncio
import os
# from scrapers.linkedin_engine import LinkedInEngine # Lazy-loaded in __init__
from utils.email_verifier import email_verifier

class EnrichmentBridge:
    """
    CLARITY PEARL - THE BRIDGE
    Logic to pivot from a business (entity) to a person (lead).
    """
    def __init__(self, page):
        from scrapers.linkedin_engine import LinkedInEngine
        from scrapers.b2b_platform_engine import B2BPlatformEngine
        from scrapers.vertical_niche_engine import VerticalNicheEngine
        from scrapers.intent_signal_engine import IntentSignalEngine
        from scrapers.tech_stack_engine import TechStackEngine
        from scrapers.legal_financial_engine import LegalFinancialEngine
        from scrapers.omega_engine import OmegaEngine
        from dotenv import load_dotenv
        
        self.page = page
        self.linkedin = LinkedInEngine(page)
        self.b2b_hubs = B2BPlatformEngine(page)
        self.verticals = VerticalNicheEngine(page)
        self.intent = IntentSignalEngine(page)
        self.tech = TechStackEngine(page)
        self.legal = LegalFinancialEngine(page)
        self.omega = OmegaEngine(page)
        
        # ZERO-COST MODE: Load configuration
        load_dotenv("zero_cost.env")
        self.zero_cost_mode = os.getenv("AI_VALIDATION_ENABLED", "false").lower() == "false"
        
        # Layer activation flags
        self.layer_config = {
            1: os.getenv("ENABLE_LAYER_1_MAPS", "true").lower() == "true",
            2: os.getenv("ENABLE_LAYER_2_REPUTATION", "true").lower() == "true",
            3: os.getenv("ENABLE_LAYER_3_FUNDING", "false").lower() == "true",
            4: os.getenv("ENABLE_LAYER_4_TECH_STACK", "false").lower() == "true",
            5: os.getenv("ENABLE_LAYER_5_HIRING", "false").lower() == "true",
            6: os.getenv("ENABLE_LAYER_6_PATENTS", "false").lower() == "true",
            7: os.getenv("ENABLE_LAYER_7_SOCIAL", "true").lower() == "true",
            8: os.getenv("ENABLE_LAYER_8_TRADE", "false").lower() == "true",
            9: os.getenv("ENABLE_LAYER_9_EVENTS", "false").lower() == "true",
            10: os.getenv("ENABLE_LAYER_10_NEWS", "true").lower() == "true",
            11: os.getenv("ENABLE_LAYER_11_GOV", "false").lower() == "true",
            12: os.getenv("ENABLE_LAYER_12_FIRMOGRAPHICS", "false").lower() == "true",
            13: os.getenv("ENABLE_LAYER_13_ACADEMIC", "false").lower() == "true",
        }
        
        if self.zero_cost_mode:
            print("🔴 ZERO-COST MODE ACTIVE: Disabled API-dependent layers")
            disabled = [k for k, v in self.layer_config.items() if not v]
            print(f"   Disabled Layers: {disabled}")
            print(f"   Active Layers: {[k for k,v in self.layer_config.items() if v]}")

    async def omega_protocol_sweep(self, lead):
        """
        The Omega Protocol: Reaching 1000/1000 certainty.
        Exhausts 13 layers of discovery for a single lead.
        """
        name = lead.get('name')
        print(f"🌌 Executing Omega Protocol for '{name}'...")
        
        # Parallel Execution of all 6 specialized engines
        tasks = [
            self.b2b_hubs.unified_b2b_enrich(lead),
            self.verticals.auto_detect_vertical_enrich(lead),
            self.intent.calculate_intent_multiplier(lead),
            self.tech.unified_tech_enrich(lead),
            self.legal.unified_legal_enrich(lead),
            self.omega.unified_omega_enrich(lead)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Calculate Sovereign Clarity Score (Synthetic)
        layer_signals = [
            lead.get('verified_on_clutch'),
            lead.get('funding_stage') != 'Stealth/Unknown',
            lead.get('actively_hiring'),
            bool(lead.get('identified_tech_stack')),
            lead.get('patent_record_found'),
            lead.get('trade_presence'),
            lead.get('is_government_contractor'),
            lead.get('academic_publication_found')
        ]
        
        signal_count = sum(1 for s in layer_signals if s)
        lead['sovereign_signal_strength'] = signal_count
        
        if signal_count >= 5:
            lead['omega_status'] = 'DIAMOND_CLASS'
            print(f"💎 DIAMOND CLASS LEAD DETECTED: {name}")
        elif signal_count >= 3:
            lead['omega_status'] = 'GOLD_CLASS'
        else:
            lead['omega_status'] = 'STANDARD'
            
        return lead

    async def enrich_business_leads(self, leads, target_industry_keywords=None, negative_keywords=None):
        """
        SOVEREIGN INTELLIGENCE: 13-Layer Deep Enrichment
        Activates ALL layers to transform basic leads into premium data assets
        """
        from scrapers.website_engine import WebsiteEngine
        website_engine = WebsiteEngine(self.page)
        
        print(f"🌉 Bridge: Enriching {len(leads)} leads with 13-Layer Sovereignty...")
        
        # Default Keywords if none provided
        if not target_industry_keywords:
            target_industry_keywords = ["marketing", "agency", "digital", "creative", "seo", "media", "growth", "advertising", "web"]
        if not negative_keywords:
            negative_keywords = ["trucking", "logistics", "shipping", "freight", "loan", "lending", "insurance", "real estate", "cleaning"]

        for lead in leads:
            # Check for cancellation signal (if possible, though bridge doesn't have job_id here)
            # We'll rely on the controller to stop iterating
            
            company_name = lead.get('name', '').strip()

            
            # PHASE 16 HARDENING: Ignore junk leads without names
            if not company_name:
                print(f"🌉 Bridge: Skipping lead with empty name")
                continue

            # --- THE BOUNCER (Name Filter) ---
            low_name = company_name.lower()
            if any(neg in low_name for neg in negative_keywords):
                print(f"🌉 Bouncer: Flagging '{company_name}' as IRRELEVANT")
                lead['status'] = 'IRRELEVANT'
                enriched_leads.append(lead)
                continue

            # ========== LAYER 1: DISCOVERY (Preserve existing data) ==========
            # Phone, Address, Category already collected from Google Maps
            # CRITICAL: Don't overwrite, just ensure fields exist
            if not lead.get('phone') and lead.get('phones'):
                lead['phone'] = lead['phones'][0] if isinstance(lead['phones'], list) else lead['phones']
            
            # --- WEBSITE DISCOVERY ---
            if not lead.get('website') or "google" in str(lead.get('website')).lower():
                found_url = await website_engine.find_company_website(company_name)
                if found_url:
                    lead['website'] = found_url

            # --- WEBSITE CONTACT EXTRACTION (emails, phones, socials) ---
            if lead.get('website'):
                print(f"   ⛏️ Layer 1: Mining contacts from {lead['website']}...")
                try:
                    scrape_results = await website_engine.scrape(lead['website'])
                    if scrape_results:
                        site_data = scrape_results[0]
                        # Merge extracted data
                        if site_data.get('emails'):
                            lead['emails'] = list(set(lead.get('emails', []) + site_data['emails']))
                            if not lead.get('email') and lead['emails']:
                                lead['email'] = lead['emails'][0]
                        
                        if site_data.get('phones'):
                            lead['phones'] = list(set(lead.get('phones', []) + site_data['phones']))
                            if not lead.get('phone') and lead['phones']:
                                lead['phone'] = lead['phones'][0]
                                
                        if site_data.get('socials'):
                            current_socials = lead.get('socials', {})
                            current_socials.update(site_data['socials'])
                            lead['socials'] = current_socials
                except Exception as e:
                    print(f"   ⚠️ Website mining error: {e}")

            # ========== EMAIL PATTERN GENERATION (High-Yield Fallback) ==========
            # If we have a website but NO email, generate standard patterns
            if lead.get('website') and not lead.get('email'):
                try:
                    import urllib.parse
                    domain = urllib.parse.urlparse(lead['website']).netloc.replace('www.', '')
                    if domain:
                        # Generate "educated guess" patterns
                        patterns = [
                            f"info@{domain}",
                            f"contact@{domain}",
                            f"hello@{domain}",
                            f"support@{domain}"
                        ]
                        # Assign the first one as a high-probability contact
                        lead['email'] = patterns[0]
                        lead['email_source'] = "pattern_generated"
                        lead['email_confidence'] = "Medium"
                        print(f"   📧 Generated email pattern: {lead['email']}")
                except: pass

            # ========== LAYER 2: REPUTATION (Clutch, G2, Trustpilot) ==========
            print(f"   ⭐ Layer 2: Checking reputation for {company_name}...")
            try:
                from scrapers.reputation_engine import ReputationEngine
                rep_engine = ReputationEngine(self.page)
                rep_data = await rep_engine.scrape(company_name)
                if rep_data and len(rep_data) > 0:
                    lead['clutch_rating'] = rep_data[0].get('clutch_rating')
                    lead['g2_rating'] = rep_data[0].get('g2_rating')
                    lead['trustpilot_rating'] = rep_data[0].get('trustpilot_rating')
                    lead['review_count'] = rep_data[0].get('review_count')
                    lead['reputation_score'] = rep_data[0].get('reputation_score')
                    print(f"   ✅ Layer 2: Found reputation data")
            except Exception as e:
                print(f"   ⚠️ Layer 2 skip: {e}")

            # ========== LAYER 3: CAPITAL (SEC EDGAR, Crunchbase) ==========
            if self.layer_config.get(3, False):
                print(f"   💰 Layer 3: Checking funding for {company_name}...")
                try:
                    from scrapers.capital_growth_engine import CapitalGrowthEngine
                    capital_engine = CapitalGrowthEngine(self.page)
                    capital_data = await capital_engine.scrape(company_name)
                    if capital_data and len(capital_data) > 0:
                        lead['funding_stage'] = capital_data[0].get('funding_stage')
                        lead['total_funding'] = capital_data[0].get('total_funding')
                        lead['last_funding_date'] = capital_data[0].get('last_funding_date')
                        lead['investor_count'] = capital_data[0].get('investor_count')
                        print(f"   ✅ Layer 3: Found funding data")
                except Exception as e:
                    print(f"   ⚠️ Layer 3 skip: {e}")
            else:
                print(f"   ⏭️ Layer 3: DISABLED (zero-cost mode)")

            # ========== LAYER 4: TECHNOGRAPHICS (BuiltWith patterns) ==========
            if self.layer_config.get(4, False) and lead.get('website'):
                print(f"   🔧 Layer 4: Detecting tech stack...")
                try:
                    from scrapers.tech_stack_engine import TechStackEngine
                    tech_engine = TechStackEngine(self.page)
                    tech_data = await tech_engine.scrape(lead['website'])
                    if tech_data and len(tech_data) > 0:
                        lead['tech_stack'] = tech_data[0].get('technologies', [])
                        lead['cms_platform'] = tech_data[0].get('cms')
                        lead['ecommerce_platform'] = tech_data[0].get('ecommerce')
                        print(f"   ✅ Layer 4: Detected {len(lead.get('tech_stack', []))} technologies")
                except Exception as e:
                    print(f"   ⚠️ Layer 4 skip: {e}")
            elif not self.layer_config.get(4, False):
                print(f"   ⏭️ Layer 4: DISABLED (zero-cost mode)")

            # ========== LAYER 5: INTENT SIGNALS (Job Boards) ==========
            if self.layer_config.get(5, False):
                print(f"   🎯 Layer 5: Checking hiring activity...")
                try:
                    from scrapers.intent_signal_engine import IntentSignalEngine
                    intent_engine = IntentSignalEngine(self.page)
                    intent_data = await intent_engine.scrape(company_name)
                    if intent_data and len(intent_data) > 0:
                        lead['actively_hiring'] = intent_data[0].get('is_hiring')
                        lead['open_positions'] = intent_data[0].get('job_count')
                        lead['recent_job_titles'] = intent_data[0].get('job_titles', [])
                        print(f"   ✅ Layer 5: Found {lead.get('open_positions', 0)} open positions")
                except Exception as e:
                    print(f"   ⚠️ Layer 5 skip: {e}")
            else:
                print(f"   ⏭️ Layer 5: DISABLED (zero-cost mode)")

            # ========== LAYER 6: INNOVATION (USPTO, Google Patents) ==========
            if self.layer_config.get(6, False):
                print(f"   💡 Layer 6: Searching patents...")
                try:
                    from scrapers.patent_intelligence_engine import PatentIntelligenceEngine
                    patent_engine = PatentIntelligenceEngine(self.page)
                    patent_data = await patent_engine.scrape(company_name)
                    if patent_data and len(patent_data) > 0:
                        lead['patent_count'] = len(patent_data)
                        lead['recent_patents'] = [p.get('title') for p in patent_data[:3] if p.get('title')]
                        lead['innovation_score'] = min(len(patent_data) * 10, 100)
                        print(f"   ✅ Layer 6: Found {lead['patent_count']} patents")
                except Exception as e:
                    print(f"   ⚠️ Layer 6 skip: {e}")
            else:
                print(f"   ⏭️ Layer 6: DISABLED (USPTO API exhausted)")

            # ========== LAYER 8: TRADE DATA (USA Trade Online) ==========
            if self.layer_config.get(8, False):
                print(f"   🚢 Layer 8: Checking import/export...")
                try:
                    from scrapers.trade_data_engine import TradeDataEngine
                    trade_engine = TradeDataEngine(self.page)
                    trade_data = await trade_engine.scrape(company_name)
                    if trade_data and len(trade_data) > 0:
                        lead['imports_exports'] = True
                        lead['trade_volume_usd'] = trade_data[0].get('trade_volume')
                        lead['top_trade_partners'] = trade_data[0].get('partners', [])
                        print(f"   ✅ Layer 8: Found trade data")
                except Exception as e:
                    print(f"   ⚠️ Layer 8 skip: {e}")
            else:
                print(f"   ⏭️ Layer 8: DISABLED (Census API exhausted)")

            # ========== LAYER 9: EVENTS (Eventbrite, Meetup) ==========
            if self.layer_config.get(9, False):
                print(f"   📅 Layer 9: Finding event participation...")
                try:
                    from scrapers.events_networking_engine import EventsNetworkingEngine
                    events_engine = EventsNetworkingEngine(self.page)
                    events_data = await events_engine.scrape(company_name)
                    if events_data and len(events_data) > 0:
                        lead['event_participation_count'] = len(events_data)
                        lead['recent_events'] = [e.get('event_name') for e in events_data[:3] if e.get('event_name')]
                        print(f"   ✅ Layer 9: Found {len(events_data)} events")
                except Exception as e:
                    print(f"   ⚠️ Layer 9 skip: {e}")
            else:
                print(f"   ⏭️ Layer 9: DISABLED (0% success rate)")

            # ========== LAYER 11: PUBLIC SECTOR (SAM.gov, USAspending) ==========
            if self.layer_config.get(11, False):
                print(f"   🏛️ Layer 11: Checking gov contracts...")
                try:
                    from scrapers.government_contracts_engine import GovernmentContractsEngine
                    gov_engine = GovernmentContractsEngine(self.page)
                    gov_data = await gov_engine.scrape(company_name)
                    if gov_data and len(gov_data) > 0:
                        lead['government_contractor'] = True
                        lead['contract_value_total'] = gov_data[0].get('total_value')
                        lead['contract_count'] = len(gov_data)
                        print(f"   ✅ Layer 11: Found {len(gov_data)} gov contracts")
                except Exception as e:
                    print(f"   ⚠️ Layer 11 skip: {e}")
            else:
                print(f"   ⏭️ Layer 11: DISABLED (SAM.gov broken)")

            # ========== LAYER 13: ACADEMIC (PubMed, arXiv) ==========
            if self.layer_config.get(13, False):
                print(f"   🔬 Layer 13: Searching research papers...")
                try:
                    from scrapers.academic_research_engine import AcademicResearchEngine
                    academic_engine = AcademicResearchEngine(self.page)
                    academic_data = await academic_engine.scrape(company_name)
                    if academic_data and len(academic_data) > 0:
                        lead['research_papers_count'] = len(academic_data)
                        lead['recent_publications'] = [p.get('title') for p in academic_data[:3] if p.get('title')]
                        print(f"   ✅ Layer 13: Found {len(academic_data)} publications")
                except Exception as e:
                    print(f"   ⚠️ Layer 13 skip: {e}")
            else:
                print(f"   ⏭️ Layer 13: DISABLED (arXiv noise)")

            # === DECISION MAKER EXTRACTION (LinkedIn - Optional, don't block) ===
            roles = ["Founder", "CEO", "Head of Marketing"]
            for role in roles:
                try:
                    search_query = f'{role} "{company_name}"'
                    person_results = await self.linkedin.scrape(search_query)
                    
                    if person_results and len(person_results) > 0:
                        person = person_results[0]
                        p_company = person.get('company', '').lower()
                        
                        if company_name.lower() in p_company or p_company in company_name.lower():
                            lead['decision_maker_name'] = person.get('name')
                            lead['decision_maker_title'] = person.get('title')
                            lead['decision_maker_linkedin'] = person.get('source_url')
                            if person.get('email'):
                                lead['decision_maker_email'] = person.get('email')
                            print(f"   💎 Found Decision Maker: {lead['decision_maker_name']}")
                            break
                except Exception as dm_err:
                    print(f"   ⚠️ Decision maker search skipped: {dm_err}")
                    continue

            # Calculate enrichment depth
            layer_count = 0
            if lead.get('phone') or lead.get('email'): layer_count += 1  # Layer 1
            if lead.get('reputation_score'): layer_count += 1  # Layer 2
            if lead.get('funding_stage'): layer_count += 1  # Layer 3
            if lead.get('tech_stack'): layer_count += 1  # Layer 4
            if lead.get('actively_hiring'): layer_count += 1  # Layer 5
            if lead.get('patent_count'): layer_count += 1  # Layer 6
            if lead.get('imports_exports'): layer_count += 1  # Layer 8
            if lead.get('event_participation_count'): layer_count += 1  # Layer 9
            if lead.get('government_contractor'): layer_count += 1  # Layer 11
            if lead.get('research_papers_count'): layer_count += 1  # Layer 13
            
            lead['enrichment_layers_active'] = layer_count
            lead['status'] = 'SOVEREIGN' if layer_count >= 6 else 'VERIFIED' if layer_count >= 3 else 'PARTIAL'
            
            print(f"   🎯 {company_name}: {layer_count}/13 layers activated - {lead['status']}")
            yield lead
                
        return


