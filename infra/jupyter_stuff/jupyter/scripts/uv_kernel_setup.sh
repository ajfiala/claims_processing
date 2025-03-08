#!/bin/bash
# uv_kernel_setup.sh
# Script to set up the uv kernel in Jupyter
# Run this in a Jupyter terminal if the lifecycle configuration didn't work

set -e  # Exit on any error

echo "Starting uv kernel setup..."

# Make sure uv is installed
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    source ~/.bashrc
fi

# Create a directory for the uv environment
mkdir -p ~/SageMaker/uv-env
cd ~/SageMaker/uv-env

echo "Creating uv virtual environment..."
uv venv --seed

# Activate the environment
#!/bin/bash
# setup_uv_sagemaker.sh
# Automates the setup of uv in AWS SageMaker Studio for the pdf-processing-eval repo

set -e  # Exit on any error

echo "Starting uv setup for SageMaker Studio..."

# Define project directory
PROJECT_DIR=~/SageMaker/claims_processing

# Step 1: Install uv if not already installed
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    source ~/.bashrc
fi

# Step 2: Ensure the project directory exists
if [ ! -d "$PROJECT_DIR" ]; then
    echo "Error: Project directory '$PROJECT_DIR' does not exist. Exiting..."
    exit 1
fi

# Step 3: Set up uv in the project directory
echo "Setting up uv in $PROJECT_DIR..."
cd "$PROJECT_DIR"

# If a previous .venv exists, remove it
if [ -d ".venv" ]; then
    echo "Removing existing virtual environment..."
    rm -rf .venv
fi

uv venv --seed

# Step 4: Activate the environment
source .venv/bin/activate

# Step 5: Install required packages
echo "Installing required Python packages..."
uv pip install ipykernel jupyter pandas numpy matplotlib scikit-learn psycopg2-binary boto3

# Step 6: Register the uv environment as the Jupyter kernel
echo "Creating Jupyter kernel for uv..."
python -m ipykernel install --user --name=pdf-processing-uv --display-name="Python (uv pdf-processing-eval)"

# Step 7: Create helper scripts
echo "Creating helper scripts..."
mkdir -p ~/SageMaker/bin

# Wrapper to run Python through uv
cat > ~/SageMaker/bin/uv-python-wrapper.sh << 'EOF'
#!/bin/bash
# Wrapper to run Python through uv
UV_PATH="$HOME/.local/bin/uv"
$UV_PATH run python "$@"
EOF
chmod +x ~/SageMaker/bin/uv-python-wrapper.sh

# Script to execute uv commands inside Jupyter notebooks
cat > ~/SageMaker/bin/notebook-uv.sh << 'EOF'
#!/bin/bash
# Execute uv commands from within a Jupyter notebook
cd ~/SageMaker/pdf-processing-eval
source .venv/bin/activate
uv "$@"
EOF
chmod +x ~/SageMaker/bin/notebook-uv.sh

# Step 8: Set up a Jupyter kernel that forces all execution through uv
echo "Creating a Jupyter kernel that forces uv execution..."
mkdir -p ~/.local/share/jupyter/kernels/uv-always
cat > ~/.local/share/jupyter/kernels/uv-always/kernel.json << EOF
{
 "argv": [
  "$HOME/SageMaker/bin/uv-python-wrapper.sh",
  "-m",
  "ipykernel_launcher",
  "-f",
  "{connection_file}"
 ],
 "display_name": "Python (uv-always pdf-processing)",
 "language": "python",
 "env": {
   "PATH": "$HOME/.local/bin:$PROJECT_DIR/.venv/bin:${PATH}"
 }
}
EOF

# Step 9: Add the ~/SageMaker/bin directory to PATH for easy access
echo 'export PATH="$HOME/SageMaker/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Final Instructions
echo "====================================================="
echo "Setup Complete! Follow these steps to get started:"
echo "====================================================="
echo ""
echo "1. Restart the Jupyter server: File > Hub Control Panel > Stop My Server, then Start My Server"
echo ""
echo "2. After restart, create a new notebook and select 'Python (uv pdf-processing-eval)' or 'Python (uv-always pdf-processing)' kernel"
echo ""
echo "3. To install additional packages in the environment, use:"
echo "   !notebook-uv.sh add <package-name>"
echo ""
echo "4. To run a Python script using uv, use:"
echo "   ~/SageMaker/bin/uv-python-wrapper.sh script.py"
echo ""
echo "====================================================="

exit 0
