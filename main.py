import subprocess
import os


# Define the path to the requirements.txt file
base_dir = os.path.dirname(__file__)  # Gets the directory of the current script
requirements_path = os.path.join(base_dir, "requirements.txt")

# Read the contents of requirements.txt and display the packages
with open(requirements_path, 'r') as file:
    requirements = file.readlines()
    print("The following packages are required to run this project:")
    for requirement in requirements:
        print(f"  - {requirement.strip()}")

# Ask user if they want to proceed with installing the packages
user_response = input("\nDo you want to install the required packages? (yes/no): ").strip().lower()

if user_response in ['yes', 'y']:
    # Install required libraries
    subprocess.run(["pip", "install", "-r", requirements_path], shell=True)

    # Define the path to the test.py script
    test_script_path = os.path.join(base_dir, "app.py")

    # Run the Streamlit command
    subprocess.run(["streamlit", "run", test_script_path], shell=True)
else:
    print(
        "\nInstallation aborted. Please make sure the required packages are installed before running the application.")
