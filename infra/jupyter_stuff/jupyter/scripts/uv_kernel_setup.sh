#!/bin/bash
set -e

# Log start of configuration
echo "Starting SageMaker notebook UV setup"

# Define paths
UV_BIN_PATH="$HOME/.local/bin"
CLAIMS_DIR="/home/ec2-user/SageMaker/claims_processing/notebooks"
SCRIPTS_DIR="/home/ec2-user/SageMaker/bin"
JUPYTER_KERNELS_DIR="$HOME/.local/share/jupyter/kernels"

# Clean up previous installation
echo "Cleaning up previous installation..."

# Remove previous kernels
if [ -d "$JUPYTER_KERNELS_DIR/claims-processing-uv" ]; then
    jupyter kernelspec remove -f claims-processing-uv
fi

if [ -d "$JUPYTER_KERNELS_DIR/uv-always-claims" ]; then
    jupyter kernelspec remove -f uv-always-claims
fi

# Remove previous virtual environment
if [ -d "$CLAIMS_DIR/.venv" ]; then
    rm -rf "$CLAIMS_DIR/.venv"
fi

# Remove previous helper scripts
if [ -d "$SCRIPTS_DIR" ]; then
    rm -f "$SCRIPTS_DIR/uv-python-wrapper.sh" "$SCRIPTS_DIR/notebook-uv.sh"
fi

# Install uv
echo "Installing uv"
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$UV_BIN_PATH:$PATH"

# Add uv to PATH permanently
sed -i '/export PATH=".*\.local\/bin.*"/d' ~/.bashrc
echo "export PATH=\"$UV_BIN_PATH:\$PATH\"" >> ~/.bashrc

# Create directories
mkdir -p $CLAIMS_DIR
mkdir -p $SCRIPTS_DIR

# Create virtual environment
cd $CLAIMS_DIR
echo "Creating uv virtual environment"
$UV_BIN_PATH/uv venv --seed

# Activate and install minimal packages
source $CLAIMS_DIR/.venv/bin/activate
echo "Installing ipykernel (required)"
$UV_BIN_PATH/uv add ipykernel 
$UV_BIN_PATH/uv add jupyter 
$UV_BIN_PATH/uv add anthropic-bedrock 

# Create helper scripts
cat > $SCRIPTS_DIR/uv-python-wrapper.sh << EOF
#!/bin/bash
$UV_BIN_PATH/uv run python "\$@"
EOF
chmod +x $SCRIPTS_DIR/uv-python-wrapper.sh

cat > $SCRIPTS_DIR/notebook-uv.sh << EOF
#!/bin/bash
cd $CLAIMS_DIR
source .venv/bin/activate
$UV_BIN_PATH/uv "\$@"
EOF
chmod +x $SCRIPTS_DIR/notebook-uv.sh

# Create Jupyter kernels
echo "Creating Jupyter kernels"
python -m ipykernel install --user --name=claims-processing-uv --display-name="Python (claims_processing uv)"

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
   "PATH": "$UV_BIN_PATH:$CLAIMS_DIR/.venv/bin:\${PATH}",
   "PYTHONPATH": "$CLAIMS_DIR/.venv/lib/python3.9/site-packages:\${PYTHONPATH:-}"
 }
}
EOF

# Create magic command file for notebooks
cat > $CLAIMS_DIR/uv_magic.py << EOF
from IPython.core.magic import register_line_magic, Magics, magics_class
import subprocess
import sys

@magics_class
class UVMagics(Magics):
    @register_line_magic
    def uv(self, line):
        cmd = ['$UV_BIN_PATH/uv'] + line.split()
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd='$CLAIMS_DIR')
            print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
            return result.returncode
        except Exception as e:
            print(f"Error executing uv command: {e}", file=sys.stderr)
            return 1

def load_ipython_extension(ipython):
    ipython.register_magics(UVMagics)
EOF

echo "==================================================="
echo "UV setup complete!"
echo "Available kernels:"
echo "- Python (claims_processing uv)"
echo "- Python (claims_processing uv-always)"
echo ""
echo "In notebooks, use: %load_ext uv_magic"
echo "Then: %uv add <package-name> "
echo "==================================================="