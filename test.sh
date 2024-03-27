

# run src.main for every file in input
mkdir -p errors
for file in input/*.c; do
    echo "Running src.main on $file"
    python -m src.main --input $file --target_llvm output.ll 2> errors/$(basename $file).err || cp $file errors/$(basename $file).c
done