# Compiler

## How to run
### To run the demo script: use the following commands
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
bash demo.sh
```
All the output files + the logs will be stored in the `output` directory.

## Llvm
If llvm complains about a wrong target triple, you can change your target triple in the output files, or change it in `src/llvm/Converter.py` line 128. 
If you dont want to do this, you can install `llvm` via apt, so our program can check the triple himself.