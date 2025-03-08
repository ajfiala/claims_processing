#!/bin/bash
set -e

# Log start of configuration
echo "Starting SageMaker notebook configuration"

# Update system packages
sudo yum update -y

# Install uv for better Python package management
echo "Installing uv Python package manager"
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to the PATH - make sure this path is correct and actually exists
UV_BIN_PATH="$HOME/.local/bin"
export PATH="$UV_BIN_PATH:$PATH"

# Explicitly verify uv is installed and in PATH
if ! command -v uv &> /dev/null; then
    echo "ERROR: uv command not found in PATH after installation!"
    echo "Current PATH: $PATH"
    echo "Checking if uv exists at $UV_BIN_PATH:"
    ls -la $UV_BIN_PATH || echo "Directory doesn't exist!"
    exit 1
fi

echo "uv successfully installed and in PATH: $(which uv)"

# Add uv to PATH permanently - for all future sessions
echo "export PATH=\"$UV_BIN_PATH:\$PATH\"" >> ~/.bashrc
echo "export PATH=\"$UV_BIN_PATH:\$PATH\"" >> ~/.bash_profile

# Create directory for the claims_processing project
CLAIMS_DIR="/home/ec2-user/SageMaker/claims_processing"
echo "Setting up claims_processing directory at $CLAIMS_DIR"
mkdir -p $CLAIMS_DIR

# Clone the git repo if needed (assuming the repo URL is set as a parameter)
if [ ! -d "$CLAIMS_DIR/.git" ]; then
  echo "Initializing git repository in claims_processing folder"
  cd $CLAIMS_DIR
  git init
fi

# Set up uv in the claims_processing directory
echo "Setting up uv virtual environment in claims_processing"
cd $CLAIMS_DIR

# Create a uv virtual environment
echo "Creating uv virtual environment"
$UV_BIN_PATH/uv venv --seed --link-mode=copy

# Install required packages in the virtual environment
echo "Installing required Python packages"
source $CLAIMS_DIR/.venv/bin/activate

# Verify path inside the virtual environment
echo "PATH inside virtual environment: $PATH"
echo "Python being used: $(which python)"
echo "uv being used: $(which uv)"

# Install packages using absolute path to uv
$UV_BIN_PATH/uv pip install ipykernel jupyter pandas numpy matplotlib seaborn scikit-learn scipy boto3 jupyter jupyterlab \
    ipywidgets plotly statsmodels nltk spacy sagemaker awswrangler psycopg2-binary

# Register the uv environment as a Jupyter kernel
echo "Creating Jupyter kernel for uv claims_processing"
python -m ipykernel install --user --name=claims-processing-uv --display-name="Python (claims_processing uv)"

# Create helper scripts directory
SCRIPTS_DIR="/home/ec2-user/SageMaker/bin"
echo "Creating helper scripts in $SCRIPTS_DIR"
mkdir -p $SCRIPTS_DIR

# Create uv Python wrapper with absolute path
cat > $SCRIPTS_DIR/uv-python-wrapper.sh << EOF
#!/bin/bash
# Wrapper to run Python through uv
UV_PATH="$UV_BIN_PATH/uv"
\$UV_PATH run python "\$@"
EOF
chmod +x $SCRIPTS_DIR/uv-python-wrapper.sh

# Create notebook uv script with absolute path
cat > $SCRIPTS_DIR/notebook-uv.sh << EOF
#!/bin/bash
# Execute uv commands from within a Jupyter notebook
cd $CLAIMS_DIR
source .venv/bin/activate
$UV_BIN_PATH/uv "\$@"
EOF
chmod +x $SCRIPTS_DIR/notebook-uv.sh

# Set up a Jupyter kernel that forces all execution through uv
echo "Creating a Jupyter kernel that forces uv execution"
mkdir -p $HOME/.local/share/jupyter/kernels/uv-always-claims
cat > $HOME/.local/share/jupyter/kernels/uv-always-claims/kernel.json << EOF
{
 "argv": [
  "$SCRIPTS_DIR/uv-python-wrapper.sh",
  "-m",
  "ipykernel_launcher",
  "-f",
  "{connection_file}"
 ],
 "display_name": "Python (claims_processing uv-always)",
 "language": "python",
 "env": {
   "PATH": "$UV_BIN_PATH:$CLAIMS_DIR/.venv/bin:\${PATH}"
 }
}
EOF

# Add the scripts directory to PATH for easy access
echo "export PATH=\"$SCRIPTS_DIR:\$PATH\"" >> ~/.bashrc

# Set up bash profile for Jupyter
if [ -f $HOME/.bash_profile ]; then
    echo "Updating .bash_profile with PATH settings"
    echo "export PATH=\"$UV_BIN_PATH:$SCRIPTS_DIR:\$PATH\"" >> $HOME/.bash_profile
fi

# Add a test script to verify uv works in Jupyter
cat > $CLAIMS_DIR/test_uv.py << EOF
import sys
import os
print("Python executable:", sys.executable)
print("PATH environment variable:", os.environ.get('PATH'))
print("Working directory:", os.getcwd())
try:
    import subprocess
    result = subprocess.run(['which', 'uv'], capture_output=True, text=True)
    print("uv location:", result.stdout.strip() if result.returncode == 0 else "Not found")
except Exception as e:
    print("Error checking for uv:", str(e))
EOF

echo "Notebook configuration complete. Available kernels:"
echo "- Python (claims_processing uv)"
echo "- Python (claims_processing uv-always)"
echo ""
echo "To install additional packages, you can use:"
echo "   !$SCRIPTS_DIR/notebook-uv.sh add <package-name>"
echo ""
echo "To run a Python script using uv, use:"
echo "   $SCRIPTS_DIR/uv-python-wrapper.sh script.py"
echo ""
echo "A test script has been created at $CLAIMS_DIR/test_uv.py"