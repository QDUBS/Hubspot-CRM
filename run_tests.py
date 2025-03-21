import os
import sys
import pytest


def main():
    """Run the tests based on command-line arguments"""
    # Setup environment variables for testing
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'

    # Default arguments
    pytest_args = ['tests']

    # Handle test type specification
    if len(sys.argv) > 1 and sys.argv[1] not in ['-v', '-c']:
        test_type = sys.argv[1]
        if test_type not in ['unit', 'integration', 'functional']:
            print(f"Unknown test type: {test_type}")
            print("Available test types: unit, integration, functional")
            sys.exit(1)

        pytest_args = [f'tests/{test_type}']
        sys.argv.pop(1)  # Remove the test type argument

    # Add verbosity if requested
    if '-v' in sys.argv:
        pytest_args.append('-v')

    # Add coverage if requested
    if '-c' in sys.argv:
        pytest_args.extend(
            ['--cov=app', '--cov-report=term', '--cov-report=html'])

    # Run the tests
    sys.exit(pytest.main(pytest_args))


if __name__ == '__main__':
    main()
