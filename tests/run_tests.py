"""
Test runner script - runs all unit tests

Usage:
    python run_tests.py              # Run all tests
    python run_tests.py -v           # Run with verbose output
    python run_tests.py test_agent   # Run specific test module
"""
import unittest
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def run_all_tests(verbosity=1, specific_module=None):
    """
    Run all unit tests
    
    Args:
        verbosity: Output verbosity level (1=normal, 2=verbose)
        specific_module: If provided, run only tests from this module
    """
    # Create test loader
    loader = unittest.TestLoader()
    
    # Discover and load tests
    if specific_module:
        # Load specific test module
        try:
            suite = loader.loadTestsFromName(f'tests.{specific_module}')
        except (ImportError, AttributeError) as e:
            print(f"Error loading test module '{specific_module}': {e}")
            return False
    else:
        # Discover all tests in tests directory
        start_dir = os.path.dirname(__file__)
        suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.wasSuccessful():
        print("\n✓ All tests passed!")
    else:
        print("\n✗ Some tests failed")
    
    return result.wasSuccessful()


def main():
    """Main entry point"""
    # Parse command line arguments
    verbosity = 1
    specific_module = None
    
    if '-v' in sys.argv or '--verbose' in sys.argv:
        verbosity = 2
        sys.argv = [arg for arg in sys.argv if arg not in ['-v', '--verbose']]
    
    if len(sys.argv) > 1:
        specific_module = sys.argv[1]
    
    # Run tests
    success = run_all_tests(verbosity=verbosity, specific_module=specific_module)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
