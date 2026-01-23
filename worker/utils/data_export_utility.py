"""
CLARITY PEARL - B2B DATA EXPORT UTILITY
Exports clean, client-ready CSV files with all contact information.
"""

import os
import csv
import asyncio
from datetime import datetime
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

class DataExportUtility:
    """Exports B2B-ready lead data to CSV format."""
    
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
        if not url or not key:
            raise Exception("Supabase credentials not found in .env")
        self.supabase = create_client(url, key)
    
    def export_job_results(self, job_id, output_path=None, min_clarity_score=50):
        """
        Export all results for a specific job to CSV.
        
        Args:
            job_id: The job ID to export
            output_path: Optional custom output path
            min_clarity_score: Minimum clarity score to include (default 50)
        """
        # Fetch results
        response = self.supabase.table('results').select('*').eq('job_id', job_id).gte('clarity_score', min_clarity_score).execute()
        
        if not response.data:
            print(f"⚠️ No results found for job {job_id} with clarity score >= {min_clarity_score}")
            return None
        
        results = response.data
        print(f"📊 Found {len(results)} qualified leads for export")
        
        # Generate output path
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"exports/job_{job_id[:8]}_{timestamp}.csv"
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Define CSV columns for B2B data
        columns = [
            'Lead Name',
            'Title/Role',
            'Company Name',
            'Company Website',
            'Email',
            'Phone',
            'Location',
            'LinkedIn URL',
            'Facebook URL',
            'Twitter URL',
            'Instagram URL',
            'Lead Score',
            'Intent Score',
            'Verified',
            'Source Platform',
            'Capture Date'
        ]
        
        # Extract and write data
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=columns)
            writer.writeheader()
            
            stats = {
                'total': len(results),
                'with_email': 0,
                'with_phone': 0,
                'with_location': 0,
                'with_socials': 0,
                'verified': 0
            }
            
            for result in results:
                payload = result.get('data_payload', {})
                
                # Extract contact data
                email = payload.get('email') or payload.get('decision_maker_email') or ''
                phone = payload.get('phone') or payload.get('phones', [None])[0] or ''
                location = payload.get('location') or payload.get('address') or ''
                
                # Extract social media
                socials = payload.get('socials', {})
                linkedin = payload.get('linkedin_url') or payload.get('source_url', '') if 'linkedin.com' in payload.get('source_url', '') else socials.get('linkedin', '')
                facebook = socials.get('facebook', '')
                twitter = socials.get('twitter', '')
                instagram = socials.get('instagram', '')
                
                # Update stats
                if email: stats['with_email'] += 1
                if phone: stats['with_phone'] += 1
                if location: stats['with_location'] += 1
                if linkedin or facebook or twitter or instagram: stats['with_socials'] += 1
                if result.get('verified'): stats['verified'] += 1
                
                row = {
                    'Lead Name': payload.get('name') or payload.get('decision_maker_name') or payload.get('full_name') or 'N/A',
                    'Title/Role': payload.get('title') or payload.get('decision_maker_title') or payload.get('job') or '',
                    'Company Name': payload.get('company') or '',
                    'Company Website': payload.get('website') or payload.get('source_url', ''),
                    'Email': email,
                    'Phone': phone,
                    'Location': location,
                    'LinkedIn URL': linkedin,
                    'Facebook URL': facebook,
                    'Twitter URL': twitter,
                    'Instagram URL': instagram,
                    'Lead Score': result.get('clarity_score', 0),
                    'Intent Score': result.get('intent_score', 0),
                    'Verified': 'Yes' if result.get('verified') else 'No',
                    'Source Platform': payload.get('platform', 'unknown'),
                    'Capture Date': result.get('created_at', '')[:10] if result.get('created_at') else ''
                }
                
                writer.writerow(row)
        
        # Print data quality report
        print(f"\n✅ Export Complete: {output_path}")
        print(f"\n📈 Data Quality Report:")
        print(f"   Total Leads: {stats['total']}")
        print(f"   With Email: {stats['with_email']} ({stats['with_email']/stats['total']*100:.1f}%)")
        print(f"   With Phone: {stats['with_phone']} ({stats['with_phone']/stats['total']*100:.1f}%)")
        print(f"   With Location: {stats['with_location']} ({stats['with_location']/stats['total']*100:.1f}%)")
        print(f"   With Social Media: {stats['with_socials']} ({stats['with_socials']/stats['total']*100:.1f}%)")
        print(f"   Verified: {stats['verified']} ({stats['verified']/stats['total']*100:.1f}%)")
        
        return output_path
    
    def export_recent_verified_leads(self, limit=100, output_path=None):
        """Export the most recent verified leads across all jobs."""
        
        response = self.supabase.table('results').select('*').eq('verified', True).order('created_at', desc=True).limit(limit).execute()
        
        if not response.data:
            print("⚠️ No verified leads found")
            return None
        
        results = response.data
        print(f"📊 Found {len(results)} verified leads")
        
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"exports/verified_leads_{timestamp}.csv"
        
        # Use same export logic as job export
        return self._export_to_csv(results, output_path)
    
    def _export_to_csv(self, results, output_path):
        """Internal method to handle CSV export logic."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        columns = [
            'Lead Name', 'Title/Role', 'Company Name', 'Company Website',
            'Email', 'Phone', 'Location',
            'LinkedIn URL', 'Facebook URL', 'Twitter URL', 'Instagram URL',
            'Lead Score', 'Intent Score', 'Verified', 'Source Platform', 'Capture Date'
        ]
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=columns)
            writer.writeheader()
            
            for result in results:
                payload = result.get('data_payload', {})
                socials = payload.get('socials', {})
                
                row = {
                    'Lead Name': payload.get('name') or payload.get('decision_maker_name') or payload.get('full_name') or 'N/A',
                    'Title/Role': payload.get('title') or payload.get('decision_maker_title') or '',
                    'Company Name': payload.get('company') or '',
                    'Company Website': payload.get('website') or payload.get('source_url', ''),
                    'Email': payload.get('email') or payload.get('decision_maker_email') or '',
                    'Phone': payload.get('phone') or '',
                    'Location': payload.get('location') or payload.get('address') or '',
                    'LinkedIn URL': payload.get('linkedin_url') or socials.get('linkedin', ''),
                    'Facebook URL': socials.get('facebook', ''),
                    'Twitter URL': socials.get('twitter', ''),
                    'Instagram URL': socials.get('instagram', ''),
                    'Lead Score': result.get('clarity_score', 0),
                    'Intent Score': result.get('intent_score', 0),
                    'Verified': 'Yes' if result.get('verified') else 'No',
                    'Source Platform': payload.get('platform', 'unknown'),
                    'Capture Date': result.get('created_at', '')[:10] if result.get('created_at') else ''
                }
                
                writer.writerow(row)
        
        print(f"✅ Export complete: {output_path}")
        return output_path


# CLI Interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Export B2B-ready lead data to CSV")
    parser.add_argument("--job-id", help="Export results for a specific job")
    parser.add_argument("--recent", type=int, help="Export N most recent verified leads")
    parser.add_argument("--output", help="Custom output file path")
    parser.add_argument("--min-score", type=int, default=50, help="Minimum clarity score (default 50)")
    
    args = parser.parse_args()
    
    exporter = DataExportUtility()
    
    if args.job_id:
        exporter.export_job_results(args.job_id, args.output, args.min_score)
    elif args.recent:
        exporter.export_recent_verified_leads(args.recent, args.output)
    else:
        print("❌ Please specify --job-id or --recent")
        print("\nExamples:")
        print("  python data_export_utility.py --job-id abc123")
        print("  python data_export_utility.py --recent 100")
