import asyncio
# from scrapers.linkedin_engine import LinkedInEngine # Lazy-loaded in __init__
from utils.email_verifier import email_verifier

class EnrichmentBridge:
    """
    CLARITY PEARL - THE BRIDGE
    Logic to pivot from a business (entity) to a person (lead).
    """
    def __init__(self, page):
        from scrapers.linkedin_engine import LinkedInEngine
        self.page = page
        self.linkedin = LinkedInEngine(page)

    async def enrich_business_leads(self, leads, target_industry_keywords=None, negative_keywords=None):
        """
        CLARITY PHASE: The "Bouncer" & "Gold Miner" Workflow.
        1. Filter by Name (Bouncer)
        2. Find & Verify Website (Clarity Check)
        3. Extract Decision Makers (Gold Mining)
        """
        from scrapers.website_engine import WebsiteEngine
        website_engine = WebsiteEngine(self.page)
        
        print(f"🌉 Bridge: Enriching {len(leads)} leads with Clarity Protocol...")
        enriched_leads = []
        
        # Default Keywords if none provided (Digital Marketing Context)
        if not target_industry_keywords:
            target_industry_keywords = ["marketing", "agency", "digital", "creative", "seo", "media", "growth", "advertising", "web"]
        if not negative_keywords:
            negative_keywords = ["trucking", "logistics", "shipping", "freight", "loan", "lending", "insurance", "real estate", "cleaning"]

        for lead in leads:
            company_name = lead.get('name', '').strip()
            
            # --- 1. THE BOUNCER (Name Filter) ---
            # If name is obviously wrong, mark as irrelevant immediately
            low_name = company_name.lower()
            if any(neg in low_name for neg in negative_keywords):
                print(f"🌉 Bouncer: Flagging '{company_name}' as IRRELEVANT (Name Mismatch)")
                lead['status'] = 'IRRELEVANT'
                lead['relevance_reason'] = 'Name contains negative keyword'
                enriched_leads.append(lead)
                continue

            # --- 2. WEBSITE DISCOVERY ---
            if not lead.get('source_url') or "google" in lead['source_url'] or "linkedin" in lead['source_url']:
                # We need a real website
                found_url = await website_engine.find_company_website(company_name)
                if found_url:
                    lead['website'] = found_url
                else:
                    print(f"🌉 Bridge: No website found for '{company_name}'. Skipping deep verification.")
            else:
                lead['website'] = lead['source_url']

            # --- 3. INDUSTRY VERIFICATION (Content Check) ---
            if lead.get('website'):
                site_results = await website_engine.scrape(
                    lead['website'], 
                    company_name, 
                    target_keywords=target_industry_keywords, 
                    negative_keywords=negative_keywords
                )
                
                # Merge generic site data
                if site_results:
                    site_data = site_results[0]
                    lead['site_emails'] = site_data.get('emails', [])
                    lead['site_phones'] = site_data.get('phones', [])
                    lead['social_links'] = site_data.get('socials', {})
                    
                    if site_data.get('verified_industry') is False:
                        print(f"🌉 Bouncer: Flagging '{company_name}' as IRRELEVANT (Content Mismatch)")
                        lead['status'] = 'IRRELEVANT'
                        lead['relevance_reason'] = site_data.get('relevance_reason')
                        # We continue adding it, but flagged
                        enriched_leads.append(lead)
                        continue # Skip expensive DM search for irrelevant companies
                    else:
                        lead['verified_industry'] = True

            # --- 4. GOLD MINING (Decision Maker Extraction) ---
            # Search for specific high-value roles
            roles = ["Founder", "CEO", "Head of Marketing"]
            dm_found = False
            
            for role in roles:
                if dm_found: break # Stop if we found a top-level person
                
                search_query = f'{role} "{company_name}"'
                print(f"🌉 Bridge: Hunting for {role} at {company_name}...")
                
                person_results = await self.linkedin.scrape(search_query)
                
                if person_results:
                    # Filter: Ensure the person actually works at OUR company
                    # (LinkedIn search sometimes gives fuzzy matches)
                    person = person_results[0]
                    p_company = person.get('company', '').lower()
                    
                    # Fuzzy match company name
                    if company_name.lower() in p_company or p_company in company_name.lower() or "linkedin" in p_company:
                        lead['decision_maker_name'] = person.get('name')
                        lead['decision_maker_title'] = person.get('title')
                        lead['decision_maker_linkedin'] = person.get('source_url')
                        
                        # --- 5. EMAIL VERIFICATION ---
                        # If we found an email, verify it
                        raw_email = person.get('email')
                        if raw_email:
                            verification = await email_verifier.verify_email(raw_email)
                            lead['decision_maker_email'] = raw_email
                            lead['email_verification'] = verification
                        
                        dm_found = True
                        print(f"💎 Bridge Hit: Found {lead['decision_maker_name']} ({lead['decision_maker_title']})")
                    else:
                        print(f"🔸 Bridge Miss: Match '{person['company']}' != '{company_name}'")

            lead['status'] = 'VERIFIED' if dm_found else 'PARTIAL'
            enriched_leads.append(lead)
                
        return enriched_leads
