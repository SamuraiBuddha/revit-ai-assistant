#!/usr/bin/env python3
"""
Revit API HTML Documentation Parser
Converts scraped Revit API HTML docs to JSON format for LLM training
"""

import os
import json
from pathlib import Path
from bs4 import BeautifulSoup
from typing import Dict, List, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RevitAPIParser:
    def __init__(self, input_dir: str, output_dir: str):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.json_raw_dir = self.output_dir / "json_raw"
        self.training_data_dir = self.output_dir / "training_data"
        
        # Create output directories
        self.json_raw_dir.mkdir(parents=True, exist_ok=True)
        self.training_data_dir.mkdir(parents=True, exist_ok=True)
        
    def parse_html_file(self, file_path: Path) -> Dict[str, Any]:
        """Parse a single HTML file and extract API documentation"""
        logger.info(f"Parsing: {file_path.name}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'lxml')
        
        data = {
            "file_name": file_path.name,
            "title": self._extract_title(soup),
            "namespace": self._extract_namespace(soup),
            "assembly": self._extract_assembly(soup),
            "inheritance": self._extract_inheritance(soup),
            "syntax": self._extract_syntax(soup),
            "parameters": self._extract_parameters(soup),
            "property_value": self._extract_property_value(soup),
            "exceptions": self._extract_exceptions(soup),
            "remarks": self._extract_remarks(soup),
            "overloads": self._extract_overloads(soup),
            "see_also": self._extract_see_also(soup),
            "api_type": self._determine_api_type(soup),
        }
        
        return data
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract the main title of the API element"""
        title_elem = soup.find('h1', class_='title')
        if title_elem:
            return title_elem.get_text(strip=True)
        return ""
    
    def _extract_namespace(self, soup: BeautifulSoup) -> str:
        """Extract namespace information"""
        namespace_elem = soup.find('a', href=lambda x: x and 'namespace' in x)
        if namespace_elem:
            return namespace_elem.get_text(strip=True)
        return ""
    
    def _extract_assembly(self, soup: BeautifulSoup) -> str:
        """Extract assembly information"""
        assembly_section = soup.find('h5', string='Assembly:')
        if assembly_section:
            assembly_text = assembly_section.find_next_sibling(text=True)
            if assembly_text:
                return assembly_text.strip()
        return ""
    
    def _extract_inheritance(self, soup: BeautifulSoup) -> List[str]:
        """Extract inheritance hierarchy"""
        inheritance = []
        inheritance_section = soup.find('h5', string='Inheritance Hierarchy')
        if inheritance_section:
            hierarchy_list = inheritance_section.find_next('ul')
            if hierarchy_list:
                for li in hierarchy_list.find_all('li'):
                    inheritance.append(li.get_text(strip=True))
        return inheritance
    
    def _extract_syntax(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract multi-language syntax examples"""
        syntax = {}
        syntax_section = soup.find('h2', string='Syntax')
        
        if syntax_section:
            # Look for language tabs
            syntax_container = syntax_section.find_next_sibling('div')
            if syntax_container:
                # C# syntax
                csharp_elem = syntax_container.find('pre', {'lang': 'csharp'})
                if not csharp_elem:
                    csharp_elem = syntax_container.find('pre', class_='csharp')
                if csharp_elem:
                    syntax['csharp'] = csharp_elem.get_text(strip=True)
                
                # VB syntax
                vb_elem = syntax_container.find('pre', {'lang': 'vbnet'})
                if not vb_elem:
                    vb_elem = syntax_container.find('pre', class_='vbnet')
                if vb_elem:
                    syntax['vbnet'] = vb_elem.get_text(strip=True)
                
                # C++ syntax
                cpp_elem = syntax_container.find('pre', {'lang': 'cpp'})
                if not cpp_elem:
                    cpp_elem = syntax_container.find('pre', class_='cpp')
                if cpp_elem:
                    syntax['cpp'] = cpp_elem.get_text(strip=True)
        
        return syntax
    
    def _extract_parameters(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract parameter information"""
        parameters = []
        params_section = soup.find('h5', string='Parameters')
        
        if params_section:
            params_list = params_section.find_next('dl')
            if params_list:
                dt_elements = params_list.find_all('dt')
                dd_elements = params_list.find_all('dd')
                
                for dt, dd in zip(dt_elements, dd_elements):
                    param_name = dt.get_text(strip=True)
                    param_desc = dd.get_text(strip=True)
                    
                    # Extract type if available
                    type_elem = dt.find('a')
                    param_type = type_elem.get_text(strip=True) if type_elem else ""
                    
                    parameters.append({
                        "name": param_name.split()[-1] if param_name else "",
                        "type": param_type,
                        "description": param_desc
                    })
        
        return parameters
    
    def _extract_property_value(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract property value information"""
        prop_section = soup.find('h5', string='Property Value')
        if prop_section:
            prop_content = prop_section.find_next_sibling()
            if prop_content:
                return {
                    "type": prop_content.get_text(strip=True),
                    "description": ""
                }
        return {}
    
    def _extract_exceptions(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract exception information"""
        exceptions = []
        exceptions_section = soup.find('h5', string='Exceptions')
        
        if exceptions_section:
            exceptions_table = exceptions_section.find_next('table')
            if exceptions_table:
                rows = exceptions_table.find_all('tr')[1:]  # Skip header
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 2:
                        exceptions.append({
                            "type": cols[0].get_text(strip=True),
                            "condition": cols[1].get_text(strip=True)
                        })
        
        return exceptions
    
    def _extract_remarks(self, soup: BeautifulSoup) -> str:
        """Extract remarks section"""
        remarks_section = soup.find('h2', string='Remarks')
        if remarks_section:
            remarks_content = []
            sibling = remarks_section.find_next_sibling()
            while sibling and sibling.name != 'h2':
                if sibling.name == 'p':
                    remarks_content.append(sibling.get_text(strip=True))
                sibling = sibling.find_next_sibling()
            return '\n\n'.join(remarks_content)
        return ""
    
    def _extract_overloads(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract method overloads"""
        overloads = []
        overload_section = soup.find('h2', string='Overload List')
        
        if overload_section:
            overload_table = overload_section.find_next('table')
            if overload_table:
                rows = overload_table.find_all('tr')[1:]  # Skip header
                for row in rows:
                    cols = row.find_all('td')
                    if cols:
                        overloads.append({
                            "signature": cols[0].get_text(strip=True),
                            "description": cols[1].get_text(strip=True) if len(cols) > 1 else ""
                        })
        
        return overloads
    
    def _extract_see_also(self, soup: BeautifulSoup) -> List[str]:
        """Extract see also references"""
        see_also = []
        see_also_section = soup.find('h2', string='See Also')
        
        if see_also_section:
            refs_list = see_also_section.find_next('div', class_='seeAlso')
            if refs_list:
                links = refs_list.find_all('a')
                for link in links:
                    see_also.append(link.get_text(strip=True))
        
        return see_also
    
    def _determine_api_type(self, soup: BeautifulSoup) -> str:
        """Determine the type of API element (Method, Property, Class, etc.)"""
        title = self._extract_title(soup)
        
        if 'Method' in title:
            return 'Method'
        elif 'Property' in title:
            return 'Property'
        elif 'Class' in title:
            return 'Class'
        elif 'Interface' in title:
            return 'Interface'
        elif 'Constructor' in title:
            return 'Constructor'
        elif 'Event' in title:
            return 'Event'
        elif 'Enumeration' in title:
            return 'Enumeration'
        else:
            return 'Unknown'
    
    def generate_training_data(self, api_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate Q&A pairs for training from parsed API data"""
        qa_pairs = []
        
        title = api_data.get('title', '')
        namespace = api_data.get('namespace', '')
        api_type = api_data.get('api_type', '')
        
        # Basic information Q&A
        if title:
            qa_pairs.append({
                "question": f"What is {title}?",
                "answer": f"{title} is a {api_type} in the {namespace} namespace of the Revit API."
            })
        
        # Syntax Q&A
        syntax = api_data.get('syntax', {})
        if syntax.get('csharp'):
            qa_pairs.append({
                "question": f"How do I use {title} in C#?",
                "answer": f"Here's the C# syntax for {title}:\n```csharp\n{syntax['csharp']}\n```"
            })
        
        # Parameters Q&A
        parameters = api_data.get('parameters', [])
        if parameters:
            param_list = []
            for param in parameters:
                param_list.append(f"- {param['name']} ({param['type']}): {param['description']}")
            
            qa_pairs.append({
                "question": f"What parameters does {title} accept?",
                "answer": f"{title} accepts the following parameters:\n" + '\n'.join(param_list)
            })
        
        # Exceptions Q&A
        exceptions = api_data.get('exceptions', [])
        if exceptions:
            exc_list = []
            for exc in exceptions:
                exc_list.append(f"- {exc['type']}: {exc['condition']}")
            
            qa_pairs.append({
                "question": f"What exceptions can {title} throw?",
                "answer": f"{title} can throw the following exceptions:\n" + '\n'.join(exc_list)
            })
        
        # Remarks Q&A
        remarks = api_data.get('remarks', '')
        if remarks:
            qa_pairs.append({
                "question": f"What should I know about using {title}?",
                "answer": remarks
            })
        
        return qa_pairs
    
    def process_all_files(self):
        """Process all HTML files in the input directory"""
        html_files = list(self.input_dir.glob('*.html'))
        logger.info(f"Found {len(html_files)} HTML files to process")
        
        all_training_data = []
        
        for html_file in html_files:
            try:
                # Parse HTML
                api_data = self.parse_html_file(html_file)
                
                # Save raw JSON
                json_output_path = self.json_raw_dir / f"{html_file.stem}.json"
                with open(json_output_path, 'w', encoding='utf-8') as f:
                    json.dump(api_data, f, indent=2, ensure_ascii=False)
                
                # Generate training data
                qa_pairs = self.generate_training_data(api_data)
                for qa in qa_pairs:
                    qa['source'] = html_file.name
                    qa['api_element'] = api_data.get('title', '')
                
                all_training_data.extend(qa_pairs)
                
                logger.info(f"Generated {len(qa_pairs)} Q&A pairs from {html_file.name}")
                
            except Exception as e:
                logger.error(f"Error processing {html_file.name}: {str(e)}")
        
        # Save all training data
        training_output_path = self.training_data_dir / "revit_api_qa_pairs.json"
        with open(training_output_path, 'w', encoding='utf-8') as f:
            json.dump(all_training_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Total Q&A pairs generated: {len(all_training_data)}")
        logger.info(f"Training data saved to: {training_output_path}")
        
        return len(all_training_data)


def main():
    # Configure paths
    input_dir = "revit-api-training/raw_data/2025/html"
    output_dir = "revit-api-training/processed_data"
    
    # Create parser instance
    parser = RevitAPIParser(input_dir, output_dir)
    
    # Process all files
    total_qa_pairs = parser.process_all_files()
    
    print(f"\nProcessing complete!")
    print(f"Total Q&A pairs generated: {total_qa_pairs}")
    print(f"Check the output directory: {output_dir}")


if __name__ == "__main__":
    main()
