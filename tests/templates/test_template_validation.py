"""
Template validation tests to prevent formatting and rendering issues
"""

import pytest
import os
import re
from jinja2 import Environment, FileSystemLoader, select_autoescape
from bs4 import BeautifulSoup


class TestTemplateValidation:
    """Test template syntax and formatting"""
    
    @pytest.fixture
    def jinja_env(self):
        """Create Jinja2 environment with Flask context"""
        from app import app
        with app.app_context():
            template_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'templates')
            env = Environment(
                loader=FileSystemLoader(template_dir),
                autoescape=select_autoescape(['html', 'xml'])
            )
            # Add Flask's url_for function to the environment
            env.globals['url_for'] = app.jinja_env.globals['url_for']
            return env
    
    def test_all_templates_parse(self, jinja_env):
        """Test that all templates parse without syntax errors"""
        template_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'templates')
        
        for filename in os.listdir(template_dir):
            if filename.endswith('.html'):
                try:
                    template = jinja_env.get_template(filename)
                    # Test that template can be parsed
                    assert template is not None
                except Exception as e:
                    pytest.fail(f"Template {filename} failed to parse: {e}")
    
    def test_template_formatting_syntax(self, jinja_env):
        """Test that templates use correct formatting syntax"""
        template_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'templates')
        
        for filename in os.listdir(template_dir):
            if filename.endswith('.html'):
                template_path = os.path.join(template_dir, filename)
                with open(template_path, 'r') as f:
                    content = f.read()
                
                # Check for problematic formatting patterns
                problematic_patterns = [
                    r'\\{:[^}]*\\}.*format',  # {:format} syntax
                    r'\\{:,\\}.*format',      # {:,} syntax
                    r'\\{:\\+\\.[^}]*\\}',    # {:+.} syntax
                ]
                
                for pattern in problematic_patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        pytest.fail(f"Template {filename} contains problematic formatting: {matches}")
    
    def test_template_percentage_formatting(self, jinja_env):
        """Test that percentage formatting is correct"""
        template_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'templates')
        
        for filename in os.listdir(template_dir):
            if filename.endswith('.html'):
                template_path = os.path.join(template_dir, filename)
                with open(template_path, 'r') as f:
                    content = f.read()
                
                # Check for single % in formatting (should be %%)
                # Look for patterns like "%.1f%" which should be "%.1f%%"
                problematic_percentage = re.findall(r'%\\.[0-9]+f%[^%]', content)
                if problematic_percentage:
                    pytest.fail(f"Template {filename} has incorrect percentage formatting: {problematic_percentage}")


class TestTemplateRendering:
    """Test template rendering with sample data"""
    
    @pytest.fixture
    def jinja_env(self):
        """Create Jinja2 environment with Flask context"""
        from app import app
        with app.app_context():
            template_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'templates')
            env = Environment(
                loader=FileSystemLoader(template_dir),
                autoescape=select_autoescape(['html', 'xml'])
            )
            # Add Flask's url_for function to the environment
            env.globals['url_for'] = app.jinja_env.globals['url_for']
            return env
    
    def test_fixed_horizon_results_template(self, jinja_env):
        """Test fixed horizon results template rendering"""
        template = jinja_env.get_template('fixed_horizon_results.html')
        
        # Sample data
        data = {
            'baseline_mean': 100,
            'baseline_std': 20,
            'test_mean': 105,
            'absolute_improvement': 5,
            'relative_improvement': 5,
            'effect_size': 0.25,
            'effect_size_ci_lower': 0.2,
            'effect_size_ci_upper': 0.3,
            'sample_size_per_group': 252,
            'total_sample_size': 504,
            'power': 0.8,
            'alpha': 0.05,
            'test_type': 'two-sided',
            'std_estimated': False
        }
        
        try:
            rendered = template.render(**data)
            assert rendered is not None
            assert 'Sample Size Calculator Results' in rendered
            assert '80.0%' in rendered  # Power formatting
            assert '5.0%' in rendered   # Alpha formatting
            
            # Parse HTML to ensure it's valid
            soup = BeautifulSoup(rendered, 'html.parser')
            assert soup.title is not None
            
        except Exception as e:
            pytest.fail(f"Fixed horizon results template failed to render: {e}")
    
    def test_msprt_results_template(self, jinja_env):
        """Test mSPRT results template rendering"""
        template = jinja_env.get_template('msprt_results.html')
        
        # Sample data
        data = {
            'baseline_mean': 100,
            'baseline_std': 20,
            'std_method': 'Known standard deviation',
            'test_mean': 105,
            'absolute_improvement': 5,
            'relative_improvement': 5,
            'effect_size': 0.25,
            'use_t_test': False,
            'alpha': 0.05,
            'beta': 0.2,
            'power': 0.8,
            'A': 16,
            'B': 0.2105,
            'expected_n_h0': 800,
            'expected_n_h1': 600,
            'max_n': 1000,
            'min_n': 100,
            'efficiency_gain': 40,
            'monitoring_points': [
                {
                    'n': 100,
                    'se': 2.83,
                    'boundary_upper': 5.55,
                    'boundary_lower': -5.55,
                    'ci_lower': -0.55,
                    'ci_upper': 10.55,
                    'rel_ci_lower': -0.55,
                    'rel_ci_upper': 10.55
                }
            ]
        }
        
        try:
            rendered = template.render(**data)
            assert rendered is not None
            assert 'mSPRT' in rendered
            assert '5.0%' in rendered   # Alpha formatting
            assert '20.0%' in rendered  # Beta formatting
            assert '80.0%' in rendered  # Power formatting
            
            # Parse HTML to ensure it's valid
            soup = BeautifulSoup(rendered, 'html.parser')
            assert soup.title is not None
            
        except Exception as e:
            pytest.fail(f"mSPRT results template failed to render: {e}")
    
    def test_std_calculator_results_template(self, jinja_env):
        """Test std calculator results template rendering"""
        template = jinja_env.get_template('std_calculator_results.html')
        
        # Sample data for different methods
        test_cases = [
            {
                'method': 'data',
                'data': {
                    'n': 10,
                    'mean': 5.5,
                    'median': 5.5,
                    'std_dev': 3.02,
                    'variance': 9.17,
                    'min': 1,
                    'max': 10,
                    'cv': 54.9,
                    'sem': 0.96,
                    'ci_lower': 3.67,
                    'ci_upper': 7.33,
                    'ci_margin': 1.83
                }
            },
            {
                'method': 'range',
                'data': {
                    'estimated_std': 5.0,
                    'min_val': 10,
                    'max_val': 30,
                    'range': 20,
                    'method': 'Range Rule (Range ÷ 4)',
                    'accuracy': 'Rough estimate',
                    'mean_estimate': 20,
                    'cv_estimate': 25
                }
            },
            {
                'method': 'percentiles',
                'data': {
                    'estimated_std_iqr': 7.41,
                    'estimated_std_mad': 18.5,
                    'iqr': 10,
                    'q1': 45,
                    'median': 50,
                    'q3': 55,
                    'method': 'Interquartile Range (IQR ÷ 1.35)',
                    'accuracy': 'Good estimate for normal data'
                }
            }
        ]
        
        for test_case in test_cases:
            try:
                rendered = template.render(method=test_case['method'], **test_case['data'])
                assert rendered is not None
                assert 'Standard Deviation' in rendered
                
                # Parse HTML to ensure it's valid
                soup = BeautifulSoup(rendered, 'html.parser')
                assert soup.title is not None
                
            except Exception as e:
                pytest.fail(f"Std calculator results template failed to render for method {test_case['method']}: {e}")
    
    def test_base_template_structure(self, jinja_env):
        """Test that base template has required structure"""
        template = jinja_env.get_template('base.html')
        
        # Minimal data for base template
        data = {}
        
        try:
            rendered = template.render(**data)
            soup = BeautifulSoup(rendered, 'html.parser')
            
            # Check required HTML structure
            assert soup.html is not None
            assert soup.head is not None
            assert soup.body is not None
            assert soup.title is not None
            
        except Exception as e:
            pytest.fail(f"Base template failed to render: {e}")
    
    def test_error_template_rendering(self, jinja_env):
        """Test error template rendering"""
        template = jinja_env.get_template('error.html')
        
        data = {
            'error_message': 'Test error message',
            'back_url': '/test-url'
        }
        
        try:
            rendered = template.render(**data)
            assert rendered is not None
            assert 'Test error message' in rendered
            assert '/test-url' in rendered
            
            # Parse HTML to ensure it's valid
            soup = BeautifulSoup(rendered, 'html.parser')
            assert soup.title is not None
            
        except Exception as e:
            pytest.fail(f"Error template failed to render: {e}")


class TestTemplateAccessibility:
    """Test template accessibility features"""
    
    @pytest.fixture
    def jinja_env(self):
        """Create Jinja2 environment with Flask context"""
        from app import app
        with app.app_context():
            template_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'templates')
            env = Environment(
                loader=FileSystemLoader(template_dir),
                autoescape=select_autoescape(['html', 'xml'])
            )
            # Add Flask's url_for function to the environment
            env.globals['url_for'] = app.jinja_env.globals['url_for']
            return env
    
    def test_templates_have_title(self, jinja_env):
        """Test that all templates have title tags"""
        template_files = ['base.html', 'home.html', 'fixed_horizon_results.html', 
                         'msprt_results.html', 'std_calculator_results.html', 'error.html']
        
        for template_name in template_files:
            try:
                template = jinja_env.get_template(template_name)
                
                # Minimal data for rendering
                data = {}
                if template_name == 'error.html':
                    data = {'error_message': 'Test', 'back_url': '/'}
                elif template_name == 'fixed_horizon_results.html':
                    data = {
                        'baseline_mean': 100, 'baseline_std': 20, 'test_mean': 105,
                        'absolute_improvement': 5, 'relative_improvement': 5,
                        'effect_size': 0.25, 'effect_size_ci_lower': 0.2,
                        'effect_size_ci_upper': 0.3, 'sample_size_per_group': 252,
                        'total_sample_size': 504, 'power': 0.8, 'alpha': 0.05,
                        'test_type': 'two-sided', 'std_estimated': False
                    }
                
                rendered = template.render(**data)
                soup = BeautifulSoup(rendered, 'html.parser')
                
                # Check for title tag
                title = soup.find('title')
                assert title is not None, f"Template {template_name} missing title tag"
                assert title.get_text().strip() != '', f"Template {template_name} has empty title"
                
            except Exception as e:
                pytest.fail(f"Template {template_name} accessibility test failed: {e}")
    
    def test_templates_have_proper_html_structure(self, jinja_env):
        """Test that templates have proper HTML structure"""
        template_files = ['base.html', 'home.html']
        
        for template_name in template_files:
            try:
                template = jinja_env.get_template(template_name)
                rendered = template.render()
                soup = BeautifulSoup(rendered, 'html.parser')
                
                # Check for required HTML elements
                assert soup.html is not None, f"Template {template_name} missing html tag"
                assert soup.head is not None, f"Template {template_name} missing head tag"
                assert soup.body is not None, f"Template {template_name} missing body tag"
                
            except Exception as e:
                pytest.fail(f"Template {template_name} structure test failed: {e}")


class TestTemplateConsistency:
    """Test consistency across templates"""
    
    @pytest.fixture
    def jinja_env(self):
        """Create Jinja2 environment with Flask context"""
        from app import app
        with app.app_context():
            template_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'templates')
            env = Environment(
                loader=FileSystemLoader(template_dir),
                autoescape=select_autoescape(['html', 'xml'])
            )
            # Add Flask's url_for function to the environment
            env.globals['url_for'] = app.jinja_env.globals['url_for']
            return env
    
    def test_all_templates_extend_base(self, jinja_env):
        """Test that all templates extend base template"""
        template_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'templates')
        
        # Templates that should extend base
        extending_templates = [
            'home.html', 'fixed_horizon_results.html', 'msprt_results.html',
            'std_calculator_results.html', 'error.html', 'fixed_horizon_form.html',
            'msprt_form.html', 'std_calculator_form.html'
        ]
        
        for template_name in extending_templates:
            template_path = os.path.join(template_dir, template_name)
            if os.path.exists(template_path):
                with open(template_path, 'r') as f:
                    content = f.read()
                
                # Check that template extends base
                assert 'extends "base.html"' in content, f"Template {template_name} should extend base.html"
    
    def test_navigation_consistency(self, jinja_env):
        """Test that navigation links are consistent"""
        # This test would check that navigation links appear consistently
        # across different templates
        pass  # Implementation depends on specific navigation structure
    
    def test_css_class_consistency(self, jinja_env):
        """Test that CSS classes are used consistently"""
        template_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'templates')
        
        # Common CSS classes that should be used consistently
        expected_classes = [
            'results-grid', 'results-section', 'results-table',
            'sample-size-results', 'navigation-links'
        ]
        
        template_files = [
            'fixed_horizon_results.html', 'msprt_results.html', 'std_calculator_results.html'
        ]
        
        for template_name in template_files:
            template_path = os.path.join(template_dir, template_name)
            if os.path.exists(template_path):
                with open(template_path, 'r') as f:
                    content = f.read()
                
                # Check for presence of expected classes
                for css_class in expected_classes:
                    if css_class in ['results-grid', 'results-section', 'results-table']:
                        assert css_class in content, f"Template {template_name} missing expected class {css_class}"