#!/usr/bin/env python3

import os
import re
import yaml
import datetime
from pathlib import Path
import logging
import glob

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('metadata_update.log'),
        logging.StreamHandler()
    ]
)

class BlogMetadataUpdater:
    def __init__(self, blog_dir):
        self.blog_dir = Path(blog_dir)
        self.stats = {
            'updated': 0,
            'up_to_date': 0,
            'backups_deleted': 0,
            'updated_files': []
        }
        
    def cleanup_backups(self):
        """Delete existing backup files"""
        # Find and delete .bak files
        for bak_file in self.blog_dir.rglob('*.bak'):
            try:
                bak_file.unlink()
                logging.info(f'Deleted backup file {bak_file}')
                self.stats['backups_deleted'] += 1
            except Exception as e:
                logging.error(f'Error deleting backup file {bak_file}: {str(e)}')
                
        # Find and delete backup directories
        for backup_dir in self.blog_dir.glob('**/backup'):
            if backup_dir.is_dir():
                try:
                    for file in backup_dir.glob('*'):
                        file.unlink()
                    backup_dir.rmdir()
                    logging.info(f'Deleted backup directory {backup_dir}')
                    self.stats['backups_deleted'] += 1
                except Exception as e:
                    logging.error(f'Error deleting backup directory {backup_dir}: {str(e)}')
                    
    def extract_metadata(self, content):
        """Extract YAML frontmatter from markdown content"""
        if not content.startswith('---'):
            return None, content
            
        parts = content.split('---', 2)
        if len(parts) < 3:
            return None, content
            
        try:
            metadata = yaml.safe_load(parts[1])
            # Clean up any extra whitespace in the content
            content = parts[2].strip()
            return metadata, content
        except yaml.YAMLError:
            logging.error('Invalid YAML frontmatter')
            return None, content
            
    def generate_excerpt(self, content, max_chars=500):
        """Generate SEO-friendly excerpt from content"""
        # Remove markdown formatting
        clean_content = re.sub(r'[#*`]', '', content)
        # Get first paragraph
        first_para = clean_content.split('\n\n')[0]
        # Limit to max_chars
        excerpt = first_para[:max_chars]
        # Add ellipsis if truncated
        if len(first_para) > max_chars:
            excerpt += '...'
        return excerpt
        
    def optimize_title(self, title):
        """Optimize title for SEO"""
        # Convert to title case
        title = title.title()
        # Remove extra spaces
        title = ' '.join(title.split())
        # Ensure it's not too long
        if len(title) > 60:
            title = title[:57] + '...'
        return title
        
    def needs_update(self, metadata):
        """Check if metadata needs to be updated"""
        required_fields = {
            'author': '4Geeks Academy',
            'template': 'landing_post',
            'status': 'published'
        }
        
        for field, default_value in required_fields.items():
            if field not in metadata or metadata[field] != default_value:
                return True
                
        if 'date' not in metadata:
            return True
            
        if 'excerpt' not in metadata:
            return True
            
        return False
        
    def update_metadata(self, file_path):
        """Update metadata for a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            metadata, main_content = self.extract_metadata(content)
            
            if metadata is None:
                metadata = {}
                
            if not self.needs_update(metadata):
                self.stats['up_to_date'] += 1
                return
                
            # Store original metadata for comparison
            original_metadata = metadata.copy()
            
            # Set default values
            defaults = {
                'author': '4Geeks Academy',
                'template': 'landing_post',
                'status': 'published',
                'date': datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S+00:00')
            }
            
            # Update missing fields
            for key, value in defaults.items():
                if key not in metadata or (key == 'template' and metadata[key] != 'landing_post'):
                    metadata[key] = value
                    
            # Generate excerpt if missing
            if 'excerpt' not in metadata:
                metadata['excerpt'] = self.generate_excerpt(main_content)
                
            # Optimize title
            if 'title' in metadata:
                metadata['title'] = self.optimize_title(metadata['title'])
                
            # Check if any changes were actually made
            if metadata == original_metadata:
                self.stats['up_to_date'] += 1
                return
                
            # Write updated content with exactly one line break between frontmatter and content
            new_content = '---\n'
            new_content += yaml.dump(metadata, allow_unicode=True)
            new_content += '---\n'  # One line break after frontmatter
            new_content += main_content
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
                
            logging.info(f'Updated metadata for {file_path}')
            self.stats['updated'] += 1
            self.stats['updated_files'].append(str(file_path))
            
        except Exception as e:
            logging.error(f'Error processing {file_path}: {str(e)}')
            
    def process_all_files(self):
        """Process all .md files in the blog directory"""
        # First, clean up existing backups
        self.cleanup_backups()
        
        # Process all markdown files
        for md_file in self.blog_dir.glob('*.md'):
            self.update_metadata(md_file)
            
        # Generate report
        self.generate_report()
        
    def generate_report(self):
        """Generate a summary report of the changes"""
        report = "\nMetadata Update Report\n"
        report += "=====================\n"
        
        if self.stats['updated'] == 0 and self.stats['backups_deleted'] == 0:
            report += "NO changes made - all files already up to date!\n"
        else:
            report += f"Files updated: {self.stats['updated']}\n"
            report += f"Files up to date: {self.stats['up_to_date']}\n"
            report += f"Backup files deleted: {self.stats['backups_deleted']}\n"
            
            if self.stats['updated'] > 0:
                report += "\nUpdated files:\n"
                for file in self.stats['updated_files']:
                    report += f"- {file}\n"
                    
        logging.info(report)
        
def main():
    blog_dir = '/home/omar-hidalgo/Documentos/Repositorios/blog/blog'
    updater = BlogMetadataUpdater(blog_dir)
    updater.process_all_files()
    
if __name__ == '__main__':
    main() 